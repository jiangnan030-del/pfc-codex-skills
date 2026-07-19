from dataclasses import replace
from pathlib import Path
import sys

import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cpb2d_scaffold import ConfigError, load_intake, validate_config

FIXTURE = Path(__file__).parent / "fixtures" / "intake_minimal.yaml"


def write_intake(tmp_path, mutate):
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "intake.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def assert_invalid(tmp_path, mutate, field):
    with pytest.raises(ConfigError, match=field):
        load_intake(write_intake(tmp_path, mutate))


def test_load_minimal_intake_normalizes_si_values():
    cfg = load_intake(FIXTURE)
    assert cfg.project.slug == "cpb_2d_ucs_demo"
    assert cfg.specimen.width_m == pytest.approx(0.04)
    assert cfg.specimen.radius_min_m == pytest.approx(0.0003)
    assert [case.name for case in cfg.cases] == ["intact", "b0_d20"]


@pytest.mark.parametrize("slug", ["my project", "CPB_Demo", "cpb-demo", "../cpb"])
def test_project_slug_rejects_unsafe_names(tmp_path, slug):
    assert_invalid(tmp_path, lambda data: data["project"].update(slug=slug), "project.slug")


@pytest.mark.parametrize(
    "name",
    ["../case", "a/b", r"a\b", "case name", "case-name", "Case", "CON", "nul"],
)
def test_case_name_rejects_unsafe_or_windows_reserved_names(tmp_path, name):
    assert_invalid(
        tmp_path,
        lambda data: data["cases"][1].update(case_name=name),
        r"cases\[1\]\.case_name",
    )


def test_case_names_allow_intact_crack_and_future_polyline_forms(tmp_path):
    cfg = load_intake(
        write_intake(
            tmp_path,
            lambda data: data["cases"].append(
                {
                    "case_name": "nl_curve_1",
                    "family": "polyline_reserved",
                    "enabled": False,
                    "experiment_file": "data/experimental/nl_curve_1.xlsx",
                    "crack_enabled": True,
                    "crack_type": "polyline_reserved",
                }
            ),
        )
    )
    assert [case.name for case in cfg.cases] == ["intact", "b0_d20", "nl_curve_1"]


def test_duplicate_names_use_windows_collision_semantics():
    cfg = load_intake(FIXTURE)
    colliding = replace(cfg.cases[1], name="INTACT. ", enabled=False)
    errors = validate_config(replace(cfg, cases=(cfg.cases[0], colliding)))
    assert any("case_name" in error and "duplicates" in error for error in errors)


@pytest.mark.parametrize("value", ["6", 6.0, "7.0"])
def test_pfc_version_only_accepts_string_6_0(tmp_path, value):
    assert_invalid(
        tmp_path,
        lambda data: data["project"].update(pfc_version=value),
        "project.pfc_version",
    )


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("project", "random_seed_base", 0),
        ("specimen", "width_mm", 0),
        ("specimen", "height_mm", -1),
        ("specimen", "particle_radius_min_mm", 0),
        ("specimen", "particle_radius_max_mm", 0),
        ("specimen", "density_kg_m3", 0),
        ("loading", "wall_velocity_m_s", 0),
        ("loading", "target_peak_strain_guess", 0),
        ("loading", "history_interval", 0),
        ("contact_model", "linear_emod_pa", 0),
        ("contact_model", "bond_emod_pa", 0),
        ("contact_model", "kratio", 0),
        ("contact_model", "pb_ten_pa", 0),
        ("contact_model", "pb_coh_pa", 0),
        ("contact_model", "friction", -0.1),
        ("contact_model", "pb_fa_deg", 90),
    ],
)
def test_direct_pfc_numeric_constraints(tmp_path, section, field, value):
    assert_invalid(
        tmp_path,
        lambda data: data[section].update({field: value}),
        field,
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("target_porosity", 0),
        ("target_porosity", 1),
        ("damping", -0.1),
        ("damping", 1.1),
    ],
)
def test_specimen_fraction_ranges(tmp_path, field, value):
    assert_invalid(
        tmp_path,
        lambda data: data["specimen"].update({field: value}),
        field,
    )


@pytest.mark.parametrize("value", [0, 1])
def test_peak_drop_fraction_is_strictly_between_zero_and_one(tmp_path, value):
    assert_invalid(
        tmp_path,
        lambda data: data["loading"].update(peak_drop_fraction=value),
        "peak_drop_fraction",
    )


def test_particle_radius_order_is_validated(tmp_path):
    assert_invalid(
        tmp_path,
        lambda data: data["specimen"].update(
            particle_radius_min_mm=0.6, particle_radius_max_mm=0.5
        ),
        "particle_radius_min_mm",
    )


@pytest.mark.parametrize(
    "fractions",
    [[0.2, 0.4, 0.6], [0.0, 0.4, 0.6, 0.8], [0.2, 0.6, 0.4, 0.8]],
)
def test_stage_fractions_require_four_in_range_increasing_values(tmp_path, fractions):
    assert_invalid(
        tmp_path,
        lambda data: data["loading"].update(stage_fractions=fractions),
        "stage_fractions",
    )


def test_first_enabled_case_must_be_intact(tmp_path):
    def mutate(data):
        data["cases"][0]["enabled"] = False

    assert_invalid(tmp_path, mutate, "first enabled case")


def test_duplicate_case_names_are_rejected(tmp_path):
    assert_invalid(
        tmp_path,
        lambda data: data["cases"][1].update(case_name="intact"),
        "case_name",
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [("family", "straight_crack"), ("crack_enabled", True), ("crack_type", "straight")],
)
def test_intact_state_must_be_consistent(tmp_path, field, value):
    assert_invalid(
        tmp_path,
        lambda data: data["cases"][0].update({field: value}),
        rf"cases\[0\]",
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [("crack_enabled", False), ("crack_type", None)],
)
def test_straight_crack_state_must_be_consistent(tmp_path, field, value):
    assert_invalid(
        tmp_path,
        lambda data: data["cases"][1].update({field: value}),
        rf"cases\[1\]",
    )


@pytest.mark.parametrize(
    "field", ["angle_deg", "length_mm", "width_mm", "center_x_mm", "center_y_mm"]
)
def test_straight_crack_requires_all_geometry_fields(tmp_path, field):
    def mutate(data):
        data["cases"][1].pop(field)

    assert_invalid(tmp_path, mutate, field)


@pytest.mark.parametrize(("field", "value"), [("length_mm", 0), ("width_mm", -1)])
def test_straight_crack_dimensions_are_positive(tmp_path, field, value):
    assert_invalid(
        tmp_path,
        lambda data: data["cases"][1].update({field: value}),
        field,
    )


@pytest.mark.parametrize("selector", ["family", "crack_type"])
def test_polyline_reserved_must_be_disabled_and_consistent(tmp_path, selector):
    assert_invalid(
        tmp_path,
        lambda data: data["cases"][1].update({selector: "polyline_reserved"}),
        rf"cases\[1\]",
    )


@pytest.mark.parametrize(
    ("family", "crack_type"),
    [("unknown", "straight"), ("straight_crack", "unknown"), ("unknown", None)],
)
def test_unknown_case_family_or_crack_type_is_rejected(tmp_path, family, crack_type):
    assert_invalid(
        tmp_path,
        lambda data: data["cases"][1].update(family=family, crack_type=crack_type),
        rf"cases\[1\]",
    )


def test_unknown_contact_family_is_rejected(tmp_path):
    assert_invalid(
        tmp_path,
        lambda data: data["contact_model"].update(family="linear"),
        "contact_model.family",
    )


@pytest.mark.parametrize(
    ("location", "field", "value"),
    [
        ("project", "title", "bad\nname"),
        ("case", "case_name", "bad\rname"),
        ("case", "family", "bad\x00name"),
        ("case", "experiment_file", "bad\nname.xlsx"),
    ],
)
def test_control_characters_are_rejected(tmp_path, location, field, value):
    def mutate(data):
        target = data["project"] if location == "project" else data["cases"][1]
        target[field] = value

    assert_invalid(tmp_path, mutate, field)


@pytest.mark.parametrize(
    "path",
    [
        "/tmp/intact.xlsx",
        r"C:\data\intact.xlsx",
        r"\\server\share\intact.xlsx",
        "../intact.xlsx",
        "data/../intact.xlsx",
        r"data\..\intact.xlsx",
    ],
)
def test_experiment_file_must_be_project_relative(tmp_path, path):
    assert_invalid(
        tmp_path,
        lambda data: data["cases"][1].update(experiment_file=path),
        "experiment_file",
    )


def test_missing_experiment_file_is_not_checked(tmp_path):
    cfg = load_intake(
        write_intake(
            tmp_path,
            lambda data: data["cases"][0].update(
                experiment_file="data/experimental/does_not_exist.xlsx"
            ),
        )
    )
    assert cfg.cases[0].experiment_file.endswith("does_not_exist.xlsx")


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("specimen", "width_mm"),
        ("contact_model", "linear_emod_pa"),
        ("loading", "wall_velocity_m_s"),
        ("case", "angle_deg"),
    ],
)
def test_validate_config_rejects_non_finite_replaced_values(section, field):
    cfg = load_intake(FIXTURE)
    if section == "case":
        changed = replace(cfg.cases[1], **{field: float("nan")})
        cfg = replace(cfg, cases=(cfg.cases[0], changed))
    else:
        attribute = "contact_model" if section == "contact_model" else section
        changed = replace(getattr(cfg, attribute), **{field: float("inf")})
        cfg = replace(cfg, **{attribute: changed})
    assert any(field in error and "finite" in error for error in validate_config(cfg))
