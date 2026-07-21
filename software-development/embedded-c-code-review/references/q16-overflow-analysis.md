# Q16 Fixed-Point Overflow Analysis with Real ADC Data

## The Bug

Q16 fixed-point EWMA filter on Cortex-M4 (int32_t) overflows when ADC deviation exceeds ±32 from baseline.

## Root Cause

```
diff_q16 = deviation * 65536    // e.g., 6000 * 65536 = 393,216,000
product  = diff_q16 * alpha_q16  // e.g., 393,216,000 * 6553 = 2,576,744,448,000
int32 max = 2,147,483,647
overflow ratio = 1200x
```

## Real Data Validation

ADC data: 100 points, range 8478111~8489946, baseline 8484000

| Scenario | std | max_err vs double | Behavior |
|----------|-----|-------------------|----------|
| Q16 Python (big int, no overflow) | 138.18 | 0.04 | Correct |
| Q16 int32 (MCU behavior) | 1.90 | 701.55 | BROKEN - stuck near baseline |
| float32 deviation domain (M4F) | 138.18 | 0.50 | Correct |

## Python Verification Script

```python
import struct

def to_int32(v):
    """Simulate int32 wrapping behavior on MCU"""
    v = int(v) & 0xFFFFFFFF
    if v >= 0x80000000:
        v -= 0x100000000
    return v

def ewma_q16_int32(data, alpha_q16, baseline):
    y_q16 = 0
    out = []
    for x in data:
        dev = x - baseline
        dev_q16 = to_int32(dev << 16)
        diff_q16 = to_int32(dev_q16 - y_q16)
        product = to_int32(diff_q16 * alpha_q16)  # OVERFLOW HERE
        y_q16 = to_int32(y_q16 + (product >> 16))
        out.append(float(y_q16) / 65536.0 + float(baseline))
    return out
```

## Why Float32 Avoids This

float32 exponent range: ±3.4×10^38. Max intermediate value in deviation domain: ~6000 × 0.1 = 600. No overflow possible.

ULP@6000 = 0.0005 (23-bit mantissa), vs Q16 ULP@6000 = 0.015 (16-bit). Float32 is 30x more precise in deviation domain.

## Fix Options

1. **Use float32** (recommended for M4F): 1-cycle multiply, no overflow, better precision
2. **Use Q31 with 64-bit intermediate**: `SMLAL` instruction gives 64-bit product, then shift right 31
3. **Use Q16 with clamping**: `__SSAT()` to clamp diff_q16 before multiply (loses signal fidelity)
4. **Reduce deviation range**: If baseline can be adjusted to reduce deviation below ±32, Q16 works
