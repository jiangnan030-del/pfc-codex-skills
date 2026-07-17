"""
ParaView Python script for force chain rendering from VTP (LINE cells).

Usage: pvbatch render_force_chain.py <case_dir> [--bg white|black]

Uses direct line rendering (no Tube) with variable line width by force magnitude.
Tube filter doesn't render LINE cells correctly in ParaView 5.12.
"""

import os, sys, glob

if len(sys.argv) < 2:
    print("Usage: pvbatch render_force_chain.py <case_dir>")
    sys.exit(1)

case_dir = sys.argv[1]
bg_color = "white"
for a in sys.argv:
    if a.startswith("--bg="):
        bg_color = a.split("=")[1]

from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()


def centered_parallel_camera(view, reader, pad=1.08):
    bounds = reader.GetDataInformation().GetBounds()
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax)
    dx = max(xmax - xmin, 1.0e-6)
    dy = max(ymax - ymin, 1.0e-6)
    aspect = float(view.ViewSize[0]) / float(view.ViewSize[1])
    half_height = max(0.5 * dy, 0.5 * dx / aspect) * pad

    view.CameraParallelProjection = 1
    view.CameraFocalPoint = [cx, cy, 0.0]
    view.CameraPosition = [cx, cy, 1.0]
    view.CameraViewUp = [0.0, 1.0, 0.0]
    view.CameraParallelScale = half_height

vtp_files = sorted(glob.glob(os.path.join(case_dir, "forcechain_stage_*.vtp")))
if not vtp_files:
    print(f"No VTP files in {case_dir}")
    sys.exit(0)

print(f"Found {len(vtp_files)} VTP files")

for vtp_path in vtp_files:
    base = os.path.splitext(os.path.basename(vtp_path))[0]
    png_name = base.replace("forcechain_stage_", "stage_") + "_fc.png"
    png_path = os.path.join(case_dir, png_name)

    if os.path.exists(png_path) and os.path.getmtime(png_path) >= os.path.getmtime(vtp_path):
        print(f"  [SKIP] {png_name}")
        continue

    print(f"  [RENDER] {base} ...")
    ResetSession()

    reader = XMLPolyDataReader(registrationName=base, FileName=[vtp_path])
    reader.UpdatePipeline()

    # Show lines directly with variable width by scalar
    view = CreateView('RenderView')
    disp = Show(reader, view)
    disp.Representation = 'Surface'
    disp.LineWidth = 3.0
    disp.ColorArrayName = ('CELLS', 'fmag')
    LUT = GetColorTransferFunction('fmag')
    LUT.ApplyPreset('Turbo', True)
    LUT.RescaleTransferFunctionToDataRange(True)
    disp.LookupTable = LUT

    # View setup
    view.ViewSize = [1600, 1200]
    bg_rgb = [1.0, 1.0, 1.0] if bg_color == "white" else [0.0, 0.0, 0.0]
    view.Background = bg_rgb
    view.CameraParallelProjection = 1

    Render()
    centered_parallel_camera(view, reader)
    Render()

    # Color bar
    disp.SetScalarBarVisibility(view, True)
    try:
        sb = GetScalarBar(LUT, view)
        sb.Title = 'Force (N)'
        sb.TitleFontSize = 14
        sb.LabelFontSize = 12
        sb.ScalarBarLength = 0.5
        if bg_color == "black":
            sb.TitleColor = [1, 1, 1]
            sb.LabelColor = [1, 1, 1]
    except:
        pass

    SaveScreenshot(png_path, view, ImageResolution=[1600, 1200])
    print(f"    -> {png_name}")
    Delete(reader)
    del view

print("Done.")
