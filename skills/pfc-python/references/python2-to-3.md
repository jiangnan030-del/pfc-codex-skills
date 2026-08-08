# Python 2 -> 3 notes and source-correction disclosure

The embedded Python interpreter differs by PFC version:

- PFC5.0: Python 2.7
- PFC6.0 / 7.0 / 9.0: Python 3.x

The source material for this skill was written for PFC5.0 (Python 2.7). Scripts here are migrated to
Python 3 where the change is unambiguous.

## Syntax differences

| Python 2 (original) | Python 3 (used here) |
| --- | --- |
| `print x` | `print(x)` |
| `dict.iteritems()` | `dict.items()` |
| `reduce(...)` builtin | `from functools import reduce` |
| integer division `4/3` | write `4.0/3.0` explicitly |

The Darcy example's `outlet_mask` uses `reduce`, so it must be imported from `functools` on Python 3.

## Transcription corrections already applied

- Full-width to half-width punctuation for quotes, parentheses, `=`, `<`, `>`, `*`.
- Split fused numbers/keywords: `domain extent -5e-26e-2-6e-25e-2-5e-25e-2` -> `-5e-2 6e-2 -6e-2 5e-2 -5e-2 5e-2`;
  `box -0.023750.02375` -> `-0.02375 0.02375`; `azimuth 0.0360.0` -> `0.0 360.0`; `size 0.050.1` -> `0.05 0.1`.
- Method/variable misreads: `it. command` / `ball. radius` / `id_list. append` -> no space;
  `bl=` -> `b1 =`; `template sl` -> `template s1`; `kn 1el` / `kn 1 el` -> `kn 1e1`.
- Power operator: `phi * * 3` -> `phi**3`; `grain_size * * 2` -> `grain_size**2`; `(1-phi)* * 2` -> `(1-phi)**2`.
- Ranges and comparisons: `clump delete range x 1.0025` -> `range x 1.002 5`; `fy = = 0` -> `fy == 0`;
  `c.props()['fric'']` -> `c.props()['fric']`.
- Reconstructed items: the `domain extent` lines for the three-ball/one-wall model and the cubic packing,
  plus some shear-box wall vertices, were reconstructed from context and must be re-checked against real
  specimen dimensions.

## Terminology

clump = clump/cluster body; pebble = constituent sphere; facet = wall triangle element;
virtual/inactive contact = contact stored but not transmitting force; mobility = lambda = K / mu;
Kozeny-Carman = porosity-based permeability law; one-way coupling = fluid -> solid only.
