model new
model title '${project_title} - ${case_name}'
model domain extent -${domain_half_extent_m} ${domain_half_extent_m}
model random ${random_seed}
wall generate box -${specimen_half_width_m} ${specimen_half_width_m} -${specimen_half_height_m} ${specimen_half_height_m} expand 1.5
ball distribute porosity ${target_porosity} radius ${particle_radius_min_m} ${particle_radius_max_m} box -${specimen_half_width_m} ${specimen_half_width_m} -${specimen_half_height_m} ${specimen_half_height_m}
contact cmat default model linear method deformability emod ${linear_emod_pa} kratio ${kratio} property fric ${friction}
ball attribute density ${density_kg_m3} damp ${damping}
model cycle 2000 calm 50
model solve ratio-average 1.0e-5
model save 'sample'
