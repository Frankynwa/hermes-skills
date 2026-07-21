---
name: signal-processing
description: "ADC/DSP signal processing — FFT analysis, filter design (EWMA/IIR/FIR), window function selection, spectrum leakage diagnosis, embedded MCU implementation. Triggers on: FFT, spectrum, ADC, filter design, EWMA, frequency analysis, signal noise, DSP."
---

# Signal Processing — ADC/DSP Analysis & Filter Design

## When to Load

- User asks about FFT, spectrum analysis, frequency domain analysis
- ADC signal noise filtering or baseline suppression
- Filter design (EWMA, Butterworth, moving average, IIR/FIR)
- Window function selection for FFT
- Embedded MCU signal processing implementation
- Comparing filter algorithms for performance/resource tradeoffs

## Core Workflow

### 1. Data Ingestion

- Excel (.xlsx): use openpyxl to read hex/decimal ADC values
- CSV: numpy.loadtxt or pandas.read_csv
- Always verify: N points, fs (sampling rate), value range, data format (hex vs dec)

### 2. FFT Spectrum Analysis

```python
import numpy as np

N = len(signal)
fs = 20.0  # sampling rate in Hz
df = fs / N  # frequency resolution

signal_centered = signal - signal.mean()  # remove DC
fft_vals = np.fft.rfft(signal_centered)
freqs = np.fft.rfftfreq(N, 1/fs)
magnitude = np.abs(fft_vals) / (N/2)
```

**Frequency resolution**: df = fs / N. Zero-padding interpolates the frequency grid but does NOT improve actual resolution.

### 3. Window Function Selection

**CRITICAL RULE for multi-frequency signals**: Do NOT add window functions.

| Signal Type | Window | Why |
|-------------|--------|-----|
| Single frequency, exact integer periods | Rectangular (none) | Zero leakage when aligned |
| Single frequency, non-integer periods | Hanning/Blackman | Reduces sidelobes |
| Multiple discrete frequencies | Rectangular (none) | Window broadens main lobes, causing inter-frequency interference |
| Broadband noise | Hanning | Standard practice |

**Verification method**: Compare side-lobe energy ratio with and without window. If windowing WORSENS the ratio, do not use it.

For the specific ADC project: Hanning worsened sidelobes by +14.7pp, Blackman by +18.1pp. Rectangular was optimal.

### 4. Spectral Leakage Diagnosis

Leakage vs real frequency components — how to distinguish:

**Step 1**: Check if main frequency aligns with FFT bin.
- If freq_main = k * df (exact integer multiple), leakage is theoretically zero.
- Example: 7.0 Hz, df=0.2Hz, k=35 → exact alignment, zero leakage.

**Step 2**: Check asymmetry of adjacent bins.
- Pure leakage from frequency offset → sinc function → RIGHT-heavy (signal closer to right neighbor)
- Real discrete component at lower frequency → LEFT-heavy
- If left/right ratio is reversed from sinc prediction → real components exist

**Step 3**: Compare with synthetic signal.
- Generate pure tone at same frequency, same N, same noise level
- Measure sidelobe ratio on synthetic vs real data
- If real >> synthetic → signal contains multiple frequency components

**Step 4**: Count significant peaks.
- Single frequency: 1 dominant peak + symmetric sidelobes
- Multiple frequencies: multiple peaks with irregular magnitudes

### 5. EWMA Filter Design

**Deviation domain** (recommended for large baseline values):
```
dev = adc_raw - baseline
y_prev += alpha * (dev - y_prev)
output = y_prev + baseline
```
Benefits: float32 ULP@6000 ≈ 0.0005, vs ULP@8484000 ≈ 1.0 (1400x precision gain).

**Alpha selection**:
- alpha = 0.1: good balance, std reduction ~6x
- alpha = 0.15: slightly faster tracking, std reduction ~6.2x
- alpha = 1/8 (shift=3): MCU-friendly power-of-2, no multiply needed

**Cutoff frequency**: fc = fs * alpha / (2 * pi * (1 - alpha))

### 6. Q16 Fixed-Point vs Float32 Selection

| Criterion | Q16 Fixed-Point | Float32 |
|-----------|----------------|---------|
| MCU without FPU (M0/M0+/M3) | Required, 10x faster | Avoid, software emulation ~70 cycles |
| MCU with FPU (M4F/M7) | Only for specific scenarios | Default choice |
| RAM | 4 bytes (int32) | 4 bytes (float) |
| Cycles (M4F) | 9 instructions | 3-4 instructions |
| Precision | 16 fractional bits | 23-bit mantissa |

**M4F scenarios where Q16 is still better**:
1. DMA zero-copy pipelines (no type conversion overhead)
2. CMSIS-DSP SIMD (__SMLAD processes two Q15 multiply-accumulates per cycle)
3. Deep interrupt nesting (FPU lazy stacking adds 64-128 bytes per nest level)
4. PID control chains (saturation arithmetic, integer-native)
5. Battery-critical low-power (FPU adds 20-30% power)
6. FPU contention with higher-priority float tasks

**Q16 overflow warning**: For ADC values in 8M range, raw_diff * alpha_q16 overflows int32. MUST use deviation domain.

### 7. Zero-Padding

Zero-padding increases frequency GRID density but NOT actual resolution.
- N=100, fs=20: df=0.2Hz, 51 bins
- N=256, fs=20: df=0.078Hz, 129 bins (grid interpolation only)
- N=512, fs=20: df=0.039Hz, 257 bins

Actual resolution is always limited by observation window T = N/fs = 5s → df = 1/T = 0.2Hz.

## Pitfalls

1. **Reporting numbers from memory**: ALWAYS use execute_code to compute and verify every numerical claim before reporting. Never quote a sidelobe ratio, asymmetry ratio, or frequency peak count without running the code first.

2. **Claiming zero leakage without verification**: Even when frequency aligns with bin, noise can create apparent sidelobes. Always compare with synthetic pure-tone signal at same SNR.

3. **Using wrong energy calculation**: Power = magnitude^2, not magnitude. Asymmetry ratios must use power, not amplitude.

4. **Hex ADC data**: Some ADC data files store raw hex values (e.g., "84A12F"). Must convert with int(hex_str, 16) before analysis.

5. **Q16 multiplication overflow**: alpha_q16 * diff_q16 can exceed int32 range for large ADC values. Always check: max_diff * alpha < 2^31.

6. **Window function for multi-frequency signals**: Adding Hanning/Blackman broadens main lobes of each frequency component, causing adjacent frequencies to interfere. Verify by comparing sidelobe energy with and without window.

## Verification Checklist

Before reporting FFT analysis results:
- [ ] Run FFT on actual data, not synthetic data
- [ ] Report sidelobe energy ratio (power-based, not amplitude)
- [ ] Compare with at least one synthetic pure-tone signal
- [ ] Verify window function impact by A/B test
- [ ] Check frequency alignment (integer bin multiple or not)
- [ ] Count peaks at defined threshold (>5% of max)
- [ ] Run asymmetry analysis on narrow and wide ranges

## References

- `references/fft-analysis-methodology.md` — Detailed FFT verification methodology with Python code templates
- `references/mcu-filter-selection.md` — Q16 vs float32 decision matrix for ARM Cortex-M platforms
- `references/ewma-design-notes.md` — EWMA parameter selection, deviation domain math, adaptive alpha design
