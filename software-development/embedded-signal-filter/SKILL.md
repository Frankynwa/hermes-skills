---
name: embedded-signal-filter
description: "Design, implement, and verify digital signal filters for MCU (EWMA, moving average, IIR). Covers Q16 fixed-point arithmetic, deviation-domain filtering, overflow safety, convergence analysis, and systematic code review for embedded C. Use when: ADC data filtering, noise suppression, baseline stabilization, fixed-point algorithm design, or reviewing embedded signal processing code."
triggers:
  - ADC filter / signal processing for MCU
  - EWMA / exponential moving average implementation
  - Q16 / fixed-point arithmetic
  - noise suppression / baseline stabilization
  - embedded C code review (filter / DSP)
  - algorithm comparison for signal filtering
  - spectral leakage / FFT analysis of ADC data
  - frequency domain analysis / windowing / broadband vs narrowband
---

# Embedded Signal Filter — Design, Implement, Review

## Core Concept: Deviation-Domain Filtering

When ADC values are large (e.g. 8,484,000) but noise is small (±6,000), raw Q16 fixed-point overflows because `8484000 * 65536 >> int32`. The solution is **deviation-domain filtering**:

```
1. Subtract known baseline → small deviation (±6000)
2. Apply filter on deviation (safe for Q16)
3. Add baseline back to output
```

This is the single most important pattern for large-value ADC filtering.

## EWMA Q16 Implementation Pattern

### Algorithm (per-sample update)
```c
// Input: x_raw (ADC value), baseline (known DC offset)
int32_t dev = x_raw - baseline;           // deviation domain
int64_t dev_q16 = (int64_t)dev << 16;     // to Q16, use int64!
int64_t inv = 65536 - alpha_q16;          // (1-alpha) in Q16

// EWMA recurrence — ALL in int64 to prevent overflow
y_q16 = (int32_t)((alpha_q16 * dev_q16 + inv * (int64_t)y_q16) >> 16);

// Output back to original domain
return (y_q16 >> 16) + baseline;
```

### Key Parameters
| alpha_q16 | alpha float | Cutoff (fs=20Hz) | Use case |
|-----------|-------------|-------------------|----------|
| 3277 | 0.05 | 0.16 Hz | Extreme smoothing |
| 6554 | 0.10 | 0.32 Hz | Strong smoothing (recommended default) |
| 9830 | 0.15 | 0.48 Hz | Medium |
| 13107 | 0.20 | 0.64 Hz | Fast tracking |

Formula: `fc ≈ alpha * fs / (2 * pi)`

### RAM: 12 bytes per channel (3x int32_t: y_q16, alpha_q16, baseline)

### Shift-only variant (no multiply, for 8051/attiny)
```c
// alpha = 1/8, only shift + add
y_prev += ((x_raw - baseline - y_prev) >> 3);
return y_prev + baseline;
```
Less precise (sigma=358 vs 137.5 for Q16) but zero multiply.

## Overflow Safety Checklist

1. **Max deviation × alpha in Q16**: Must fit int64. Check: `max_dev * 65536 * 65536 < 2^63`
2. **y_q16 after >>16**: Must fit int32. Check: result of step is < 2^31
3. **set_baseline shift**: `baseline_diff << 16` can overflow int32 if diff > 32767. Use int64 cast.
4. **Negative right-shift**: Implementation-defined in C. ARM GCC/Keil use arithmetic shift (safe), but add `-fwrapv` or use unsigned intermediate for portability.

## Algorithm Selection Guide

For MCU ADC noise suppression, compare candidates on these axes:

| Algorithm | Sigma suppression | RAM | CPU per sample | Best for |
|-----------|-------------------|-----|----------------|----------|
| EWMA Q16 | 16x | 12B | 1 multiply + shifts | Most cases (best tradeoff) |
| EWMA shift-only | 6x | 4B | shifts only | 8-bit MCUs without hardware multiply |
| Moving Average W=5 | 5x | 20B | 5 adds + divide | When you need exact window |
| Moving Average W=10 | 7x | 40B | 10 adds + divide | When RAM is cheap |
| Median W=5 | 3x | 20B | sort | Impulse noise (not continuous) |
| Butterworth 4-pole | 10x | ~64B | 9 multiplies | When you have FPU or DSP |
| Clamp + EWMA | 6x | 4B | clamp + 1 multiply | When spikes are outliers |

Selection rules:
- No hardware multiply → shift-only EWMA
- RAM < 20 bytes → EWMA Q16 (12B)
- Need best sigma → Butterworth (but heavy) or EWMA Q16 (best bang/buck)
- Impulse/spike noise → add median pre-filter, then EWMA

## MCU Integration Patterns

### Pattern 1: ADC interrupt (recommended)
```c
void ADC_IRQHandler(void) {
    int32_t raw = (int32_t)ADC_DR;
    g_filtered = ewma_update(&g_filter, raw);  // ~30 cycles
    g_new_flag = 1;
}
```

### Pattern 2: DMA double-buffer
```c
void DMA_HalfTC_IRQHandler(void) {
    for (int i = 0; i < BUF_SIZE/2; i++)
        g_filtered = ewma_update(&g_filter, dma_buf[i]);
}
```

### Pattern 3: Main loop polling
```c
while(1) {
    while (!(ADC_SR & EOC));
    g_filtered = ewma_update(&g_filter, ADC_DR);
}
```

## Code Review Checklist for Embedded Filters

When reviewing embedded filter code, check systematically:

### Arithmetic Safety
- [ ] int64 used for all intermediate products (int32 × int32 can overflow)
- [ ] Right-shift on signed values: is it arithmetic or logical? (implementation-defined)
- [ ] Left-shift overflow: `val << 16` overflows int32 if |val| > 32767
- [ ] Baseline/runtime calibration: does the state remap correctly?
- [ ] Q-format alpha quantization error: e.g. 6554/65536 = 0.100006 (0.006% off from 0.1)

### Correctness
- [ ] Initialization: is output initialized to baseline (not 0)?
- [ ] Reset: does reset set state to baseline-domain zero?
- [ ] Alpha bounds: clamped to [1, 65535]? (alpha=0 freezes, alpha=65536 passes through)
- [ ] Convergence time: is it acceptable for the application? (tau = 1/alpha samples, 95% at 3*tau)

### MCU-specific
- [ ] All types from `<stdint.h>` — no implicit int/short
- [ ] No dynamic allocation (malloc/new)
- [ ] No floating point (unless FPU is confirmed)
- [ ] Volatile for hardware registers and ISR-shared variables
- [ ] DMA buffer types match ADC data width (uint16_t for 12-bit ADC, not int32_t)
- [ ] Include guards and self-contained headers

### Python verification
- [ ] Simulate C code exactly (int32 truncation, right-shift behavior)
- [ ] Compare float vs fixed with SAME alpha quantization (not exact 0.1 vs 6554/65536)
- [ ] Test boundary values: max ADC, min ADC, zero deviation, rapid transitions

## Template Files
- `templates/ewma_q16.h` — Verified single-header EWMA Q16 implementation. Copy and adapt for new projects.

## Cortex-M4F / M7 FPU Optimization (float32)

When the target MCU has a hardware FPU (Cortex-M4F, M7), float32 is often BETTER than Q16:

### Why float32 wins on M4F
| Dimension | Q16 fixed-point | float32 (M4F) |
|-----------|-----------------|---------------|
| Instructions | 4 integer (SUB+MUL+SAR+ADD) | 4 FPU (VSUB+VSUB+VFMA+VADD) |
| Cycles | ~4 | ~5 |
| RAM | 4 bytes (int32) | 12 bytes (3x float) |
| Precision | 16-bit fractional (ULP=0.000015) | 23-bit mantissa (ULP≈0.0007@6000) |
| vs double max error | 2284 | 0.0001 |
| Code complexity | Q16 scaling, overflow checks | Direct formula |

float32 is 22,000,000x more precise than Q16 for this use case.

### FMA (Fused Multiply-Add) is the key
M4F has VFMA.F32: `y = alpha * diff + y` in 1 cycle with 1 rounding (not 2).
This means the EWMA recurrence compiles to exactly 4 FPU instructions.

```c
// Cortex-M4F optimized EWMA (deviation domain + FMA)
static inline float ewma_update(ewma_filter_t *f, float x_raw) {
    float dev = x_raw - f->baseline;
    f->y = __fmaf(f->alpha, dev - f->y, f->y);  // 1 FMA instruction
    return f->y + f->baseline;
}
// Compiles to: VSUB + VSUB + VFMA + VADD = 4 FPU cycles
```

### When Q16 STILL wins on M4F (5 scenarios)
1. **DMA zero-copy pipeline**: DMA→Q16 filter→DMA/DAC, no int↔float conversion overhead
2. **CMSIS-DSP SIMD**: __SMLAD processes two Q15 multiply-accumulates in 1 cycle (2x float throughput)
3. **Interrupt-heavy systems**: Float ISR saves S0-S31 (128 bytes stack), integer saves R0-R3 (32 bytes). 5-level nesting: Q16=160B vs float=800B stack
4. **PID control chains**: ADC(Q16)→Q16 filter→Q16 PID→PWM, zero float conversion in the loop
5. **FPU contention**: Heavy float tasks (FFT/Kalman) monopolize FPU; low-priority Q16 filters run on integer core with zero resource conflict

### Deviation-domain is MANDATORY for float32 too
IEEE 754 float32 has 23-bit mantissa ≈ 7 decimal digits.
Value 8,484,000 needs 23 bits → ULP ≈ 1.0 at that magnitude.
Deviation domain (±6000) → ULP ≈ 0.0007, precision improves 1400x.

```c
// WRONG: direct domain — ULP@8484000 = 1.0, ±1 error per sample
f->y = __fmaf(alpha, x_raw - f->y, f->y);

// RIGHT: deviation domain — ULP@6000 = 0.0007, ±0.0001 error
float dev = x_raw - f->baseline;  // now working with ±6000
f->y = __fmaf(alpha, dev - f->y, f->y);
```

### Adaptive alpha (M4F, branchless-ish)
```c
float ewma_adaptive_update(ewma_filter_t *f, float x_raw,
                           float alpha_max, float alpha_min, float threshold) {
    float dev   = x_raw - f->baseline;
    float diff  = dev - f->y;
    float error = fabsf(diff);              // VABS: 1 cycle
    float ratio = error / threshold;        // VDIV: ~14 cycles
    if (ratio > 1.0f) ratio = 1.0f;        // branch — use fminf() for true branchless
    float alpha = __fmaf(ratio, alpha_max - alpha_min, alpha_min);  // VFMA: 1 cycle
    f->y = __fmaf(alpha, diff, f->y);       // VFMA: 1 cycle
    return f->y + f->baseline;
    // Total: ~20 cycles (VDIV dominates)
}
```

Optimization: precompute `inv_threshold = 1.0f / threshold` at init, replace VDIV with VMUL (saves 13 cycles).

### Multi-channel float pipeline unrolling
M4F can overlap independent VFMA instructions in its pipeline. Unroll 4 channels:
```c
m->y[0] = __fmaf(alpha, dev0 - m->y[0], m->y[0]);
m->y[1] = __fmaf(alpha, dev1 - m->y[1], m->y[1]);  // overlaps with y[0]
m->y[2] = __fmaf(alpha, dev2 - m->y[2], m->y[2]);  // overlaps with y[1]
m->y[3] = __fmaf(alpha, dev3 - m->y[3], m->y[3]);  // overlaps with y[2]
// 4 channels in ~5 cycles (vs 20 cycles sequential)
```

## Spectral Leakage Diagnosis for ADC Signals

When doing FFT on ADC data, "leakage" may not be what you think. Follow this diagnostic pipeline:

### Step 1: Check if main frequency is integer cycle
```python
cycles_in_window = total_time * peak_freq  # e.g. 5.0s * 7.0Hz = 35.0
is_integer = abs(cycles_in_window - round(cycles_in_window)) < 0.05
```
If integer → main tone should NOT leak. If non-integer → classic windowing leakage.

### Step 2: Quantify sidelobe energy ratio
```python
# Energy outside main-lobe (±3 bins) / total energy
main_lobe_mask = ...  # exclude peak ± 3 bins
leakage_ratio = sum(amp[main_lobe_mask]**2) / sum(amp[1:]**2) * 100
# >5% = significant leakage
```

### Step 3: Distinguish broadband vs narrowband
Build a simulated single-tone + white noise signal with same peak amplitude. Compare leakage ratios:
- Real leakage >> Simulated → **broadband signal** (many real frequency components)
- Real leakage ≈ Simulated → **narrowband + windowing leakage**

### Step 3b: Sinc direction diagnostic (definitive for asymmetric neighbors)
When main peak has asymmetric neighbors, determine if it's leakage or real components:
```python
# Simulate signal at f0 + small positive offset
# Sinc leakage makes the neighbor CLOSER to (f0+offset) HEAVIER
# If actual data has the OPPOSITE side heavier → real component, not leakage
left_amp, right_amp = amp[left_neighbor], amp[right_neighbor]
# If left > right but sinc-offset would predict right > left → real component at left_freq
```

### Step 4: Energy distribution analysis
```python
# Count bins with >10% of peak amplitude
significant_bins = sum(amp[1:] > max(amp[1:]) * 0.1)
spread_pct = significant_bins / (N//2) * 100
# >30% = broadband, windowing won't help much
```

### Solutions ranked by effectiveness

| Problem | Solution | Effectiveness |
|---------|----------|---------------|
| Non-integer cycle (classic leakage) | Hanning/Blackman window | High |
| Broadband signal (many freq components) | Increase N (better resolution) | High |
| Broadband + need quick analysis | Bandpass filter before FFT | High |
| Broadband + limited data | Welch PSD estimation (segmented averaging) | Medium |
| Any leakage | Zero-padding | None (only interpolates, doesn't reduce leakage) |
| Broadband | Windowing alone | Low-Moderate (changes sidelobe shape, not total energy; WORSENS for multi-peak signals) |
| Multi-peak signal | Keep rectangular window | High (rectangular is optimal for discrete peaks) |

**Key insight**: Windowing only suppresses sidelobes of each spectral peak. If the signal genuinely has energy spread across many frequencies (broadband), windowing cannot reduce the total energy spread — it just redistributes it. For multi-peak signals, windowing WORSENS results by widening each peak's main lobe into neighbors.

### Real case: 100-point ADC at fs=20Hz (corrected values)
- Main freq 7.0Hz = 35.0 integer cycles → should not leak from the main tone
- Sidelobe energy ratio = 61.3% (>5% threshold — looks severe)
- But pure 7Hz aligned simulation gives 0.00% sidelobe (perfect alignment = zero leakage)
- Signal contains 15 discrete frequency peaks, not continuous broadband
- Energy concentrated in 6-10Hz band (88.5% of total)
- Windowing WORSENS results (61.3% → 76.0% with Hanning)

### Sinc Leakage Direction Diagnostic (definitive test)
When a peak has asymmetric neighbors, use this to distinguish leakage from real components:

```python
# Simulate signal at f0+delta (small offset)
# Sinc leakage makes the neighbor CLOSER to (f0+delta) heavier
# Real components can make EITHER side heavier

# Example: main peak at 7.0Hz, left neighbor 6.8Hz, right neighbor 7.2Hz
# If signal is actually at 7.05Hz → sinc makes 7.2Hz heavier (right > left)
# If real 6.8Hz component exists → 6.8Hz heavier (left > right)
# Actual data: 6.8Hz=995, 7.2Hz=361, left/right=2.76 → REAL component at 6.8Hz
```

Rule: If the heavier side is OPPOSITE to what sinc offset would produce, there are real frequency components — not leakage.

### Observation Window Asymmetry
Energy asymmetry depends on the analysis window:
- ±1.5Hz (5.5~8.5Hz): left/right = 2.09:1 (asymmetric — real components near main peak)
- ±3.0Hz (4.0~10.0Hz): left/right = 1.00:1 (symmetric — distant components balance out)
Both numbers are real. The narrower window isolates the immediate neighborhood where discrete peaks create asymmetry; the wider window averages it out.

## Agent vs Pure Coding Tools for Embedded

What agent does WELL (equal or better than IDE):
- Algorithm design and mathematical analysis (EWMA frequency domain, Q16 overflow math)
- C code generation (correct syntax, complete structure, good comments)
- Data analysis and visualization (Python scripts, comparison charts)
- Code review (finding bugs, static logic analysis, cross-file consistency)
- Multi-algorithm comparison and architecture decisions

What agent CANNOT do (IDE/debugger wins):
- Compile verification (no arm-none-eabi-gcc locally)
- Hardware debugging (no JTAG/SWD, no register inspection)
- Register-level precision (may hallucinate addresses — always verify against datasheet)
- Real-time timing proof (needs oscilloscope/cycle counter on actual hardware)
- Flash/RAM size (needs actual .map file)

Best workflow: agent designs + generates + reviews → human compiles + flashes + debugs.

## Code Review Pitfalls (from real project audits)

Watch for these patterns when reviewing embedded filter projects:
1. **Two code versions concatenated in one file** — old Q16 + new float, duplicate main(), duplicate globals. Split into separate files.
2. **Misleading SIMD comments** — code comments claim __SMLAD but implementation uses float VFMA. Fix the comments.
3. **Unused precomputed fields** — `inv_alpha` computed but never read. Delete or use it.
4. **"No branches" claim with actual if-statement** — use fminf/fmaxf for true branchless.
5. **Test data incomplete** — test array has 10 values but comment says "import from xlsx". Fill it or mark TODO.
6. **LOG output commented out** — tests run silently with no verification output. Uncomment or add assertions.
7. **Hardcoded absolute paths** — Python scripts with /Users/xxx/Desktop/... break on other machines.
8. **DMA buffer type mismatch** — `int32_t` for 12-bit ADC (should be uint16_t).

## Python Environment Note (macOS)

For data analysis scripts: homebrew Python3 at `/opt/homebrew/bin/python3` has pandas/numpy/scipy. Hermes venv may not have them. Use:
```bash
export PATH="/opt/homebrew/bin:$PATH" && python3 script.py
```
