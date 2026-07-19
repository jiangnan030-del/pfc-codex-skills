"""Typed configuration contract for the CPB2D project scaffold."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re
from typing import Any

import yaml


_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_DRIVE_PATTERN = re.compile(r"^[a-zA-Z]:")
_WINDOWS_DEVICES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}
_CASE_FAMILIES = {"intact", "straight_crack", "polyline_reserved"}
_CRACK_TYPES = {"straight", "polyline_reserved"}
_MISSING = object()


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


def _windows_name_key(name: str) -> str:
    return name.rstrip(" .").casefold()


def _validate_slug(value: str, field: str, errors: list[str]) -> None:
    if _has_forbidden_controls(value) or not _SLUG_PATTERN.fullmatch(value):
        errors.append(f"{field} has an unsafe format")
    if _windows_name_key(value) in _WINDOWS_DEVICES:
        errors.append(f"{field} is a reserved Windows device name")


def _validate_relative_path(value: str, field: str, errors: list[str]) -> None:
    if _has_forbidden_controls(value):
        errors.append(f"{field} may not contain CR, LF, or NUL")
        return
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if (
        normalized.startswith("/")
        or _DRIVE_PATTERN.match(normalized)
        or any(part in {"", ".", ".."} for part in parts)
    ):
        errors.append(f"{field} must be a project-relative path without traversal")


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
    )
    errors = validate_config(config)
    if errors:
        raise ConfigError("Invalid intake configuration:\n- " + "\n- ".join(errors))
    return config
