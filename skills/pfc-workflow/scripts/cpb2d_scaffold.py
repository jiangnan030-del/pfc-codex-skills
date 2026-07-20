"""Typed configuration contract for the CPB2D project scaffold."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
from string import Template
import tempfile
from typing import Any, Mapping
import uuid

import yaml


_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_DRIVE_PATTERN = re.compile(r"^[a-zA-Z]:")
_WINDOWS_DEVICES = {
    "con",
    "prn",
    "aux",
    "nul",
    "conin$",
    "conout$",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}
_CASE_FAMILIES = {"intact", "straight_crack", "polyline_reserved"}
_CRACK_TYPES = {"straight", "polyline_reserved"}
_MISSING = object()
_TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates" / "cpb2d-scaffold"
_TEMPLATE_OUTPUTS = {
    "1model.dat": "1model.dat.tpl",
    "2bond.dat": "2bond.dat.tpl",
    "3load.dat": "3load.dat.tpl",
    "4export.dat": "4export.dat.tpl",
    "run_all.dat": "run_all.dat.tpl",
}
_REQUIRED_CASE_FILES = {*_TEMPLATE_OUTPUTS, "fracture.p2fis"}


class ConfigError(ValueError):
    """Raised when an intake file violates the scaffold contract."""


@dataclass(frozen=True)
class ProjectConfig:
    slug: str
    title: str
    pfc_version: str
    random_seed_base: int


@dataclass(frozen=True)
class SpecimenConfig:
    width_mm: float
    height_mm: float
    radius_min_mm: float
    radius_max_mm: float
    porosity: float
    density_kg_m3: float
    damping: float

    @property
    def width_m(self) -> float:
        return self.width_mm / 1000.0

    @property
    def height_m(self) -> float:
        return self.height_mm / 1000.0

    @property
    def radius_min_m(self) -> float:
        return self.radius_min_mm / 1000.0

    @property
    def radius_max_m(self) -> float:
        return self.radius_max_mm / 1000.0


@dataclass(frozen=True)
class ContactConfig:
    family: str
    linear_emod_pa: float
    bond_emod_pa: float
    kratio: float
    pb_ten_pa: float
    pb_coh_pa: float
    pb_fa_deg: float
    friction: float


@dataclass(frozen=True)
class LoadingConfig:
    wall_velocity_m_s: float
    peak_drop_fraction: float
    target_peak_strain_guess: float
    stage_fractions: tuple[float, ...]
    history_interval: int


@dataclass(frozen=True)
class OutputConfig:
    stress_strain: bool
    crack_counts: bool
    heavy_ae: bool


@dataclass(frozen=True)
class CaseConfig:
    name: str
    family: str
    enabled: bool
    experiment_file: str
    crack_enabled: bool
    crack_type: str | None = None
    angle_deg: float | None = None
    distance_mm: float | None = None
    length_mm: float | None = None
    width_mm: float | None = None
    center_x_mm: float | None = None
    center_y_mm: float | None = None


@dataclass(frozen=True)
class ScaffoldConfig:
    project: ProjectConfig
    specimen: SpecimenConfig
    contact_model: ContactConfig
    loading: LoadingConfig
    outputs: OutputConfig
    cases: tuple[CaseConfig, ...]
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class CrackGeometry:
    end1_m: tuple[float, float]
    end2_m: tuple[float, float]
    radius_m: float


@dataclass(frozen=True)
class CreateResult:
    root: Path
    warnings: list[str]
    managed_files: list[str]
    case_order: list[str]


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{field} must be a mapping")
    return value


def _required(mapping: dict[str, Any], key: str, field: str) -> Any:
    value = mapping.get(key, _MISSING)
    if value is _MISSING or value is None:
        raise ConfigError(f"{field}.{key} is required")
    return value


def _has_forbidden_controls(value: str) -> bool:
    return any(character in value for character in ("\r", "\n", "\x00"))


def _string(mapping: dict[str, Any], key: str, field: str) -> str:
    value = _required(mapping, key, field)
    qualified = f"{field}.{key}"
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{qualified} must be a non-empty string")
    if _has_forbidden_controls(value):
        raise ConfigError(f"{qualified} may not contain CR, LF, or NUL")
    return value


def _number(mapping: dict[str, Any], key: str, field: str) -> float:
    value = _required(mapping, key, field)
    qualified = f"{field}.{key}"
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{qualified} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ConfigError(f"{qualified} must be finite")
    return result


def _optional_number(mapping: dict[str, Any], key: str, field: str) -> float | None:
    value = mapping.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{field}.{key} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ConfigError(f"{field}.{key} must be finite")
    return result


def _integer(mapping: dict[str, Any], key: str, field: str) -> int:
    value = _required(mapping, key, field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{field}.{key} must be an integer")
    return value


def _boolean(mapping: dict[str, Any], key: str, field: str) -> bool:
    value = _required(mapping, key, field)
    if not isinstance(value, bool):
        raise ConfigError(f"{field}.{key} must be a boolean")
    return value


def _parse_project(data: dict[str, Any]) -> ProjectConfig:
    section = _mapping(data.get("project"), "project")
    return ProjectConfig(
        slug=_string(section, "slug", "project"),
        title=_string(section, "title", "project"),
        pfc_version=_string(section, "pfc_version", "project"),
        random_seed_base=_integer(section, "random_seed_base", "project"),
    )


def _parse_specimen(data: dict[str, Any]) -> SpecimenConfig:
    section = _mapping(data.get("specimen"), "specimen")
    return SpecimenConfig(
        width_mm=_number(section, "width_mm", "specimen"),
        height_mm=_number(section, "height_mm", "specimen"),
        radius_min_mm=_number(section, "particle_radius_min_mm", "specimen"),
        radius_max_mm=_number(section, "particle_radius_max_mm", "specimen"),
        porosity=_number(section, "target_porosity", "specimen"),
        density_kg_m3=_number(section, "density_kg_m3", "specimen"),
        damping=_number(section, "damping", "specimen"),
    )


def _parse_contact(data: dict[str, Any]) -> ContactConfig:
    section = _mapping(data.get("contact_model"), "contact_model")
    return ContactConfig(
        family=_string(section, "family", "contact_model"),
        linear_emod_pa=_number(section, "linear_emod_pa", "contact_model"),
        bond_emod_pa=_number(section, "bond_emod_pa", "contact_model"),
        kratio=_number(section, "kratio", "contact_model"),
        pb_ten_pa=_number(section, "pb_ten_pa", "contact_model"),
        pb_coh_pa=_number(section, "pb_coh_pa", "contact_model"),
        pb_fa_deg=_number(section, "pb_fa_deg", "contact_model"),
        friction=_number(section, "friction", "contact_model"),
    )


def _parse_loading(data: dict[str, Any]) -> LoadingConfig:
    section = _mapping(data.get("loading"), "loading")
    fractions = _required(section, "stage_fractions", "loading")
    if not isinstance(fractions, list):
        raise ConfigError("loading.stage_fractions must be a list")
    parsed_fractions: list[float] = []
    for index, value in enumerate(fractions):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ConfigError(f"loading.stage_fractions[{index}] must be a number")
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ConfigError(f"loading.stage_fractions[{index}] must be finite")
        parsed_fractions.append(parsed)
    return LoadingConfig(
        wall_velocity_m_s=_number(section, "wall_velocity_m_s", "loading"),
        peak_drop_fraction=_number(section, "peak_drop_fraction", "loading"),
        target_peak_strain_guess=_number(
            section, "target_peak_strain_guess", "loading"
        ),
        stage_fractions=tuple(parsed_fractions),
        history_interval=_integer(section, "history_interval", "loading"),
    )


def _parse_outputs(data: dict[str, Any]) -> OutputConfig:
    section = _mapping(data.get("outputs"), "outputs")
    return OutputConfig(
        stress_strain=_boolean(section, "stress_strain", "outputs"),
        crack_counts=_boolean(section, "crack_counts", "outputs"),
        heavy_ae=_boolean(section, "heavy_ae", "outputs"),
    )


def _parse_cases(data: dict[str, Any]) -> tuple[CaseConfig, ...]:
    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list):
        raise ConfigError("cases must be a list")
    cases: list[CaseConfig] = []
    for index, raw_case in enumerate(raw_cases):
        field = f"cases[{index}]"
        section = _mapping(raw_case, field)
        crack_type = section.get("crack_type")
        if crack_type is not None:
            if not isinstance(crack_type, str) or not crack_type:
                raise ConfigError(f"{field}.crack_type must be a non-empty string")
            if _has_forbidden_controls(crack_type):
                raise ConfigError(f"{field}.crack_type may not contain CR, LF, or NUL")
        cases.append(
            CaseConfig(
                name=_string(section, "case_name", field),
                family=_string(section, "family", field),
                enabled=_boolean(section, "enabled", field),
                experiment_file=_string(section, "experiment_file", field),
                crack_enabled=_boolean(section, "crack_enabled", field),
                crack_type=crack_type,
                angle_deg=_optional_number(section, "angle_deg", field),
                distance_mm=_optional_number(section, "distance_mm", field),
                length_mm=_optional_number(section, "length_mm", field),
                width_mm=_optional_number(section, "width_mm", field),
                center_x_mm=_optional_number(section, "center_x_mm", field),
                center_y_mm=_optional_number(section, "center_y_mm", field),
            )
        )
    return tuple(cases)


def _parse_assumptions(data: dict[str, Any]) -> tuple[str, ...]:
    raw = data.get("assumptions", [])
    if not isinstance(raw, list):
        raise ConfigError("assumptions must be a list of strings")
    assumptions: list[str] = []
    for index, value in enumerate(raw):
        if not isinstance(value, str) or not value:
            raise ConfigError(f"assumptions[{index}] must be a non-empty string")
        if _has_forbidden_controls(value):
            raise ConfigError(f"assumptions[{index}] may not contain CR, LF, or NUL")
        assumptions.append(value)
    return tuple(assumptions)


def _windows_name_key(name: str) -> str:
    return name.rstrip(" .").casefold()


def _validate_slug(value: str, field: str, errors: list[str]) -> None:
    if _has_forbidden_controls(value) or not _SLUG_PATTERN.fullmatch(value):
        errors.append(f"{field} has an unsafe format")
    if _windows_name_key(value) in _WINDOWS_DEVICES:
        errors.append(f"{field} is a reserved Windows device name")


def _unsafe_posix_part(part: str) -> bool:
    base = part.split(".", 1)[0].casefold()
    return (
        part in {"", ".", ".."}
        or part.endswith((".", " "))
        or any(character in part for character in '<>:"|?*')
        or part[0] in "=+@"
        or base in _WINDOWS_DEVICES
    )


def _validate_relative_path(value: str, field: str, errors: list[str]) -> None:
    if _has_forbidden_controls(value):
        errors.append(f"{field} may not contain CR, LF, or NUL")
        return
    parts = value.split("/")
    if (
        "\\" in value
        or value.startswith("/")
        or _DRIVE_PATTERN.match(value)
        or parts[:2] != ["data", "experimental"]
        or len(parts) < 3
        or any(_unsafe_posix_part(part) for part in parts)
    ):
        errors.append(
            f"{field} must be a safe POSIX path under data/experimental"
        )


def _check_finite(field: str, value: float, errors: list[str]) -> bool:
    if not math.isfinite(value):
        errors.append(f"{field} must be finite")
        return False
    return True


def validate_config(config: ScaffoldConfig) -> list[str]:
    """Return every domain validation error found in a typed configuration."""
    errors: list[str] = []

    _validate_slug(config.project.slug, "project.slug", errors)
    if _has_forbidden_controls(config.project.title):
        errors.append("project.title may not contain CR, LF, or NUL")
    if config.project.pfc_version != "6.0":
        errors.append('project.pfc_version must be the string "6.0"')
    if config.project.random_seed_base <= 0:
        errors.append("project.random_seed_base must be a positive integer")

    specimen_values = (
        ("specimen.width_mm", config.specimen.width_mm, True),
        ("specimen.height_mm", config.specimen.height_mm, True),
        ("specimen.particle_radius_min_mm", config.specimen.radius_min_mm, True),
        ("specimen.particle_radius_max_mm", config.specimen.radius_max_mm, True),
        ("specimen.target_porosity", config.specimen.porosity, False),
        ("specimen.density_kg_m3", config.specimen.density_kg_m3, True),
        ("specimen.damping", config.specimen.damping, False),
    )
    for field, value, positive in specimen_values:
        if _check_finite(field, value, errors) and positive and value <= 0:
            errors.append(f"{field} must be positive")
    if (
        math.isfinite(config.specimen.radius_min_mm)
        and math.isfinite(config.specimen.radius_max_mm)
        and config.specimen.radius_min_mm > config.specimen.radius_max_mm
    ):
        errors.append(
            "specimen.particle_radius_min_mm must be less than or equal to "
            "specimen.particle_radius_max_mm"
        )
    if math.isfinite(config.specimen.porosity) and not 0 < config.specimen.porosity < 1:
        errors.append("specimen.target_porosity must be between 0 and 1")
    if math.isfinite(config.specimen.damping) and not 0 <= config.specimen.damping <= 1:
        errors.append("specimen.damping must be between 0 and 1 inclusive")

    contact = config.contact_model
    if _has_forbidden_controls(contact.family) or contact.family != "linearpbond":
        errors.append("contact_model.family must be linearpbond")
    positive_contact = (
        ("linear_emod_pa", contact.linear_emod_pa),
        ("bond_emod_pa", contact.bond_emod_pa),
        ("kratio", contact.kratio),
        ("pb_ten_pa", contact.pb_ten_pa),
        ("pb_coh_pa", contact.pb_coh_pa),
    )
    for name, value in positive_contact:
        field = f"contact_model.{name}"
        if _check_finite(field, value, errors) and value <= 0:
            errors.append(f"{field} must be positive")
    if _check_finite("contact_model.friction", contact.friction, errors):
        if contact.friction < 0:
            errors.append("contact_model.friction must be non-negative")
    if _check_finite("contact_model.pb_fa_deg", contact.pb_fa_deg, errors):
        if not 0 <= contact.pb_fa_deg < 90:
            errors.append("contact_model.pb_fa_deg must be in [0, 90)")

    loading = config.loading
    loading_floats = (
        ("wall_velocity_m_s", loading.wall_velocity_m_s),
        ("peak_drop_fraction", loading.peak_drop_fraction),
        ("target_peak_strain_guess", loading.target_peak_strain_guess),
    )
    for name, value in loading_floats:
        _check_finite(f"loading.{name}", value, errors)
    if math.isfinite(loading.wall_velocity_m_s) and loading.wall_velocity_m_s <= 0:
        errors.append("loading.wall_velocity_m_s must be positive")
    if math.isfinite(loading.peak_drop_fraction) and not 0 < loading.peak_drop_fraction < 1:
        errors.append("loading.peak_drop_fraction must be between 0 and 1")
    if (
        math.isfinite(loading.target_peak_strain_guess)
        and loading.target_peak_strain_guess <= 0
    ):
        errors.append("loading.target_peak_strain_guess must be positive")
    if loading.history_interval <= 0:
        errors.append("loading.history_interval must be a positive integer")

    fractions = loading.stage_fractions
    fractions_finite = True
    for index, value in enumerate(fractions):
        fractions_finite &= _check_finite(
            f"loading.stage_fractions[{index}]", value, errors
        )
    if len(fractions) != 4:
        errors.append("loading.stage_fractions must contain exactly four values")
    elif fractions_finite and not all(0 < value < 1 for value in fractions):
        errors.append("loading.stage_fractions values must be between 0 and 1")
    elif fractions_finite and not all(
        left < right for left, right in zip(fractions, fractions[1:])
    ):
        errors.append("loading.stage_fractions must be strictly increasing")

    for index, assumption in enumerate(config.assumptions):
        if not isinstance(assumption, str) or not assumption:
            errors.append(f"assumptions[{index}] must be a non-empty string")
        elif _has_forbidden_controls(assumption):
            errors.append(f"assumptions[{index}] may not contain CR, LF, or NUL")

    enabled_cases = [case for case in config.cases if case.enabled]
    if not enabled_cases or enabled_cases[0].name != "intact":
        errors.append("cases: first enabled case must be intact")

    seen_names: set[str] = set()
    for index, case in enumerate(config.cases):
        field = f"cases[{index}]"
        _validate_slug(case.name, f"{field}.case_name", errors)
        collision_key = _windows_name_key(case.name)
        if collision_key in seen_names:
            errors.append(f"{field}.case_name duplicates case name {case.name!r}")
        seen_names.add(collision_key)

        if _has_forbidden_controls(case.family) or case.family not in _CASE_FAMILIES:
            errors.append(f"{field}.family must be intact, straight_crack, or polyline_reserved")
        if case.crack_type is not None and (
            _has_forbidden_controls(case.crack_type) or case.crack_type not in _CRACK_TYPES
        ):
            errors.append(f"{field}.crack_type must be straight or polyline_reserved")
        _validate_relative_path(case.experiment_file, f"{field}.experiment_file", errors)

        geometry = (
            ("angle_deg", case.angle_deg),
            ("distance_mm", case.distance_mm),
            ("length_mm", case.length_mm),
            ("width_mm", case.width_mm),
            ("center_x_mm", case.center_x_mm),
            ("center_y_mm", case.center_y_mm),
        )
        for name, value in geometry:
            if value is not None:
                _check_finite(f"{field}.{name}", value, errors)

        is_intact_state = (
            case.name == "intact"
            or case.family == "intact"
            or (case.name == "intact" and not case.crack_enabled)
        )
        if is_intact_state and not (
            case.name == "intact"
            and case.family == "intact"
            and not case.crack_enabled
            and case.crack_type is None
        ):
            errors.append(
                f"{field}: intact requires case_name=intact, family=intact, "
                "crack_enabled=false, and no crack_type"
            )

        is_polyline = (
            case.family == "polyline_reserved" or case.crack_type == "polyline_reserved"
        )
        if is_polyline:
            if case.enabled:
                errors.append(f"{field}.enabled must be false for polyline_reserved")
            if not (
                case.family == "polyline_reserved"
                and case.crack_type == "polyline_reserved"
                and case.crack_enabled
            ):
                errors.append(
                    f"{field}: polyline_reserved requires matching family and "
                    "crack_type with crack_enabled=true"
                )

        is_straight = case.family == "straight_crack" or case.crack_type == "straight"
        if is_straight:
            if not (
                case.family == "straight_crack"
                and case.crack_type == "straight"
                and case.crack_enabled
            ):
                errors.append(
                    f"{field}: straight_crack requires family=straight_crack, "
                    "crack_type=straight, and crack_enabled=true"
                )
            required_geometry = (
                ("angle_deg", case.angle_deg),
                ("length_mm", case.length_mm),
                ("width_mm", case.width_mm),
                ("center_x_mm", case.center_x_mm),
                ("center_y_mm", case.center_y_mm),
            )
            for name, value in required_geometry:
                if value is None:
                    errors.append(f"{field}.{name} is required for a straight crack")
            if case.length_mm is not None and math.isfinite(case.length_mm):
                if case.length_mm <= 0:
                    errors.append(f"{field}.length_mm must be positive")
            if case.width_mm is not None and math.isfinite(case.width_mm):
                if case.width_mm <= 0:
                    errors.append(f"{field}.width_mm must be positive")

        known_enabled_state = (
            case.family == "intact"
            or is_straight
            or is_polyline
        )
        if case.enabled and not known_enabled_state:
            errors.append(f"{field}.family is not a supported enabled case type")

    return errors


def load_intake(path: Path) -> ScaffoldConfig:
    """Load, type, and validate a CPB2D YAML intake file."""
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            raw = yaml.safe_load(stream)
    except OSError as exc:
        raise ConfigError(f"intake path could not be read: {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"intake YAML is invalid: {exc}") from exc

    data = _mapping(raw, "intake")
    config = ScaffoldConfig(
        project=_parse_project(data),
        specimen=_parse_specimen(data),
        contact_model=_parse_contact(data),
        loading=_parse_loading(data),
        outputs=_parse_outputs(data),
        cases=_parse_cases(data),
        assumptions=_parse_assumptions(data),
    )
    errors = validate_config(config)
    if errors:
        raise ConfigError("Invalid intake configuration:\n- " + "\n- ".join(errors))
    return config


def _require_finite_case_value(case: CaseConfig, field: str) -> float:
    value = getattr(case, field)
    if value is None or not math.isfinite(value):
        raise ConfigError(f"case {case.name}: {field} must be a finite number")
    return value


def crack_geometry(case: CaseConfig, specimen: SpecimenConfig) -> CrackGeometry:
    """Calculate a straight-crack cylinder and ensure its full area fits."""
    if not (
        case.family == "straight_crack"
        and case.crack_enabled
        and case.crack_type == "straight"
    ):
        raise ConfigError(f"case {case.name}: straight crack geometry is required")

    angle_deg = _require_finite_case_value(case, "angle_deg")
    length_mm = _require_finite_case_value(case, "length_mm")
    width_mm = _require_finite_case_value(case, "width_mm")
    center_x_mm = _require_finite_case_value(case, "center_x_mm")
    center_y_mm = _require_finite_case_value(case, "center_y_mm")
    if length_mm <= 0:
        raise ConfigError(f"case {case.name}: length_mm must be positive")
    if width_mm <= 0:
        raise ConfigError(f"case {case.name}: width_mm must be positive")

    half_length_m = length_mm / 2000.0
    angle_rad = math.radians(angle_deg)
    center_x_m = center_x_mm / 1000.0
    center_y_m = center_y_mm / 1000.0
    dx_m = half_length_m * math.cos(angle_rad)
    dy_m = half_length_m * math.sin(angle_rad)
    result = CrackGeometry(
        end1_m=(center_x_m - dx_m, center_y_m - dy_m),
        end2_m=(center_x_m + dx_m, center_y_m + dy_m),
        radius_m=width_mm / 2000.0,
    )

    half_specimen_width_m = specimen.width_m / 2.0
    half_specimen_height_m = specimen.height_m / 2.0
    normal_x_extent_m = result.radius_m * abs(math.sin(angle_rad))
    normal_y_extent_m = result.radius_m * abs(math.cos(angle_rad))
    tolerance_m = 1.0e-12
    for endpoint_name, (x_m, y_m) in (
        ("end1_m", result.end1_m),
        ("end2_m", result.end2_m),
    ):
        if (
            abs(x_m) > half_specimen_width_m + tolerance_m
            or abs(y_m) > half_specimen_height_m + tolerance_m
        ):
            raise ConfigError(
                f"case {case.name}: crack endpoint {endpoint_name} is outside specimen"
            )
        if (
            abs(x_m) + normal_x_extent_m
            > half_specimen_width_m + tolerance_m
            or abs(y_m) + normal_y_extent_m
            > half_specimen_height_m + tolerance_m
        ):
            raise ConfigError(
                f"case {case.name}: crack cylinder radius at {endpoint_name} "
                "extends outside specimen"
            )
    return result


def _scientific(value: float) -> str:
    if not math.isfinite(value):
        raise ConfigError("render context numeric values must be finite")
    return format(value, ".6e")


def _pfc_single_line_string(value: str, field: str) -> str:
    if _has_forbidden_controls(value):
        raise ConfigError(f"{field} may not contain CR, LF, or NUL")
    return value.replace("'", "''")


def render_context(
    config: ScaffoldConfig, case: CaseConfig, case_index: int
) -> dict[str, str | int | float]:
    """Build a deterministic, locale-independent, template-safe context."""
    errors = validate_config(config)
    if errors:
        raise ConfigError("Invalid render configuration:\n- " + "\n- ".join(errors))

    if (
        isinstance(case_index, bool)
        or not isinstance(case_index, int)
        or not 0 <= case_index < len(config.cases)
    ):
        raise ConfigError("case_index must identify a configured case")
    if case != config.cases[case_index]:
        raise ConfigError("case must equal the configured case at case_index")

    random_seed = config.project.random_seed_base + case_index
    if not 1 <= random_seed <= 2_147_483_647:
        raise ConfigError("random_seed must be in the PFC integer range [1, 2147483647]")

    specimen = config.specimen
    contact = config.contact_model
    loading = config.loading
    stage_d_strain = (
        loading.target_peak_strain_guess * loading.stage_fractions[3]
    )
    max_abs_strain = max(
        loading.target_peak_strain_guess * 2.0,
        stage_d_strain * 1.25,
    )
    context: dict[str, str | int | float] = {
        "project_slug": config.project.slug,
        "project_title": _pfc_single_line_string(config.project.title, "project.title"),
        "pfc_version": config.project.pfc_version,
        "case_name": case.name,
        "random_seed": random_seed,
        "specimen_width_m": _scientific(specimen.width_m),
        "specimen_height_m": _scientific(specimen.height_m),
        "specimen_half_width_m": _scientific(specimen.width_m / 2.0),
        "specimen_half_height_m": _scientific(specimen.height_m / 2.0),
        "domain_half_extent_m": _scientific(
            max(specimen.width_m, specimen.height_m) * 1.25
        ),
        "particle_radius_min_m": _scientific(specimen.radius_min_m),
        "particle_radius_max_m": _scientific(specimen.radius_max_m),
        "target_porosity": _scientific(specimen.porosity),
        "density_kg_m3": _scientific(specimen.density_kg_m3),
        "damping": _scientific(specimen.damping),
        "contact_family": contact.family,
        "linear_emod_pa": _scientific(contact.linear_emod_pa),
        "bond_emod_pa": _scientific(contact.bond_emod_pa),
        "kratio": _scientific(contact.kratio),
        "pb_ten_pa": _scientific(contact.pb_ten_pa),
        "pb_coh_pa": _scientific(contact.pb_coh_pa),
        "pb_fa_deg": _scientific(contact.pb_fa_deg),
        "friction": _scientific(contact.friction),
        "wall_velocity_m_s": _scientific(loading.wall_velocity_m_s),
        "peak_drop_fraction": _scientific(loading.peak_drop_fraction),
        "target_peak_strain_guess": _scientific(loading.target_peak_strain_guess),
        "max_abs_strain": _scientific(max_abs_strain),
        "history_interval": loading.history_interval,
    }
    for label, fraction in zip("abcd", loading.stage_fractions, strict=True):
        context[f"stage_{label}_strain"] = _scientific(
            loading.target_peak_strain_guess * fraction
        )

    warning = ""
    if case.family == "intact" and not case.crack_enabled and case.crack_type is None:
        context["crack_command"] = "; intact case: no crack deletion"
    elif (
        case.family == "straight_crack"
        and case.crack_enabled
        and case.crack_type == "straight"
    ):
        geometry = crack_geometry(case, specimen)
        context["crack_command"] = (
            "ball delete range cylinder "
            f"end-1 {_scientific(geometry.end1_m[0])} {_scientific(geometry.end1_m[1])} "
            f"end-2 {_scientific(geometry.end2_m[0])} {_scientific(geometry.end2_m[1])} "
            f"radius {_scientific(geometry.radius_m)}"
        )
        width_mm = _require_finite_case_value(case, "width_mm")
        threshold_mm = 2.0 * specimen.radius_max_mm
        if width_mm < threshold_mm:
            warning = (
                f"case {case.name}: crack width_mm {_scientific(width_mm)} is less "
                "than twice particle_radius_max_mm "
                f"{_scientific(threshold_mm)}"
            )
    else:
        raise ConfigError(f"case {case.name}: unsupported render case state")

    context["warnings"] = warning
    return context


def render_template(name: str, context: Mapping[str, object]) -> str:
    """Render one allow-listed PFC template and fail on every missing key."""
    if name not in _TEMPLATE_OUTPUTS.values():
        raise ConfigError(f"unknown CPB2D template: {name}")
    template_path = _TEMPLATE_ROOT / name
    return Template(template_path.read_text(encoding="utf-8-sig")).substitute(context)


def render_case_files(
    config: ScaffoldConfig, case: CaseConfig, case_index: int
) -> dict[str, str]:
    """Render the exact six-file PFC2D case contract."""
    context = render_context(config, case, case_index)
    files = {
        output_name: render_template(template_name, context)
        for output_name, template_name in _TEMPLATE_OUTPUTS.items()
    }
    files["fracture.p2fis"] = (_TEMPLATE_ROOT / "fracture.p2fis").read_text(
        encoding="utf-8-sig"
    )
    if set(files) != _REQUIRED_CASE_FILES:
        raise ConfigError("rendered case does not match the six-file contract")
    unresolved = [name for name, text in files.items() if "${" in text]
    if unresolved:
        raise ConfigError(f"unresolved template placeholders in: {', '.join(unresolved)}")
    return files


_MANIFEST_SCHEMA = "cpb2d-scaffold-manifest"
_MANIFEST_VERSION = 2
_RUN_ALL_TEXT = """program call '1model.dat'
program call '2bond.dat'
program call '3load.dat'
program call '4export.dat'
"""
_PROJECT_DIRS = (
    "data/experimental",
    "geometry/cracks",
    "pfc_cases",
    "calibration/trials",
    "postprocess",
    "figures",
    "tables",
    "reports",
)


def _enabled_cases(config: ScaffoldConfig) -> list[tuple[int, CaseConfig]]:
    return [
        (index, case)
        for index, case in enumerate(config.cases)
        if case.enabled
    ]


def project_warnings(config: ScaffoldConfig, output_dir: Path) -> list[str]:
    """Return deterministic warnings using paths relative to the output project."""
    enabled = _enabled_cases(config)
    warnings = [
        f"missing experiment file: {case.experiment_file}"
        for _, case in enabled
        if not (output_dir / PurePosixPath(case.experiment_file)).is_file()
    ]
    warnings.extend(
        warning
        for index, case in enabled
        if (warning := str(render_context(config, case, index)["warnings"]))
    )
    return warnings


def _csv_text(header: list[str], rows: list[list[object]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue()


def _normalized_config(config: ScaffoldConfig) -> dict[str, object]:
    return {
        "schema": "cpb2d-project-config",
        "version": 1,
        "units": {"length_input": "mm", "model_length": "m", "stress": "Pa"},
        "project": {
            "slug": config.project.slug,
            "title": config.project.title,
            "pfc_version": config.project.pfc_version,
            "random_seed_base": config.project.random_seed_base,
        },
        "specimen": {
            "width_mm": config.specimen.width_mm,
            "height_mm": config.specimen.height_mm,
            "particle_radius_min_mm": config.specimen.radius_min_mm,
            "particle_radius_max_mm": config.specimen.radius_max_mm,
            "target_porosity": config.specimen.porosity,
            "density_kg_m3": config.specimen.density_kg_m3,
            "damping": config.specimen.damping,
        },
        "contact_model": {
            "family": config.contact_model.family,
            "linear_emod_pa": config.contact_model.linear_emod_pa,
            "bond_emod_pa": config.contact_model.bond_emod_pa,
            "kratio": config.contact_model.kratio,
            "pb_ten_pa": config.contact_model.pb_ten_pa,
            "pb_coh_pa": config.contact_model.pb_coh_pa,
            "pb_fa_deg": config.contact_model.pb_fa_deg,
            "friction": config.contact_model.friction,
        },
        "loading": {
            "wall_velocity_m_s": config.loading.wall_velocity_m_s,
            "peak_drop_fraction": config.loading.peak_drop_fraction,
            "target_peak_strain_guess": config.loading.target_peak_strain_guess,
            "stage_fractions": list(config.loading.stage_fractions),
            "history_interval": config.loading.history_interval,
        },
        "outputs": {
            "stress_strain": config.outputs.stress_strain,
            "crack_counts": config.outputs.crack_counts,
            "heavy_ae": config.outputs.heavy_ae,
        },
        "assumptions": list(config.assumptions),
    }


def _case_rows(config: ScaffoldConfig) -> list[list[object]]:
    rows: list[list[object]] = []
    for case in config.cases:
        rows.append([
            case.name,
            case.family,
            str(case.enabled).lower(),
            case.experiment_file,
            str(case.crack_enabled).lower(),
            case.crack_type or "",
            "" if case.angle_deg is None else case.angle_deg,
            "" if case.distance_mm is None else case.distance_mm,
            "" if case.length_mm is None else case.length_mm,
            "" if case.width_mm is None else case.width_mm,
            "" if case.center_x_mm is None else case.center_x_mm,
            "" if case.center_y_mm is None else case.center_y_mm,
        ])
    return rows


def _runbook(config: ScaffoldConfig, warnings: list[str]) -> str:
    warning_lines = "\n".join(f"- {warning}" for warning in warnings) or "- none"
    cases = ", ".join(case.name for _, case in _enabled_cases(config))
    return f"""# {config.project.title}: CPB2D runbook

## Contract

- Use an intact-first workflow. Run and inspect `pfc_cases/intact/run_all.dat` before `{cases}`.
- In the PFC GUI, set the working directory to one case directory and call `run_all.dat`; use the equivalent general file-call operation in other PFC interfaces. No machine-specific launch command is assumed.
- Stage A-D files can be a fallback final state when a threshold was not reached.
- `peak.sav` is a confirmed near-peak/post-peak state, not an exact peak rollback.
- heavy AE is disabled in this v1 scaffold. Enable it only after standard files, stages, and input contracts are confirmed.
- Expected standard artifacts include `sample.sav`, `parallel_bonded.sav`, `stage_a.sav` through `stage_d.sav`, `peak.sav`, `final.sav`, `stress_strain.csv`, `stress_strain_step.csv`, and `plotdata_fracture_orientations.csv`.
- After exports exist, read `pfc-postprocessing/references/script-catalog.md` and the selected owning script before postprocessing.

## Missing experiment warnings

{warning_lines}
"""


def _modeling_notes(config: ScaffoldConfig, intake_path: Path) -> str:
    assumption_lines = "\n".join(f"- {value}" for value in config.assumptions)
    if not assumption_lines:
        assumption_lines = "- None recorded."
    return f"""# Modeling notes

- Intake source at generation time: `{intake_path}`.
- Model units are SI; intake lengths are normalized from mm to m.
- Contact model seed family: `{config.contact_model.family}`. Seed parameters are assumptions for trial runs, not final calibrated values.
- The enabled case order is intact-first: {', '.join(case.name for _, case in _enabled_cases(config))}.
- Stage A-D fallback may represent the final state; peak denotes a confirmed near-peak/post-peak state.
- heavy AE is disabled for the initial standard-output workflow.
- Experiment paths are interpreted relative to the generated output project, not relative to the intake file directory.

## Recorded assumptions

{assumption_lines}
"""


def _parameter_bounds(config: ScaffoldConfig) -> str:
    values = config.contact_model
    data = {
        "note": "Seed search ranges only; not final calibrated values.",
        "parameters": {
            "linear_emod_pa": {"min": values.linear_emod_pa * 0.5, "seed": values.linear_emod_pa, "max": values.linear_emod_pa * 2.0},
            "bond_emod_pa": {"min": values.bond_emod_pa * 0.5, "seed": values.bond_emod_pa, "max": values.bond_emod_pa * 2.0},
            "kratio": {"min": max(0.1, values.kratio * 0.5), "seed": values.kratio, "max": values.kratio * 2.0},
            "pb_ten_pa": {"min": values.pb_ten_pa * 0.5, "seed": values.pb_ten_pa, "max": values.pb_ten_pa * 2.0},
            "pb_coh_pa": {"min": values.pb_coh_pa * 0.5, "seed": values.pb_coh_pa, "max": values.pb_coh_pa * 2.0},
            "friction": {"min": 0.0, "seed": values.friction, "max": max(1.0, values.friction * 1.5)},
            "random_seed": {
                "min": config.project.random_seed_base,
                "seed": config.project.random_seed_base,
                "max": config.project.random_seed_base + 99,
            },
        },
    }
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=False)


def _manifest_alias(value: str) -> str:
    return "/".join(part.rstrip(" .").casefold() for part in value.split("/"))


def _safe_manifest_path(root: Path, value: object) -> Path:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or _has_forbidden_controls(value)
    ):
        raise ConfigError(f"unsafe managed path: {value!r}")
    parts = value.split("/")
    if (
        value.startswith("/")
        or _DRIVE_PATTERN.match(value)
        or any(_unsafe_posix_part(part) for part in parts)
    ):
        raise ConfigError(f"unsafe managed path: {value!r}")
    candidate = root.joinpath(*parts)
    try:
        candidate.resolve(strict=False).relative_to(root.resolve(strict=False))
    except (OSError, ValueError) as exc:
        raise ConfigError(f"unsafe managed path: {value!r}") from exc
    return candidate


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    if is_junction is not None and is_junction():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _assert_tree_has_no_reparse_points(root: Path) -> None:
    """Reject links and Windows reparse points without traversing them."""
    if not root.exists() or not root.is_dir():
        raise ConfigError(f"output root is not a regular directory: {root}")
    pending = [root]
    while pending:
        current = pending.pop()
        if _is_reparse_point(current):
            raise ConfigError(f"output tree contains symlink/junction/reparse point: {current}")
        with os.scandir(current) as entries:
            for entry in entries:
                path = Path(entry.path)
                if _is_reparse_point(path):
                    raise ConfigError(
                        f"output tree contains symlink/junction/reparse point: {path}"
                    )
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


_REQUIRED_ROOT_ARTIFACTS = {
    "README_runbook.md",
    "project_config.yaml",
    "cases.csv",
    "calibration/targets.csv",
    "calibration/parameter_bounds.yaml",
    "postprocess/manifest.csv",
    "reports/modeling_notes.md",
    "geometry/cracks/README.md",
    "geometry/cracks/polyline_schema.csv",
    "scaffold_manifest.json",
}


def _write_stage(
    stage: Path,
    config: ScaffoldConfig,
    intake_path: Path,
    output_dir: Path,
    warnings: list[str],
) -> list[str]:
    for relative in _PROJECT_DIRS:
        (stage / relative).mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {
        "project_config.yaml": yaml.safe_dump(
            _normalized_config(config), sort_keys=False, allow_unicode=True
        ),
        "cases.csv": _csv_text(
            [
                "case_name", "family", "enabled", "experiment_file",
                "crack_enabled", "crack_type", "angle_deg", "distance_mm",
                "length_mm", "width_mm", "center_x_mm", "center_y_mm",
            ],
            _case_rows(config),
        ),
        "README_runbook.md": _runbook(config, warnings),
        "reports/modeling_notes.md": _modeling_notes(config, intake_path),
        "geometry/cracks/README.md": (
            "# Crack geometry files\n\n"
            "`polyline_schema.csv` defines the reserved future polyline contract. "
            "Straight cracks are parameterized in `cases.csv`; v1 does not execute "
            "polyline cutting.\n"
        ),
        "geometry/cracks/polyline_schema.csv": _csv_text(
            ["point_id", "x_mm", "y_mm"], [[0, "", ""]]
        ),
        "calibration/parameter_bounds.yaml": _parameter_bounds(config),
        "postprocess/manifest.csv": (
            "# Read pfc-postprocessing/references/script-catalog.md and the owning script first.\n"
            "artifact,owning_script,required\n"
            "stress_strain.csv,pfc-postprocessing/scripts/plot_curves.py,true\n"
            "stress_strain_step.csv,pfc-postprocessing/scripts/plot_curves.py,false\n"
            "plotdata_fracture_orientations.csv,pfc-postprocessing/scripts/plot_rose.py,false\n"
        ),
    }
    targets = [
        [
            case.name,
            case.experiment_file,
            "registered"
            if (output_dir / PurePosixPath(case.experiment_file)).is_file()
            else "missing_experiment",
        ]
        for _, case in _enabled_cases(config)
    ]
    files["calibration/targets.csv"] = _csv_text(
        ["case_name", "experiment_file", "status"], targets
    )
    enabled_names: list[str] = []
    for index, case in _enabled_cases(config):
        enabled_names.append(case.name)
        for name, text in render_case_files(config, case, index).items():
            files[f"pfc_cases/{case.name}/{name}"] = text

    for relative, text in files.items():
        destination = _safe_manifest_path(stage, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8", newline="\n")
    managed_files = sorted([*files, "scaffold_manifest.json"])
    manifest = {
        "schema": _MANIFEST_SCHEMA,
        "version": _MANIFEST_VERSION,
        "run_order": enabled_names,
        "cases": [
            {"name": case.name, "family": case.family, "enabled": case.enabled}
            for case in config.cases
        ],
        "warnings": warnings,
        "managed_files": managed_files,
        "managed_sha256": {
            relative: _sha256(_safe_manifest_path(stage, relative))
            for relative in managed_files
            if relative != "scaffold_manifest.json"
        },
    }
    (stage / "scaffold_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return managed_files


def _manifest_errors(root: Path, manifest: object, *, check_hashes: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["scaffold_manifest.json root must be an object"]
    if manifest.get("schema") != _MANIFEST_SCHEMA:
        errors.append(f"manifest schema must be {_MANIFEST_SCHEMA}")
    if manifest.get("version") != _MANIFEST_VERSION:
        errors.append(f"manifest version must be {_MANIFEST_VERSION}")
    managed = manifest.get("managed_files")
    hashes = manifest.get("managed_sha256")
    if not isinstance(managed, list) or not all(isinstance(item, str) for item in managed):
        errors.append("manifest managed_files must be a list of strings")
        managed = []
    aliases = [_manifest_alias(value) for value in managed]
    if len(managed) != len(set(managed)):
        errors.append("manifest managed_files contains duplicate paths")
    if len(aliases) != len(set(aliases)):
        errors.append("manifest managed_files contains Windows alias collisions")
    if "scaffold_manifest.json" not in managed:
        errors.append("manifest managed_files must contain manifest self path")
    expected_hash_keys = set(managed) - {"scaffold_manifest.json"}
    if not isinstance(hashes, dict):
        errors.append("manifest managed_sha256 must be an object")
        hashes = {}
    elif set(hashes) != expected_hash_keys:
        errors.append("manifest managed_sha256 keys must exactly match non-manifest managed files")
    for relative in managed:
        try:
            path = _safe_manifest_path(root, relative)
        except ConfigError as exc:
            errors.append(str(exc))
            continue
        if not path.is_file():
            errors.append(f"managed file is missing: {relative}")
        elif check_hashes and relative != "scaffold_manifest.json":
            expected = hashes.get(relative)
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                errors.append(f"invalid managed_sha256 value: {relative}")
            elif _sha256(path) != expected:
                errors.append(f"managed file hash mismatch: {relative}")
    return errors


def _read_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / "scaffold_manifest.json"
    if not manifest_path.is_file():
        raise ConfigError("force requires a prior scaffold_manifest.json")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"prior scaffold_manifest.json is invalid: {exc}") from exc
    errors = _manifest_errors(root, manifest, check_hashes=True)
    if errors:
        raise ConfigError("Invalid prior scaffold manifest:\n- " + "\n- ".join(errors))
    return manifest


def validate_generated_project(root: Path) -> list[str]:
    """Return static contract errors for a generated project."""
    errors: list[str] = []
    for relative in sorted(_REQUIRED_ROOT_ARTIFACTS):
        if not _safe_manifest_path(root, relative).is_file():
            errors.append(f"required root artifact is missing: {relative}")
    manifest_path = root / "scaffold_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [*errors, f"invalid scaffold_manifest.json: {exc}"]
    errors.extend(_manifest_errors(root, manifest, check_hashes=True))
    if not isinstance(manifest, dict):
        return errors
    cases = manifest.get("cases")
    enabled_names: list[str] = []
    if not isinstance(cases, list):
        errors.append("manifest cases must be a list")
    else:
        for entry in cases:
            if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
                errors.append("manifest case entry is invalid")
            elif entry.get("enabled") is True:
                enabled_names.append(entry["name"])
    if manifest.get("run_order") != enabled_names:
        errors.append("manifest run_order does not match enabled cases")
    cases_root = root / "pfc_cases"
    actual_case_dirs = (
        sorted(path.name for path in cases_root.iterdir() if path.is_dir())
        if cases_root.is_dir()
        else []
    )
    if actual_case_dirs != sorted(enabled_names):
        errors.append("pfc_cases directories do not match enabled cases")
    for case_name in enabled_names:
        try:
            case_dir = _safe_manifest_path(root, f"pfc_cases/{case_name}")
        except ConfigError as exc:
            errors.append(str(exc))
            continue
        actual_files = (
            {path.name for path in case_dir.iterdir() if path.is_file()}
            if case_dir.is_dir()
            else set()
        )
        if actual_files != _REQUIRED_CASE_FILES:
            errors.append(f"case {case_name} does not contain the exact six-file contract")
        run_all = case_dir / "run_all.dat"
        if run_all.is_file() and run_all.read_text(encoding="utf-8") != _RUN_ALL_TEXT:
            errors.append(f"case {case_name}: run_all.dat does not match exact run order")
        for name in sorted(actual_files):
            try:
                text = (case_dir / name).read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"case {case_name}/{name} is unreadable: {exc}")
                continue
            if "${" in text:
                errors.append(f"case {case_name}/{name} has unresolved placeholder")
    return errors


def _remove_old_managed_from_stage(
    stage: Path, old_files: list[str], new_files: list[str]
) -> None:
    old_set = set(old_files)
    for relative in new_files:
        target = _safe_manifest_path(stage, relative)
        if target.exists() and relative not in old_set:
            raise ConfigError(f"unmanaged existing path blocks force: {relative}")
    for relative in old_files:
        target = _safe_manifest_path(stage, relative)
        if target.is_file():
            target.unlink()
    for directory in sorted(
        (path for path in stage.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        try:
            directory.rmdir()
        except OSError:
            pass


def _unique_sibling(output_dir: Path, kind: str) -> Path:
    return output_dir.parent / f".{output_dir.name}.cpb2d-{kind}-{uuid.uuid4().hex}"


def _acquire_lock(output_dir: Path) -> tuple[Path, int]:
    lock_path = output_dir.parent / f".{output_dir.name}.cpb2d.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ConfigError(f"another CPB2D generation holds lock: {lock_path}") from exc
    return lock_path, descriptor


def _swap_directories(stage: Path, output_dir: Path) -> str | None:
    backup = _unique_sibling(output_dir, "backup")
    os.replace(output_dir, backup)
    try:
        os.replace(stage, output_dir)
    except Exception as publish_error:
        try:
            os.replace(backup, output_dir)
        except Exception as rollback_error:
            raise ConfigError(
                "directory publish failed and rollback failed; backup preserved at "
                f"{backup.resolve()}"
            ) from rollback_error
        raise publish_error
    try:
        shutil.rmtree(backup)
    except OSError:
        return f"published project but could not remove backup: {backup.resolve()}"
    return None


def create_project(
    intake_path: Path, output_dir: Path, *, force: bool = False
) -> CreateResult:
    """Generate and validate a CPB2D project with transactional publication."""
    intake_path = Path(intake_path)
    output_dir = Path(output_dir)
    config = load_intake(intake_path)
    case_order = [case.name for _, case in _enabled_cases(config)]
    output_parent = output_dir.parent
    output_parent.mkdir(parents=True, exist_ok=True)
    lock_path, lock_descriptor = _acquire_lock(output_dir)
    stage = _unique_sibling(output_dir, "stage")
    try:
        output_exists = os.path.lexists(output_dir)
        if output_exists and not force:
            raise FileExistsError(f"output directory already exists: {output_dir}")
        warnings = project_warnings(config, output_dir)
        if output_exists:
            _assert_tree_has_no_reparse_points(output_dir)
            prior = _read_manifest(output_dir)
            prior_errors = validate_generated_project(output_dir)
            if prior_errors:
                raise ConfigError(
                    "Prior generated project validation failed:\n- "
                    + "\n- ".join(prior_errors)
                )
            old_files = list(prior["managed_files"])
            shutil.copytree(output_dir, stage, symlinks=False)
            new_preview = sorted([
                "README_runbook.md", "project_config.yaml", "cases.csv",
                "calibration/targets.csv", "calibration/parameter_bounds.yaml",
                "postprocess/manifest.csv", "reports/modeling_notes.md",
                "geometry/cracks/README.md", "geometry/cracks/polyline_schema.csv",
                "scaffold_manifest.json",
                *(
                    f"pfc_cases/{case.name}/{name}"
                    for _, case in _enabled_cases(config)
                    for name in _REQUIRED_CASE_FILES
                ),
            ])
            _remove_old_managed_from_stage(stage, old_files, new_preview)
        else:
            stage.mkdir()
            old_files = []
        managed_files = _write_stage(stage, config, intake_path, output_dir, warnings)
        errors = validate_generated_project(stage)
        if errors:
            raise ConfigError("Generated project validation failed:\n- " + "\n- ".join(errors))
        if output_exists:
            _assert_tree_has_no_reparse_points(output_dir)
            current = _read_manifest(output_dir)
            if current != prior:
                raise ConfigError("output project changed during force generation")
            cleanup_warning = _swap_directories(stage, output_dir)
            if cleanup_warning is not None:
                warnings.append(cleanup_warning)
        else:
            os.replace(stage, output_dir)
        return CreateResult(output_dir, warnings, managed_files, case_order)
    finally:
        os.close(lock_descriptor)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
