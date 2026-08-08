# Findings and acceptance checks

Source basis: Wang Yujie et al. (2026), *Effects of fabric characteristics on small-strain shear modulus of sandy soil*.

## Main trends

1. G0 decreases with increasing void ratio for all particle shapes.
2. The reported overall G0-void-ratio fit has approximately `R2=0.94`.
3. At comparable relative density, ellipsoidal-particle specimens are stiffer than spherical specimens; G0 generally increases with aspect ratio.
4. For the same shape, greater fabric anisotropy lowers G0.
5. The fabric effect becomes more pronounced as void ratio rises.
6. For matched fabric, G0 increases from 0 to 45 to 90 degree loading.
7. Stiffness is greatest when more particle major axes align with the loading direction, producing a more efficient contact-normal/force-chain network.
8. Strong-fabric 90-degree cases may depart from a simple exponential G0-e relationship.

## Acceptance logic

A reproduction should not be accepted on trend alone. Check:

- matched void ratio, pressure and approximately matched `Zm`;
- achieved `ad` and orientation distribution;
- at least three seeds with uncertainty bars;
- stable G0 under lower strain amplitude;
- negligible mean-pressure/volume drift according to the chosen test definition;
- low kinetic-to-strain-energy ratio;
- unchanged fabric over the one-loop small-strain test.

## Scope boundary

This workflow estimates initial small-strain stiffness. It does not by itself validate pore-pressure generation, modulus degradation at medium strain, damping, liquefaction resistance or post-liquefaction deformation.
