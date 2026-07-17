# Cross-Correlation Time Delay

Velocity-free AE localization depends on accurate time delays inside each sensor cluster. Use cross-correlation instead of manual first-arrival picking when cluster waveforms are similar.

## Continuous Definition

For two signals `x(t)` and `y(t)`:

```text
R_xy(tau) = (1/T) * integral_0^T x(t) * y(t + tau) dt
```

The time delay is the lag where correlation is maximum:

```text
tau_0 = argmax_tau R_xy(tau)
```

## Discrete Implementation

For sampled signals `x[n]`, `y[n]`, sample interval `dt`:

```text
lag_samples = argmax_lag correlate(y, x)
time_delay = lag_samples * dt
```

Sign convention must be consistent with the localization equations. This skill uses:

```text
t_21 = arrival_time_sensor2 - arrival_time_sensor1
```

If `sensor2` arrives earlier than `sensor1`, `t_21` is negative.

## Recommended Preprocessing

- subtract mean from each waveform
- optionally normalize by standard deviation
- restrict correlation to a window around expected first arrival
- optionally bandpass around the source frequency band
- use sub-sample peak interpolation when timing precision is critical

## Parabolic Sub-Sample Peak

If the correlation peak occurs at index `i` with neighboring values `c[i-1]`, `c[i]`, `c[i+1]`, the sub-sample offset is:

```text
delta = 0.5 * (c[i-1] - c[i+1]) / (c[i-1] - 2*c[i] + c[i+1])
```

Corrected lag:

```text
lag = i + delta
```

## Quality Metrics

Record these with every time delay:

```text
correlation_peak
normalized_correlation_peak
lag_seconds
window_start
window_end
signal_pair
```

Reject or flag if:

- normalized correlation peak is too low
- lag is outside physically possible bounds
- multiple peaks have similar amplitude
- the waveform window includes boundary reflections

## Figure Reproduction

The canonical script `scripts/canonical/plot_cross_correlation_demo.py` reproduces the two-panel cross-correlation time-delay illustration:

```bash
python scripts/canonical/plot_cross_correlation_demo.py --out cross_correlation_delay_demo.png
```

It generates:

```text
cross_correlation_delay_demo.png
cross_correlation_delay_demo.svg
cross_correlation_delay_demo.pdf
```

The demo uses two similar wavelets with a 20 microsecond delay and marks the cross-correlation peak near `A(-20, 0.2)`, matching the source figure convention.

## PFC Export Contract

For every sensor, export:

```text
time, displacement_x, displacement_y, velocity_x, velocity_y, or force component
```

For plate out-of-plane source tests, export the component that best matches the source direction, such as `z` velocity or force when available.
