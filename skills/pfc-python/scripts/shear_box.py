"""Soil-rock mixture 3D direct shear specimen built from Python.

Strategy: place clump stones bin-by-bin at a target volume fraction, delete clumps crossing the
specimen boundary, fill the soil matrix with spherical `cement` clumps, then back-calculate the real
stone content.

    R_stone  = V_stone  / V_total
    R_cement = V_cement / V_total

Case-specific assets: `input_clump_moban` (defines clump templates s1..s5) and all geometric values.
Replace them with project values and verify command syntax for your PFC version.
"""

import itasca as it
import numpy as np

# --- specimen geometry and generation parameters ---------------------------------
x0 = 0.0
y0 = 0.0
z0 = 0.0
xlength = 1.0
ylength = 1.0
zlength = 1.0
x_extend = 0.2 * xlength
y_extend = 0.2 * ylength
z_extend = 0.2 * zlength
wlength = 0.2 * xlength      # baffle (dangban) length
ballFriction = 0.1
wallFriction = 0.1
w_resolution = 0.05
poros = 0.35
rlo = 0.05e-2
rhi = 0.1e-2
clump_poro = 0.7
stone_need = 0.33

ratio_stone = None
ratio_cement = None


def in_box():
    """Delete any clump whose pebbles cross the specimen box."""
    clump_delete = []
    for cp in it.clump.pebble.list():
        p_x = cp.pos_x()
        p_y = cp.pos_y()
        p_z = cp.pos_z()
        p_r = cp.radius()
        if p_x + p_r >= x0 + xlength or p_x - p_r <= x0 \
           or p_y + p_r >= y0 + ylength or p_y - p_r <= y0 \
           or p_z + p_r >= z0 + zlength or p_z - p_r <= z0:
            if cp.clump().id() not in clump_delete:
                clump_delete.append(cp.clump().id())
    for cp_delete in clump_delete:
        it.clump.find(cp_delete).delete()


def compute_block_ratio():
    """Back-calculate the real stone / cement volume fractions from clump groups."""
    v_stone = 0.0
    v_total = 0.0
    v_cement = 0.0
    for cl in it.clump.list():
        if cl.in_group('stone'):
            vc = cl.vol()
            v_total += vc
            v_stone += vc
        if cl.in_group('cement'):
            vb = cl.vol()
            v_total += vb
            v_cement += vb
    global ratio_stone, ratio_cement
    ratio_stone = v_stone / v_total
    ratio_cement = v_cement / v_total
    return ratio_stone, ratio_cement


def _wall(wall_id, name, p1, p2, p3, p4):
    """Create one quadrilateral wall as two triangular facets."""
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3
    x4, y4, z4 = p4
    it.command("""
    wall create id {0} name {1} vertices ...
        {2} {3} {4} ... {5} {6} {7} ... {8} {9} {10} ...
        {2} {3} {4} ... {8} {9} {10} ... {11} {12} {13}
    """.format(wall_id, name,
               x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4))


def Generate_Shear_Box():
    """Ten walls: bottom, right_bottom, dangban_right, right_top, top_wall,
    left_top, dangban_left, left_bottom, front, behind.

    The upper half box is offset from the lower half at z = zlength/2; the baffles
    (dangban) close the mid-height gap.
    """
    zmid = z0 + zlength / 2.0

    # 1 bottom (z = z0)
    _wall(1, "bottom",
          (x0 - x_extend, y0 - y_extend, z0),
          (x0 + xlength + x_extend, y0 - y_extend, z0),
          (x0 + xlength + x_extend, y0 + ylength + y_extend, z0),
          (x0 - x_extend, y0 + ylength + y_extend, z0))

    # 2 right_bottom (x = x0 + xlength, z from -z_extend to zmid)
    _wall(2, "right_bottom",
          (x0 + xlength, y0 - y_extend, z0 - z_extend),
          (x0 + xlength, y0 - y_extend, zmid),
          (x0 + xlength, y0 + ylength + y_extend, zmid),
          (x0 + xlength, y0 + ylength + y_extend, z0 - z_extend))

    # 3 dangban_right (horizontal baffle at z = zmid)
    _wall(3, "dangban_right",
          (x0 + xlength, y0 - y_extend, zmid),
          (x0 + xlength + wlength, y0 - y_extend, zmid),
          (x0 + xlength + wlength, y0 + ylength + y_extend, zmid),
          (x0 + xlength, y0 + ylength + y_extend, zmid))

    # 4 right_top (x = x0 + xlength, z from zmid to zlength + z_extend)
    _wall(4, "right_top",
          (x0 + xlength, y0 - y_extend, zmid),
          (x0 + xlength, y0 - y_extend, z0 + zlength + z_extend),
          (x0 + xlength, y0 + ylength + y_extend, z0 + zlength + z_extend),
          (x0 + xlength, y0 + ylength + y_extend, zmid))

    # 5 top_wall (z = z0 + zlength)
    _wall(5, "top_wall",
          (x0 - x_extend, y0 - y_extend, z0 + zlength),
          (x0 - x_extend, y0 + y_extend + ylength, z0 + zlength),
          (x0 + xlength + x_extend, y0 + ylength + y_extend, z0 + zlength),
          (x0 + xlength + x_extend, y0 - y_extend, z0 + zlength))

    # 6 left_top (x = x0, z from zmid to zlength + z_extend)
    _wall(6, "left_top",
          (x0, y0 - y_extend, zmid),
          (x0, y0 + ylength + y_extend, zmid),
          (x0, y0 + ylength + y_extend, z0 + zlength + z_extend),
          (x0, y0 - y_extend, z0 + zlength + z_extend))

    # 7 dangban_left (horizontal baffle at z = zmid)
    _wall(7, "dangban_left",
          (x0 - wlength, y0 - y_extend, zmid),
          (x0, y0 - y_extend, zmid),
          (x0, y0 + ylength + y_extend, zmid),
          (x0 - wlength, y0 + ylength + y_extend, zmid))

    # 8 left_bottom (x = x0, z from -z_extend to zmid)
    _wall(8, "left_bottom",
          (x0, y0 - y_extend, z0 - z_extend),
          (x0, y0 + ylength + y_extend, z0 - z_extend),
          (x0, y0 + ylength + y_extend, zmid),
          (x0, y0 - y_extend, zmid))

    # 9 front (y = y0)
    _wall(9, "front",
          (x0 - x_extend, y0, z0 - z_extend),
          (x0 - x_extend, y0, z0 + zlength + z_extend),
          (x0 + xlength + x_extend, y0, z0 + zlength + z_extend),
          (x0 + xlength + x_extend, y0, z0 - z_extend))

    # 10 behind (y = y0 + ylength)
    _wall(10, "behind",
          (x0 - x_extend, y0 + ylength, z0 - z_extend),
          (x0 - x_extend, y0 + ylength, z0 + zlength + z_extend),
          (x0 + xlength + x_extend, y0 + ylength, z0 + zlength + z_extend),
          (x0 + xlength + x_extend, y0 + ylength, z0 - z_extend))


def clump_distribute():
    """Create the domain and shear box, then place stone and cement clumps."""
    global clump_poro
    extent_x1 = x0 - x_extend * 2.0
    extent_x2 = x0 + xlength + x_extend * 2.0
    extent_y1 = y0 - y_extend * 2.0
    extent_y2 = y0 + ylength + y_extend * 2.0
    extent_z1 = z0 - z_extend * 2.0
    extent_z2 = z0 + zlength + z_extend * 2.0
    it.command("""
    new
    set random 10001
    domain extent {0} {1} {2} {3} {4} {5} condition destroy
    cmat default model linear method deform emod 1.0e9 kratio 3.0
    """.format(extent_x1, extent_x2, extent_y1, extent_y2, extent_z1, extent_z2))

    Generate_Shear_Box()

    # stone templates s1..s5 come from input_clump_moban; cement is a single-pebble sphere
    it.command("""
    call input_clump_moban
    clump template create ...
        name cement ...
        pebbles 1 ...
        {0} 0 0 0 ...
        volume {1} ...
        inertia {2} {2} {2} 0 0 0
    """.format(rhi,
               4.0 / 3.0 * np.pi * pow(rhi, 3),
               (2.0 / 5.0) * 4.0 / 3.0 * np.pi * pow(rhi, 3)))

    # five size bins of stones, 0.2 volume fraction each, random orientation
    it.command("""
    clump distribute
        diameter
        porosity {}
        numbin 5
        bin 1 template s1 azimuth 0.0 360.0 tilt 0.0 360.0 elevation 0.0 360.0 size 0.05 0.1 volumefraction 0.2 group 'stone'
        bin 2 template s2 azimuth 0.0 360.0 tilt 0.0 360.0 elevation 0.0 360.0 size 0.05 0.1 volumefraction 0.2 group 'stone'
        bin 3 template s3 azimuth 0.0 360.0 tilt 0.0 360.0 elevation 0.0 360.0 size 0.05 0.1 volumefraction 0.2 group 'stone'
        bin 4 template s4 azimuth 0.0 360.0 tilt 0.0 360.0 elevation 0.0 360.0 size 0.05 0.1 volumefraction 0.2 group 'stone'
        bin 5 template s5 azimuth 0.0 360.0 tilt 0.0 360.0 elevation 0.0 360.0 size 0.05 0.1 volumefraction 0.2 group 'stone'
        range x 0 1 y 0 1 z 0 1
    """.format(clump_poro))

    in_box()

    it.command("""
    clump attri density 2700 damp 0.3 range group 'stone'
    ; set timestep scale
    ; cycle 3000 calm 1000
    """)

    # fill the soil matrix with cement clumps
    it.command("""
    clump distribute
        diameter
        porosity 0.55
        numbin 1
        bin 1 template cement size {0} {1} volumefraction 1 group 'cement'
        box {2} {3} {4} {5} {6} {7}
    clump attri density 1500 damp 0.3 range group 'cement'
    """.format(0.03, 0.05,
               x0, x0 + xlength, y0, y0 + ylength, z0, z0 + zlength))


def trim_and_save():
    """Trim overhanging clumps, equilibrate, zero kinematics and save the initial state."""
    it.command("""
    set timestep scale
    cycle 1000 calm 100
    """)

    it.command("""
    clump delete range z 1.001 4
    clump delete range z -1 -0.001
    clump delete range x 1.002 5
    clump delete range x -1 -0.002
    clump delete range y -1 -0.002
    clump delete range y 1.002 2
    set timestep auto
    cyc 1000
    calm
    clump attribute spin multiply 0.0
    clump attribute velocity multiply 0.0
    clump attribute displacement multiply 0.0
    clump attribute contactforce multiply 0.0 contactmoment multiply 0.0
    save ini
    """)


if __name__ == "__main__":
    clump_distribute()
    print("stone / cement ratio:", compute_block_ratio())
    trim_and_save()
