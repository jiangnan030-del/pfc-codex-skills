# Complete PFC 6.0 Source-Code Route

This reference preserves the full mineral heterogeneity command-flow logic as a staged, PFC 6.0-oriented template. It is intentionally written as an auditable route rather than a hidden monolithic script.

Use this when the user asks for:

- complete code
- original command-flow migration
- all A-G mineral heterogeneity stages
- a full PFC 6.0 implementation skeleton

## Stage A: Restore, Reset, Seed, And Measure Total Area

```text
model restore 'biaxial-isoloose'
ball attribute velocity multiply 0.0
ball attribute displacement multiply 0.0
ball attribute contactforce multiply 0.0 contactmoment multiply 0.0
model random 10001
ball group 'mineral_feldspar'
```

```fish
[area_total = 0.0]
[area_feldspar = 0.0]
[area_quartz = 0.0]
[area_mica = 0.0]

define mineral_ball_area(bp)
    mineral_ball_area = math.pi * ball.radius(bp) * ball.radius(bp)
end

define mineral_area_total
    area_total = 0.0
    loop foreach local bp ball.list
        area_total = area_total + mineral_ball_area(bp)
    endloop
end
@mineral_area_total
```

## Stage B: Cellular-Automata Mineral Cluster Construction

```fish
[target_feldspar = 0.5932]
[target_quartz = 0.3586]
[target_mica = 0.0481]

define mineral_assign_matrix
    area_feldspar = 0.0
    area_quartz = 0.0
    area_mica = 0.0
    loop foreach local bp ball.list
        ball.group(bp) = 'mineral_feldspar'
        area_feldspar = area_feldspar + mineral_ball_area(bp)
    endloop
end

define mineral_seed_fillers
    loop foreach local bp ball.list
        local r = math.random.uniform
        if r < 0.16 then
            ball.group(bp) = 'mineral_quartz'
        endif
        if r > 0.985 then
            ball.group(bp) = 'mineral_mica'
        endif
    endloop
end

define mineral_recount_areas
    area_feldspar = 0.0
    area_quartz = 0.0
    area_mica = 0.0
    loop foreach local bp ball.list
        local a = mineral_ball_area(bp)
        local g = ball.group(bp)
        if g = 'mineral_feldspar' then
            area_feldspar = area_feldspar + a
        endif
        if g = 'mineral_quartz' then
            area_quartz = area_quartz + a
        endif
        if g = 'mineral_mica' then
            area_mica = area_mica + a
        endif
    endloop
end

define mineral_grow_one_pass
    @mineral_recount_areas
    loop foreach local bp ball.list
        local phase = ball.group(bp)
        if phase = 'mineral_feldspar' then
            continue
        endif
        loop foreach local cp ball.contactmap(bp, contact.typeid('ball-ball'))
            local other = contact.end1(cp)
            if other = bp then
                other = contact.end2(cp)
            endif
            if ball.group(other) # 'mineral_feldspar' then
                continue
            endif
            local accept = 0.0
            if phase = 'mineral_quartz' then
                accept = math.max((target_quartz * area_total - area_quartz) / (target_quartz * area_total), 0.0)
            endif
            if phase = 'mineral_mica' then
                accept = math.max((target_mica * area_total - area_mica) / (target_mica * area_total), 0.0)
            endif
            if math.random.uniform < accept then
                ball.group(other) = phase
            endif
        endloop
    endloop
end

define mineral_build_groups
    @mineral_area_total
    @mineral_assign_matrix
    @mineral_seed_fillers
    loop local i (1, 12)
        @mineral_grow_one_pass
    endloop
    @mineral_recount_areas
end
@mineral_build_groups
```

## Stage C: Base Contact Model

```text
model clean

contact model linear range contact type 'ball-facet'
contact method deform emod 2.5e9 kratio 2.0 range contact type 'ball-facet'

contact model linearpbond range contact type 'ball-ball'
contact method bond gap 1e-3 range contact type 'ball-ball'
contact group 'pbond_feldspar' range contact type 'ball-ball'
```

## Stage D: Assign Contact Groups From Mineral Endpoints

```fish
define mineral_assign_contacts
    loop foreach local cp contact.list
        if type.pointer(cp) = 'ball-ball' then
            local b1 = contact.end1(cp)
            local b2 = contact.end2(cp)
            local g1 = ball.group(b1)
            local g2 = ball.group(b2)
            if g1 = g2 then
                if g1 = 'mineral_feldspar' then
                    contact.group(cp) = 'pbond_feldspar'
                endif
                if g1 = 'mineral_quartz' then
                    contact.group(cp) = 'pbond_quartz'
                endif
                if g1 = 'mineral_mica' then
                    contact.group(cp) = 'pbond_mica'
                endif
            else
                contact.group(cp) = 'pbond_boundary'
                if g1 = 'mineral_mica' then
                    contact.group(cp) = 'pbond_mica'
                endif
                if g2 = 'mineral_mica' then
                    contact.group(cp) = 'pbond_mica'
                endif
            endif
        endif
    endloop
end
@mineral_assign_contacts
```

## Stage E: Per-Mineral LPBM Parameters

```text
; feldspar matrix
contact method deform emod 9.6e9 kratio 2.7 range group 'pbond_feldspar'
contact method pb_deform emod 32.0e9 kratio 2.7 range group 'pbond_feldspar'
contact property fric 1.5 pb_rmul 1.0 range group 'pbond_feldspar'
contact property pb_ten 332.5e6 pb_coh 332.5e6 range group 'pbond_feldspar'

; quartz filling
contact method deform emod 7.5e9 kratio 2.7 range group 'pbond_quartz'
contact method pb_deform emod 28.0e9 kratio 2.7 range group 'pbond_quartz'
contact property fric 1.5 pb_rmul 1.0 range group 'pbond_quartz'
contact property pb_ten 66.2e6 pb_coh 66.2e6 range group 'pbond_quartz'

; mica filling / weak mineral
contact method deform emod 1.9e9 kratio 2.7 range group 'pbond_mica'
contact method pb_deform emod 6.8e9 kratio 2.7 range group 'pbond_mica'
contact property fric 1.5 pb_rmul 1.0 range group 'pbond_mica'
contact property pb_ten 49.6e6 pb_coh 49.6e6 range group 'pbond_mica'

; generic boundary fallback
contact method deform emod 5.0e9 kratio 2.7 range group 'pbond_boundary'
contact method pb_deform emod 18.0e9 kratio 2.7 range group 'pbond_boundary'
contact property fric 1.5 pb_rmul 1.0 range group 'pbond_boundary'
contact property pb_ten 60.0e6 pb_coh 60.0e6 range group 'pbond_boundary'
```

## Stage F: Weibull Damage

```fish
[weibull_alpha = 1.0]
[weibull_beta = 3.3]

define weibull_random(alpha, beta)
    local r = math.random.uniform
    if r >= 1.0 then
        r = 1.0 - 1.0e-12
    endif
    weibull_random = alpha * (-math.ln(1.0 - r))^(1.0 / beta)
end

define mineral_apply_weibull_damage
    loop foreach local cp contact.list
        if type.pointer(cp) = 'ball-ball' then
            if contact.model(cp) = 'linearpbond' then
                local factor_strength = weibull_random(weibull_alpha, weibull_beta)
                local factor_stiffness = weibull_random(weibull_alpha, weibull_beta)
                contact.prop(cp, 'pb_ten') = contact.prop(cp, 'pb_ten') * factor_strength
                contact.prop(cp, 'pb_coh') = contact.prop(cp, 'pb_coh') * factor_strength
                contact.prop(cp, 'pb_kn') = contact.prop(cp, 'pb_kn') * factor_stiffness
                contact.prop(cp, 'pb_ks') = contact.prop(cp, 'pb_ks') * factor_stiffness
            endif
        endif
    endloop
end
@mineral_apply_weibull_damage
```

## Stage G: Calm, Save, And Hand Off To Loading Test

```text
model clean
model calm
model save 'mineral_weibull_damaged'
```

Then return to `pfc-workflow` or `pfc-standard-tests` for UCS, BTS, biaxial, triaxial, or other validation tests.

## Complete Modular Run Skeleton

```text
model restore 'biaxial-isoloose'
model random 10001
model clean
program call 'mineral_cluster_assignment.p2fis'
model clean
program call 'mineral_lpbm_parameters.dat'
program call 'weibull_damage.p2fis'
model calm
model save 'mineral_ready_for_loading'
```

## Migration Notes

- This is a PFC 6.0-oriented command skeleton, not a guaranteed drop-in command file for every project.
- Verify callback, intrinsic, and contact-property names with `pfc-mcp` and the installed PFC version before production use.
- Keep the original concepts separated by stage so calibration changes do not accidentally alter clustering or damage logic.
