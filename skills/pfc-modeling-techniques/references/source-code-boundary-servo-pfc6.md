# Source Code: Boundary Servo and Wall Motion (PFC 6.0)

This file carries migrated source blocks `03` to `04`.

## Block 03 - Particle-expansion stress control

```fish
model restore 'ini'
measure delete

[target_stress = -1.0e6]
[measure_radius = 1.0]
[nstep = 0]
[nstep_total = 0]
[stress_avg = 0.0]
[stress_error = 1.0]
[avg_ratio = 1.0]

fish define create_measures_according_to_model_box
    local xxmin =  1.0e10
    local xxmax = -1.0e10
    local yymin =  1.0e10
    local yymax = -1.0e10
    loop foreach local bp ball.list
        local xx1 = ball.pos.x(bp) + ball.radius(bp)
        local xx2 = ball.pos.x(bp) - ball.radius(bp)
        local yy1 = ball.pos.y(bp) + ball.radius(bp)
        local yy2 = ball.pos.y(bp) - ball.radius(bp)
        if xx1 > xxmax
            xxmax = xx1
        endif
        if xx2 < xxmin
            xxmin = xx2
        endif
        if yy2 < yymin
            yymin = yy2
        endif
        if yy1 > yymax
            yymax = yy1
        endif
    endloop
    local nnnx = int((xxmax - xxmin) / (2.0 * measure_radius))
    local nnny = int((yymax - yymin) / (2.0 * measure_radius))
    local nums = 0
    loop local n (1, nnnx)
        local x0 = xxmin + 2.0 * measure_radius * (n - 0.5)
        loop local m (1, nnny)
            nums = nums + 1
            local y0 = yymin + 2.0 * measure_radius * (m - 0.5)
            command
                measure create id [nums] position [x0] [y0] radius [measure_radius]
            endcommand
        endloop
    endloop
end
@create_measures_according_to_model_box

fish define delete_some_measure
    loop foreach local mp measure.list
        local por = measure.porosity(mp)
        if por > 0.25
            command
                measure delete range id [measure.id(mp)]
            endcommand
        endif
    endloop
end
@delete_some_measure

fish define ball_expand_coefficient
    stress_avg = 0.0
    local num_meas = 0
    loop foreach local mp measure.list
        num_meas = num_meas + 1
        local stress_xx = measure.stress.xx(mp)
        local stress_yy = measure.stress.yy(mp)
        local stress_pj = (stress_xx + stress_yy) / 2.0
        stress_avg = stress_avg + stress_pj
        local rad_mea = measure.radius(mp)
        local x0 = measure.pos.x(mp)
        local y0 = measure.pos.y(mp)
        local ddsigma = target_stress - stress_pj
        local gangdu = 0.0
        local num = 0
        loop foreach local cp contact.list
            local xl = contact.pos.x(cp)
            local yl = contact.pos.y(cp)
            local dd = math.sqrt((xl - x0)^2 + (yl - y0)^2)
            if dd < rad_mea
                gangdu = gangdu + contact.prop(cp,'kn')
                num = num + 1
            endif
        endloop
        if num > 0
            gangdu = gangdu / float(num)
            loop foreach local bp ball.list
                local xl = ball.pos.x(bp)
                local yl = ball.pos.y(bp)
                local dd = math.sqrt((xl - x0)^2 + (yl - y0)^2)
                if dd < rad_mea
                    local drr = ddsigma / gangdu * 0.1
                    ball.radius(bp) = ball.radius(bp) - drr
                endif
            endloop
        endif
    endloop
    if num_meas > 0
        stress_avg = stress_avg / float(num_meas)
    endif
end
@ball_expand_coefficient

fish define load
    load = 0
    nstep_total = nstep_total + 1
    if nstep_total > 100000
        load = 1
        exit
    endif
    nstep = nstep + 1
    if nstep >= 1000
        ball_expand_coefficient
        nstep = 0
    endif
    stress_error = math.abs((stress_avg - target_stress) / target_stress)
    avg_ratio = mech.solve("ratio-average")
    if stress_error > 0.05
        exit
    endif
    if avg_ratio > 1.0e-5
        exit
    endif
    load = 1
end

measure create id 1000 position 0.0 0.0 radius 8.0

fish define measure_1000_stress_xx
    local mp = measure.find(1000)
    measure_1000_stress_xx = measure.stress.xx(mp)
end

fish define measure_1000_stress_yy
    local mp = measure.find(1000)
    measure_1000_stress_yy = measure.stress.yy(mp)
end

fish history name 'stress_error' @stress_error
fish history name 'avg_ratio' @avg_ratio
fish history name 'measure_1000_sxx' @measure_1000_stress_xx
fish history name 'measure_1000_syy' @measure_1000_stress_yy
fish history name 'stress_avg' @stress_avg

model solve fishhalt @load
```

## Block 04 - Wall motion without servo / ball-mill style example

```fish
model new
model domain extent -3.0 3.0
wall generate circle position 0.0 0.0 radius 1.0 resolution 0.05
ball generate number 100 radius 0.05 group 'steelball' range annulus center 0.0 0.0 radius 0.0 0.9
contact cmat default model linear property kn 1e9 ks 5e8 fric 0.2 dp_nratio 0.0
ball attribute density 7850 damp 0.0
model cycle 2000 calm 50
model gravity 0.0 -9.8
model solve ratio-average 1e-5

ball attribute damp 0.0
contact cmat default type ball-facet model linear property kn 1e9 ks 5e8 fric 0.8 lin_mode 1 dp_nratio 0.1
contact property lin_force 0.0 0.0 lin_mode 1

fish define delete_facet
    local num = wall.facet.num
    loop local m (1, num)
        local nn = m - int(m / 5) * 5
        if nn = 0
            command
                wall delete facets range id [m]
            endcommand
        endif
    endloop
end
@delete_facet

wall generate circle position 0.0 0.0 radius 1.5 resolution 0.05

fish define create_rock
    loop local n (1, 15)
        command
            ball generate cubic radius 0.02 box [-0.7 + 0.1 * (n - 1)] [-0.65 + 0.1 * (n - 1)] 0.10 0.15 group 'rock'
            ball generate cubic radius 0.02 box [-0.7 + 0.1 * (n - 1)] [-0.65 + 0.1 * (n - 1)] 0.20 0.25 group 'rock'
            ball generate cubic radius 0.02 box [-0.7 + 0.1 * (n - 1)] [-0.65 + 0.1 * (n - 1)] 0.30 0.35 group 'rock'
            ball generate cubic radius 0.02 box [-0.7 + 0.1 * (n - 1)] [-0.65 + 0.1 * (n - 1)] 0.40 0.45 group 'rock'
            ball generate cubic radius 0.02 box [-0.7 + 0.1 * (n - 1)] [-0.65 + 0.1 * (n - 1)] 0.50 0.55 group 'rock'
        endcommand
    endloop
end
@create_rock

ball attribute density 2400 range group 'rock'
model clean
contact groupbehavior and
contact cmat add 1 model linear property kn 1e9 ks 5e8 fric 0.2 dp_nratio 0.1 range group 'steelball'
contact cmat apply range group 'steelball'
contact cmat add 2 model linearpbond property kn 1e8 ks 1e8 fric 0.3 dp_nratio 0.1 lin_mode 1 ...
    pb_rmul 1.0 pb_kn 1e8 pb_ks 1e8 pb_ten 2e5 pb_coh 1e7 pb_fa 15 range group 'rock'
contact cmat apply range group 'rock'
contact method bond gap 1e-3 range group 'rock'
model cycle 20000
ball attribute displacement multiply 0.0
ball attribute velocity multiply 0.0
[count = 0]

fish define bond_break_rock(entries)
    count = count + 1
end

wall attribute rotation-center 0.0 0.0 spin -2.0 range name 'circle wall'
fish callback add @bond_break_rock event bond_break
fish history name 'bond_break_count' @count
model solve time 20.0
```
