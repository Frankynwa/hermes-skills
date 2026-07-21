#!/usr/bin/env python3
"""
EWMA Filter Precision Verification Script
Compares: Q16 int32, float32 deviation domain, float32 direct domain, double reference
Usage: python3 verify_ewma_precision.py <data.xlsx> [--column N] [--baseline N] [--alpha N]
"""

import sys
import os
import numpy as np
import statistics

def ewma_double(data, alpha, baseline):
    y = 0.0
    out = []
    for x in data:
        dev = float(x) - baseline
        diff = dev - y
        y = alpha * diff + y
        out.append(y + baseline)
    return out

def ewma_f32_deviation(data, alpha, baseline):
    y = np.float32(0.0)
    a = np.float32(alpha)
    b = np.float32(baseline)
    out = []
    for x in data:
        dev = np.float32(np.float32(float(x)) - b)
        diff = np.float32(dev - y)
        y = np.float32(np.float32(a * diff) + y)
        out.append(float(np.float32(y + b)))
    return out

def ewma_f32_direct(data, alpha, baseline):
    y = np.float32(baseline)
    a = np.float32(alpha)
    o = np.float32(np.float32(1.0) - a)
    out = []
    for x in data:
        y = np.float32(np.float32(a * np.float32(float(x))) + np.float32(o * y))
        out.append(float(y))
    return out

def to_int32(v):
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
        product = to_int32(diff_q16 * alpha_q16)
        y_q16 = to_int32(y_q16 + (product >> 16))
        out.append(float(y_q16) / 65536.0 + float(baseline))
    return out

def check_overflow(data, alpha_q16, baseline):
    overflow_count = 0
    max_product = 0
    for x in data:
        dev = x - baseline
        diff_q16 = dev << 16
        product = diff_q16 * alpha_q16
        if abs(product) > 2**31 - 1:
            overflow_count += 1
        max_product = max(max_product, abs(product))
    return overflow_count, max_product

def ulp_analysis(values):
    print("\nULP Analysis (IEEE 754 float32):")
    for v in values:
        f = np.float32(v)
        n = np.nextafter(f, np.float32(np.inf))
        ulp = float(n) - float(f)
        print(f"  @ {v:>10.1f}: ULP = {ulp:.6f}")

def report(label, ref, flt, raw_std):
    errs = [abs(a-b) for a,b in zip(ref, flt)]
    std_flt = statistics.stdev(flt)
    print(f"\n{label}:")
    print(f"  std = {std_flt:.2f} (suppress {raw_std/std_flt:.1f}x)")
    print(f"  vs double: max_err = {max(errs):.4f}, mean_err = {statistics.mean(errs):.4f}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='EWMA Filter Precision Verification')
    parser.add_argument('data_file', help='Excel file with ADC data')
    parser.add_argument('--column', type=int, default=2, help='Column index (0-based, default: 2)')
    parser.add_argument('--baseline', type=float, default=8484000.0, help='Baseline value')
    parser.add_argument('--alpha', type=float, default=0.1, help='EWMA alpha')
    args = parser.parse_args()

    import pandas as pd
    df = pd.read_excel(args.data_file, header=None)
    col = df.iloc[:, args.column].dropna()
    data = [int(x) for x in col.tolist()]

    raw_std = statistics.stdev(data)
    raw_mean = statistics.mean(data)
    print(f"Data: {len(data)} points, std={raw_std:.2f}, mean={raw_mean:.2f}")
    print(f"Baseline: {args.baseline}, Alpha: {args.alpha}")

    # Overflow check
    alpha_q16 = int(args.alpha * 65536)
    overflow_count, max_product = check_overflow(data, alpha_q16, int(args.baseline))
    print(f"\nQ16 Overflow Check:")
    print(f"  alpha_q16 = {alpha_q16}")
    print(f"  max product = {max_product:,}")
    print(f"  int32 max = {2**31-1:,}")
    print(f"  overflow ratio = {max_product / (2**31-1):.0f}x")
    print(f"  overflow samples = {overflow_count}/{len(data)}")

    # All schemes
    out_double = ewma_double(data, args.alpha, args.baseline)
    out_f32_dev = ewma_f32_deviation(data, args.alpha, args.baseline)
    out_f32_direct = ewma_f32_direct(data, args.alpha, args.baseline)
    out_q16 = ewma_q16_int32(data, alpha_q16, int(args.baseline))

    print("\n" + "="*60)
    print("Precision Comparison")
    print("="*60)
    report("float32 deviation domain (M4F)", out_double, out_f32_dev, raw_std)
    report("float32 direct domain", out_double, out_f32_direct, raw_std)
    report("Q16 int32 (MCU behavior)", out_double, out_q16, raw_std)

    # ULP
    ulp_analysis([100.0, 1000.0, 6000.0, args.baseline])

if __name__ == '__main__':
    main()
