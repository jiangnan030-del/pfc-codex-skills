from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from dual_target_common import (  # noqa: E402
    CalibrationError,
    exact_solution,
    fit_response_surfaces,
    nearest_controlled_pair,
    require_mixed_signs,
)


def test_require_mixed_signs_accepts_zero_and_both_sides():
    require_mixed_signs(np.array([-0.1, 0.0, 0.2]), "A")
    with pytest.raises(CalibrationError, match="same sign"):
        require_mixed_signs(np.array([0.1, 0.2, 0.3]), "A")


def test_exact_solution_recovers_two_target_intersection():
    # A = 1 + 2X + Y; B = 3 - X + 2Y. Target A=8, B=4 -> X=2.6, Y=1.8.
    data = np.array([
        [1.0, 1.0, 4.0, 4.0],
        [3.0, 1.0, 8.0, 2.0],
        [1.0, 3.0, 6.0, 8.0],
    ])
    x_opt, y_opt = exact_solution(data, 8.0, 4.0)
    assert x_opt == pytest.approx(2.6)
    assert y_opt == pytest.approx(1.8)


def test_exact_solution_rejects_collinear_design():
    data = np.array([
        [1.0, 1.0, 4.0, 4.0],
        [2.0, 2.0, 7.0, 5.0],
        [3.0, 3.0, 10.0, 6.0],
    ])
    with pytest.raises(CalibrationError, match="rank"):
        exact_solution(data, 8.0, 4.0)


def test_fit_response_surfaces_reports_exact_r2_and_solution():
    xy = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=float)
    a = 1 + 2 * xy[:, 0] + xy[:, 1]
    b = 3 - xy[:, 0] + 2 * xy[:, 1]
    data = np.column_stack([xy, a, b])
    fit = fit_response_surfaces(data, 8.0, 4.0)
    assert fit["r2_a"] == pytest.approx(1.0)
    assert fit["r2_b"] == pytest.approx(1.0)
    assert fit["x_opt"] == pytest.approx(2.6)
    assert fit["y_opt"] == pytest.approx(1.8)


def test_nearest_controlled_pair_limits_y_confounding():
    data = np.array([
        [1.00, 10.0, 1.0, 1.0],
        [1.01, 20.0, 2.0, 2.0],  # nearest X, but Y is badly confounded
        [1.10, 10.1, 1.2, 1.1],
        [1.20, 10.0, 1.3, 1.2],
    ])
    i, j = nearest_controlled_pair(data, max_relative_y_change=0.02)
    assert 1 not in {i, j}
    assert abs(data[j, 0] - data[i, 0]) == pytest.approx(0.1)
    assert abs(data[j, 1] - data[i, 1]) / max(abs(data[i, 1]), abs(data[j, 1])) <= 0.02


def test_nearest_controlled_pair_rejects_uncontrolled_trials():
    data = np.array([[1.0, 1.0, 1.0, 1.0], [2.0, 4.0, 2.0, 2.0]])
    with pytest.raises(CalibrationError, match="controlled pair"):
        nearest_controlled_pair(data, max_relative_y_change=0.05)


def test_exact_cli_passes_safe_crossing_and_rejects_same_sign(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text(
        """targets:
  A: {value: 8.0}
  B: {value: 4.0}
levers:
  X: {bounds: [0.0, 4.0]}
  Y: {bounds: [0.0, 4.0]}
thresholds:
  exact_basin_error_span: 2.0
budget: {max_trials: 10}
""",
        encoding="utf-8",
    )
    trials = tmp_path / "trials.csv"
    trials.write_text("trial,X,Y,A,B\nT1,1,1,4,4\nT2,3,1,8,2\nT3,1,3,6,8\n", encoding="utf-8")
    command = [sys.executable, str(SCRIPTS / "regress_exact.py"), str(trials), str(config)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    assert "X_opt=2.6" in completed.stdout
    trials.write_text("trial,X,Y,A,B\nT1,1,1,9,5\nT2,3,1,10,6\nT3,1,3,11,7\n", encoding="utf-8")
    blocked = subprocess.run(command, capture_output=True, text=True, check=False)
    assert blocked.returncode == 2
    assert "same sign" in blocked.stderr
