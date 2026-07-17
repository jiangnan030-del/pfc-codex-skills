"""
Convert PFC contact CSV → VTK PolyData (.vtp) with LINE cells.

Each contact becomes a line segment from (x1,y1) to (x2,y2),
colored by fmag (force magnitude). ParaView reads directly — no Glyph needed.

Usage:
    python gen_force_chain_vtp.py <case_dir>              # All stages
    python gen_force_chain_vtp.py <case_dir> --stage A    # Single stage

Output per stage:
    forcechain_stage_A.vtp, forcechain_stage_B.vtp, etc.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

from config import MODEL_TO_MM

STAGES = ['A', 'B', 'C', 'D']


def csv_to_vtp(case_dir: Path, stage: str):
    """Convert one stage contact CSV → VTK PolyData (.vtp) with line cells."""
    csv_path = case_dir / f'plotdata_contacts_stage_{stage}.csv'
    if not csv_path.exists():
        print(f'  [SKIP] {csv_path.name} not found')
        return None

    df = pd.read_csv(csv_path)
    for col in ['x1', 'y1', 'x2', 'y2', 'fx', 'fy', 'fmag']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['x1', 'y1', 'x2', 'y2', 'fmag'])

    n_contacts = len(df)
    if n_contacts == 0:
        print(f'  [SKIP] Stage {stage}: no valid contacts')
        return None

    n_points = n_contacts * 2

    # Points: interleaved (x1,y1,0) (x2,y2,0) ...
    points = np.zeros((n_points, 3), dtype=np.float32)
    points[0::2, 0] = df['x1'].values * MODEL_TO_MM
    points[0::2, 1] = df['y1'].values * MODEL_TO_MM
    points[1::2, 0] = df['x2'].values * MODEL_TO_MM
    points[1::2, 1] = df['y2'].values * MODEL_TO_MM

    # Connectivity: line 0 → points (0,1), line 1 → points (2,3), ...
    connectivity = np.arange(n_points, dtype=np.int32)
    offsets = np.arange(2, n_points + 1, 2, dtype=np.int32)

    fmag = df['fmag'].values.astype(np.float32)

    out_path = case_dir / f'forcechain_stage_{stage}.vtp'

    # Write ASCII VTP XML
    root = ET.Element('VTKFile', type='PolyData', version='0.1',
                      byte_order='LittleEndian')
    poly = ET.SubElement(root, 'PolyData')
    piece = ET.SubElement(poly, 'Piece',
                          NumberOfPoints=str(n_points),
                          NumberOfLines=str(n_contacts))

    # Points
    pts_elem = ET.SubElement(piece, 'Points')
    pts_da = ET.SubElement(pts_elem, 'DataArray',
                           type='Float32', NumberOfComponents='3',
                           format='ascii')
    pts_da.text = '\n'.join(f'{p[0]:.6f} {p[1]:.6f} {p[2]:.1f}' for p in points)

    # Lines
    lines_elem = ET.SubElement(piece, 'Lines')
    ET.SubElement(lines_elem, 'DataArray', type='Int32',
                  Name='connectivity', format='ascii').text = ' '.join(str(c) for c in connectivity)
    ET.SubElement(lines_elem, 'DataArray', type='Int32',
                  Name='offsets', format='ascii').text = ' '.join(str(o) for o in offsets)

    # Cell data (fmag for coloring, fx/fy optional)
    cell_data = ET.SubElement(piece, 'CellData', Scalars='fmag')
    ET.SubElement(cell_data, 'DataArray', type='Float32',
                  Name='fmag', format='ascii').text = ' '.join(f'{v:.4f}' for v in fmag)

    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(str(out_path), xml_declaration=True, encoding='utf-8')

    print(f'  Stage {stage}: {n_contacts} contacts → {out_path.name}')
    return out_path


def main():
    ap = argparse.ArgumentParser(description='Convert contact CSV to VTP for ParaView')
    ap.add_argument('case_dir', help='Path to case directory')
    ap.add_argument('--stage', choices=STAGES, help='Single stage (default: all)')
    args = ap.parse_args()

    case_dir = Path(args.case_dir)
    if not case_dir.exists():
        sys.exit(f'Directory not found: {case_dir}')

    stages = [args.stage] if args.stage else STAGES
    for s in stages:
        csv_to_vtp(case_dir, s)
    print('Done. Open .vtp in ParaView → Tube filter → color by fmag')


if __name__ == '__main__':
    main()
