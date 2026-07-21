# FFT Numerical Verification Reference

## Common Fabrication Patterns in Spectral Analysis

When analyzing FFT results, agents (and humans) commonly fabricate numbers by:
- Estimating percentages from visual plot inspection
- Citing "typical" values from training data
- Reporting numbers that sound reasonable without computation
- Assuming pure aligned signals have sidelobe leakage (they don't)

## Mandatory Verification Checklist

Before reporting ANY spectral analysis number:

1. Load actual data (not from memory, not from plots)
2. Run actual numpy computation
3. Verify pipeline with pure signal simulation
4. Report only computed values with source code

## Pure Signal Verification Template

```python
import numpy as np

# Generate pure aligned signal
t = np.arange(N) / fs
pure = np.sin(2 * np.pi * target_freq * t)
fft_pure = np.fft.rfft(pure)
psd_pure = np.abs(fft_pure) ** 2
total_pure = psd_pure.sum()
main_bin = int(round(target_freq / (fs/N)))
main_pure = psd_pure[main_bin]
sidelobe_pure = total_pure - main_pure

# This MUST be ~0 for aligned signals
sidelobe_pct = sidelobe_pure / total_pure * 100
assert sidelobe_pct < 1.0, f"Sidelobe {sidelobe_pct:.2f}% — check alignment"
```

## Key Rules

- Aligned signals (integer periods in window) have ZERO sidelobe leakage
- Sidelobe ratio = (total_PSD - main_bin_PSD) / total_PSD * 100
- Window functions can WORSEN results for multi-frequency signals
- Energy asymmetry requires bin-by-bin computation, not estimation

## Real-World Errors Caught

| Claim | Actual | Error Source |
|-------|--------|-------------|
| 42.8% sidelobe | 61.3% | Estimated from plot |
| 18.1% pure 7Hz sidelobe | 0.00% | Fabricated — aligned=0 |
| 2.09:1 asymmetry | 1.01:1 | Fabricated without computation |
| Hanning improves sidelobe | Worsens 61%→76% | Wrong assumption |
