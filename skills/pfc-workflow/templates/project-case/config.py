from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
TEMPLATES_DIR = ROOT / "templates"
COMMON_CASE_FILES_DIR = TEMPLATES_DIR / "common_case_files"

BRIDGE_URL = "ws://localhost:9001"
POSTPROCESS_PYTHON_EXE = sys.executable
PFC_PYTHON_EXE = sys.executable
PFC_CONSOLE_EXE = Path("<PFC_CONSOLE_EXE>")
PARAVIEW_PVBATCH_EXE = Path("<PARAVIEW_PVBATCH_EXE>")

EXPERIMENT_DATA_ROOT = PROJECT_ROOT
MODEL_TO_MM = 1000.0
SPECIMEN_EXTENT_MODEL = (-0.02, 0.02)
MEASUREMENT_EXTENT_MODEL = (-0.018, 0.018)

ANGLES = [0, 30, 45, 60, 90]
DISTANCES = [14, 16, 18, 20]
INTACT_CASE = "Intact"
CASE_NAMES = [INTACT_CASE] + [f"b{angle}_d{distance}" for angle in ANGLES for distance in DISTANCES]

PLOT_STAGES = ["peak", "final"]
CONTACT_STAGES = ["A", "B", "C", "D"]

OUTPUT_SUMMARY_FILES = [
    "curve_metrics_summary_2d.xlsx",
    "experiment_simulation_comparison_2d.xlsx",
    "summary_2d.png",
]

CASE_CORE_FILES = [
    "1model.dat",
    "2bond.dat",
    "3load.dat",
    "4export.dat",
    "5plot.dat",
    "fracture.p2fis",
    "main.prj",
]

COMMON_CASE_FILES = [
    "export_peak_ball_plot.dat",
    "export_stage_A_contact_native.dat",
    "export_stage_A_fracture_native.dat",
    "export_stage_A_native.dat",
    "export_stage_B_contact_native.dat",
    "export_stage_B_fracture_native.dat",
    "export_stage_B_native.dat",
    "export_stage_C_contact_native.dat",
    "export_stage_C_fracture_native.dat",
    "export_stage_C_native.dat",
    "export_stage_D_contact_native.dat",
    "export_stage_D_fracture_native.dat",
    "export_stage_D_native.dat",
    "probe_ball_plot.dat",
    "probe_contact_plot.dat",
    "probe_fracture_plot.dat",
]


def to_mm(value: float) -> float:
    return value * MODEL_TO_MM


def specimen_extent_mm() -> tuple[float, float]:
    return tuple(to_mm(value) for value in SPECIMEN_EXTENT_MODEL)


def case_dir(case_name: str) -> Path:
    return ROOT / case_name


def case_title(case_name: str) -> str:
    if case_name == INTACT_CASE:
        return "Intact 2D"
    if case_name.startswith("b") and "_d" in case_name:
        angle, distance = case_name[1:].split("_d", maxsplit=1)
        return f"2D  beta={angle} deg  d={distance} mm"
    return case_name


def case_sort_key(case_name: str) -> tuple[int, int, int]:
    if case_name == INTACT_CASE:
        return (0, -1, -1)
    if case_name.startswith("b") and "_d" in case_name:
        angle_text, distance_text = case_name[1:].split("_d", maxsplit=1)
        if angle_text.isdigit() and distance_text.isdigit():
            return (1, int(angle_text), int(distance_text))
    return (2, 999, 999)


def existing_case_names() -> list[str]:
    names = []
    for name in CASE_NAMES:
        path = case_dir(name)
        if path.is_dir() and (path / "3load.dat").exists():
            names.append(name)
    return sorted(names, key=case_sort_key)


def map_case_to_experiment_file(case_name: str) -> Path:
    if case_name == INTACT_CASE:
        return EXPERIMENT_DATA_ROOT / "intact-7.xlsx"
    if case_name.startswith("b") and "_d" in case_name:
        angle_text, distance_text = case_name[1:].split("_d", maxsplit=1)
        return EXPERIMENT_DATA_ROOT / f"{int(angle_text)}-{int(distance_text)}-7.xlsx"
    raise ValueError(f"Unsupported case name: {case_name}")
