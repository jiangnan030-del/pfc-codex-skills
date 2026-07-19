from pathlib import Path
import sys

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cpb2d_scaffold import ConfigError, load_intake


def test_load_minimal_intake_normalizes_si_values():
    cfg = load_intake(Path(__file__).parent / "fixtures" / "intake_minimal.yaml")
    assert cfg.project.slug == "cpb_2d_ucs_demo"
    assert cfg.specimen.width_m == pytest.approx(0.04)
    assert cfg.specimen.radius_min_m == pytest.approx(0.0003)
    assert [case.name for case in cfg.cases] == ["intact", "b0_d20"]


@pytest.mark.parametrize("slug", ["我的项目", "CPB Demo", "cpb-demo", "../cpb"])
def test_project_slug_rejects_unsafe_names(tmp_path, slug):
    intake = tmp_path / "bad.yaml"
    intake.write_text(f"project:\n  slug: {slug!r}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="project.slug"):
        load_intake(intake)


def test_non_positive_particle_radius_is_rejected(tmp_path):
    intake = tmp_path / "bad.yaml"
    intake.write_text(
        "project:\n  slug: cpb_demo\n"
        "specimen:\n  particle_radius_min_mm: 0\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="particle_radius_min_mm"):
        load_intake(intake)
