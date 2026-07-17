# Source Excitation

## Source Choice

| Source | Frequency behavior | Dispersion risk | Recommendation |
| --- | --- | --- | --- |
| sine displacement pulse | high-frequency corners if abruptly started/stopped | high | avoid unless intentionally testing harmonic response |
| Ricker velocity pulse | compact, zero-phase wavelet with controlled dominant frequency | lower | default for wave propagation and AE-location validation |
| Ricker force pulse | useful for plate source / pencil-lead-break style numerical input | lower | good for AE-location waveforms |

## Ricker Velocity Source

Velocity form:

```text
u_dot(t) = A0 * [1 - 2*pi^2*f^2*(t - 1/f)^2] * exp[-pi^2*f^2*(t - 1/f)^2]
```

Source example:

```text
A0 = -1.0e-3 m/s
f = 16 Hz
maximum significant frequency about 50 Hz
```

## Ricker Force Source

For point-force excitation:

```text
F(t) = A0 * [1 - 2*pi^2*f^2*(t - 1/f)^2] * exp[-pi^2*f^2*(t - 1/f)^2]
```

Flat-joint plate example:

```text
frequency = 100 kHz
amplitude = 1.0e-8 N
timestep = 5.0e-8 s
```

## PFC Implementation Pattern

Before dynamic source excitation:

```text
model configure dynamic
model mechanical time-total 0.0
ball attribute damp 0.0
model mechanical timestep fix <dt>
```

Use a FISH function to compute source value from mechanical time:

```fish
fish define ricker_value
    local t = mech.time.total
    local tau = t - 1.0 / source_freq
    ricker_value = source_amp * (1.0 - 2.0 * math.pi^2 * source_freq^2 * tau^2) * math.exp(-math.pi^2 * source_freq^2 * tau^2)
end
```

Apply as velocity or force in a callback:

```fish
fish define apply_source_velocity
    local v = ricker_value
    ball.vel.x(source_ball) = v
end

fish callback add @apply_source_velocity -1.0
```

or:

```fish
fish define apply_source_force
    local f = ricker_value
    ball.force.app.z(source_ball) = f
end

fish callback add @apply_source_force -1.0
```

Remove or zero the source after its duration:

```fish
if mech.time.total > source_duration then
    ; remove callback or set applied force to zero
endif
```

## Frequency Selection Checklist

Given minimum wave speed `c_min`, maximum relevant frequency `f_max`, and particle spacing `D`:

```text
lambda = c_min / f_max
ratio = lambda / D
```

Accept only if:

```text
ratio >= 10
```

If not:

- reduce source frequency
- reduce particle spacing
- use a coarser interpretation that does not rely on precise arrival times

## Signal Recording

Record at least:

```text
time
source signal
monitor displacement/velocity/force in relevant directions
```

Use `fish history`, `ball history`, `wall history`, or exported tables depending on the implementation.
