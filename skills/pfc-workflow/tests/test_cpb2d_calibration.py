from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import pytest
import yaml

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cpb2d_calibration import (  # noqa: E402
    BASELINE_PARAMETERS,
    calibration_objective,
    extract_curve_metrics,
    materialize_case,
    validate_runtime_outputs,
)


def write_curve(path: Path, rows: list[tuple[float, float, int]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["strain", "stress_mpa", "crack_num"])
        writer.writerows(rows)


def test_extract_curve_metrics_uses_prepeak_interpolation_and_target_final_strain(tmp_path):
    curve = tmp_path / "stress_strain.csv"
    write_curve(
        curve,
        [
            (0.0, 0.0, 0),
            (-0.02, 0.04, 1),
            (-0.04, 0.08, 2),
            (-0.06, 0.10, 3),
            (-0.08, 0.08, 4),
            (-0.10, 0.06, 5),
        ],
    )
    metrics = extract_curve_metrics(curve, target_final_strain=0.09)
    assert metrics["peak_stress_mpa"] == pytest.approx(0.10)
    assert metrics["peak_strain"] == pytest.approx(0.06)
    assert metrics["middle_secant_stiffness_mpa"] == pytest.approx(1.916666666666667)
    assert metrics["late_secant_stiffness_mpa"] == pytest.approx(1.666666666666667)
    assert metrics["final_peak_ratio"] == pytest.approx(0.7)
    assert metrics["final_crack_count"] == 5


def test_calibration_objective_matches_approved_relative_tolerances():
    targets = {
        "peak_stress_mpa": 0.10,
        "peak_strain": 0.05,
        "middle_secant_stiffness_mpa": 2.0,
        "late_secant_stiffness_mpa": 1.5,
        "final_peak_ratio": 0.80,
    }
    metrics = dict(targets)
    metrics["peak_stress_mpa"] = 0.105
    objective, details = calibration_objective(metrics, targets)
    assert objective == pytest.approx(2.0)
    assert details["peak_stress_mpa"] == pytest.approx(2.0)


def test_materialize_case_creates_only_independent_intact_project(tmp_path):
    params = dict(BASELINE_PARAMETERS)
    artifact = tmp_path / "artifact"
    case_dir = materialize_case(params, artifact)
    assert case_dir == artifact / "project" / "pfc_cases" / "intact"
    assert case_dir.is_dir()
    assert not (artifact / "project" / "pfc_cases" / "b0_d20").exists()
    intake = yaml.safe_load((artifact / "intake.yaml").read_text(encoding="utf-8"))
    assert intake["contact_model"]["linear_emod_pa"] == BASELINE_PARAMETERS["linear_emod_pa"]
    assert intake["loading"]["target_peak_strain_guess"] == 0.10
    assert "2.200000e+06" in (case_dir / "1model.dat").read_text(encoding="utf-8")


def test_validate_runtime_outputs_rejects_fallback_or_missing_final(tmp_path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    write_curve(case_dir / "stress_strain.csv", [(0, 0, 0), (0.1, 0.1, 1)])
    status = {"peak_confirmed": False, "safety_stop": True, "stage_fallback": True}
    (case_dir / "runtime_status.json").write_text(json.dumps(status), encoding="utf-8")
    with pytest.raises(ValueError, match="final.sav"):
        validate_runtime_outputs(case_dir)
    for name in ["final.sav", "peak.sav", "stage_a.sav", "stage_b.sav", "stage_c.sav", "stage_d.sav"]:
        (case_dir / name).write_bytes(b"not-empty")
    with pytest.raises(ValueError, match="unconfirmed peak"):
        validate_runtime_outputs(case_dir)
