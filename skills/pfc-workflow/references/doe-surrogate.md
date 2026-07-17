# DOE and Surrogate Modeling

Use this file when the user asks about `拉丁超立方采样`, `DOE`, `代理模型`, `少跑算例多出信息`, or `响应面`.

## Core idea

Expensive PFC calibration should separate **true simulation cost** from **cheap statistical learning**:

- use DOE to buy informative true samples
- use a surrogate to interpolate and rank new candidates cheaply
- only spend new PFC runs where the surrogate predicts value or uncertainty is high

## LHS design rules

### Sample count

Default initial size:

`n_init = max(24, 8 * d)`

where `d` is the number of active parameters.

Use more only when:

- parameter interactions are strong
- the space contains large invalid regions
- the user can afford the budget

### Parameter handling

- continuous parameters: sample in linear or log space according to physics
- integer parameters: sample continuously first, then round and clamp
- strongly linked parameters: encode the dependency explicitly instead of pretending they are independent

### Sampling goal

Choose `maximin`-style LHS so early samples are spread out rather than clustered.

## Surrogate family roles

### Gaussian process

Best when:

- dimension is modest
- sample size is not too large
- uncertainty estimates matter

Good for Bayesian optimization because it provides mean + uncertainty naturally.

### Random forest

Best when:

- dimension grows
- the response surface is rough
- GP fitting becomes unstable or slow

Use tree-to-tree variance as an uncertainty proxy.

### Quadratic response surface

Best when:

- the user wants interpretable main effects and pair interactions
- the active parameter count is small
- a baseline trend model is enough for first-pass screening

## Validation rules

Never trust a surrogate without diagnostics. Report at least:

- cross-validated RMSE
- cross-validated MAE
- R2
- best model selected by policy and by error table

If all surrogate errors are poor, do not keep exploiting aggressively. Add more exploration points or switch methods.

## Sample-efficiency heuristics

To get more information from fewer solves:

- start with space-filling samples, not hand-picked guesses
- scalarize the macro targets consistently so all runs are comparable
- keep failed points with penalties
- add one expensive case per BO iteration for GUI-bound or serial PFC environments
- inspect surrogate residuals before trusting predicted improvements

## Recommended diagnostics

- convergence curve of best objective vs evaluation count
- CV error comparison of GP / RF / RSM
- parameter importance or sensitivity chart
- 2D projection scatter of sampled points colored by objective
- target-hit table for the best run
