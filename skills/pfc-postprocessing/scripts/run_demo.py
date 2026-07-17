from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "examples"
DEMO_OUT = EXAMPLES / "demo_outputs"


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True)


def main() -> None:
    if DEMO_OUT.exists():
        shutil.rmtree(DEMO_OUT)
    (DEMO_OUT / "figures").mkdir(parents=True, exist_ok=True)
    (DEMO_OUT / "animations").mkdir(parents=True, exist_ok=True)
    (DEMO_OUT / "tables").mkdir(parents=True, exist_ok=True)

    minimal = EXAMPLES / "minimal_case" / "data"
    plugin = EXAMPLES / "plugin_migration_case"
    anim = EXAMPLES / "animation_case" / "raw_frames"

    run(str(SCRIPTS / "plot_curves.py"), "--input-dir", str(minimal), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "minimal_case", "--stage", "demo")
    run(str(SCRIPTS / "plot_fields.py"), "--input-dir", str(minimal), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "minimal_case", "--stage", "demo")
    run(str(SCRIPTS / "plot_rose.py"), "--input-dir", str(minimal), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "minimal_case", "--stage", "demo")

    converted = DEMO_OUT / "converted_plugin"
    run(str(SCRIPTS / "convert_legacy_contact_export.py"), "--input-file", str(plugin / "legacy_contact_export.txt"), "--output-dir", str(converted))
    run(str(SCRIPTS / "plot_rose.py"), "--input-dir", str(converted), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "plugin_contact_case", "--stage", "demo")

    run(str(SCRIPTS / "convert_legacy_ball_export.py"), "--input-file", str(plugin / "legacy_ball_export.dat"), "--output-dir", str(converted))
    run(str(SCRIPTS / "plot_fields.py"), "--input-dir", str(converted), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "plugin_ball_case", "--stage", "demo")

    ordered = DEMO_OUT / "ordered_frames"
    run(str(SCRIPTS / "export_animation_frames.py"), "--input-dir", str(anim), "--output-dir", str(ordered), "--glob", "*.png")
    run(str(SCRIPTS / "export_animation.py"), "--input-dir", str(ordered), "--output-dir", str(DEMO_OUT / "animations"), "--stem", "demo_animation", "--fps", "4")
    print(DEMO_OUT)


if __name__ == "__main__":
    main()
