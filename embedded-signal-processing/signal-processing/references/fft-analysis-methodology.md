# FFT Analysis Methodology — Verification-First Approach

## Core Principle

Every numerical claim must be verified with code before reporting. No exceptions.

## Step-by-Step FFT Analysis Template

```python
import numpy as np

# 1. Load data
signal = np.array([...])  # ADC raw values
N = len(signal)
fs = 20.0  # sampling rate
df = fs / N  # frequency resolution
print(f"N={N}, fs={fs}Hz, df={df:.4f}Hz")

# 2. Remove DC and compute FFT
signal_centered = signal - signal.mean()
fft_vals = np.fft.rfft(signal_centered)
freqs = np.fft.rfftfreq(N, 1/fs)
magnitude = np.abs(fft_vals) / (N/2)

# 3. Find main frequency
main_idx = np.argmax(magnitude)
main_freq = freqs[main_idx]
main_mag = magnitude[main_idx]
print(f"Main: {main_freq:.2f} Hz, mag={main_mag:.4f}")

# 4. Side-lobe energy ratio (POWER-based, not amplitude)
total_power = np.sum(magnitude**2)
main_power = main_mag**2
sll = (total_power - main_power) / total_power
print(f"Side-lobe energy ratio: {sll*100:.1f}%")

# 5. Asymmetry analysis (two ranges)
# Narrow: ±7 bins around main
left_n = np.sum(magnitude[max(0,main_idx-7):main_idx]**2)
right_n = np.sum(magnitude[main_idx+1:main_idx+8]**2)
print(f"Narrow asymmetry: {left_n/right_n:.2f}:1" if right_n > 0 else "N/A")

# Wide: ±15 bins
left_w = np.sum(magnitude[max(0,main_idx-15):main_idx]**2)
right_w = np.sum(magnitude[main_idx+1:main_idx+16]**2)
print(f"Wide asymmetry: {left_w/right_w:.2f}:1" if right_w > 0 else "N/A")

# 6. Peak counting
threshold_5pct = 0.05 * magnitude.max()
peaks = np.where(magnitude > threshold_5pct)[0]
print(f"Peaks >5%: {len(peaks)}")
for idx in peaks:
    print(f"  {freqs[idx]:.2f} Hz: {magnitude[idx]:.4f} ({magnitude[idx]/magnitude.max()*100:.1f}%)")

# 7. Window comparison (A/B test)
for win_name, win_func in [("Rectangular", np.ones(N)), ("Hanning", np.hanning(N)), ("Blackman", np.blackman(N))]:
    fft_w = np.fft.rfft(signal_centered * win_func)
    mag_w = np.abs(fft_w) / (N/2)
    tp = np.sum(mag_w**2)
    mp = mag_w[np.argmax(mag_w)]**2
    sl = (tp - mp) / tp
    print(f"{win_name}: sidelobe={sl*100:.1f}%")

# 8. Synthetic comparison
np.random.seed(42)
synth = main_mag * np.sin(2*np.pi*main_freq*np.arange(N)/fs) + np.random.normal(0, signal_centered.std()*0.1, N)
fft_synth = np.fft.rfft(synth)
mag_synth = np.abs(fft_synth) / (N/2)
tp_s = np.sum(mag_synth**2)
mp_s = mag_synth[np.argmax(mag_synth)]**2
sl_s = (tp_s - mp_s) / tp_s
print(f"Synthetic sidelobe: {sl_s*100:.1f}% (real: {sll*100:.1f}%)")
print(f"Ratio real/synthetic: {sll/sl_s:.1f}x → {'real components' if sll/sl_s > 3 else 'likely leakage' if sll/sl_s > 1.5 else 'noise'}")
```

## Key Metrics to Always Report

| Metric | Formula | Meaning |
|--------|---------|---------|
| Side-lobe energy ratio | (total_power - main_power) / total_power | Lower = cleaner spectrum |
| Asymmetry ratio | left_power / right_power | >1 = left-heavy (real components), <1 = right-heavy (leakage offset) |
| Peak count (>5%) | count of bins with mag > 5% of max | More peaks = more frequency components |
| Real/synthetic ratio | real_sidelobe / synthetic_sidelobe | >3x strongly suggests real components |

## Common Mistakes

1. Reporting sidelobe RATIO as a percentage of amplitude instead of power
2. Using ±3Hz window for asymmetry (dilutes the signal, makes it appear symmetric)
3. Claiming "12 peaks" without specifying the threshold (5%? 1%? varies widely)
4. Forgetting to check if main frequency aligns with bin (integer multiple of df)
5. Adding window function to multi-frequency signal (broadens main lobes, worsens results)
