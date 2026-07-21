# Sensor/ADC Data Processing from Excel

When user provides ADC readings or sensor data in .xlsx and wants signal processing or filtering applied.

## Workflow Pattern

1. Read raw data with pandas (`pd.read_excel`, `header=None` for messy sensor exports)
2. Identify the data column (usually col 2 or 3, skip header rows with hex/label data)
3. Implement candidate algorithms in Python, compare metrics (σ, max deviation, baseline offset)
4. Generate visualization (matplotlib, 3-panel: overlay, deviation, bar comparison)
5. Output processed .xlsx with color-coded deviation cells
6. If MCU target: generate C code alongside

## MCU-Safe Algorithms (no float, minimal RAM)

### EWMA (Exponential Weighted Moving Average) — RECOMMENDED
- State: 1 int32_t (4 bytes)
- Formula: `y[n] = y[n-1] + (x[n] - y[n-1]) >> shift`
- alpha=1/8 (shift=3) is a good default; alpha=1/16 (shift=4) for heavier smoothing
- No multiplication, no division, just add + arithmetic shift
- Typical suppression: σ reduced 5-6x

### Sliding Average (Window=5)
- State: 5 int32_t ring buffer (20 bytes) + index
- Division by N needed (or use shift-approximate)
- Suppression: σ reduced ~5x

### Delta Clamp (increment limiter)
- State: 1 int32_t (4 bytes)
- Clamp each step's delta to ±max_step
- Prevents sudden spikes, good for burst noise
- Suppression: σ reduced ~4x

## Pitfalls

- `execute_code` sandbox does NOT have pandas/numpy/matplotlib. Always use `terminal` for numerical analysis.
- Sensor .xlsx files often have hex columns mixed with decimal — read with `header=None` and inspect before assuming column layout.
- EWMA with too small alpha (e.g. 0.01) drifts slowly and may never converge on short data (<200 points). Use α=0.1~0.2 for 100-point datasets.
- When generating comparison charts, always include the raw signal as gray background so the suppression effect is visually obvious.
