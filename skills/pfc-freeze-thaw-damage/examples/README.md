# pfc-freeze-thaw-damage example

These files are reference templates, not a universally calibrated model. Check all commands against the official documentation for the target PFC version.

## Run order

1. Run `../scripts/gen_ftc_specimen.p3dat` to save `ftc_ini` and `ftc_bonded`.
2. Calibrate rock-rock parameters against the pre-freeze UCS and modulus.
3. Run `../scripts/axial_servo.p3fis`, set `sig_frac`, call `[apply_sigma1]`, and save `ftc_state1`.
4. Run `../scripts/ftc_cycle.p3fis` and call `[ftc_run]` to create `ftc_cycle_n` saves.
5. Export cracks and run `python ../scripts/crack_stats.py cracks.csv`.

## Calibration gate

Before freeze-thaw cycling, reproduce the reference numerical UCS of 73.40 MPa and elastic modulus of 8.72 GPa. Laboratory targets are 75.05 MPa and 9.02 GPa, corresponding to errors of about 2.2% and 3.3%. Re-calibrate for every different rock.

## Driver checks

- `T(0)=0`, `T(30 min)=-30 C`, and `T(60 min)=0`.
- Unfrozen water content approaches zero near -25 C; new cracks should then flatten.
- Use the incremental volume convention `dV=V0*(rho_w/rho_i-1)`, giving about 9% full-freezing volume growth and radius factor `1.09^(1/3)`.
- Solve to mechanical equilibrium after every pore-particle radius change.
- Keep the axial servo active for `sigma_1/sigma_0 = 0, 0.2, 0.4, 0.6`.

## Acceptance checks

- With no axial load, radial strain exceeds axial strain and deformation stabilizes after roughly 10 cycles.
- Under axial load, radial strain accelerates after about 30 cycles; the `0.6 sigma_0` case may fail near 45 cycles.
- Crack count rises during cooling and changes little below about -25 C.
- Radial crack density is about `0.90e7-1.17e7 cracks/m3` at 0-20 mm and about `2.45e7 cracks/m3` in the 20-25 mm edge band for the reference `0.6 sigma_0` case.
- The 0-5 degree crack share rises from 10.86% to 15.01% with axial stress, while the 85-90 degree share falls from 0.52% to 0.24%.
- Tensile cracking remains dominant: about 68.76% without axial stress and 58.97% at `0.6 sigma_0`.

## Assumptions

The reference model assigns a uniform specimen temperature and does not simulate heat conduction or pore-water migration toward the freezing front.
