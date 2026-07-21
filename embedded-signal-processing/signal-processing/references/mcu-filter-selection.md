# Q16 vs Float32 Decision Matrix for ARM Cortex-M

## Quick Decision Tree

```
Does MCU have FPU?
├── No (M0/M0+/M3) → Q16 fixed-point (mandatory)
│   └── Use deviation domain to prevent overflow
└── Yes (M4F/M7) → Check constraints:
    ├── Battery critical? → Q16 (save 20-30% power)
    ├── Deep interrupt nesting (>3 levels)? → Q16 (smaller stack)
    ├── DMA zero-copy pipeline? → Q16 (no type conversion)
    ├── PID control chain? → Q16 (saturation arithmetic)
    ├── FPU contention with higher-priority task? → Q16
    └── None of above? → Float32 (faster, more precise)
```

## Performance Comparison on Cortex-M4F

| Metric | Q16 (deviation domain) | Float32 (deviation domain) |
|--------|----------------------|---------------------------|
| RAM per channel | 12 bytes (int32 state + baseline) | 12 bytes (float state + baseline) |
| Cycles per sample | ~9 (sub + shift + add) | ~3-4 (VMLS.F32 single-cycle) |
| Precision vs double | max_err=2284 LSB | max_err=0.50 LSB |
| Interrupt stack | 32 bytes (R0-R3+R12+LR+PC) | 160 bytes (if FPU used in ISR) |
| Power | Baseline | +20-30% with FPU enabled |

## Q16 Overflow Analysis

For ADC values around 8,484,000 with baseline subtraction:
- Safe range: deviation within ±32767 → alpha_q16 * dev < 2^31
- With deviation domain (baseline 8484000): deviation ≈ ±6000 → safe
- Without deviation domain: raw_diff ≈ ±6000, but alpha * diff ≈ ±393M → still within int32
- HOWEVER: if alpha_q16=6553 and diff=393216, product=2.57 trillion → OVERFLOW

**Rule**: Always use deviation domain for Q16 when baseline > 10000.

## Float32 Precision Analysis

float32 ULP (Unit in the Last Place) at different magnitudes:
- @6000 (deviation domain): ULP ≈ 0.0005 → excellent
- @8484000 (direct domain): ULP ≈ 1.0 → loses sub-LSB precision
- Gain from deviation domain: 2000x precision improvement

## ARM Cortex-M FPU Lazy Stacking

When interrupt uses FPU registers:
- Hardware saves S0-S15 (64 bytes) on first FPU instruction
- S16-S31 (additional 64 bytes) saved only if context switch occurs
- With 5-level nesting using FPU: 5 × 160 = 800 bytes
- With 5-level nesting using Q16 only: 5 × 32 = 160 bytes
- RAM savings: 640 bytes — significant for 16KB RAM MCUs

## CMSIS-DSP SIMD on M4

`__SMLAD` (Signed Multiply Accumulate Dual):
- Processes two Q15 multiply-accumulates in ONE cycle
- 4 Q15 MAC operations per 2 cycles (vs 4 cycles for float32)
- Only works with 16-bit integer data
- ARM CMSIS-DSP library: arm_fir_q15(), arm_biquad_q15()
