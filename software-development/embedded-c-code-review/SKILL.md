---
name: embedded-c-code-review
description: "Embedded C code review methodology — compile-first validation, integer overflow analysis, float32 precision verification, real-data testing for MCU projects."
triggers:
  - "review embedded C code"
  - "MCU code audit"
  - "ARM code review"
  - "check C code for MCU"
  - "EWMA code review"
  - "signal processing code review"
  - "Q16 fixed-point review"
  - "float32 precision check"
---

# Embedded C Code Review

Systematic methodology for reviewing embedded C code targeting ARM Cortex-M (M0/M3/M4/M7) and similar MCUs.

## Review Pipeline (in order)

### Phase 1: Compilation Gate
Always compile before reading. A file that can't compile is immediately broken.

```
# Host compilation (syntax + logic check)
gcc -O2 -Wall -Wextra -Werror -fsyntax-only file.c

# If header dependencies exist
gcc -O2 -Wall -Wextra -c file.c -I.

# Cross-compilation (if toolchain available)
arm-none-eabi-gcc -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -O2 -fsyntax-only file.c
```

Check for:
- Duplicate symbols (two main() functions, redefined globals)
- Undefined macros (EWMA_BASELINE, EWMA_ALPHA_Q16 — old API names in new code)
- Type conflicts (float vs int32_t function signature mismatch)
- Macro redefinition (DMA_BUF_SIZE defined twice with different values)

### Phase 2: Static Analysis
- `%lu` for `uint32_t` — use `PRIu32` or `%u` (platform-dependent size)
- `volatile` correctness for ISR-shared variables
- Missing `static` on file-scope variables
- Unused variables/parameters

### Phase 3: Integer Overflow Analysis (CRITICAL for Q16/fixed-point)

**The #1 hidden bug in fixed-point embedded code: int32 overflow in multiplication.**

For Q16 fixed-point: `diff_q16 * alpha_q16` can overflow int32 even when both operands fit in int32.

Example with real ADC data (range 8478111~8489946, baseline 8484000):
```
diff_q16 max = 6000 * 65536 = 393,216,000
alpha_q16 = 6553 (0.1 in Q16)
product = 393,216,000 * 6553 = 2,576,744,448,000
int32 max = 2,147,483,647
overflow ratio = 1200x
```

**How to check:**
```python
# Python script to verify overflow with real data
def check_overflow(data, alpha_q16, baseline):
    for x in data:
        dev = x - baseline
        diff_q16 = dev << 16
        product = diff_q16 * alpha_q16
        if abs(product) > 2**31 - 1:
            print(f"OVERFLOW: x={x}, product={product}")
```

**Overflow consequences on MCU:**
- int32 wraps around → filter output stuck near baseline
- std looks artificially small (1.90 vs real 138.18)
- max_err can reach 700+ ADC LSB
- Filter completely fails to track signal

**Fix:** Use float32 on M4F (1-cycle multiply, no overflow risk), or Q31 on M4 (64-bit intermediate via SMLAL).

### Phase 4: Float32 Precision Verification

For Cortex-M4F with hardware FPU:

**ULP (Units in Last Place) analysis:**
```python
import numpy as np
for val in [100.0, 1000.0, 6000.0, 8484000.0]:
    f = np.float32(val)
    next_f = np.nextafter(f, np.float32(np.inf))
    ulp = float(next_f) - float(f)
    print(f"@ {val}: ULP = {ulp}")
```

**Key insight: deviation domain vs direct domain**
- Direct domain: work with raw values (8484000) → ULP@8484000 = 1.0
- Deviation domain: work with (x - baseline) → ULP@6000 = 0.0005
- Precision improvement: 2000x

**Always verify with real data, not synthetic:**
```python
# WRONG: synthetic test with small values
test_data = [100, 200, 150, 180]  # Doesn't trigger real-world issues

# RIGHT: actual ADC data from Excel/scope
df = pd.read_excel('actual_adc_data.xlsx')
data = df.iloc[:, 2].dropna().tolist()
```

### Phase 5: Test Execution
- Run all test files, count pass/fail
- Check for tests that "pass" but test the wrong thing (e.g., Q16 with Python big ints vs MCU int32)
- Verify test data matches real data distribution

## Common Pitfalls

1. **Code concatenation bugs**: Two versions of same file pasted together (two main(), duplicate globals). Always check file length and search for duplicate function definitions.

2. **Q16 overflow with real data**: Synthetic test data with small values won't trigger. Always test with actual ADC data (typically ±6000 from baseline).

3. **Format string portability**: `%lu` is for `unsigned long`, not `uint32_t`. Use `PRIu32` from `<inttypes.h>`.

4. **"No branch" claims**: `if (ratio > 1.0f) ratio = 1.0f;` is a branch. Use `fminf(ratio, 1.0f)` for branchless code on M4.

5. **Object file in repo**: `.o` files are build artifacts. Check `file ewma_filter.o` to verify target architecture matches intended MCU.

6. **Hardcoded absolute paths in Python**: `INPUT_FILE = '/Users/...'` breaks on other machines. Use `os.path.dirname(__file__)` or argparse.

## M4F-Specific Review Points

- FPU enable: CPACR register (0xE000ED88) bits [23:20] must be 0xF
- FMA: `__fmaf(a,b,c)` = a*b+c in 1 cycle, 1 rounding (vs 2 rounding for separate multiply+add)
- VDIV: 2~14 cycles (iterative), avoid in hot ISR path
- Lazy stacking: FPU context only saved if ISR uses FPU (saves stack space)
- DWT cycle counter: SCB_DEMCR bit 24 + DWT_CTRL bit 0 for precise timing

## Related Reference Files

- `references/q16-overflow-analysis.md` — Q16 fixed-point overflow with real ADC data
- `references/lvgl-macos-simulator-pitfalls.md` — LVGL v9 SDL2 simulator on macOS: C23 compiler, GPU bugs, color depth

## Output Format

Review report should include:
1. File inventory (count, sizes, types)
2. Compilation result (errors first, then warnings)
3. Bug list with severity (致命/严重/中等/低)
4. Real-data validation results (std, max_err, mean_err)
5. Optimization suggestions (prioritized)
