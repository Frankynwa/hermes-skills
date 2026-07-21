# A-Share Empirical Factor IC Findings

Source: AlphaSeeker backtest on 4869 A-shares, 2024-12 financial data, 6-month forward returns (2025-02 to 2025-07).

## Factor IC Summary

| Dimension | Raw Metric | Raw IC | Scored IC | Verdict |
|-----------|-----------|--------|-----------|---------|
| Growth | net_profit_growth | **+0.125** | +0.141 | ✅ Strongest factor |
| Moat | gross_margin | +0.044 | +0.044 | ✅ Moderate |
| Safety | debt_to_equity | -0.050 | +0.036 | ✅ Scoring correctly inverts |
| Profitability | roe | -0.026 | -0.029 | ⚠️ Factor is noise (IC≈0) |
| Cashflow | cash_to_income | -0.027 | -0.024 | ⚠️ Factor is noise |
| Valuation (PE) | pe | **+0.086** | **-0.187** | ❌ Scoring inverts valid signal |
| Valuation (PB) | pb | **+0.198** | **-0.187** | ❌ Scoring inverts valid signal |
| Efficiency | asset_turnover | **-0.112** | -0.093 | ❌ Factor is reverse |
| Shareholder | dividend_yield | **-0.167** | NaN | ❌ Scoring not connected |

## A-Share PE/PB: Growth Premium, Not Value

In this 2024-12 → 2025-07 period, PE/PB showed **positive** correlation with returns (opposite to Western value investing). However, this is **period-specific** — do NOT reverse scoring direction based on this finding. The user's value-oriented PE/PB scoring (low PE = cheap = buy) is a valid investment thesis that may work in other regimes.

### PE Quintile Returns (6M holding)
| Quintile | PE Range | Mean Return | Interpretation |
|----------|----------|-------------|----------------|
| Q1 (lowest) | PE < 0 (loss-making) | 26.1% | Turnaround plays |
| Q2 | 0 < PE < 22 | **13.7%** | Value trap zone in this period |
| Q3 | 22 < PE < 46 | 19.7% | Moderate |
| Q4 | 46 < PE < 105 | 22.1% | Growth premium |
| Q5 (highest) | PE > 105 | **30.3%** | Highest growth expectations |

### PB Quintile Returns (6M holding)
| Quintile | PB Range | Mean Return |
|----------|----------|-------------|
| Q1 | PB < 1.64 | **11.4%** |
| Q5 | PB > 5.80 | **36.2%** |

### Asset Turnover Quintile Returns
| Quintile | TO Range | Mean Return |
|----------|----------|-------------|
| Q1 (lowest) | 0-0.06 | **25.9%** |
| Q5 (highest) | > 0.18 | **17.9%** |

### Dividend Yield Quintile Returns
| Quintile | DY Range | Mean Return |
|----------|----------|-------------|
| Q1 (lowest) | 0.01-0.23% | **31.1%** |
| Q5 (highest) | > 1.61% | **14.5%** |

## Scoring Function Calibration Bug (SAFE FIX)

Three scoring functions had thresholds that didn't match A-share data distribution, causing most stocks to get identical scores. This is a **discrimination bug**, not a directional issue. Fix: adjust thresholds to match actual percentiles while keeping the original investment logic direction.

### A-Share Financial Metric Distributions (2024-12, n≈4800)

| Metric | P10 | P25 | P50 | P75 | P90 | P95 |
|--------|-----|-----|-----|-----|-----|-----|
| debt_to_equity | 14.2 | 24.8 | 40.8 | 57.2 | 71.6 | 80.3 |
| cash_to_income | -8.5 | -2.1 | 0.23 | 1.45 | 3.69 | 7.62 |
| asset_turnover | 0.04 | 0.06 | 0.11 | 0.16 | 0.23 | 0.30 |

### Before/After Score Distribution

| Dimension | Before: %at extremes | After: %at extremes | Fix |
|-----------|---------------------|---------------------|-----|
| Safety | 64.6% at 100, 0.1% at 0 | 0% at 100, 0% at 0 | Threshold 50→15 for full marks |
| Cashflow | 74.2% at 0, 0.3% at 100 | 0% at 0, 0% at 100 | Threshold 150→10 for full marks |
| Efficiency | 80.7% at 0, 0.2% at 100 | 0% at 0, 0% at 100 | Threshold 0.2→0.03 for any marks |

### ✅ How to Verify a Calibration Fix is Legitimate

After adjusting thresholds:
1. Score distribution should have std > 15 (not clustered)
2. No single score bucket should contain > 40% of stocks
3. The DIRECTION of scoring should be unchanged (low debt still = high score)
4. Total score IC should improve (better discrimination → better ranking)
5. Do NOT check if total returns improved — that's overfitting

## ⚠️ Overfitting Warning

The initial v3.1 approach reversed PE/PB/turnover/dividend scoring directions based on what "worked" in 2021-2026 data. This produced +8pp backtest improvement but was correctly identified as **shooting the arrow first, then drawing the target** (先射箭后画靶). The improvement was illusory — it would fail in a value-rotation market regime.

**Lesson**: Factor IC diagnostics should inform you about market conditions, not drive scoring function redesign. Report the findings; don't auto-optimize.
