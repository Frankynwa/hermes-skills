# Spectral Leakage Case Study: 100-point ADC at fs=20Hz

## Signal Parameters
- N=100, fs=20Hz, dt=0.05s, total_time=5.0s
- Frequency resolution: 0.2 Hz
- Nyquist: 10 Hz
- Data: 副本1A_1Ω_100(2)(1).xlsx, column index 2

## FFT Results (no window, raw FFT)
- Peak freq: 7.0000 Hz
- Peak amplitude: 1985.22
- Cycles in window: 35.00 (integer — should NOT leak from main tone)
- Sidelobe energy ratio: 61.3% (>5% threshold — appears severe)
- Pure 7Hz aligned simulation: 0.00% sidelobe (confirmed: zero leakage at perfect alignment)

## Diagnosis: Discrete Frequency Peaks, Not Windowing Leakage

### Key evidence: sinc leakage direction test
- Simulated 7Hz with +0.1Hz offset: 6.8Hz=410, 7.2Hz=1289 → right heavier (sinc expected)
- Actual data: 6.8Hz=995, 7.2Hz=361 → LEFT heavier (opposite direction)
- Conclusion: real frequency component exists near 6.8Hz, not FFT leakage

### Simulation comparison (corrected)
- Simulated pure 7Hz aligned: leakage = 0.00% (perfect alignment = zero leakage)
- Simulated 7Hz + white noise: neighbor bins ~100-130 amplitude (noise floor)
- Actual 6.8Hz amplitude: 995.42 (far above noise floor → real component)

### Signal structure (15 discrete peaks, not continuous broadband)
- 7Hz main peak: ~40% of energy
- 6-8Hz surrounding peaks: ~24% of energy
- Other discrete peaks (3-5Hz, 9-10Hz): ~12% of energy
- White noise background: ~24% of energy

### Energy distribution by band
| Band | Energy % |
|------|----------|
| DC-1Hz | 0.1% |
| 1-2Hz | 0.1% |
| 2-3Hz | 0.5% |
| 3-4Hz | 2.0% |
| 4-5Hz | 2.6% |
| 5-6Hz | 6.4% |
| 6-7Hz | 19.8% |
| 7-8Hz | 44.0% |
| 8-9Hz | 8.9% |
| 9-10Hz | 15.6% |

88.5% of energy in 6-10Hz band. Energy spread across 15 discrete peaks.

### Top peaks (no window, corrected)
1. 7.0 Hz: 1985.22 (main frequency)
2. 6.8 Hz: 995.42 (real component — 2.76x heavier than 7.2Hz, opposite to sinc direction)
3. 9.2 Hz: 766.67
4. 9.8 Hz: 671.72
5. 8.4 Hz: 624.53
6. 5.2 Hz: 555.31
7. 6.2 Hz: 568.41
8. 6.0 Hz: 464.73
9. 8.0 Hz: 439.92
10. 6.4 Hz: 442.93

### Window function comparison

| Window | Peak amp (corrected) | Sidelobe ratio | Effect |
|--------|---------------------|----------------|--------|
| Rectangular (none) | 1985.22 | 61.3% | baseline |
| Hanning | 2400.43 | 76.0% | WORSENED by +14.7% |
| Hamming | 2332.75 | ~73% | WORSENED |
| Blackman | 2531.66 | ~78% | WORSENED |

**Windowing WORSENS this signal** because it spreads each discrete peak into a wider
main lobe. With 15 peaks, the widened lobes overlap and increase total sidelobe energy.
This is the correct behavior for multi-component signals — windowing is designed for
single-tone leakage suppression, not multi-peak separation.

### Neighbor asymmetry (definitive proof of real components)
| Frequency | Amplitude | Direction |
|-----------|-----------|-----------|
| 6.8 Hz (left neighbor) | 995.42 | ← heavier |
| 7.0 Hz (main) | 1985.22 | — |
| 7.2 Hz (right neighbor) | 360.72 | → lighter |
| Left/Right ratio | 2.76:1 | |

If this were sinc leakage from a frequency offset (e.g. 7.05Hz), the RIGHT neighbor
(7.2Hz, closer to 7.05Hz) would be heavier. But the LEFT neighbor is heavier.
This proves a real frequency component exists near 6.8Hz.

### Zero-padding effect (not a fix)
| N (padded) | Main/Side dB | Freq resolution |
|------------|-------------|-----------------|
| 100 | 8.3 dB | 0.2000 Hz |
| 400 | 6.8 dB | 0.0500 Hz |
| 800 | 6.7 dB | 0.0250 Hz |

Zero-padding only interpolates — doesn't reduce leakage energy.

## Conclusion
This ADC signal contains 15 discrete frequency peaks (not continuous broadband noise),
with 88.5% of energy concentrated in 6-10Hz. The "leakage" is actually real frequency
content. The sinc direction diagnostic (left neighbor 2.76x heavier than right, opposite
to what frequency-offset leakage would produce) definitively proves real components exist.

Windowing is counterproductive for multi-peak signals. Solutions:
1. Increase N (100→1000) for better frequency resolution to separate the peaks
2. Bandpass filter (6-8Hz) before FFT to isolate the main peak
3. Welch PSD with more segments (nperseg=50, noverlap=25) for smoother estimation
4. Keep rectangular window (optimal for this signal type)
