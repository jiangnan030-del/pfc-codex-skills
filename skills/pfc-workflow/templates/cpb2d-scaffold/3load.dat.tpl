model restore 'parallel_bonded'
ball attribute displacement multiply 0.0 velocity multiply 0.0
ball attribute force-contact multiply 0.0 moment-contact multiply 0.0
[specimen_width = ${specimen_width_m}]
[peak_drop_fraction = ${peak_drop_fraction}]
[stage_a_strain = ${stage_a_strain}]
[stage_b_strain = ${stage_b_strain}]
[stage_c_strain = ${stage_c_strain}]
[stage_d_strain = ${stage_d_strain}]
[stage_a_saved = 0]
[stage_b_saved = 0]
[stage_c_saved = 0]
[stage_d_saved = 0]

fish define wallpoint
    wp1 = wall.find(1)
    wp3 = wall.find(3)
end
@wallpoint
[wly0 = wall.pos.y(wp3) - wall.pos.y(wp1)]

fish define monitor
    whilestepping
    wsyy = -0.5 * (wall.force.contact.y(wp1) - wall.force.contact.y(wp3)) / specimen_width
    weyy = (wall.pos.y(wp3) - wall.pos.y(wp1) - wly0) / wly0
end

wall attribute velocity-y ${wall_velocity_m_s} range id 1
wall attribute velocity-y -${wall_velocity_m_s} range id 3
program echo off
program call 'fracture.p2fis'
program echo on
@track_init
history purge
history interval ${history_interval}
history id 99 @monitor
history id 1 @wsyy
history id 2 @weyy
history id 3 @crack_num
history id 4 @crack_tension_num
history id 5 @crack_shear_num
model history id 6 mechanical cycles-total
model mechanical timestep automatic

[peak_stress = 0.0]
[previous_stress = 0.0]
[peak_saved = 0]
fish define peak_drop_halt
    peak_drop_halt = 0
    local abs_stress = math.abs(wsyy)
    local abs_strain = math.abs(weyy)
    if abs_stress > peak_stress
        peak_stress = abs_stress
    end_if
    if stage_a_saved = 0
        if abs_strain >= stage_a_strain
            command
                model save 'stage_a'
            endcommand
            stage_a_saved = 1
        end_if
    end_if
    if stage_b_saved = 0
        if abs_strain >= stage_b_strain
            command
                model save 'stage_b'
            endcommand
            stage_b_saved = 1
        end_if
    end_if
    if stage_c_saved = 0
        if abs_strain >= stage_c_strain
            command
                model save 'stage_c'
            endcommand
            stage_c_saved = 1
        end_if
    end_if
    if stage_d_saved = 0
        if abs_strain >= stage_d_strain
            command
                model save 'stage_d'
            endcommand
            stage_d_saved = 1
        end_if
    end_if
    if peak_saved = 0
        if stage_d_saved = 1
            if abs_stress < previous_stress * 0.995
                if previous_stress >= peak_stress * 0.995
                    command
                        model save 'peak'
                    endcommand
                    peak_saved = 1
                end_if
            end_if
        end_if
    end_if
    previous_stress = abs_stress
    if peak_saved = 1
        if abs_stress <= peak_stress * peak_drop_fraction
            peak_drop_halt = 1
        end_if
    end_if
end

fish define save_peak_if_missing
    if peak_saved = 0
        command
            model save 'peak'
        endcommand
        peak_saved = 1
    end_if
end

model solve fishhalt @peak_drop_halt
@save_peak_if_missing
model save 'final'
