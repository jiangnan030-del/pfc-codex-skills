from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from config import BRIDGE_URL, CONTACT_STAGES, PARAVIEW_PVBATCH_EXE, PFC_CONSOLE_EXE, POSTPROCESS_PYTHON_EXE, case_dir

try:
    import websockets
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"Missing dependency 'websockets': {exc}") from exc


ROOT = Path(__file__).resolve().parent
EXPORT_STAGE_CONTACT_SCRIPT = ROOT / "export_stage_contact_python_data.py"
POSTPROCESS_SCRIPT = ROOT / "postprocess_results_2d.py"
CONTOUR_SCRIPT = ROOT / "plot_contours_2d.py"
PEAK_FIELDS_SCRIPT = ROOT / "plot_peak_fields.py"
STAGE_CONTACT_SCRIPT = ROOT / "plot_stage_contact_maps.py"
STRESS_STRAIN_ANALYSIS_SCRIPT = ROOT / "analyze_stress_strain.py"
FORCECHAIN_VTP_SCRIPT = ROOT / "gen_force_chain_vtp.py"
FORCECHAIN_RENDER_SCRIPT = ROOT / "render_force_chain.py"
AE_ENERGY_SCRIPT = ROOT / "plot_ae_energy.py"
SOLVE_ONLY_INPUT_FILES = [
    "1model.dat",
    "2bond.dat",
    "3load.dat",
    "4export.dat",
    "fracture.p2fis",
]
SOLVE_ONLY_OUTPUT_PATTERNS = [
    "*.sav",
    "stress_strain.csv",
    "ae_*.csv",
]


def ensure_case(case_name: str) -> Path:
    subprocess.run([sys.executable, str(ROOT / "generate_cases.py"), case_name], cwd=str(ROOT), check=True)
    case_path = case_dir(case_name)
    if not case_path.is_dir():
        raise FileNotFoundError(f"Case directory not found: {case_path}")
    return case_path


def native_export_lines() -> list[str]:
    lines: list[str] = []
    lines.extend(
        [
            "def _restore_for_native(save_name, fallback_name='final'):",
            "    primary = save_name + '.sav'",
            "    target = save_name if os.path.exists(primary) else fallback_name",
            "    itasca.command(f\"model restore '{target}'\")",
        ]
    )
    for stage in ["A", "B", "C", "D"]:
        lines.extend(
            [
                f"_restore_for_native('stage_{stage.lower()}')",
                f"itasca.command(\"program call 'export_stage_{stage}_native.dat'\")",
                f"itasca.command(\"program call 'export_stage_{stage}_fracture_native.dat'\")",
                f"itasca.command(\"program call 'export_stage_{stage}_contact_native.dat'\")",
            ]
        )
    lines.extend(
        [
            "_restore_for_native('peak')",
            "itasca.command(\"program call 'export_peak_ball_plot.dat'\")",
        ]
    )
    for index, (skip, name, scale_by_force) in enumerate(
        [
            (0, "force_s1", "on"),
            (2, "force_s2", "on"),
            (4, "force_s3", "on"),
            (1, "dist_s1", "off"),
            (3, "dist_s2", "off"),
        ]
    ):
        lines.extend(
            [
                "itasca.command(\"[contact_save_count = 1]\")",
                f"itasca.command(\"[contact_save_count_inc = {1 if index == 0 else 0}]\")",
                f"itasca.command(\"[contact_skip_count = {skip}]\")",
                f"itasca.command(\"[plot_name = 'probe_contact_{name}']\")",
                f"itasca.command(\"plot create 'probe_contact_{name}'\")",
                "itasca.command(\"plot clear\")",
                "itasca.command(\"plot view extent (-1.6,-1.6) (1.6,1.6)\")",
                "itasca.command(\"plot item create contact active on\")",
                "itasca.command(\"plot item modify 1 shape cylinder scale target 0.05 value 1 radius-factor automatic target 0.01 value 0.02\")",
                f"itasca.command(\"plot item modify 1 color-by vector-attribute 'force' color-options scaled ramp rainbow minimum automatic maximum automatic scale-by-force {scale_by_force}\")",
                f"itasca.command(\"plot export bitmap filename 'probe_contact_{name}.png' size 1600 1200\")",
            ]
        )
    lines.extend(
        [
            "_restore_for_native('final')",
            "itasca.command(\"plot create 'probe_contact_visibility'\")",
            "itasca.command(\"plot clear\")",
            "itasca.command(\"plot view extent (-0.025,-0.025) (0.025,0.025)\")",
            "itasca.command(\"plot item create ball active on\")",
            "itasca.command(\"plot item modify 1 shape ball shrink-factor target 0.05 value 1 pixel-size 5 spheres off\")",
            "itasca.command(\"plot item modify 1 color-by 'default'\")",
            "itasca.command(\"plot export bitmap filename 'probe_contact_visibility.png' size 1600 1200\")",
        ]
    )
    return lines


def write_native_exports_script(case_path: Path) -> Path:
    output = case_path / "run_native_exports.p2dat"
    lines = ["; Auto-generated native export runner"]
    for stage in ["A", "B", "C", "D"]:
        lines.append(f"model restore 'stage_{stage.lower()}'")
        lines.append(f"program call 'export_stage_{stage}_native.dat'")
        lines.append(f"program call 'export_stage_{stage}_fracture_native.dat'")
        lines.append(f"program call 'export_stage_{stage}_contact_native.dat'")
    lines.append("model restore 'peak'")
    lines.append("program call 'export_peak_ball_plot.dat'")
    for index, (skip, name, scale_by_force) in enumerate(
        [
            (0, "force_s1", "on"),
            (2, "force_s2", "on"),
            (4, "force_s3", "on"),
            (1, "dist_s1", "off"),
            (3, "dist_s2", "off"),
        ]
    ):
        lines.append("[contact_save_count = 1]")
        lines.append(f"[contact_save_count_inc = {1 if index == 0 else 0}]")
        lines.append(f"[contact_skip_count = {skip}]")
        lines.append(f"[plot_name = 'probe_contact_{name}']")
        lines.append(f"plot create 'probe_contact_{name}'")
        lines.append("plot clear")
        lines.append("plot view extent (-1.6,-1.6) (1.6,1.6)")
        lines.append("plot item create contact active on")
        lines.append("plot item modify 1 shape cylinder scale target 0.05 value 1 radius-factor automatic target 0.01 value 0.02")
        lines.append(
            "plot item modify 1 color-by vector-attribute 'force' "
            f"color-options scaled ramp rainbow minimum automatic maximum automatic scale-by-force {scale_by_force}"
        )
        lines.append(f"plot export bitmap filename 'probe_contact_{name}.png' size 1600 1200")
    lines.extend(
        [
            "model restore 'final'",
            "plot create 'probe_contact_visibility'",
            "plot clear",
            "plot view extent (-0.025,-0.025) (0.025,0.025)",
            "plot item create ball active on",
            "plot item modify 1 shape ball shrink-factor target 0.05 value 1 pixel-size 5 spheres off",
            "plot item modify 1 color-by 'default'",
            "plot export bitmap filename 'probe_contact_visibility.png' size 1600 1200",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def write_stage_contact_export_datafile(case_path: Path) -> Path:
    output = case_path / "export_stage_contact_data.dat"
    content = """; Auto-generated stage contact export using FISH
fish define create_measurement_grid
    command
        measure delete
    endcommand
    global measure_count = 0
    global measure_cx = array.create(500)
    global measure_cy = array.create(500)
    local nx = 15
    local ny = 15
    local x_min = -0.018
    local x_max = 0.018
    local y_min = -0.018
    local y_max = 0.018
    local dx = (x_max - x_min) / nx
    local dy = (y_max - y_min) / ny
    local mrad = dx * 0.55
    loop local j (0, ny - 1)
        loop local i (0, nx - 1)
            local cx = x_min + (i + 0.5) * dx
            local cy = y_min + (j + 0.5) * dy
            measure_count = measure_count + 1
            measure_cx(measure_count) = cx
            measure_cy(measure_count) = cy
            command
                measure create id [measure_count] position [cx] [cy] radius [mrad]
            endcommand
        endloop
    endloop
end

fish define export_stage_contacts
    local fname = 'plotdata_contacts_stage_' + stage_label + '.csv'
    local count_max = 400000
    local arr = array.create(count_max)
    arr(1) = 'id,x,y,x1,y1,x2,y2,fx,fy,fmag'
    local idx = 1
    loop foreach local cp contact.list
        if contact.model(cp) = 'linearpbond'
            local bp1 = contact.end1(cp)
            local bp2 = contact.end2(cp)
            if bp1 # null
                if bp2 # null
                    local pos = contact.pos(cp)
                    local p1 = ball.pos(bp1)
                    local p2 = ball.pos(bp2)
                    local force = contact.force.global(cp)
                    local fx = comp.x(force)
                    local fy = comp.y(force)
                    local fmag = math.sqrt(fx * fx + fy * fy)
                    idx = idx + 1
                    arr(idx) = string(contact.id(cp)) + ',' + string(comp.x(pos)) + ',' + string(comp.y(pos)) + ',' + string(comp.x(p1)) + ',' + string(comp.y(p1)) + ',' + string(comp.x(p2)) + ',' + string(comp.y(p2)) + ',' + string(fx) + ',' + string(fy) + ',' + string(fmag)
                end_if
            end_if
        end_if
    endloop
    local status = file.open(fname, 1, 1)
    status = file.write(arr, idx + 1)
    status = file.close()
end

fish define export_stage_measures
    command
        model clean
    endcommand
    local fname = 'plotdata_measures_stage_' + stage_label + '.csv'
    local status = file.open(fname, 1, 1)
    local arr = array.create(10000)
    arr(1) = 'x,y,porosity,coord_num'
    local idx = 1
    loop local k (1, measure_count)
        local m = measure.find(k)
        if m # null
            local por = measure.porosity(m)
            local coord = measure.coordination(m)
            idx = idx + 1
            arr(idx) = string(measure_cx(k)) + ',' + string(measure_cy(k)) + ',' + string(por) + ',' + string(coord)
        end_if
    endloop
    status = file.write(arr, idx + 1)
    status = file.close()
end

[stage_label = 'A']
model restore 'stage_a'
@create_measurement_grid
@export_stage_contacts
@export_stage_measures

[stage_label = 'B']
model restore 'stage_b'
@create_measurement_grid
@export_stage_contacts
@export_stage_measures

[stage_label = 'C']
model restore 'stage_c'
@create_measurement_grid
@export_stage_contacts
@export_stage_measures

[stage_label = 'D']
model restore 'stage_d'
@create_measurement_grid
@export_stage_contacts
@export_stage_measures
"""
    output.write_text(content, encoding="utf-8")
    return output


def bridge_root() -> Path:
    alias_root = Path(os.environ.get("TEMP", str(ROOT))) / "pfc2d_bridge_data"
    if alias_root.exists():
        return alias_root
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                f"$alias = '{alias_root}'; "
                f"New-Item -ItemType Junction -Path $alias -Target '{ROOT.parent}' -Force | Out-Null"
            ),
        ],
        check=True,
    )
    return alias_root


def bridge_case_path(case_path: Path) -> Path:
    return bridge_root() / "pfc_2d" / case_path.name


def bridge_script_path(script_path: Path) -> Path:
    return bridge_root() / "pfc_2d" / script_path.name


def prepare_minimal_solve_workspace(case_path: Path, skip_1model: bool = False) -> Path:
    solve_root = bridge_root() / "_solve_minimal"
    case_root = solve_root / case_path.name
    case_root.mkdir(parents=True, exist_ok=True)
    for old_path in case_root.iterdir():
        if old_path.is_dir():
            try:
                shutil.rmtree(old_path)
            except PermissionError:
                pass
    work_path = case_root / f"run_{uuid.uuid4().hex[:8]}"
    work_path.mkdir(parents=True, exist_ok=True)
    for name in SOLVE_ONLY_INPUT_FILES:
        shutil.copy2(case_path / name, work_path / name)
    if skip_1model:
        sample_path = case_path / "sample.sav"
        if not sample_path.exists():
            raise FileNotFoundError(f"Missing sample.sav for --skip-1model: {sample_path}")
        shutil.copy2(sample_path, work_path / "sample.sav")
    return work_path


def sync_minimal_solve_outputs(work_path: Path, case_path: Path) -> None:
    for pattern in SOLVE_ONLY_OUTPUT_PATTERNS:
        for source in work_path.glob(pattern):
            if source.is_file():
                shutil.copy2(source, case_path / source.name)


def build_bridge_preamble(work_path: Path, minimal_plot_mode: bool = False) -> list[str]:
    lines = ["import os", "import itasca", f"os.chdir(r'{work_path.as_posix()}')"]
    if minimal_plot_mode:
        lines.extend(
            [
                "try:",
                "    itasca.command(\"plot clear\")",
                "except Exception:",
                "    pass",
            ]
        )
    return lines


def clean_case_outputs(case_path: Path, preserve_sample: bool = False, include_visual_outputs: bool = True) -> None:
    patterns = [
        "*.sav",
        "stress_strain.csv",
        "plotdata_*.csv",
        "forcechain_stage_*.vtp",
    ]
    if include_visual_outputs:
        patterns.extend(
            [
        "curve_compare_2d.png",
        "curve_metrics_2d.xlsx",
        "ae_*.csv",
        "ae_*.png",
        "ae_*.svg",
        "ae_*.pdf",
        "ae_*.xlsx",
        "plot_*.png",
        "plot_*.svg",
        "plot_*.pdf",
        "peak_*_field.png",
        "peak_*_field.svg",
        "stage_*_contact_*.png",
        "stage_*_fracture_*.png",
        "stage_*_native.png",
        "probe_contact_*.png",
        "probe_contact_visibility.png",
        "peak_ball_native.png",
            ]
        )
    for pattern in patterns:
        for path in case_path.glob(pattern):
            if path.is_file():
                if preserve_sample and path.name.lower() == "sample.sav":
                    continue
                try:
                    path.unlink()
                except PermissionError:
                    # Keep going when an external viewer is holding a figure open.
                    print(f"skip locked output: {path.name}")


async def execute_pfc(code: str, timeout_s: int = 600) -> dict:
    wrapped_code = f"exec(compile({json.dumps(code)}, '<codex-bridge>', 'exec'))"
    async with websockets.connect(
        BRIDGE_URL,
        compression=None,
        max_size=50 * 2**20,
        ping_interval=None,
        ping_timeout=None,
    ) as ws:
        message = {
            "type": "execute_code",
            "request_id": str(uuid.uuid4()),
            "code": wrapped_code,
            "timeout_ms": timeout_s * 1000,
        }
        await ws.send(json.dumps(message))
        response = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout_s + 60))
        data = response.get("data", {})
        stdout = data.get("stdout", "") or data.get("message", "")
        stderr = data.get("stderr", "")
        if stdout:
            for line in stdout.splitlines()[-30:]:
                print(line)
        if stderr:
            for line in stderr.splitlines()[-20:]:
                print(f"[stderr] {line}")
        return response


def bridge_is_available() -> bool:
    try:
        response = asyncio.run(execute_pfc("print('bridge-ok')", timeout_s=20))
    except Exception:
        return False
    return response.get("status") != "error"


def run_pfc_pipeline_via_bridge(
    work_path: Path,
    skip_1model: bool = False,
    skip_native: bool = False,
    include_post_exports: bool = True,
    minimal_plot_mode: bool = False,
) -> None:
    dat_files = ["1model.dat", "2bond.dat", "3load.dat", "4export.dat"]
    if include_post_exports:
        dat_files.append("5plot.dat")
    if skip_1model:
        dat_files = [name for name in dat_files if name != "1model.dat"]

    export_script_text = bridge_script_path(EXPORT_STAGE_CONTACT_SCRIPT).as_posix()
    lines = build_bridge_preamble(work_path, minimal_plot_mode=minimal_plot_mode)
    for name in dat_files:
        lines.append(f"itasca.command(\"program call '{name}'\")")
    if include_post_exports:
        lines.append(f"exec(open(r'{export_script_text}', encoding='utf-8').read(), {{}})")
    if include_post_exports and not skip_native:
        lines.extend(native_export_lines())
    response = asyncio.run(execute_pfc("\n".join(lines), timeout_s=7200))
    if response.get("status") == "error":
        raise RuntimeError("PFC bridge pipeline returned error status.")


def run_console_datafile(case_path: Path, datafile: Path, timeout_s: int = 7200) -> None:
    if not PFC_CONSOLE_EXE.exists():
        raise FileNotFoundError(f"PFC console executable not found: {PFC_CONSOLE_EXE}")
    subprocess.run([str(PFC_CONSOLE_EXE), str(datafile)], cwd=str(case_path), check=True, timeout=timeout_s)


def run_pfc_pipeline_via_console(
    work_path: Path,
    skip_1model: bool = False,
    skip_native: bool = False,
    include_post_exports: bool = True,
) -> None:
    if include_post_exports:
        write_stage_contact_export_datafile(work_path)
    commands = []
    if not skip_1model:
        commands.append("program call '1model.dat'")
    commands.extend(
        [
            "program call '2bond.dat'",
            "program call '3load.dat'",
            "program call '4export.dat'",
        ]
    )
    if include_post_exports:
        commands.extend(
            [
                "program call '5plot.dat'",
                "program call 'export_stage_contact_data.dat'",
            ]
        )
    if include_post_exports and not skip_native:
        commands.append("program call 'run_native_exports.p2dat'")
    commands.append("program quit")
    datafile = work_path / "run_case_console.dat"
    datafile.write_text("\n".join(commands) + "\n", encoding="ascii")
    run_console_datafile(work_path, datafile)


def run_python_script(script_path: Path, *args: str) -> None:
    subprocess.run([POSTPROCESS_PYTHON_EXE, str(script_path), *args], cwd=str(ROOT), check=True)


def run_forcechain_render(case_path: Path) -> None:
    if not PARAVIEW_PVBATCH_EXE.exists():
        print(f"ParaView pvbatch not found, skip force-chain PNG render: {PARAVIEW_PVBATCH_EXE}")
        return
    subprocess.run(
        [str(PARAVIEW_PVBATCH_EXE), str(FORCECHAIN_RENDER_SCRIPT), str(case_path), "--bg=white"],
        cwd=str(ROOT),
        check=True,
    )


def run_postprocess(case_name: str, case_path: Path) -> None:
    run_python_script(POSTPROCESS_SCRIPT, case_name)
    run_python_script(CONTOUR_SCRIPT, case_name, "all")
    run_python_script(PEAK_FIELDS_SCRIPT, case_name)
    run_python_script(STAGE_CONTACT_SCRIPT, case_name)
    run_python_script(STRESS_STRAIN_ANALYSIS_SCRIPT, case_name)
    if (case_path / "ae_events.csv").exists():
        run_python_script(AE_ENERGY_SCRIPT, case_name)
    subprocess.run([POSTPROCESS_PYTHON_EXE, str(FORCECHAIN_VTP_SCRIPT), str(case_path)], cwd=str(ROOT), check=True)
    run_forcechain_render(case_path)


def verify_outputs(case_path: Path) -> None:
    required = [
        case_path / "curve_compare_2d.png",
        case_path / "curve_metrics_2d.xlsx",
        case_path / "ae_events.csv",
        case_path / "ae_clustered_events.csv",
        case_path / "ae_energy_overview.png",
        case_path / "ae_event_map.png",
        case_path / "ae_event_evolution.png",
        case_path / "ae_source_event_map.png",
        case_path / "ae_tk_source_map.png",
        case_path / "ae_energy_metrics.xlsx",
        case_path / "plot_stress_peak.png",
        case_path / "plot_porosity_peak.png",
        case_path / "peak_stress_field.png",
        case_path / "peak_porosity_field.png",
        case_path / "peak_ball_field.png",
        case_path / "peak_ball_native.png",
        case_path / "stage_A_fc.png",
        case_path / "stage_A_native.png",
        case_path / "stage_A_fracture_only.png",
        case_path / "stage_A_contact_distribution.png",
        case_path / "probe_contact_force_s1.png",
        case_path / "probe_contact_visibility.png",
        case_path / "stress_strain.csv",
    ]
    missing = [path.name for path in required if not path.exists()]
    for stage in CONTACT_STAGES:
        if not (case_path / f"plotdata_contacts_stage_{stage}.csv").exists():
            missing.append(f"plotdata_contacts_stage_{stage}.csv")
        if not (case_path / f"plotdata_measures_stage_{stage}.csv").exists():
            missing.append(f"plotdata_measures_stage_{stage}.csv")
    if missing:
        raise FileNotFoundError("Missing expected outputs: " + ", ".join(missing))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a migrated PFC 2D case end-to-end.")
    parser.add_argument("case", help="Case name, for example Intact or b60_d20")
    parser.add_argument("--skip-pfc", action="store_true", help="Skip PFC solve/export steps.")
    parser.add_argument("--skip-1model", action="store_true", help="Reuse an existing sample.sav if present.")
    parser.add_argument("--skip-native", action="store_true", help="Skip native PFC export scripts.")
    parser.add_argument(
        "--solve-only",
        action="store_true",
        help="Run only 1model/2bond/3load/4export, then stop before any plotting/postprocess.",
    )
    args = parser.parse_args()

    case_path = ensure_case(args.case)
    write_native_exports_script(case_path)
    minimal_solve_mode = args.solve_only
    work_path = prepare_minimal_solve_workspace(case_path, skip_1model=args.skip_1model) if minimal_solve_mode else case_path

    if not args.skip_pfc:
        clean_case_outputs(
            case_path,
            preserve_sample=args.skip_1model,
            include_visual_outputs=not args.solve_only,
        )
        if bridge_is_available():
            print("Using bridge mode")
            run_pfc_pipeline_via_bridge(
                work_path if minimal_solve_mode else bridge_case_path(case_path),
                skip_1model=args.skip_1model,
                skip_native=args.skip_native,
                include_post_exports=not args.solve_only,
                minimal_plot_mode=minimal_solve_mode,
            )
        else:
            print("Bridge unavailable, falling back to console mode")
            run_pfc_pipeline_via_console(
                work_path,
                skip_1model=args.skip_1model,
                skip_native=args.skip_native,
                include_post_exports=not args.solve_only,
            )
        if minimal_solve_mode:
            sync_minimal_solve_outputs(work_path, case_path)

    if args.solve_only:
        print(f"Solve-only complete: {case_path}")
        return
    run_postprocess(args.case, case_path)
    verify_outputs(case_path)
    print(f"Case complete: {case_path}")


if __name__ == "__main__":
    main()
