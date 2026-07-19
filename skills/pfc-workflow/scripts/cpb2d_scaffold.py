"""Typed configuration contract for the CPB2D project scaffold."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re
from typing import Any

import yaml


_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
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
    stage_fractions: tuple[float, float, float, float]
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


def _string(mapping: dict[str, Any], key: str, field: str) -> str:
    value = _required(mapping, key, field)
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{field}.{key} must be a non-empty string")
    return value


def _number(mapping: dict[str, Any], key: str, field: str) -> float:
    value = _required(mapping, key, field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{field}.{key} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ConfigError(f"{field}.{key} must be finite")
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
    slug = _string(section, "slug", "project")
    if not _SLUG_PATTERN.fullmatch(slug):
        raise ConfigError(
            "project.slug must contain lowercase letters, digits, and single underscores only"
        )
    return ProjectConfig(
        slug=slug,
        title=_string(section, "title", "project"),
        pfc_version=_string(section, "pfc_version", "project"),
        random_seed_base=_integer(section, "random_seed_base", "project"),
    )


def _parse_specimen(data: dict[str, Any]) -> SpecimenConfig:
    section = _mapping(data.get("specimen"), "specimen")
    radius_min = _number(section, "particle_radius_min_mm", "specimen")
    if radius_min <= 0:
        raise ConfigError("specimen.particle_radius_min_mm must be positive")
    return SpecimenConfig(
        width_mm=_number(section, "width_mm", "specimen"),
        height_mm=_number(section, "height_mm", "specimen"),
        radius_min_mm=radius_min,
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
        stage_fractions=tuple(parsed_fractions),  # type: ignore[arg-type]
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
        if crack_type is not None and not isinstance(crack_type, str):
            raise ConfigError(f"{field}.crack_type must be a string")
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


def validate_config(config: ScaffoldConfig) -> list[str]:
    """Return every domain validation error found in a typed configuration."""
    errors: list[str] = []

    if not _SLUG_PATTERN.fullmatch(config.project.slug):
        errors.append("project.slug has an unsafe format")
    if config.project.pfc_version != "6.0":
        errors.append('project.pfc_version must be the string "6.0"')

    positive_specimen_fields = (
        ("specimen.width_mm", config.specimen.width_mm),
        ("specimen.height_mm", config.specimen.height_mm),
        ("specimen.particle_radius_min_mm", config.specimen.radius_min_mm),
        ("specimen.particle_radius_max_mm", config.specimen.radius_max_mm),
        ("specimen.density_kg_m3", config.specimen.density_kg_m3),
    )
    for field, value in positive_specimen_fields:
        if value <= 0:
            errors.append(f"{field} must be positive")
    if config.specimen.radius_min_mm > config.specimen.radius_max_mm:
        errors.append(
            "specimen.particle_radius_min_mm must be less than or equal to "
            "specimen.particle_radius_max_mm"
        )
    if not 0 < config.specimen.porosity < 1:
        errors.append("specimen.target_porosity must be between 0 and 1")
    if not 0 <= config.specimen.damping <= 1:
        errors.append("specimen.damping must be between 0 and 1 inclusive")

    if config.loading.wall_velocity_m_s <= 0:
        errors.append("loading.wall_velocity_m_s must be positive")
    if not 0 < config.loading.peak_drop_fraction < 1:
        errors.append("loading.peak_drop_fraction must be between 0 and 1")
    fractions = config.loading.stage_fractions
    if len(fractions) != 4:
        errors.append("loading.stage_fractions must contain exactly four values")
    elif not all(0 < value < 1 for value in fractions):
        errors.append("loading.stage_fractions values must be between 0 and 1")
    elif not all(left < right for left, right in zip(fractions, fractions[1:])):
        errors.append("loading.stage_fractions must be strictly increasing")

    enabled_cases = [case for case in config.cases if case.enabled]
    if not enabled_cases or enabled_cases[0].name != "intact":
        errors.append("cases: first enabled case must be intact")

    seen_names: set[str] = set()
    for index, case in enumerate(config.cases):
        field = f"cases[{index}]"
        if case.name in seen_names:
            errors.append(f"{field}.case_name duplicates case name {case.name!r}")
        seen_names.add(case.name)

        if case.name == "intact" and case.crack_enabled:
            errors.append(f"{field}.crack_enabled must be false for intact")

        is_straight = case.family == "straight_crack" or case.crack_type == "straight"
        if is_straight:
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

        if case.crack_type == "polyline_reserved" and case.enabled:
            errors.append(f"{field}.enabled must be false for polyline_reserved")

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

    # Report an explicitly supplied invalid radius before unrelated missing fields.
    raw_specimen = data.get("specimen")
    if isinstance(raw_specimen, dict) and "particle_radius_min_mm" in raw_specimen:
        radius_min = _number(raw_specimen, "particle_radius_min_mm", "specimen")
        if radius_min <= 0:
            raise ConfigError("specimen.particle_radius_min_mm must be positive")

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
