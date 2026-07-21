# Real-World Analysis: ADC Signal 8484000 Baseline

## Input Data Characteristics
- File: 100 ADC samples, fs=20Hz (dt=0.05s), 5 seconds total
- Value range: 8478111 ~ 8489946
- Mean: 8484285, Std: 2242, Peak-peak: 11835
- Dominant noise frequency: 7 Hz (period ≈ 2.86 samples)
- Signal is continuous noise (not impulse/spike)

## Verified Results (from actual analysis)

### Algorithm Comparison Table
| Algorithm | Std | Suppression | Max deviation | RAM | Notes |
|-----------|-----|-------------|---------------|-----|-------|
| Raw | 2242 | 1x | 5946 | 0 | — |
| EWMA Q16 α=0.1 | 137.5 | 16.3x | 704 | 12B | Best tradeoff |
| Butterworth 4-pole | 213.9 | 10.5x | 1592 | ~64B | filtfilt (offline only) |
| Moving Avg W=5 | ~452 | ~5x | — | 20B | — |
| Moving Avg W=10 | ~317 | ~7x | — | 40B | — |
| Shift-only (>>3) | ~358 | ~6.3x | — | 4B | No multiply needed |
| Clamp(500) + EWMA | ~361 | ~6.2x | — | 4B | — |

### Key Finding: EWMA outperformed Butterworth
- EWMA Q16 std=137.5 < Butterworth std=213.9
- EWMA used 12B RAM vs Butterworth's ~64B
- Butterworth required offline filtfilt (not causal); EWMA is real-time
- This was surprising — expected Butterworth (4th order) to be better

### Q16 Precision Verification
- alpha quantization: 6554/65536 = 0.100006 (error 0.006%)
- Float vs fixed max error: 0.96 (< 1 ADC LSB)
- y_q16 range: [-2105419, 46146521] — safe within int32
- Overflow: max product 350M < int32 limit 2.1G (16.6% margin)

### Bugs Found in Review
1. [SEVERE] `ewma_set_baseline()`: baseline_diff << 16 can overflow int32 if diff > 32767
2. [MEDIUM] Missing `<stdint.h>` include in main_example.c
3. [MEDIUM] DMA buffer type should be uint16_t (not int32_t) for 12-bit ADC
4. [LOW] Negative right-shift is implementation-defined in C (ARM GCC is safe)
5. [LOW] Hardcoded absolute paths in Python scripts

### Convergence Profile (alpha=0.1)
- tau = 10 samples = 0.5s
- 95% settle = 30 samples = 1.5s (30% of total dataset)
- If too slow for startup: use adaptive alpha (0.3 first 50 samples, then 0.1)
