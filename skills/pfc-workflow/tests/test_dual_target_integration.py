from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).parents[3]
SKILL = ROOT / "skills" / "dual-target-calibration"


def test_dual_target_skill_is_routed_and_licensed():
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    workflow = (ROOT / "skills/pfc-workflow/SKILL.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    notice = (SKILL / "NOTICE.md").read_text(encoding="utf-8")
    assert "exactly two active" in skill_text
    assert "dual-target-calibration" in workflow
    assert "24 个技能" in readme
    assert "AGPL-3.0" in readme
    assert "AGPL-3.0" in notice
    assert (SKILL / "LICENSE").is_file()
    assert (SKILL / "icon.svg").is_file()
    assert (SKILL / "agents/openai.yaml").is_file()


def test_installed_submit_adapter_has_no_default_engine_side_effect():
    sys.path.insert(0, str(SKILL / "adapters"))
    import submit  # noqa: PLC0415

    with pytest.raises(NotImplementedError):
        submit.submit({"X": 1.0, "Y": 2.0})


def test_dual_target_clis_expose_help():
    for name in ("regress_exact.py", "regress_lstsq.py", "sensitivity.py"):
        completed = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / name), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        assert "usage:" in completed.stdout.lower()
