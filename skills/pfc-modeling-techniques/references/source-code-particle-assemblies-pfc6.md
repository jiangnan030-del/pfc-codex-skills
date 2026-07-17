# Source Code: Particle Assemblies (PFC 6.0)

This file carries migrated source blocks `05` to `08`.

## Block 05 - Particle construction examples

```fish
ball distribute porosity 0.3 radius @radmin @radmax box [-xx] [xx] [-yy] [yy] [-zz] [zz]

geometry import 'moban1.stl' format stl
clump template create ...
    name 'moban1' ...
    geometry 'moban1' ...
    bubblepack ...
        distance 120.0 ...
        ratio 0.1 ...
        radfactor 1.05 ...
        surfcalculate
clump distribute diameter ...
    porosity 0.40
    number-bins 5
    bin 1
        template 'moban1'
        azimuth 0.0 360.0
        tilt 0.0 360.0
        elevation 0.0 360.0
        size [radmin] [radmax]
        volume-fraction 0.2
        group 's1'
    bin 2
        template 'moban2'
        azimuth 0.0 360.0
        tilt 0.0 360.0
        elevation 0.0 360.0
        size [radmin * 0.8] [radmax * 0.8]
        volume-fraction 0.2
        group 's2'
    bin 3
        template 'moban3'
        azimuth 0.0 360.0
        tilt 0.0 360.0
        elevation 0.0 360.0
        size [radmin * 0.7] [radmax * 0.7]
        volume-fraction 0.2
        group 's3'
    bin 4
        template 'moban4'
        azimuth 0.0 360.0
        tilt 0.0 360.0
        elevation 0.0 360.0
        size [radmin * 0.6] [radmax * 0.6]
        volume-fraction 0.2
        group 's4'
    bin 5
        template 'moban5'
        azimuth 0.0 360.0
        tilt 0.0 360.0
        elevation 0.0 360.0
        size [radmin * 0.5] [radmax * 0.5]
        volume-fraction 0.2
        group 's5'
    resolution 1.0 box [-xx] [xx] [-yy] [yy] [-zz] [zz]
clump attribute damp 0.3 density 3000
model mechanical timestep scale
model cycle 5000 calm 100
model mechanical timestep automatic
model solve ratio-average 1e-5 calm 100

geometry import 'moban1.stl' format stl
rblock template create from-geometry 'moban1'
geometry import 'moban2.stl'
rblock template create from-geometry 'moban2'
geometry import 'moban3.stl'
rblock template create from-geometry 'moban3'
geometry import 'moban4.stl'
rblock template create from-geometry 'moban4'
geometry import 'moban5.stl'
rblock template create from-geometry 'moban5'
rblock distribute ...
```

## Block 06 - Geometry-driven irregular particles -> regroup to balls and contacts

```fish
model new
fish define parameter_setup
    xx = 0.5
    yy = 0.5
    zz = 1.0
    radmin = 0.02
    radmax = 0.04
    emod0 = 1.0e7
    kratio0 = 2.0
end
@parameter_setup

model domain extent [-xx * 1.5] [xx * 1.5] [-yy * 1.5] [yy * 1.5] [-zz * 1.5] [zz * 1.5]
model domain condition destroy
model random 10001
contact cmat default model linear property kn 1e8 fric 0.3
wall generate box [-xx] [xx] [-yy] [yy] [-zz] [zz]
geometry import 'moban1.stl' format stl
rblock template create from-geometry 'moban1'
rblock distribute ...
    diameter
    porosity 0.50
    number-bins 1
    bin 1
        template 'moban1'
        azimuth 0.0 360.0
        tilt 0.0 360.0
        elevation 0.0 360.0
        size [0.1] [0.3]
        volume-fraction 1.0
        group 's1'
    resolution 1.0 box [-xx] [xx] [-yy] [yy] [-zz] [zz]
rblock attribute damp 0.3 density 3000
model mechanical timestep scale
model cycle 5000 calm 1000
model mechanical timestep automatic
model cycle 5000
geometry delete
[nnn = 0]

fish define creatgroup
    loop foreach local rp rblock.list
        nnn = nnn + 1
        local name = 'rblock' + string(nnn)
        rblock.group(rp) = name
        command
            rblock export to-geometry @name split slot 'Default' range group [name]
        endcommand
    endloop
end
@creatgroup

rblock delete
ball distribute porosity 0.3 radius @radmin @radmax box [-xx] [xx] [-yy] [yy] [-zz] [zz]
ball attribute damp 0.3 density 3000
model mechanical timestep scale
model cycle 5000 calm 100
model mechanical timestep automatic
model solve ratio-average 1e-5

fish define assign_material
    loop foreach local gs geom.set.list
        local name111 = geom.set.name(gs)
        command
            ball group @name111 range geometry-space @name111 count odd
            contact group @name111 range geometry-space @name111 count odd
        endcommand
    endloop
end
@assign_material

fish define contact_between_particles
    loop foreach local cp contact.list('ball-ball')
        local bp1 = contact.end1(cp)
        local bp2 = contact.end2(cp)
        local ss11 = ball.group(bp1)
        local ss22 = ball.group(bp2)
        if ss11 # ss22
            contact.group(cp) = 'boundary'
        endif
    endloop
end
@contact_between_particles
```

## Block 07 - Zone to rblock conversion

```fish
fish define area_3d(x1,y1,z1,x2,y2,z2,x3,y3,z3)
    local vx1 = x2 - x1
    local vy1 = y2 - y1
    local vz1 = z2 - z1
    local vx2 = x3 - x1
    local vy2 = y3 - y1
    local vz2 = z3 - z1
    local vx = vy1 * vz2 - vz1 * vy2
    local vy = vz1 * vx2 - vx1 * vz2
    local vz = vx1 * vy2 - vy1 * vx2
    local s = 0.5 * math.sqrt(vx * vx + vy * vy + vz * vz)
    area_3d = math.abs(s)
end

fish define zone_to_rblock
    local p_z = zone.head
    tetranum = 0
    bricknum = 0
    wedgenum = 0
    pyramidnum = 0
    num_total = 0
    loop while p_z # null
        local z1_code = zone.code(p_z)
        local z2_code = zone.group(p_z)
        local sss = zone.model(p_z)
        local nflag = 0
        if z2_code = '2'
            if sss = 'null'
                nflag = 1
            endif
        endif
        if nflag = 1
            if z1_code = 4
                tetranum = tetranum + 1
                n1 = zone.gp(p_z,1)
                n2 = zone.gp(p_z,2)
                n3 = zone.gp(p_z,3)
                n4 = zone.gp(p_z,3)
                n5 = zone.gp(p_z,4)
                n6 = zone.gp(p_z,4)
                n7 = zone.gp(p_z,4)
                n8 = zone.gp(p_z,4)
                num_total = num_total + 1
            else
                if z1_code = 0
                    bricknum = bricknum + 1
                    n1 = zone.gp(p_z,1)
                    n2 = zone.gp(p_z,2)
                    n3 = zone.gp(p_z,5)
                    n4 = zone.gp(p_z,3)
                    n5 = zone.gp(p_z,4)
                    n6 = zone.gp(p_z,7)
                    n7 = zone.gp(p_z,8)
                    n8 = zone.gp(p_z,6)
                    num_total = num_total + 1
                else
                    if z1_code = 1
                        wedgenum = wedgenum + 1
                        n1 = zone.gp(p_z,1)
                        n2 = zone.gp(p_z,4)
                        n3 = zone.gp(p_z,2)
                        n4 = zone.gp(p_z,2)
                        n5 = zone.gp(p_z,3)
                        n6 = zone.gp(p_z,6)
                        n7 = zone.gp(p_z,5)
                        n8 = zone.gp(p_z,5)
                        num_total = num_total + 1
                    else
                        if z1_code = 2
                            pyramidnum = pyramidnum + 1
                            n1 = zone.gp(p_z,1)
                            n2 = zone.gp(p_z,2)
                            n3 = zone.gp(p_z,5)
                            n4 = zone.gp(p_z,3)
                            n5 = zone.gp(p_z,4)
                            n6 = zone.gp(p_z,4)
                            n7 = zone.gp(p_z,4)
                            n8 = zone.gp(p_z,4)
                            num_total = num_total + 1
                        endif
                    endif
                endif
            endif

            local gname = 'deposit' + string(num_total)
            geom.set.create(gname)
            x1 = gp.pos.x(n1)
            y1 = gp.pos.y(n1)
            z1 = gp.pos.z(n1)
            x2 = gp.pos.x(n2)
            y2 = gp.pos.y(n2)
            z2 = gp.pos.z(n2)
            x3 = gp.pos.x(n3)
            y3 = gp.pos.y(n3)
            z3 = gp.pos.z(n3)
            x4 = gp.pos.x(n4)
            y4 = gp.pos.y(n4)
            z4 = gp.pos.z(n4)
            x5 = gp.pos.x(n5)
            y5 = gp.pos.y(n5)
            z5 = gp.pos.z(n5)
            x6 = gp.pos.x(n6)
            y6 = gp.pos.y(n6)
            z6 = gp.pos.z(n6)
            x7 = gp.pos.x(n7)
            y7 = gp.pos.y(n7)
            z7 = gp.pos.z(n7)
            x8 = gp.pos.x(n8)
            y8 = gp.pos.y(n8)
            z8 = gp.pos.z(n8)

            s1 = area_3d(x1,y1,z1,x2,y2,z2,x3,y3,z3)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x1],[y1],[z1]) ([x2],[y2],[z2]) ([x3],[y3],[z3])
                endcommand
            endif
            s1 = area_3d(x1,y1,z1,x3,y3,z3,x4,y4,z4)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x1],[y1],[z1]) ([x3],[y3],[z3]) ([x4],[y4],[z4])
                endcommand
            endif
            s1 = area_3d(x1,y1,z1,x5,y5,z5,x6,y6,z6)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x1],[y1],[z1]) ([x5],[y5],[z5]) ([x6],[y6],[z6])
                endcommand
            endif
            s1 = area_3d(x1,y1,z1,x6,y6,z6,x2,y2,z2)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x1],[y1],[z1]) ([x6],[y6],[z6]) ([x2],[y2],[z2])
                endcommand
            endif
            s1 = area_3d(x2,y2,z2,x6,y6,z6,x7,y7,z7)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x2],[y2],[z2]) ([x6],[y6],[z6]) ([x7],[y7],[z7])
                endcommand
            endif
            s1 = area_3d(x2,y2,z2,x7,y7,z7,x3,y3,z3)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x2],[y2],[z2]) ([x7],[y7],[z7]) ([x3],[y3],[z3])
                endcommand
            endif
            s1 = area_3d(x5,y5,z5,x8,y8,z8,x7,y7,z7)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x5],[y5],[z5]) ([x8],[y8],[z8]) ([x7],[y7],[z7])
                endcommand
            endif
            s1 = area_3d(x5,y5,z5,x7,y7,z7,x6,y6,z6)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x5],[y5],[z5]) ([x7],[y7],[z7]) ([x6],[y6],[z6])
                endcommand
            endif
            s1 = area_3d(x1,y1,z1,x4,y4,z4,x8,y8,z8)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x1],[y1],[z1]) ([x4],[y4],[z4]) ([x8],[y8],[z8])
                endcommand
            endif
            s1 = area_3d(x1,y1,z1,x8,y8,z8,x5,y5,z5)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x1],[y1],[z1]) ([x8],[y8],[z8]) ([x5],[y5],[z5])
                endcommand
            endif
            s1 = area_3d(x4,y4,z4,x3,y3,z3,x7,y7,z7)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x4],[y4],[z4]) ([x3],[y3],[z3]) ([x7],[y7],[z7])
                endcommand
            endif
            s1 = area_3d(x4,y4,z4,x8,y8,z8,x7,y7,z7)
            if s1 > 1e-5
                command
                    geometry polygon create by-positions ([x4],[y4],[z4]) ([x8],[y8],[z8]) ([x7],[y7],[z7])
                endcommand
            endif
            command
                rblock create from-geometry [gname] id [num_total] rounding relative 0.0001 group [z2_code]
                geometry delete
            endcommand
        endif
        p_z = zone.next(p_z)
    endloop
end
@zone_to_rblock
```

## Block 08 - Voronoi/polycrystal style regrouping from large seeds

```fish
model new
fish define parameter_setup
    xx = 1.0
    yy = 1.0
    zz = 2.0
    radmin = 0.02
    radmax = 0.03
    emod0 = 1.0e8
    kratio0 = 2.0
end
@parameter_setup

model domain extent [-xx * 1.5] [xx * 1.5] [-yy * 1.5] [yy * 1.5] [-zz * 1.5] [zz * 1.5]
model domain condition destroy
model random 10001
contact cmat default model linear method deform emod @emod0 kratio @kratio0 property fric 0.3

ball distribute porosity 0.4 radius 0.1 0.3 box [-xx] [xx] [-yy] [yy] [-zz] [zz]
ball attribute damp 0.3 density 3000
model mechanical timestep scale
model cycle 5000 calm 500
model mechanical timestep automatic
model cycle 10000
rblock construct from-balls polydisperse true
[nnn = 0]

fish define creatgroup
    loop foreach local rp rblock.list
        nnn = nnn + 1
        local name = 'rblock' + string(nnn)
        rblock.group(rp) = name
        command
            rblock export to-geometry @name split slot 'Default' range group [name]
        endcommand
    endloop
end
@creatgroup

ball delete
rblock delete

ball distribute porosity 0.35 radius @radmin @radmax box [-xx] [xx] [-yy] [yy] [-zz] [zz]
ball attribute damp 0.3 density 3000
model mechanical timestep scale
model cycle 5000 calm 100
model mechanical timestep automatic
model solve ratio-average 1e-5 calm 100

fish define geometry_expand(xishu)
    loop foreach local gs geom.set.list
        loop foreach local n geom.node.list(gs)
            geom.node.pos(n,1) = geom.node.pos(n,1) * xishu
            geom.node.pos(n,2) = geom.node.pos(n,2) * xishu
            geom.node.pos(n,3) = geom.node.pos(n,3) * xishu
        endloop
    endloop
end
[geometry_expand(1.1)]

fish define assign_material
    loop foreach local gs geom.set.list
        local name111 = geom.set.name(gs)
        command
            ball group @name111 range geometry-space @name111 count odd
            contact group @name111 range geometry-space @name111 count odd
        endcommand
    endloop
end
@assign_material

fish define contact_between_particles
    loop foreach local cp contact.list('ball-ball')
        local bp1 = contact.end1(cp)
        local bp2 = contact.end2(cp)
        local ss11 = ball.group(bp1)
        local ss22 = ball.group(bp2)
        if ss11 # ss22
            contact.group(cp) = 'boundary'
        endif
    endloop
end
@contact_between_particles
```
