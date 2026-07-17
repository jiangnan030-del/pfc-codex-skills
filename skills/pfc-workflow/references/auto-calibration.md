# Auto Calibration

Use this file when the user asks how to replace manual trial-and-error with `贝叶斯优化`, `代理模型`, `响应面`, `遗传算法`, or `差分进化`.

## Default recommendation

For expensive PFC calibration, use:

1. **LHS initial design** to cover the parameter space
2. **true-case evaluation** to build the first dataset
3. **surrogate fitting** to estimate the objective surface cheaply
4. **sequential Bayesian optimization** to add one expensive case at a time

Do **not** start with a genetic algorithm unless the objective is extremely rough, failure-heavy, or the surrogate route has already failed.

## Method split

### A. LHS + surrogate + Bayesian optimization (default)

Use this when:

- each PFC run is expensive
- the parameter dimension is low to medium
- the macro targets are well defined
- the user wants sample efficiency more than brute-force global coverage

Default behavior:

- initial sample size: `n_init = max(24, 8 * d)`
- fit at least GP + RF + quadratic response surface diagnostics
- choose one new expensive case per iteration
- acquisition: `Expected Improvement`
- stop when the best objective is within tolerance or the iteration budget is exhausted

### B. Response surface method (baseline)

Use this when:

- the user wants quick global trend insight
- the active parameter count is small
- the main need is to understand dominant effects and coarse interactions

Recommended role:

- fit a quadratic polynomial model after the LHS stage
- use it to screen promising neighborhoods
- use it as a baseline against the GP/RF surrogate, not as the only source of truth

### C. Differential evolution / genetic-style search (fallback)

Use this when:

- the objective is non-smooth or highly discontinuous
- many runs fail or produce invalid outputs
- the surrogate cross-validation error stays poor for several rounds
- the user accepts a larger evaluation budget

Recommended implementation:

- use `scipy.optimize.differential_evolution` first
- keep `workers=1` by default for PFC workflows unless the user explicitly confirms multi-case parallelism is safe
- log every failed or invalid point instead of dropping it

## Budget strategy

Default budget split:

- 50% to 70%: initial exploration + early BO iterations
- 20% to 30%: local refinement near the best region
- 10% to 20%: fallback or confirmation runs

For very expensive cases, prefer fewer but better chosen iterations over large generations.

## Failure handling

When a true run fails:

- keep the point in the history table
- mark `status=failed`
- assign a large penalty to the scalar objective
- store the failure reason, elapsed time, and artifact path

Failed runs are useful because they help the optimizer learn infeasible or unstable regions.

## When to switch methods

Switch from Bayesian optimization to DE when:

- the surrogate error remains unstable after enough samples
- the predicted optimum keeps landing in failed regions
- the objective changes abruptly with small parameter moves

Switch from DE back to surrogate-led refinement when:

- a stable basin has been found
- the user now wants higher sample efficiency near the optimum

## Why this is better than manual trial-and-error

LHS + surrogate + BO usually beats hand tuning because it:

- covers the space more evenly at the start
- reuses information from all previous runs
- avoids repeatedly sampling near-duplicate points
- concentrates expensive solves near the most promising regions
