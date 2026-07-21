# M4F FPU Case Study: EWMA for 1Ω ADC Signal

## Signal Profile
- 100 samples, fs=20Hz (0.05s interval)
- Range: 8,478,111 ~ 8,489,946 (7-digit values)
- Target baseline: 8,484,000
- Std: 2,241.76 (high-frequency noise, period 2-3 samples)
- Mean offset from baseline: +285

## Verified Algorithm Comparison (Python simulation)

| Algorithm | Std | Max deviation from baseline | vs double max err | Suppression |
|-----------|-----|-----------------------------|--------------------|-------------|
| Raw signal | 2241.76 | 5946 | — | 1x |
| Q16 fixed (alpha=0.1) | 748.95 | 2618 | 2284.11 | 3.0x |
| float32 FMA dev-domain (alpha=0.1) | 145.44 | 702.6 | 0.0001 | 15.4x |
| float32 naive dev-domain | 145.44 | 702.6 | 0.0001 | 15.4x |
| float32 direct domain | 145.44 | 702.6 | 2.82 | 15.4x |
| Adaptive alpha (0.05-0.5) | 838.12 | 2831.1 | 2128.43 | 2.7x |

### Key numbers
- float32 FMA vs Q16 precision: 22,840,000x better
- Deviation domain vs direct domain: 28,000x better precision
- FMA vs naive multiply: max diff 0.000099 (negligible at ±6000 deviation)
- Q16 alpha quantization: 6554/65536 = 0.100006 (0.006% off)

### ULP analysis (IEEE 754 float32)
- Direct domain ULP@8,484,000: 1.0
- Deviation domain ULP@6,000: 0.000488
- Precision improvement: ~2,048x

### Convergence times (alpha → tau → 95% settling)
- 0.05 → 20 samples → 60 samples (3.0s)
- 0.10 → 10 samples → 30 samples (1.5s)
- 0.15 → 6.7 samples → 20 samples (1.0s)
- 0.20 → 5.0 samples → 15 samples (0.8s)

## Cycle Budget (M4F @168MHz)

| Operation | Cycles | Notes |
|-----------|--------|-------|
| ewma_update (float32 FMA) | ~5 | VSUB+VSUB+VFMA+VADD |
| ewma_update (Q16) | ~4 | SUB+MUL+SAR+ADD |
| ewma_adaptive_update | ~20 | VDIV (~14) dominates |
| int32→float32 (VCVT) | 1 | |
| fabsf (VABS) | 1 | |
| fminf/fmaxf | 1-2 | Compiler may emit branch anyway |

### M4F FPU instruction reference
- VADD.F32: 1 cycle (pipelined)
- VMUL.F32: 1 cycle (pipelined)
- VFMA.F32: 1 cycle (pipelined) — equivalent to 2 operations
- VSUB.F32: 1 cycle (pipelined)
- VABS.F32: 1 cycle
- VDIV.F32: 2-14 cycles (iterative, NOT pipelined)
- VCVT.S32.F32: 1 cycle (int↔float)

## Adaptive Alpha Optimization
Replace VDIV with precomputed reciprocal:
```c
// At init:
f->inv_threshold = 1.0f / threshold;  // one-time cost

// At update (saves 13 cycles per sample):
float ratio = error * f->inv_threshold;  // VMUL: 1 cycle vs VDIV: 14 cycles
```

## Compilation flags for M4F
```
arm-none-eabi-gcc -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -O2
```
- `-mfloat-abi=hard`: FPU instructions generated, float args in S-registers
- `-mfpu=fpv4-sp-d16`: Single-precision FPU with 16 double-word registers
- `-O2`: Enables FMA instruction selection (may not emit VFMA at -O0)
