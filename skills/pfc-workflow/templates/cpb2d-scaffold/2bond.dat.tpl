model restore 'sample'
${crack_command}
; PFC6 legal assignment; equivalent intent: contact model linearpbond.
contact cmat default type ball-ball model linearpbond method deform emod ${bond_emod_pa} kratio ${kratio} ...
    pb_deform emod ${bond_emod_pa} kratio ${kratio} ...
    property pb_ten ${pb_ten_pa} pb_coh ${pb_coh_pa} pb_fa ${pb_fa_deg} fric ${friction}
contact cmat apply
model clean
contact method bond gap ${particle_radius_min_m}
ball attribute displacement multiply 0.0 velocity multiply 0.0
contact property lin_force 0.0 0.0 lin_mode 1
ball attribute force-contact multiply 0.0 moment-contact multiply 0.0
wall delete walls range id 2
wall delete walls range id 4
model calm
model cycle 200 calm 20
model solve ratio-average 1.0e-6
model save 'parallel_bonded'
