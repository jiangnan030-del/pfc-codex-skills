# Source Code: Reliability and Scaling (PFC 6.0)

This file carries migrated source blocks `09` to `14`.

## Block 09 - Initial-state consistency / confining stress stop condition

```fish
fish define stop_me
    stop_me = 0
    if nsteps <= 20000
        exit
    endif
    if math.abs((wszz - tszz) / tszz) > tol
        exit
    endif
    if math.abs((wsrr_outer - tsrr_outer) / tsrr_outer) > tol
        exit
    endif
    if mech.solve("ratio-average") > 1.0e-5
        exit
    endif
    stop_me = 1
end
model solve fishhalt @stop_me
```

## Block 10 - contact vs cmat: assign properties to current contacts

```fish
model clean
contact groupbehavior contact
contact group 'contact1111' range contact type 'ball-ball'
contact model linearpbond range group 'contact1111'
contact method bond gap 0.0 range group 'contact1111'
contact method pb_deform emod [pb_modules * 1.0] krat [pb_kratio] range group 'contact1111'
contact method deform emod [emod000] krat [pb_kratio] range group 'contact1111'
contact property pb_ten [ten_] pb_coh [coh_] fric [fric_coefficient] pb_fa [fric_] pb_mcf [coeff_mcf] pb_rmul 1.0 range group 'contact1111'
contact property lin_mode 1 dp_nratio 0.3 dp_sratio 0.3 range group 'contact1111'
```

## Block 11 - Randomly weaken a subset of existing contacts

```fish
fish define part_contact_turn_off
    loop foreach local cp contact.list.all('ball-ball')
        local sss000 = contact.model(cp)
        if sss000 = 'linearpbond'
            local x = math.random.uniform
            if x < 0.4
                contact.group(cp) = 'contact2222'
            endif
        endif
    endloop
end
@part_contact_turn_off

contact model linearpbond range group 'contact2222'
contact method bond gap 0.0 range group 'contact2222'
contact method pb_deform emod [pb_modules * moduls_bili] krat [pb_kratio * kratio_bili] range group 'contact2222'
contact method deform emod [emod000] krat [pb_kratio] range group 'contact2222'
contact property pb_ten [ten_ * strength_bili] pb_coh [coh_ * strength_bili] fric [fric_coefficient * 1.0] pb_fa [fric_] pb_mcf [coeff_mcf] pb_rmul 1.0 range group 'contact2222'
contact property lin_mode 1 dp_nratio 0.3 dp_sratio 0.0 range group 'contact2222'
```

## Block 12 - Assign current contact groups and properties directly in FISH

```fish
model restore 'ini'

fish define obtain_typeid
    typeid_ball_facet = contact.typeid('ball-facet')
    typeid_ball_ball  = contact.typeid('ball-ball')
end
@obtain_typeid

fish define assign_current_contact_group
    loop foreach local cp contact.list
        local bp1 = contact.end1(cp)
        local bp2 = contact.end2(cp)
        local type_con = type.pointer.id(cp)
        if type_con = typeid_ball_ball
            local sss1 = ball.group(bp1)
            local sss2 = ball.group(bp2)
            if sss1 = 'A' & sss2 = 'A'
                local emod1 = 1e5
                local pb_emod1 = 1e5
                local kratio1 = 1.0
                local area1 = math.pi * (math.min(ball.radius(bp1), ball.radius(bp2)))^2
                contact.group(cp) = 'A-A'
                contact.model(cp) = 'linearpbond'
                contact.prop(cp,'kn') = emod1 * area1 / (ball.radius(bp1) + ball.radius(bp2))
                contact.prop(cp,'ks') = contact.prop(cp,'kn') / kratio1
                contact.prop(cp,'pb_kn') = pb_emod1 / (ball.radius(bp1) + ball.radius(bp2))
                contact.prop(cp,'pb_ks') = contact.prop(cp,'pb_kn') / kratio1
                contact.prop(cp,'dp_nratio') = 0.5
                contact.prop(cp,'dp_sratio') = 0.5
                contact.prop(cp,'pb_ten') = 4e3
                contact.prop(cp,'pb_coh') = 4e3
                contact.prop(cp,'fric') = 0.5
            endif
        endif

        if type_con = typeid_ball_facet
            local wp = contact.end2(cp)
            local wp2 = wall.facet.wall(wp)
            if wall.id(wp2) = 6
                contact.group(cp) = 'ball-facet111'
                contact.model(cp) = 'linearpbond'
                local emod7 = 1e5
                local pb_emod7 = 1e5
                local kratio7 = 1.0
                local area7 = math.pi * (ball.radius(bp1))^2
                contact.prop(cp,'kn') = emod7 * area7 / ball.radius(bp1)
                contact.prop(cp,'ks') = contact.prop(cp,'kn') / kratio7
                contact.prop(cp,'pb_kn') = pb_emod7 / ball.radius(bp1)
                contact.prop(cp,'pb_ks') = contact.prop(cp,'pb_kn') / kratio7
                contact.prop(cp,'dp_nratio') = 0.5
                contact.prop(cp,'dp_sratio') = 0.5
                contact.prop(cp,'pb_ten') = 4e5
                contact.prop(cp,'pb_coh') = 4e5
                contact.prop(cp,'fric') = 0.5
            endif
            if wall.id(wp2) # 6
                contact.group(cp) = 'ball-facet222'
                contact.model(cp) = 'linearpbond'
                local emod8 = 1e5
                local pb_emod8 = 1e5
                local kratio8 = 1.0
                local area8 = math.pi * (ball.radius(bp1))^2
                contact.prop(cp,'kn') = emod8 * area8 / ball.radius(bp1)
                contact.prop(cp,'ks') = contact.prop(cp,'kn') / kratio8
                contact.prop(cp,'pb_kn') = pb_emod8 / ball.radius(bp1)
                contact.prop(cp,'pb_ks') = contact.prop(cp,'pb_kn') / kratio8
                contact.prop(cp,'dp_nratio') = 0.5
                contact.prop(cp,'dp_sratio') = 0.5
                contact.prop(cp,'pb_ten') = 4e3
                contact.prop(cp,'pb_coh') = 4e3
                contact.prop(cp,'fric') = 0.5
            endif
        endif
    endloop
end
@assign_current_contact_group
```

## Block 13 - Assign future contacts with a callback

```fish
fish define assign_contact_group(entries)
    local cp = entries(1)
    local bp1 = contact.end1(cp)
    local bp2 = contact.end2(cp)
    local type_con = type.pointer.id(cp)

    if type_con = typeid_ball_ball
        local sss1 = ball.group(bp1)
        local sss2 = ball.group(bp2)
        if sss1 = 'A' & sss2 = 'A'
            local emod1 = 1e5
            local pb_emod1 = 1e5
            local kratio1 = 1.0
            local area1 = math.pi * (math.min(ball.radius(bp1), ball.radius(bp2)))^2
            contact.group(cp) = 'A-A'
            contact.model(cp) = 'linearpbond'
            contact.prop(cp,'kn') = emod1 * area1 / (ball.radius(bp1) + ball.radius(bp2))
            contact.prop(cp,'ks') = contact.prop(cp,'kn') / kratio1
            contact.prop(cp,'pb_kn') = pb_emod1 / (ball.radius(bp1) + ball.radius(bp2))
            contact.prop(cp,'pb_ks') = contact.prop(cp,'pb_kn') / kratio1
            contact.prop(cp,'dp_nratio') = 0.5
            contact.prop(cp,'dp_sratio') = 0.5
            contact.prop(cp,'pb_ten') = 4e3
            contact.prop(cp,'pb_coh') = 4e3
            contact.prop(cp,'fric') = 0.5
        endif
    endif

    if type_con = typeid_ball_facet
        local wp = contact.end2(cp)
        local wp2 = wall.facet.wall(wp)
        if wall.id(wp2) = 6
            contact.group(cp) = 'ball-facet111'
            contact.model(cp) = 'linearpbond'
            local emod7 = 1e5
            local pb_emod7 = 1e5
            local kratio7 = 1.0
            local area7 = math.pi * (ball.radius(bp1))^2
            contact.prop(cp,'kn') = emod7 * area7 / ball.radius(bp1)
            contact.prop(cp,'ks') = contact.prop(cp,'kn') / kratio7
            contact.prop(cp,'pb_kn') = pb_emod7 / ball.radius(bp1)
            contact.prop(cp,'pb_ks') = contact.prop(cp,'pb_kn') / kratio7
            contact.prop(cp,'dp_nratio') = 0.5
            contact.prop(cp,'dp_sratio') = 0.5
            contact.prop(cp,'pb_ten') = 4e5
            contact.prop(cp,'pb_coh') = 4e5
            contact.prop(cp,'fric') = 0.5
        endif
        if wall.id(wp2) # 6
            contact.group(cp) = 'ball-facet222'
            contact.model(cp) = 'linearpbond'
            local emod8 = 1e5
            local pb_emod8 = 1e5
            local kratio8 = 1.0
            local area8 = math.pi * (ball.radius(bp1))^2
            contact.prop(cp,'kn') = emod8 * area8 / ball.radius(bp1)
            contact.prop(cp,'ks') = contact.prop(cp,'kn') / kratio8
            contact.prop(cp,'pb_kn') = pb_emod8 / ball.radius(bp1)
            contact.prop(cp,'pb_ks') = contact.prop(cp,'pb_kn') / kratio8
            contact.prop(cp,'dp_nratio') = 0.5
            contact.prop(cp,'dp_sratio') = 0.5
            contact.prop(cp,'pb_ten') = 4e3
            contact.prop(cp,'pb_coh') = 4e3
            contact.prop(cp,'fric') = 0.5
        endif
    endif
end

fish callback add @assign_contact_group event contact_activated
```

## Block 14 - Loading-rate control

```fish
[rate = 0.05]
wall attribute zvelocity [-rate * _wH0] range id 6
wall attribute zvelocity [ rate * _wH0] range id 5

[rate = 0.05]
fish define apply_zvel_ban
    local strain_kz = 1e-3
    local xishu = math.abs(wezz) / strain_kz
    if xishu < 0.05
        xishu = 0.05
    endif
    if xishu > 1.0
        xishu = 1.0
        command
            fish callback remove @apply_zvel_ban -1.0
        endcommand
    endif
    wall.vel.z(wadd6) = -rate * _wH0 * xishu
    wall.vel.z(wadd5) =  rate * _wH0 * xishu
end
fish callback add @apply_zvel_ban -1.0
```
