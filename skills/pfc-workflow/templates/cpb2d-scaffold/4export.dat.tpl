fish define export_csv
    local t_stress = table.create('stress_table')
    local t_crack = table.create('crack_table')
    local t_crack_tension = table.create('crack_tension_table')
    local t_crack_shear = table.create('crack_shear_table')
    local t_stress_step = table.create('stress_step_table')
    local t_strain_step = table.create('strain_step_table')
    local t_crack_step = table.create('crack_step_table')
    local t_crack_tension_step = table.create('crack_tension_step_table')
    local t_crack_shear_step = table.create('crack_shear_step_table')
    command
        history export 1 vs 2 table 'stress_table'
        history export 3 vs 2 table 'crack_table'
        history export 4 vs 2 table 'crack_tension_table'
        history export 5 vs 2 table 'crack_shear_table'
        history export 1 vs 6 table 'stress_step_table'
        history export 2 vs 6 table 'strain_step_table'
        history export 3 vs 6 table 'crack_step_table'
        history export 4 vs 6 table 'crack_tension_step_table'
        history export 5 vs 6 table 'crack_shear_step_table'
    endcommand
    local n = table.size(t_stress)
    local rows = array.create(n + 1)
    rows(1) = 'strain,stress_mpa,crack_num,crack_tension_num,crack_shear_num'
    loop local i (1, n)
        rows(i + 1) = string(table.x(t_stress,i)) + ',' + string(table.y(t_stress,i) / 1.0e6) + ',' + string(table.y(t_crack,i)) + ',' + string(table.y(t_crack_tension,i)) + ',' + string(table.y(t_crack_shear,i))
    end_loop
    local status = file.open('stress_strain.csv', 1, 1)
    status = file.write(rows, n + 1)
    status = file.close()

    local ns = table.size(t_stress_step)
    local step_rows = array.create(ns + 1)
    step_rows(1) = 'step,strain,stress_mpa,crack_num,crack_tension_num,crack_shear_num'
    loop local j (1, ns)
        step_rows(j + 1) = string(table.x(t_stress_step,j)) + ',' + string(table.y(t_strain_step,j)) + ',' + string(table.y(t_stress_step,j) / 1.0e6) + ',' + string(table.y(t_crack_step,j)) + ',' + string(table.y(t_crack_tension_step,j)) + ',' + string(table.y(t_crack_shear_step,j))
    end_loop
    status = file.open('stress_strain_step.csv', 1, 1)
    status = file.write(step_rows, ns + 1)
    status = file.close()
end
@export_csv

fish define export_fracture_orientations
    local n = crack_record_count
    local rows = array.create(n + 1)
    rows(1) = 'angle_deg,type'
    loop local i (1, n)
        rows(i + 1) = string(crack_angle_record(i)) + ',' + crack_type_record(i)
    end_loop
    local status = file.open('plotdata_fracture_orientations.csv', 1, 1)
    status = file.write(rows, n + 1)
    status = file.close()
end
@export_fracture_orientations
