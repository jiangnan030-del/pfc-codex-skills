# Source Code: FISH Parameter Extraction (PFC 6.0)

This file carries migrated source blocks `15` to `23`.

## Block 15 - Elastic modulus extraction

```fish
[nnnflag111 = 0]
[nnnflag222 = 0]

fish define compute_elastic_modulus
    local axial_strain_wall = math.abs(wezz)
    if axial_strain_wall > 1e-4
        if nnnflag111 = 0
            strain1 = axial_strain_wall
            stress1 = math.abs(wszz2)
            nnnflag111 = 1
        endif
    endif
    if axial_strain_wall > 2e-3
        if nnnflag222 = 0
            strain2 = axial_strain_wall
            stress2 = math.abs(wszz2)
            nnnflag222 = 1
            compute_elastic_modulus = (stress2 - stress1) / (strain2 - strain1)
            command
                fish callback remove @compute_elastic_modulus 9.0
            endcommand
        endif
    endif
end
fish callback add @compute_elastic_modulus 9.0
```

## Block 16 - Deformation modulus / peak secant modulus

```fish
[peak_str = 0.0]

fish define bulk_moduls
    local abs_stress = math.abs(wszz2)
    if abs_stress > peak_str
        peak_str = abs_stress
        peak_strain = math.abs(wezz)
        bulk_moduls = peak_str / peak_strain
    endif
end
fish callback add @bulk_moduls 9.01
```

## Block 17 - Poisson ratio from wall strain

```fish
fish define wezz
    wezz = (_wdz - _wH0) / _wH0
end

fish define wexx
    wexx = (_wdr - _wdr0) / _wdr0
end

[nnnflag333 = 0]
[nnnflag444 = 0]

fish define possion_pingjun
    local axial_strain_wall = math.abs(wezz)
    possion0 = -wexx / wezz
    if axial_strain_wall > 1e-3
        if nnnflag333 = 0
            possion1 = possion0
            nnnflag333 = 1
        endif
    endif
    if axial_strain_wall > 2e-3
        if nnnflag444 = 0
            possion2 = possion0
            nnnflag444 = 1
            possion_pingjun = (possion1 + possion2) / 2.0
        endif
    endif
end
fish callback add @possion_pingjun 9.01
```

## Block 18 - Poisson ratio from lateral gauges

```fish
fish define compute_lateral_strain
    local xmin = 100000.0
    local xmax = -100000.0
    local ymin = 100000.0
    local ymax = -100000.0
    loop foreach local bp ball.list
        local xc = ball.pos.x(bp)
        local yc = ball.pos.y(bp)
        if xc > xmax
            xmax = xc
        endif
        if xc < xmin
            xmin = xc
        endif
        if yc < ymin
            ymin = yc
        endif
        if yc > ymax
            ymax = yc
        endif
    endloop
    local vect_111 = vector(xmin, 0.0, height / 2.0)
    local vect_222 = vector(xmax, 0.0, height / 2.0)
    local vect_333 = vector(0.0, ymin, height / 2.0)
    local vect_444 = vector(0.0, ymax, height / 2.0)
    gage_111 = ball.near(vect_111)
    gage_222 = ball.near(vect_222)
    gage_333 = ball.near(vect_333)
    gage_444 = ball.near(vect_444)
    width111 = ball.pos(gage_222,1) - ball.pos(gage_111,1)
    width222 = ball.pos(gage_444,2) - ball.pos(gage_333,2)
    lateral_strain000 = (width111 + width222) / 2.0
end
@compute_lateral_strain

fish define lateral_strain
    width111 = ball.pos(gage_222,1) - ball.pos(gage_111,1)
    width222 = ball.pos(gage_444,2) - ball.pos(gage_333,2)
    lateral_strain = ((width111 + width222) / 2.0 - lateral_strain000) / lateral_strain000
end

fish define possion2222
    possion2222 = -lateral_strain / wezz
end

fish history name 'nu_from_lateral_gages' @possion2222
```

## Block 19 - Strain rate integration from a measure object

```fish
measure create id 1 position 0.0 0.0 [height / 2.0] radius [width * 0.5 * 0.8]

fish define ini_msrate(id)
    global mstrains = matrix(3,3)
    global mp = measure.find(id)
end
@ini_msrate(1)

fish define accumulate_strain
    local msrate = measure.strainrate.full(mp)
    mstrains = mstrains + msrate * global.timestep
    wexx_measure = mstrains(1,1)
    weyy_measure = mstrains(2,2)
    wezz_measure = mstrains(3,3)
    if math.abs(wezz_measure) < 1e-6
        wezz_measure = math.sgn(wezz_measure) * 1e-6
    endif
    possion_meas = wexx_measure / wezz_measure
end
fish callback add @accumulate_strain 9.2
```

## Block 20 - Peak stress and peak strain

```fish
[peak_str = 1.0]

fish define peak_stress_wall
    local abs_stress = math.abs(wszz)
    local dd = math.sqrt((abs_stress - peak_str)^2) / peak_str
    peak_str = math.max(abs_stress, peak_str)
    if dd > 0.001
        peak_strain_wall = math.abs(wezz)
    endif
end
fish callback add @peak_stress_wall 9.01
```

## Block 21 - Crack initiation stress sigma_ci

```fish
fish define sigma_ci
    local strain_v = -wvol
    peak_strain_v = math.max(strain_v, peak_strain_v)
    if peak_strain_v >= strain_v
        sigma_ci000 = -wszz2
    endif
    if strain_v > 0.0
        if strain_v < 0.999 * peak_strain_v
            sigma_ci = sigma_ci000
            command
                fish callback remove @sigma_ci 9.01
            endcommand
        endif
    endif
end
fish callback add @sigma_ci 9.01
```

## Block 22 - add_crack / DFN crack tracking

```fish
fish define add_crack(entries)
    local cp = entries(1)
    local mode = entries(2)
    local frac_pos = contact.pos(cp)
    local norm = contact.normal(cp)
    local dfn_label = 'crack'
    local frac_size
    local bp1 = contact.end1(cp)
    local bp2 = contact.end2(cp)
    local type1 = type.pointer.id(cp)

    if type1 = typeid_contact_ball_ball
        ret = math.min(ball.radius(bp1), ball.radius(bp2))
    endif
    if type1 = typeid_contact_ball_pebble
        ret = math.min(ball.radius(bp1), clump.pebble.radius(bp2))
    endif
    if type1 = typeid_contact_pebble_pebble
        ret = math.min(clump.pebble.radius(bp1), clump.pebble.radius(bp2))
    endif
    frac_size = ret

    local arg = array.create(5)
    arg(1) = 'disk'
    arg(2) = frac_pos
    arg(3) = frac_size
    arg(4) = math.dip.from.normal(norm) / math.degrad
    arg(5) = math.ddir.from.normal(norm) / math.degrad
    if arg(5) < 0.0
        arg(5) = 360.0 + arg(5)
    endif

    crack_num = crack_num + 1
    if mode = 1
        dfn_label = dfn_label + '_tension'
    else if mode = 2
        dfn_label = dfn_label + '_shear'
    endif

    global dfn = dfn.find(dfn_label)
    if dfn = null
        dfn = dfn.create(dfn_label)
    endif
    local fnew = fracture.create(dfn, arg)
    fracture.prop(fnew,'age') = mech.time.total
    fracture.extra(fnew,1) = bp1
    fracture.extra(fnew,2) = bp2

    crack_accum += 1
    if crack_accum > 50
        if frag_time < mech.time.total
            frag_time = mech.time.total
            crack_accum = 0
            command
                fragment compute
            endcommand

            loop local i (0, 1)
                local name = 'crack_tension'
                if i = 1
                    name = 'crack_shear'
                endif
                dfn = dfn.find(name)
                if dfn # null
                    loop foreach local frac dfn.fracturelist(dfn)
                        local ball1 = fracture.extra(frac,1)
                        local ball2 = fracture.extra(frac,2)
                        if ball1 # null
                            if ball2 # null
                                local len = fracture.diameter(frac) / 2.0
                                local pos
                                if type1 = typeid_contact_pebble_pebble
                                    pos = (clump.pebble.pos(ball1) + clump.pebble.pos(ball2)) / 2.0
                                endif
                                if type1 = typeid_contact_ball_ball
                                    pos = (ball.pos(ball1) + ball.pos(ball2)) / 2.0
                                endif
                                if type1 = typeid_contact_ball_pebble
                                    pos = (ball.pos(ball1) + clump.pebble.pos(ball2)) / 2.0
                                endif
                                if comp.x(pos) - len > xmin
                                    if comp.x(pos) + len < xmax
                                        if comp.y(pos) - len > ymin
                                            if comp.y(pos) + len < ymax
                                                if comp.z(pos) - len > zmin
                                                    if comp.z(pos) + len < zmax
                                                        fracture.pos(frac) = pos
                                                    endif
                                                endif
                                            endif
                                        endif
                                    endif
                                endif
                            endif
                        endif
                    endloop
                endif
            endloop
        endif
    endif
end

fish define obtain_typeid
    typeid_ball = ball.typeid
    typeid_clump = clump.typeid
    typeid_clump_pebble = clump.pebble.typeid
    typeid_wall = wall.typeid
    typeid_wall_facet = wall.facet.typeid
    typeid_contact_ball_ball = contact.typeid('ball-ball')
    typeid_contact_ball_facet = contact.typeid('ball-facet')
    typeid_contact_ball_pebble = contact.typeid('ball-pebble')
    typeid_contact_pebble_facet = contact.typeid('pebble-facet')
    typeid_contact_pebble_pebble = contact.typeid('pebble-pebble')
end
@obtain_typeid

fish define track_init
    command
        fracture delete
        ball result clear
        clump result clear
        fragment clear
        fragment register ball-ball
        ; fragment register ball-pebble
        fragment register pebble-pebble
    endcommand
    command
        fish callback remove @add_crack
        fish callback add @add_crack event bond_break
    endcommand
    global crack_accum = 0
    global crack_num = 0
    global track_time0 = mech.time.total
    global frag_time = mech.time.total
    global xmin = domain.min.x()
    global ymin = domain.min.y()
    global zmin = domain.min.z()
    global xmax = domain.max.x()
    global ymax = domain.max.y()
    global zmax = domain.max.z()
end
@track_init
```

## Block 23 - Particle-average stress in 3D

```fish
[typeid_contact_ball_ball = contact.typeid('ball-ball')]
[typeid_contact_ball_facet = contact.typeid('ball-facet')]

fish define compute_particle_average_stress_3D
    loop foreach local bp ball.list
        local ssxx = 0.0
        local ssyy = 0.0
        local sszz = 0.0
        local ssxy = 0.0
        local ssyx = 0.0
        local ssxz = 0.0
        local sszx = 0.0
        local ssyz = 0.0
        local sszy = 0.0
        loop foreach local cp ball.contactmap(bp)
            local cf = contact.force.global(cp)
            local type1 = type.pointer.id(cp)
            local cl
            if type1 = typeid_contact_ball_ball
                cl = ball.pos(contact.end2(cp)) - ball.pos(contact.end1(cp))
            endif
            if type1 = typeid_contact_ball_facet
                cl = contact.pos(cp) - ball.pos(contact.end1(cp))
            endif
            ssxx = ssxx + comp.x(cf) * comp.x(cl)
            ssyy = ssyy + comp.y(cf) * comp.y(cl)
            sszz = sszz + comp.z(cf) * comp.z(cl)
            ssxy = ssxy + comp.x(cf) * comp.y(cl)
            ssyx = ssyx + comp.y(cf) * comp.x(cl)
            ssxz = ssxz + comp.x(cf) * comp.z(cl)
            sszx = sszx + comp.z(cf) * comp.x(cl)
            ssyz = ssyz + comp.y(cf) * comp.z(cl)
            sszy = sszy + comp.z(cf) * comp.y(cl)
        endloop
        local vol = 4.0 / 3.0 * math.pi * ball.radius(bp)^3
        ssxx = -ssxx / vol
        ssyy = -ssyy / vol
        sszz = -sszz / vol
        ssxy = -ssxy / vol
        ssyx = -ssyx / vol
        ssxz = -ssxz / vol
        sszx = -sszx / vol
        ssyz = -ssyz / vol
        sszy = -sszy / vol
        ball.extra(bp,21) = ssxx
        ball.extra(bp,22) = ssyy
        ball.extra(bp,23) = sszz
        ball.extra(bp,24) = ssxy
        ball.extra(bp,25) = ssyx
        ball.extra(bp,26) = ssxz
        ball.extra(bp,27) = sszx
        ball.extra(bp,28) = ssyz
        ball.extra(bp,29) = sszy
    endloop
end

fish callback add @compute_particle_average_stress_3D 5.0

plot create 'extras'
plot item create ball
plot item modify 1 color-by extra 23
```
