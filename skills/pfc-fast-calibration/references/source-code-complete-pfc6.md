# Complete PFC 6.0 Source-Code Route

This reference migrates the source command flow into a staged PFC 6.0-oriented route. The code is intentionally split into reusable stages so `pfc-workflow`, `pfc-servo-calibration`, `pfc-standard-tests`, and `pfc-fish` can own their specialist portions.

## Stage A: Particle Generation

Purpose: create a cylindrical PFC3D specimen.

```text
model new

fish define setup
    expand_xishu = 10.0
    height = 1.0 * expand_xishu
    width = 0.5 * expand_xishu
    cylinder_axis_vec = vector(0,0,1)
    cylinder_base_vec = vector(0.0,0.0,-0.2 * height)
    cylinder_base_vec_middle = vector(0.0,0.0,0.5 * height)
    cylinder_height = 1.4 * height
    cylinder_rad = 0.5 * width
    bottom_disk_position_vec = vector(0.0,0.0,0.0)
    top_disk_position_vec = vector(0.0,0.0,height)
    disk_rad = 1.5 * cylinder_rad
    w_resolution = 0.05
    poros = 0.35
    rlo = 0.8e-2 * expand_xishu
    rhi = 1.2e-2 * expand_xishu
    dens = 3000
end
@setup

model domain extent [-width*1.05] [width*1.05] [-width*1.05] [width*1.05] [-0.3*height] [1.3*height]
model domain condition destroy
model random 10001

contact cmat default model linear method deform emod 1e8 kratio 1.5

wall generate id 1 cylinder axis @cylinder_axis_vec base @cylinder_base_vec height [cylinder_height/2.0] radius @cylinder_rad cap false false onewall resolution @w_resolution
wall generate id 2 cylinder axis @cylinder_axis_vec base @cylinder_base_vec_middle height [cylinder_height/2.0] radius @cylinder_rad cap false false onewall resolution @w_resolution
wall generate id 5 plane position @bottom_disk_position_vec dip 0 ddir 0
wall generate id 6 plane position @top_disk_position_vec dip 0 ddir 0

geometry set 'geo_cylinder'
geometry generate cylinder axis (0,0,1) base (0,0,0) height [height] cap true true radius [cylinder_rad] resolution 0.05

ball distribute porosity [poros] resolution 1.0 numbins 1 bin 1 radius [rlo] [rhi] volumefraction 1.0 group 'soil' range geometry 'geo_cylinder' count odd direction (0,0,1)
ball attribute density [dens] damp 0.3
model cycle 5000 calm 100
ball delete range geometry 'geo_cylinder' count odd not
model solve ratio-average 1e-3 calm 5000
model calm
ball attribute spin multiply 0.0 velocity multiply 0.0 displacement multiply 0.0
ball attribute contactforce multiply 0.0 contactmoment multiply 0.0
model save 'ini'
```

## Stage B: Servo Consolidation

Purpose: consolidate the cylindrical specimen before bonding. Route detailed servo implementation to `pfc-servo-calibration`.

Essential logic:

```text
model restore 'ini'
contact cmat default model linear method deform emod 5e9 kratio 1.4
contact cmat default type ball-facet model linear method deform emod 1e9 kratio 1.4
contact cmat default type ball-ball model linear method deform emod 5e9 kratio 1.4
contact cmat apply
model cycle 1000 calm 100
```

Core FISH blocks from the source:

```text
wall_addr: find radial and axial walls
_mvsUpdateDim: update current radial dimension
_mvsRadForce: compute radial contact force from cylinder walls
_mvsSetRadVel: impose radial wall-vertex velocity
compute_wAreas: compute axial and radial wall areas
compute_wStress: compute axial and radial stresses
compute_gain: compute stiffness-based servo gains
servo_walls: apply axial and radial stress-control velocities
stop_me: stop when stress error and mechanical ratio are acceptable
```

Recommended staged save:

```text
history delete
history id 1 @wszz
history id 2 @wsrr_outer
model solve fish-halt @stop_me
model save 'consolidation_state'
```

## Stage C: Improved LPBM Parameter Assignment

Use bundled script `scripts/canonical/improved_lpbm_assign.p3fis` for a clean template.

Source-style parameter block:

```text
model restore 'consolidation_state'
[pb_modules = 70.0e9]
[emod000 = 0.2 * pb_modules]
[pb_kratio = 1.5]
[ten_ = 11.0e7]
[coh_ = ten_ * 2]
[fric_coefficient = 0.7]
[fric_ = 38]
[coeff_mcf = 0.3]
[crack_bili = 0.65]
[beta000 = 200]
[strength_bili = 0.1]
[moduls_bili = 0.1]
[kratio_bili = 2]
```

Strong contact assignment:

```text
contact group 'contact1111' range contact type 'ball-ball'
contact model linearpbond range group 'contact1111'
contact method bond gap 0 range group 'contact1111'
contact method pb_deformability emod [pb_modules] krat [pb_kratio] deform emod [emod000] kratio [pb_kratio] range group 'contact1111'
contact property pb_ten [ten_] pb_coh [coh_] fric [fric_coefficient] pb_fa [fric_] pb_mcf [coeff_mcf] pb_rmul 1.0 range group 'contact1111'
```

Weak-contact grouping:

```fish
fish define part_contact_turn_off
    loop foreach local cp contact.list('ball-ball')
        if contact.model(cp) = 'linearpbond' then
            local z0 = contact.pos.z(cp)
            if z0 < 0.99 * height then
                if z0 > 0.01 * height then
                    if math.random.uniform < crack_bili then
                        contact.group(cp) = 'contact2222'
                    endif
                endif
            endif
        endif
    endloop
end
@part_contact_turn_off
```

Weak contact assignment:

```text
contact model linearpbond range group 'contact2222'
contact method bond gap 0 range group 'contact2222'
contact method pb_deformability emod [pb_modules * moduls_bili] krat [pb_kratio * kratio_bili] deform emod [emod000] kratio [pb_kratio] range group 'contact2222'
contact property pb_ten [ten_ * strength_bili] pb_coh [coh_ * strength_bili] fric [fric_coefficient] pb_fa [fric_] pb_mcf [coeff_mcf] pb_rmul 1.0 range group 'contact2222'
```

Weibull random damage:

```fish
fish define weibull_random(alfa, beta)
    local freq = math.random.uniform
    weibull_random = alfa * (-math.ln(1.0 - freq))^(1.0 / beta)
end

fish define weibull_parameter
    loop foreach local cp contact.list
        if type.pointer(cp) = 'ball-ball' then
            if contact.model(cp) = 'linearpbond' then
                local xishu = weibull_random(1.0, beta000)
                contact.prop(cp,'pb_ten') = contact.prop(cp,'pb_ten') * xishu
                contact.prop(cp,'pb_coh') = contact.prop(cp,'pb_coh') * xishu
                contact.prop(cp,'pb_kn') = contact.prop(cp,'pb_kn') * xishu
                contact.prop(cp,'pb_ks') = contact.prop(cp,'pb_ks') * xishu
            endif
        endif
    endloop
end
@weibull_parameter
model cycle 1000 calm 100
model save 'consolidation_state222'
```

## Stage D: Triaxial / UCS Compression

Route loading-template selection to `pfc-standard-tests` and servo details to `pfc-servo-calibration`.

Key metric definitions:

```fish
fish define wezz
    wezz = (_wdz - _wH0) / _wH0
end

fish define wexx
    wexx = (_wdr - _wdr0) / _wdr0
end

fish define wvol
    wvol = wezz + 2.0 * wexx
end

fish define possion
    possion0 = -wexx / wezz
    possion = possion0
end
```

Elastic modulus extraction:

```fish
fish define compute_elastic_modulus
    axial_strain_wall = math.abs(wezz)
    if axial_strain_wall > 0.3e-3 then
        ; store first strain/stress point
    endif
    if axial_strain_wall > 1.0e-3 then
        ; compute secant modulus and remove callback
    endif
end
```

Run and export:

```text
measure create id 1 position (0,0,[height/2.0]) radius [width * 0.5 * 0.8]
history id 1 @wezz
history id 2 @wszz
history id 3 @wsrr_outer
history id 4 @wexx
history id 5 @wvol
history id 6 @possion
history id 7 measure stress-zz id 1
wall attribute zvelocity [-rate * _wH0] range id 6
wall attribute zvelocity [rate * _wH0] range id 5
model solve fish-halt @loadhalt_wall
history export 4 5 3 2 7 vs 1 file 'compress_3d.dat'
model save 'tri-compress2'
```

## Stage E: Uniaxial Tension

The source tension route deletes walls, finds top/bottom gauge balls, fixes grip groups, and pulls them apart.

Core route:

```text
model restore 'consolidation_state222'
; remove servo callbacks
wall delete
model cycle 10000 calm 100
```

Gauge and grip setup:

```fish
fish define setup_gage
    global vertical_direction = global.dim
    local bottom_ = 1.0e12
    local top_ = -1.0e12
    loop foreach local bp ball.list
        top_ = math.max(ball.pos(bp,vertical_direction), top_)
        bottom_ = math.min(ball.pos(bp,vertical_direction), bottom_)
    endloop
    global gage_top = ball.near(vector(0,0,top_))
    global gage_bottom = ball.near(vector(0,0,bottom_))
    sample_height = ball.pos(gage_top,vertical_direction) - ball.pos(gage_bottom,vertical_direction)
end
@setup_gage
```

Tension loading:

```text
[rate = 0.0005]
ball group 'top_grip' range z [0.9 * height] [1.1 * height]
ball group 'bottom_grip' range z [-0.1 * height] [0.1 * height]
ball fix z range group 'top_grip'
ball attribute zvel [rate * sample_height] range group 'top_grip'
ball fix z range group 'bottom_grip'
ball attribute zvel [-rate * sample_height] range group 'bottom_grip'
```

Export:

```text
measure create id 1 position (0,0,[height/2.0]) radius [width * 0.5 * 0.8]
history id 1 @axial_strain_gage
history id 3 measure stress-zz id 1
model solve fish-halt @loadhalt_meas
history export 3 vs 1 file 'tension000.dat'
model save 'tension'
```

## Stage F: Batch Orthogonal Campaign

Use `program call` to run modular files:

```text
program call 'generate_or_restore_specimen.dat'
program call 'servo_consolidation.dat'
program call 'improved_lpbm_assign.p3fis'
program call 'run_ucs_or_triaxial.dat'
program call 'run_uts.dat'
```

Each run folder should save:

```text
params.json
compress_3d.dat
tension000.dat
triaxial_summary.csv
metrics.json
```

## Version Caution

This route preserves the source logic but normalizes names toward PFC 6.0 style. Verify exact command names such as `history export`, `fish callback`, `contact.prop`, and model property names against the installed PFC version before production solves.
