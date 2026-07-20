from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cpb2d_scaffold import (
    ConfigError,
    _assert_tree_has_no_reparse_points,
    crack_geometry,
    create_project,
    load_intake,
    render_case_files,
    render_context,
    render_template,
    validate_config,
    validate_generated_project,
)

REQUIRED_CASE_FILES = {
    "1model.dat",
    "2bond.dat",
    "3load.dat",
    "4export.dat",
    "fracture.p2fis",
    "run_all.dat",
}

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
        "C:/data/intact.xlsx",
        "C:data/intact.xlsx",
        r"\\server\share\intact.xlsx",
        "//server/share/intact.xlsx",
        "../intact.xlsx",
        "data/../intact.xlsx",
        r"data\..\intact.xlsx",
        "intact.xlsx",
        "other/intact.xlsx",
        "data/experimental/file:stream.xlsx",
        "data/experimental/bad<name.xlsx",
        "data/experimental/bad>name.xlsx",
        'data/experimental/bad"name.xlsx',
        "data/experimental/bad|name.xlsx",
        "data/experimental/bad?name.xlsx",
        "data/experimental/bad*name.xlsx",
        "data/experimental/CON.xlsx",
        "data/experimental/trailing./intact.xlsx",
        "data/experimental/trailing /intact.xlsx",
        "data/experimental/=formula.xlsx",
        "data/experimental/+formula.xlsx",
        "data/experimental/@formula.xlsx",
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


def test_assumptions_default_empty_and_are_validated_and_recorded(tmp_path):
    assert load_intake(FIXTURE).assumptions == ()
    intake = write_intake(
        tmp_path,
        lambda data: data.update(
            assumptions=["Seed stiffness from pilot study.", "Dry specimen."]
        ),
    )
    config = load_intake(intake)
    assert config.assumptions == (
        "Seed stiffness from pilot study.",
        "Dry specimen.",
    )
    root = create_project(intake, tmp_path / "assumptions-project").root
    normalized = yaml.safe_load((root / "project_config.yaml").read_text(encoding="utf-8"))
    notes = (root / "reports/modeling_notes.md").read_text(encoding="utf-8")
    assert normalized["assumptions"] == list(config.assumptions)
    assert "- Seed stiffness from pilot study." in notes
    assert "- Dry specimen." in notes


def test_missing_assumptions_are_explicit_in_modeling_notes(tmp_path):
    root = create_project(FIXTURE, tmp_path / "project").root
    notes = (root / "reports/modeling_notes.md").read_text(encoding="utf-8")
    assert "## Recorded assumptions\n\n- None recorded." in notes


@pytest.mark.parametrize(
    "assumptions",
    [["bad\nline"], ["bad\rline"], ["bad\x00line"], "not-a-list", [1]],
)
def test_invalid_assumptions_are_rejected(tmp_path, assumptions):
    assert_invalid(
        tmp_path,
        lambda data: data.update(assumptions=assumptions),
        "assumptions",
    )


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


@pytest.mark.parametrize(
    "changes",
    [
        {"angle_deg": 0.0, "center_x_mm": 14.0, "length_mm": 12.0,
         "width_mm": 2.0},
        {"angle_deg": 90.0, "center_y_mm": 14.0, "length_mm": 12.0,
         "width_mm": 2.0},
    ],
)
def test_axis_aligned_crack_uses_normal_half_width_projection(changes):
    cfg = load_intake(FIXTURE)
    crack_geometry(replace(cfg.cases[1], **changes), cfg.specimen)


def test_rotated_crack_half_width_projection_accepts_boundary_and_rejects_overflow():
    cfg = load_intake(FIXTURE)
    boundary_center = 20.0 - 6.0 / (2**0.5)
    boundary = replace(
        cfg.cases[1], angle_deg=45.0, length_mm=10.0, width_mm=2.0,
        center_x_mm=boundary_center, center_y_mm=boundary_center,
    )
    crack_geometry(boundary, cfg.specimen)

    outside = replace(
        boundary, center_x_mm=boundary_center + 0.001,
        center_y_mm=boundary_center + 0.001,
    )
    with pytest.raises(ConfigError, match=r"case b0_d20.*cylinder radius.*outside specimen"):
        crack_geometry(outside, cfg.specimen)


def test_crack_geometry_rejects_intact_case_with_case_field():
    cfg = load_intake(FIXTURE)
    with pytest.raises(ConfigError, match=r"case intact"):
        crack_geometry(cfg.cases[0], cfg.specimen)


def test_case_seed_is_deterministic_and_index_is_strictly_bound():
    cfg = load_intake(FIXTURE)
    intact = render_context(cfg, cfg.cases[0], 0)
    crack = render_context(cfg, cfg.cases[1], 1)
    assert intact["random_seed"] == 31000
    assert crack["random_seed"] == 31001

    for case, index in [
        (cfg.cases[0], -1),
        (cfg.cases[0], len(cfg.cases)),
        (cfg.cases[1], 0),
        (replace(cfg.cases[0], experiment_file="data/experimental/fake.xlsx"), 0),
    ]:
        with pytest.raises(ConfigError, match="case_index|configured case"):
            render_context(cfg, case, index)


def test_render_context_rejects_seed_outside_pfc_integer_range():
    cfg = load_intake(FIXTURE)
    project = replace(cfg.project, random_seed_base=2_147_483_647)
    overflow = replace(cfg, project=project)
    with pytest.raises(ConfigError, match="random_seed"):
        render_context(overflow, overflow.cases[1], 1)


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


@pytest.mark.parametrize(
    ("width_mm", "has_warning"),
    [(0.999, True), (1.0, False), (1.001, False)],
)
def test_render_context_returns_scalar_narrow_crack_warning(width_mm, has_warning):
    cfg = load_intake(FIXTURE)
    changed = replace(cfg.cases[1], width_mm=width_mm)
    changed_cfg = replace(cfg, cases=(cfg.cases[0], changed))
    warning = render_context(changed_cfg, changed_cfg.cases[1], 1)["warnings"]
    if has_warning:
        assert warning == (
            f"case b0_d20: crack width_mm {width_mm:.6e} is less than twice "
            "particle_radius_max_mm 1.000000e+00"
        )
    else:
        assert warning == ""


def test_render_context_rejects_invalid_replaced_config_as_config_error():
    cfg = load_intake(FIXTURE)
    negative_specimen = replace(cfg.specimen, width_mm=-1.0)
    invalid_specimen = replace(cfg, specimen=negative_specimen)
    with pytest.raises(ConfigError, match="specimen.width_mm"):
        render_context(invalid_specimen, invalid_specimen.cases[0], 0)

    short_stages = replace(cfg.loading, stage_fractions=(0.25, 0.5, 0.75))
    invalid_stages = replace(cfg, loading=short_stages)
    with pytest.raises(ConfigError, match="stage_fractions"):
        render_context(invalid_stages, invalid_stages.cases[0], 0)


def test_render_context_rejects_forged_intact_case():
    cfg = load_intake(FIXTURE)
    forged = replace(cfg.cases[1], name="intact", family="intact", crack_enabled=False,
                     crack_type=None)
    with pytest.raises(ConfigError, match="configured case"):
        render_context(cfg, forged, 1)


def test_project_title_is_pfc_safe_single_line_text():
    cfg = load_intake(FIXTURE)
    quoted = replace(cfg.project, title="O'Brien's CPB")
    quoted_cfg = replace(cfg, project=quoted)
    context = render_context(quoted_cfg, quoted_cfg.cases[0], 0)
    assert context["project_title"] == "O''Brien''s CPB"


def test_rendered_intact_has_complete_stage_and_export_contract():
    cfg = load_intake(FIXTURE)
    files = render_case_files(cfg, cfg.cases[0], 0)
    assert set(files) == REQUIRED_CASE_FILES
    assert "model save 'sample'" in files["1model.dat"]
    assert "ball delete range cylinder" not in files["2bond.dat"]
    assert "contact model linearpbond" in files["2bond.dat"]
    for name in ["stage_a", "stage_b", "stage_c", "stage_d"]:
        assert files["3load.dat"].count(f"model save '{name}'") == 2
        assert files["3load.dat"].count(f"if {name}_saved = 0") == 2
    assert "model save 'peak'" in files["3load.dat"]
    assert "model save 'final'" in files["3load.dat"]
    assert "peak_drop_fraction" in files["3load.dat"]
    assert (
        "strain,stress_mpa,crack_num,crack_tension_num,crack_shear_num"
        in files["4export.dat"]
    )
    assert "stress_strain_step.csv" in files["4export.dat"]


def test_rendered_crack_uses_parameterized_cylinder():
    cfg = load_intake(FIXTURE)
    files = render_case_files(cfg, cfg.cases[1], 1)
    assert "contact model linearpbond" in files["2bond.dat"]
    assert "ball delete range cylinder" in files["2bond.dat"]
    assert "-1.000000e-02" in files["2bond.dat"]
    assert "1.500000e-03" in files["2bond.dat"]


def test_run_all_is_single_ordered_entrypoint():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["run_all.dat"]
    assert text.splitlines() == [
        "program call '1model.dat'",
        "program call '2bond.dat'",
        "program call '3load.dat'",
        "program call '4export.dat'",
    ]


def test_template_rendering_is_strict_and_validates_case_binding():
    with pytest.raises(KeyError):
        render_template("1model.dat.tpl", {})

    cfg = load_intake(FIXTURE)
    with pytest.raises(ConfigError, match="configured case"):
        render_case_files(cfg, cfg.cases[1], 0)


def test_rendered_templates_have_no_unresolved_or_private_heavy_ae_content():
    cfg = load_intake(FIXTURE)
    forbidden = ("${", "ghp_", "moment_tensor", "fig9", "export_ae", "ae_event")
    drive_path = r"[A-Za-z]:[\\/]"
    for case_index, case in enumerate(cfg.cases):
        files = render_case_files(cfg, case, case_index)
        assert set(files) == REQUIRED_CASE_FILES
        for text in files.values():
            assert not any(token.lower() in text.lower() for token in forbidden)
            assert not __import__("re").search(drive_path, text)


def test_fracture_template_has_minimal_mode_counts_and_orientation_records():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["fracture.p2fis"]
    assert "crack_tension_num" in text
    assert "crack_shear_num" in text
    assert "crack_angle_record" in text
    assert "crack_type_record" in text
    assert "bond_break" in text


def test_peak_detection_is_independent_of_stage_d_and_confirms_decline():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["3load.dat"]
    peak_logic = text.split("if peak_saved = 0", 1)[1].split("previous_stress", 1)[0]
    assert "stage_d_saved" not in peak_logic
    assert "decline_count >= 3" in peak_logic
    assert "peak_stress * 0.995" in text


def test_maximum_strain_safety_stop_is_independent_and_peak_fallback_is_reachable():
    cfg = load_intake(FIXTURE)
    context = render_context(cfg, cfg.cases[0], 0)
    assert context["max_abs_strain"] == "1.600000e-01"
    text = render_case_files(cfg, cfg.cases[0], 0)["3load.dat"]
    safety = text.split("if abs_strain >= max_abs_strain", 1)[1].split("end_if", 1)[0]
    assert "peak_saved" not in safety
    assert "peak_drop_halt = 1" in safety
    assert text.index("model solve fishhalt @peak_drop_halt") < text.index(
        "@save_peak_if_missing"
    ) < text.index("model save 'final'")


def test_fracture_template_retains_canonical_fragment_position_updates():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["fracture.p2fis"]
    for token in [
        "crack_accum",
        "frag_time",
        "fragment compute",
        "dfn.fracturelist",
        "fracture.pos(frac) = pos",
        "domain.min.x()",
        "domain.max.y()",
    ]:
        assert token in text


def test_decline_tracking_starts_after_stage_a_and_normal_drop_requires_stage_d():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["3load.dat"]
    tracking = text.split("if stage_a_saved = 1", 1)[1].split(
        "if peak_saved = 0", 1
    )[0]
    assert "decline_count = decline_count + 1" in tracking
    assert "else\n        decline_count = 0\n        stress_initialized = 0" in tracking
    normal_halt = text.split("if peak_saved = 1", 1)[1].split(
        "if abs_strain >= max_abs_strain", 1
    )[0]
    assert "if stage_d_saved = 1" in normal_halt


def test_missing_stage_fallback_saves_all_stage_contract_names_in_order():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["3load.dat"]
    fallback = text.split("fish define save_missing_stages", 1)[1].split("end\n", 1)[0]
    positions = [fallback.index(f"model save 'stage_{label}'") for label in "abcd"]
    assert positions == sorted(positions)
    assert "fallback final state" in fallback.lower()
    assert text.index("@save_missing_stages") < text.index("@save_peak_if_missing")
    assert "confirmed near-peak/post-peak state" in text


def test_bond_template_sets_official_cmat_proximity_before_clean_and_bond_gap():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["2bond.dat"]
    assert text.index("contact cmat apply") < text.index(
        "contact cmat proximity 3.000000e-04"
    ) < text.index("model clean") < text.index("contact method bond gap")


def test_export_uses_common_minimum_table_sizes_before_allocating_rows():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["4export.dat"]
    assert text.count("math.min") >= 7
    assert "table.size(t_crack)" in text
    assert "table.size(t_strain_step)" in text
    assert text.index("local n = math.min") < text.index("array.create(n + 1)")
    assert text.index("local ns = math.min") < text.index("array.create(ns + 1)")


def test_fracture_normalizes_orientation_and_finalizes_pending_fragments():
    cfg = load_intake(FIXTURE)
    files = render_case_files(cfg, cfg.cases[0], 0)
    fracture = files["fracture.p2fis"]
    assert "if crack_angle < 0.0" in fracture
    assert "crack_angle = crack_angle + 180.0" in fracture
    assert "if crack_angle >= 180.0" in fracture
    assert "crack_angle = crack_angle - 180.0" in fracture
    assert "crack_record_truncated = 1" in fracture
    assert "fish define update_fracture_positions" in fracture
    assert "fish define finalize_tracking" in fracture
    assert "if crack_accum > 0" in fracture
    load = files["3load.dat"]
    assert load.index("@finalize_tracking") < load.index("model save 'final'")


def test_create_project_writes_mixed_tree_and_manifest(tmp_path):
    result = create_project(FIXTURE, tmp_path / "cpb_2d_ucs_demo")
    root = result.root
    expected_dirs = {
        "data/experimental",
        "geometry/cracks",
        "pfc_cases",
        "calibration/trials",
        "postprocess",
        "figures",
        "tables",
        "reports",
    }
    assert all((root / relative).is_dir() for relative in expected_dirs)
    for relative in [
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
    ]:
        assert (root / relative).is_file()
    for case in ["intact", "b0_d20"]:
        assert {path.name for path in (root / "pfc_cases" / case).iterdir()} == REQUIRED_CASE_FILES

    expected_warnings = [
        "missing experiment file: data/experimental/intact.xlsx",
        "missing experiment file: data/experimental/b0_d20.xlsx",
    ]
    assert result.warnings == expected_warnings
    manifest = json.loads((root / "scaffold_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "cpb2d-scaffold-manifest"
    assert manifest["version"] == 2
    assert manifest["run_order"] == ["intact", "b0_d20"]
    assert manifest["warnings"] == expected_warnings
    assert manifest["managed_files"] == sorted(manifest["managed_files"])
    assert "reports" not in manifest["managed_files"]
    assert "scaffold_manifest.json" in manifest["managed_files"]
    expected_hash_keys = set(manifest["managed_files"]) - {"scaffold_manifest.json"}
    assert set(manifest["managed_sha256"]) == expected_hash_keys
    for relative, expected_hash in manifest["managed_sha256"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected_hash
    assert result.case_order == ["intact", "b0_d20"]
    assert validate_generated_project(root) == []


def test_generated_content_is_honest_and_routes_postprocessing(tmp_path):
    root = create_project(FIXTURE, tmp_path / "project").root
    runbook = (root / "README_runbook.md").read_text(encoding="utf-8")
    notes = (root / "reports/modeling_notes.md").read_text(encoding="utf-8")
    postprocess = (root / "postprocess/manifest.csv").read_text(encoding="utf-8")
    bounds = (root / "calibration/parameter_bounds.yaml").read_text(encoding="utf-8")
    assert "intact-first" in runbook
    assert "PFC executable" not in runbook
    assert "run_all.dat" in runbook
    assert "fallback final state" in runbook
    assert "confirmed near-peak/post-peak" in runbook
    assert "heavy AE is disabled" in runbook
    assert "missing experiment" in runbook
    assert "pfc-postprocessing/references/script-catalog.md" in postprocess
    assert "stress_strain.csv,pfc-postprocessing/scripts/plot_curves.py" in postprocess
    assert "not final calibrated values" in bounds
    assert "heavy AE is disabled" in notes
    schema = (root / "geometry/cracks/polyline_schema.csv").read_text(encoding="utf-8")
    assert schema.startswith("point_id,x_mm,y_mm")


def test_targets_use_output_project_experiment_semantics(tmp_path):
    output = tmp_path / "project"
    create_project(FIXTURE, output)
    experiment = output / "data" / "experimental" / "intact.xlsx"
    experiment.parent.mkdir(parents=True, exist_ok=True)
    experiment.write_bytes(b"fixture")
    result = create_project(FIXTURE, output, force=True)
    assert result.warnings == [
        "missing experiment file: data/experimental/b0_d20.xlsx"
    ]
    targets = (output / "calibration/targets.csv").read_text(encoding="utf-8")
    assert "intact,data/experimental/intact.xlsx,registered" in targets
    assert "b0_d20,data/experimental/b0_d20.xlsx,missing_experiment" in targets


def test_render_context_warnings_are_collected_in_stable_case_order(tmp_path):
    intake = write_intake(
        tmp_path,
        lambda data: data["cases"][1].update(width_mm=0.5),
    )
    result = create_project(intake, tmp_path / "project")
    assert result.warnings == [
        "missing experiment file: data/experimental/intact.xlsx",
        "missing experiment file: data/experimental/b0_d20.xlsx",
        "case b0_d20: crack width_mm 5.000000e-01 is less than twice "
        "particle_radius_max_mm 1.000000e+00",
    ]


def test_existing_output_is_rejected_without_force(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        create_project(FIXTURE, output)


def test_force_replaces_only_managed_files_and_preserves_user_file(tmp_path):
    output = tmp_path / "project"
    create_project(FIXTURE, output)
    user_file = output / "reports" / "user_notes.md"
    user_file.write_text("keep", encoding="utf-8")
    create_project(FIXTURE, output, force=True)
    assert user_file.read_text(encoding="utf-8") == "keep"


def test_force_rejects_output_without_prior_manifest(tmp_path):
    output = tmp_path / "project"
    output.mkdir()
    with pytest.raises(ConfigError, match="prior scaffold_manifest.json"):
        create_project(FIXTURE, output, force=True)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda manifest: manifest.update(schema="fake"), "schema"),
        (lambda manifest: manifest.update(version=999), "version"),
        (lambda manifest: manifest["managed_files"].remove("scaffold_manifest.json"), "self"),
        (lambda manifest: manifest.pop("managed_sha256"), "managed_sha256"),
        (
            lambda manifest: manifest["managed_sha256"].pop("README_runbook.md"),
            "keys must exactly match",
        ),
        (
            lambda manifest: manifest["managed_sha256"].update({"extra.txt": "0" * 64}),
            "keys must exactly match",
        ),
        (lambda manifest: manifest["managed_files"].append("README_runbook.md"), "duplicate"),
        (lambda manifest: manifest["managed_files"].append("readme_RUNBOOK.md"), "alias"),
        (lambda manifest: manifest["managed_files"].append("C:/outside"), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append("safe:stream"), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append("bad<name"), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append("bad>name"), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append('bad"name'), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append("bad|name"), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append("bad?name"), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append("bad*name"), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append("CON/file"), "unsafe managed path"),
        (lambda manifest: manifest["managed_files"].append("trail./file"), "unsafe managed path"),
    ],
)
def test_force_rejects_invalid_prior_manifest(tmp_path, mutate, message):
    output = tmp_path / "project"
    create_project(FIXTURE, output)
    manifest_path = output / "scaffold_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ConfigError, match=message):
        create_project(FIXTURE, output, force=True)


def test_force_rejects_unmanaged_existing_collision(tmp_path):
    output = tmp_path / "project"
    create_project(FIXTURE, output)
    manifest_path = output / "scaffold_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["managed_files"].remove("README_runbook.md")
    manifest["managed_sha256"].pop("README_runbook.md")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ConfigError, match="unmanaged existing path"):
        create_project(FIXTURE, output, force=True)
    assert (output / "README_runbook.md").is_file()


def test_force_rejects_modified_managed_file(tmp_path):
    output = tmp_path / "project"
    create_project(FIXTURE, output)
    managed = output / "README_runbook.md"
    managed.write_text("user changed managed content", encoding="utf-8")
    with pytest.raises(ConfigError, match="managed file hash mismatch"):
        create_project(FIXTURE, output, force=True)
    assert managed.read_text(encoding="utf-8") == "user changed managed content"


def _tree_snapshot(root):
    return {
        path.relative_to(root).as_posix(): (
            "dir" if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()
        )
        for path in root.rglob("*")
    }


def test_second_directory_rename_failure_restores_exact_project(tmp_path, monkeypatch):
    import cpb2d_scaffold

    output = tmp_path / "project"
    create_project(FIXTURE, output)
    user_file = output / "reports" / "user_notes.md"
    user_file.write_text("keep", encoding="utf-8")
    before = _tree_snapshot(output)
    real_replace = cpb2d_scaffold.os.replace

    def fail_stage_publish(source, destination):
        source_path = Path(source)
        if ".cpb2d-stage-" in source_path.name and Path(destination) == output:
            raise OSError("injected second rename failure")
        return real_replace(source, destination)

    monkeypatch.setattr(cpb2d_scaffold.os, "replace", fail_stage_publish)
    with pytest.raises(OSError, match="injected second rename failure"):
        create_project(FIXTURE, output, force=True)
    assert _tree_snapshot(output) == before
    assert not list(tmp_path.glob(".project.cpb2d-backup-*"))


def test_backup_cleanup_failure_returns_success_and_preserves_backup(tmp_path, monkeypatch):
    import cpb2d_scaffold

    output = tmp_path / "project"
    create_project(FIXTURE, output)
    intake = write_intake(
        tmp_path,
        lambda data: data["project"].update(title="Published replacement"),
    )
    real_rmtree = cpb2d_scaffold.shutil.rmtree

    def fail_backup_only(path, *args, **kwargs):
        if ".cpb2d-backup-" in Path(path).name:
            raise OSError("injected backup cleanup failure")
        return real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(cpb2d_scaffold.shutil, "rmtree", fail_backup_only)
    result = create_project(intake, output, force=True)

    backups = list(tmp_path.glob(".project.cpb2d-backup-*"))
    assert len(backups) == 1
    expected = (
        "published project but could not remove backup: "
        f"{backups[0].resolve()}"
    )
    assert expected in result.warnings
    assert backups[0].is_dir()
    assert yaml.safe_load(
        (output / "project_config.yaml").read_text(encoding="utf-8")
    )["project"]["title"] == "Published replacement"
    manifest = json.loads(
        (output / "scaffold_manifest.json").read_text(encoding="utf-8")
    )
    assert expected not in manifest["warnings"]
    assert validate_generated_project(output) == []


def test_rollback_failure_keeps_backup_and_reports_absolute_path(tmp_path, monkeypatch):
    import cpb2d_scaffold

    output = tmp_path / "project"
    create_project(FIXTURE, output)
    before = _tree_snapshot(output)
    real_replace = cpb2d_scaffold.os.replace

    def fail_publish_and_rollback(source, destination):
        source_path = Path(source)
        destination_path = Path(destination)
        if destination_path == output and (
            ".cpb2d-stage-" in source_path.name or ".cpb2d-backup-" in source_path.name
        ):
            raise OSError("injected rename failure")
        return real_replace(source, destination)

    monkeypatch.setattr(cpb2d_scaffold.os, "replace", fail_publish_and_rollback)
    with pytest.raises(ConfigError, match="rollback failed; backup preserved at") as caught:
        create_project(FIXTURE, output, force=True)
    backups = list(tmp_path.glob(".project.cpb2d-backup-*"))
    assert len(backups) == 1
    assert str(backups[0].resolve()) in str(caught.value)
    assert _tree_snapshot(backups[0]) == before


def test_reparse_scan_rejects_root_junction_flag(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    real_is_junction = getattr(Path, "is_junction", None)
    if real_is_junction is None:
        pytest.skip("Path.is_junction requires Python 3.12")
    monkeypatch.setattr(Path, "is_junction", lambda self: self == root)
    with pytest.raises(ConfigError, match="reparse"):
        _assert_tree_has_no_reparse_points(root)


def test_cli_validate_only_prints_order_and_warnings_without_output(tmp_path):
    output = tmp_path / "not-created"
    script = SCRIPTS / "create_cpb2d_project.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--from-intake",
            str(FIXTURE),
            "--output-dir",
            str(output),
            "--validate-only",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "validate-only preflight for proposed output directory" in completed.stdout
    assert "enabled case order: intact, b0_d20" in completed.stdout
    assert "missing experiment file:" in completed.stdout
    assert not output.exists()


def test_cli_creation_loads_intake_once(tmp_path, monkeypatch, capsys):
    import create_cpb2d_project
    import cpb2d_scaffold

    calls = 0
    real_load = cpb2d_scaffold.load_intake

    def load_once(path):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise ConfigError("second load forbidden")
        return real_load(path)

    monkeypatch.setattr(cpb2d_scaffold, "load_intake", load_once)
    output = tmp_path / "project"
    assert create_cpb2d_project.main([
        "--from-intake", str(FIXTURE), "--output-dir", str(output)
    ]) == 0
    assert calls == 1
    assert "enabled case order: intact, b0_d20" in capsys.readouterr().out


def test_cli_creation_prints_dynamic_result_warning_and_returns_zero(
    tmp_path, monkeypatch, capsys
):
    import create_cpb2d_project
    from cpb2d_scaffold import CreateResult

    output = tmp_path / "project"
    warning = "published project but could not remove backup: C:\\absolute\\backup"
    monkeypatch.setattr(
        create_cpb2d_project,
        "create_project",
        lambda *args, **kwargs: CreateResult(output, [warning], [], ["intact"]),
    )

    assert create_cpb2d_project.main([
        "--from-intake", str(FIXTURE), "--output-dir", str(output)
    ]) == 0
    captured = capsys.readouterr()
    assert f"warning: {warning}" in captured.out
    assert "created project:" in captured.out
    assert captured.err == ""


def test_cli_user_error_returns_two(tmp_path):
    script = SCRIPTS / "create_cpb2d_project.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--from-intake",
            str(tmp_path / "missing.yaml"),
            "--output-dir",
            str(tmp_path / "output"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "error:" in completed.stderr.lower()


def test_static_validator_returns_error_for_non_object_manifest(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "scaffold_manifest.json").write_text("[]", encoding="utf-8")
    errors = validate_generated_project(root)
    assert "scaffold_manifest.json root must be an object" in errors
    assert any("required root artifact is missing" in error for error in errors)


def test_static_validator_requires_root_artifacts_independently_of_manifest(tmp_path):
    root = create_project(FIXTURE, tmp_path / "project").root
    missing = root / "calibration" / "targets.csv"
    missing.unlink()
    manifest_path = root / "scaffold_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["managed_files"].remove("calibration/targets.csv")
    manifest["managed_sha256"].pop("calibration/targets.csv")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    errors = validate_generated_project(root)
    assert any(
        "required root artifact is missing: calibration/targets.csv" in error
        for error in errors
    )


def test_static_validator_reports_tampered_case_contract(tmp_path):
    root = create_project(FIXTURE, tmp_path / "project").root
    (root / "pfc_cases" / "intact" / "run_all.dat").write_text(
        "program call '4export.dat'\n", encoding="utf-8"
    )
    (root / "pfc_cases" / "b0_d20" / "2bond.dat").write_text(
        "${unresolved}\n", encoding="utf-8"
    )
    errors = validate_generated_project(root)
    assert any("run_all.dat does not match exact run order" in error for error in errors)
    assert any("unresolved placeholder" in error for error in errors)
