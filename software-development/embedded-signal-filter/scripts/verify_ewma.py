#!/usr/bin/env python3
"""
EWMA Q16 fixed-point verification script template.

Simulates the C ewma_update() function in Python (arbitrary precision ints)
to verify: overflow safety, float vs fixed precision, convergence behavior.

Usage: python3 verify_ewma.py [--data path.xlsx] [--col 2] [--baseline 8484000] [--alpha 0.1]
"""

import sys
import argparse

Q_BITS = 16
ONE_Q16 = 1 << Q_BITS


def ewma_c_sim(y_q16: int, x_raw: int, alpha_q16: int, baseline: int) -> tuple:
    """Exact simulation of ewma_update() from ewma_q16.h"""
    dev = int(x_raw - baseline)
    dev_q16 = dev << Q_BITS
    inv = ONE_Q16 - alpha_q16
    result = (alpha_q16 * dev_q16 + inv * y_q16) >> Q_BITS
    # int32 truncation
    result = result & 0xFFFFFFFF
    if result >= 0x80000000:
        result -= 0x100000000
    output = (result >> Q_BITS) + baseline
    return result, output


def check_overflow(max_dev: int, alpha_q16: int):
    """Verify no int32/int64 overflow for given deviation range."""
    dev_q16 = max_dev << Q_BITS
    max_coeff = max(alpha_q16, ONE_Q16 - alpha_q16)
    product = max_coeff * dev_q16
    product_after_shift = product >> Q_BITS

    checks = {
        "dev_q16 fits int64": dev_q16 < (1 << 63),
        "product fits int64": product < (1 << 63),
        "result fits int32": -(1 << 31) <= product_after_shift < (1 << 31),
    }
    for name, ok in checks.items():
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}: {product_after_shift}" if "int32" in name else f"  [{status}] {name}")
    return all(checks.values())


def verify(signal, baseline, alpha, alpha_q16, fs=20.0):
    """Run full verification suite."""
    import numpy as np

    N = len(signal)

    # Float EWMA (using Q16-quantized alpha for fair comparison)
    actual_alpha = alpha_q16 / ONE_Q16
    y_f = float(baseline)
    out_float = []
    for x in signal:
        dev = x - baseline
        y_f = actual_alpha * dev + (1 - actual_alpha) * (y_f - baseline) + baseline
        out_float.append(y_f)

    # Q16 EWMA
    y_q16 = 0
    out_fixed = []
    y_q16_vals = []
    for x in signal:
        y_q16, out = ewma_c_sim(y_q16, int(x), alpha_q16, baseline)
        out_fixed.append(out)
        y_q16_vals.append(y_q16)

    out_f = np.array(out_float)
    out_q = np.array(out_fixed, dtype=float)
    sig = np.array(signal, dtype=float)
    diff = np.abs(out_f - out_q)

    print(f"\n--- Precision ---")
    print(f"  Q16 alpha: {alpha_q16}/{ONE_Q16} = {actual_alpha:.8f} (target {alpha})")
    print(f"  Max error (float vs fixed): {diff.max():.2f}")
    print(f"  Mean error: {diff.mean():.2f}")

    print(f"\n--- Filtering ---")
    print(f"  Raw std:  {sig.std():.1f}")
    print(f"  Q16 std:  {out_q.std():.1f}")
    print(f"  Float std:{out_f.std():.1f}")
    print(f"  Suppression: {sig.std()/out_q.std():.1f}x ({20*np.log10(out_q.std()/sig.std()):.1f} dB)")

    print(f"\n--- Convergence ---")
    tau = 1.0 / actual_alpha
    print(f"  tau = {tau:.0f} samples = {tau/fs:.2f}s")
    print(f"  95% settle = {3*tau:.0f} samples = {3*tau/fs:.2f}s")
    print(f"  Data length = {N} samples ({N/fs:.2f}s)")

    print(f"\n--- y_q16 range ---")
    print(f"  [{min(y_q16_vals)}, {max(y_q16_vals)}]  (int32: [{-(1<<31)}, {(1<<31)-1}])")
    safe = all(-(1<<31) <= v < (1<<31) for v in y_q16_vals)
    print(f"  Overflow safe: {safe}")

    return out_f, out_q


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data.xlsx")
    parser.add_argument("--col", type=int, default=2)
    parser.add_argument("--baseline", type=int, default=8484000)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--alpha-q16", type=int, default=None)
    parser.add_argument("--fs", type=float, default=20.0)
    args = parser.parse_args()

    alpha_q16 = args.alpha_q16 or round(args.alpha * ONE_Q16)

    print(f"Overflow check (max_dev=6000):")
    check_overflow(6000, alpha_q16)

    try:
        import pandas as pd
        df = pd.read_excel(args.data)
        signal = df.iloc[:, args.col].astype(float).values.tolist()
        print(f"\nLoaded {len(signal)} samples from {args.data}")
        verify(signal, args.baseline, args.alpha, alpha_q16, args.fs)
    except FileNotFoundError:
        print(f"\nNo data file. Place xlsx at {args.data} or pass --data path.")
