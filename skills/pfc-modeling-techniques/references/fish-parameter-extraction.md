# FISH Parameter Extraction

Use this reference for formulas, measurement windows, and interpretation.
Full code lives in:

- `source-code-fish-parameter-extraction-pfc6.md`

## 1. Minimum monitoring set

For most UCS, biaxial, or triaxial problems, store at least:

- axial or principal stress
- axial or principal strain
- crack count or damage count
- optional tension and shear crack counts separately
- saved states at milestone stages, peak, and final

## 2. Core formulas

### Elastic modulus

$$
E = \frac{\sigma_2 - \sigma_1}{\varepsilon_2 - \varepsilon_1}
$$

### Deformation modulus

$$
E_d = \frac{\sigma_{peak}}{\varepsilon_{peak}}
$$

### Poisson ratio

$$
\nu = - \frac{\Delta \varepsilon_{lat}}{\Delta \varepsilon_{ax}}
$$

### Mohr-Coulomb conversion from triaxial peaks

If peak data are fitted by

$$
\sigma_1 = A + B \sigma_3
$$

then one convenient conversion is

$$
\phi = \arcsin\left(\frac{B - 1}{B + 1}\right)
$$

$$
c = \frac{A(1 - \sin\phi)}{2\cos\phi}
$$

### Particle-average stress

$$
\sigma_{ij} = \frac{1}{V^P} \sum_{c \subset N_c} f_j^{(c)} d_i^{(c)}
$$

## 3. Measurement windows

Typical windows used in the migrated source code:

- elastic modulus from two points on the ascending branch
- Poisson ratio from a small-strain interval
- peak stress and peak strain from running maxima
- `sigma_ci` from volumetric-strain turning behavior

The exact thresholds belong in the code file, not here.

## 4. Crack and field extraction

- crack tracking usually depends on a bond-capable law such as `linearpbond`
- `bond_break` callback is the standard route for event tracking
- stress fields should use multiple measurement regions, not one point value

## 5. Delivery rule

When reporting extracted parameters, always provide:

- the formula
- the strain or stress window
- the variable source
- any post-processing assumption used to compute the final number
