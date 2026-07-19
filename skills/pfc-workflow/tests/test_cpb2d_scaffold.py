from dataclasses import replace
from pathlib import Path
import sys

import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cpb2d_scaffold import (
    ConfigError,
    crack_geometry,
    load_intake,
    render_context,
    validate_config,
)

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


def test_horizontal_crack_geometry_uses_metres_half_length_center_and_half_width():
    cfg = load_intake(FIXTURE)
    crack = crack_geometry(cfg.cases[1], cfg.specimen)
    assert crack.end1_m == pytest.approx((-0.01, 0.0))
    assert crack.end2_m == pytest.approx((0.01, 0.0))
    assert crack.radius_m == pytest.approx(0.0015)


def test_vertical_and_rotated_crack_geometry_uses_angle_and_center():
    cfg = load_intake(FIXTURE)
    vertical = replace(
        cfg.cases[1], angle_deg=90.0, length_mm=10.0, center_x_mm=2.0,
        center_y_mm=-3.0,
    )
    crack = crack_geometry(vertical, cfg.specimen)
    assert crack.end1_m == pytest.approx((0.002, -0.008))
    assert crack.end2_m == pytest.approx((0.002, 0.002))

    rotated = replace(
        cfg.cases[1], angle_deg=45.0, length_mm=10.0, center_x_mm=1.0,
        center_y_mm=2.0,
    )
    crack = crack_geometry(rotated, cfg.specimen)
    offset = 0.005 / (2**0.5)
    assert crack.end1_m == pytest.approx((0.001 - offset, 0.002 - offset))
    assert crack.end2_m == pytest.approx((0.001 + offset, 0.002 + offset))


@pytest.mark.parametrize(
    "case",
    [
        {"center_x_mm": 19.0, "length_mm": 20.0},
        {"center_y_mm": 19.0, "angle_deg": 90.0, "length_mm": 20.0},
    ],
)
def test_crack_endpoint_outside_specimen_is_rejected(case):
    cfg = load_intake(FIXTURE)
    bad = replace(cfg.cases[1], **case)
    with pytest.raises(ConfigError, match=r"case b0_d20.*outside specimen"):
        crack_geometry(bad, cfg.specimen)


def test_crack_cylinder_radius_must_fit_inside_specimen():
    cfg = load_intake(FIXTURE)
    bad = replace(
        cfg.cases[1], center_x_mm=14.0, length_mm=10.0, width_mm=4.0,
    )
    with pytest.raises(ConfigError, match=r"case b0_d20.*cylinder radius.*outside specimen"):
        crack_geometry(bad, cfg.specimen)


def test_crack_geometry_rejects_intact_case_with_case_field():
    cfg = load_intake(FIXTURE)
    with pytest.raises(ConfigError, match=r"case intact"):
        crack_geometry(cfg.cases[0], cfg.specimen)


def test_case_seed_is_deterministic_and_negative_index_is_rejected():
    cfg = load_intake(FIXTURE)
    intact = render_context(cfg, cfg.cases[0], 0)
    crack = render_context(cfg, cfg.cases[1], 1)
    assert intact["random_seed"] == 31000
    assert crack["random_seed"] == 31001
    with pytest.raises(ConfigError, match="case_index"):
        render_context(cfg, cfg.cases[0], -1)


def test_render_context_formats_numbers_and_calculates_stage_strains():
    cfg = load_intake(FIXTURE)
    context = render_context(cfg, cfg.cases[1], 1)
    assert context["specimen_width_m"] == "4.000000e-02"
    assert context["particle_radius_min_m"] == "3.000000e-04"
    assert context["linear_emod_pa"] == "2.200000e+06"
    assert context["stage_a_strain"] == "2.000000e-02"
    assert context["stage_b_strain"] == "4.000000e-02"
    assert context["stage_c_strain"] == "6.000000e-02"
    assert context["stage_d_strain"] == "7.200000e-02"


def test_render_context_builds_only_known_safe_crack_commands():
    cfg = load_intake(FIXTURE)
    intact = render_context(cfg, cfg.cases[0], 0)
    straight = render_context(cfg, cfg.cases[1], 1)
    assert intact["crack_command"].startswith(";")
    assert "ball delete" not in intact["crack_command"]
    assert straight["crack_command"] == (
        "ball delete range cylinder end-1 -1.000000e-02 0.000000e+00 "
        "end-2 1.000000e-02 0.000000e+00 radius 1.500000e-03"
    )


def test_render_context_returns_testable_narrow_crack_warning():
    cfg = load_intake(FIXTURE)
    narrow = replace(cfg.cases[1], width_mm=0.9)
    context = render_context(cfg, narrow, 1)
    assert context["warnings"] == (
        "case b0_d20: crack width_mm 9.000000e-01 is less than twice "
        "particle_radius_max_mm 1.000000e+00",
    )
    assert render_context(cfg, cfg.cases[1], 1)["warnings"] == ()


def test_project_title_is_pfc_safe_single_line_text():
    cfg = load_intake(FIXTURE)
    quoted = replace(cfg.project, title="O'Brien's CPB")
    context = render_context(replace(cfg, project=quoted), cfg.cases[0], 0)
    assert context["project_title"] == "O''Brien''s CPB"
