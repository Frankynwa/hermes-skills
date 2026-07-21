# Backtest Methodology Reference

## AlphaSeeker Backtest Results (Session 2026-06-07)

### Test 1: 6-Dimension Model (2024Q4 → 2025)
- 3,364 stocks scored from 2024-12 financial data
- Quintile groups: Q5(60.3-92.0) to Q1(11.5-33.7)
- Average IC = +0.054, IC IR = +2.64, IC > 0 in 5/5 periods
- Best horizon: 9 months (IC=0.090, Spread=+10.0%)

### Test 2: PE/PB Value Model (2021-2026, 74 cases)
- 20 scoring dates × 4 holding periods
- Average IC = +0.034, but regime-dependent:
  - BEAR 12M: IC = +0.120, Spread = +12.7%
  - BULL: IC ≈ 0

### Test 3: IC Decay (63 weeks, weekly granularity)
- Week 1: IC = +0.074 (strong)
- Week 5-10: IC = -0.05 (SHORT-TERM REVERSAL)
- Week 33-40: IC = +0.10 (PEAK)
- Week 55+: IC drops below 0.03

### Key Finding: Short-Term Reversal
Factor scores go NEGATIVE in weeks 5-10 after scoring. This means:
- Do NOT rebalance too early (before week 13)
- Optimal rebalancing: every 26-40 weeks
- This is a well-known phenomenon in quant finance

## Implementation Notes

### Market Proxy (when no index data)
Use 10-12 blue-chip stocks equally weighted:
```python
BM_CODES = ['600519','601318','600036','000858','601166',
            '600276','600900','601398','600030','000001']
```

### Regime Detection (simple version)
```python
if breadth > 60 and vol < 15 and mom > 10:
    regime = "BULL"   # position = 80-100%
elif breadth < 30 and vol > 25 and mom < -10:
    regime = "BEAR"   # position = 50-65%
else:
    regime = "NEUTRAL" # position = 65-80%
```

### Risk Veto Checks
```python
veto_conditions = [
    (roe < 0 and pe > 50, "Negative ROE + high PE"),
    (debt > 150, "Extreme debt"),
    (growth < -50, "Profit collapsing"),
    (margin < 0, "Negative gross margin"),
    (mcap < 2e9, "Micro-cap"),
    (pe > 300, "Bubble PE"),
]
```

## Daily Mark-to-Market (Essential for Real Risk Metrics)

**Problem**: Only computing returns at rebalance entry/exit dates (2 points per quarter) gives fake risk metrics — 0% drawdown, inflated Sharpe.

**Solution**: Compute portfolio value EVERY trading day during holding periods:
```python
for date in period_dates:
    port_rets_today = []
    for code in selected_codes:
        entry_price = selected_entry[code]
        current_price = find_price(price_series[code], date)
        if current_price:
            port_rets_today.append((current_price - entry_price) / entry_price)
    daily_value = base_value * (1 + np.mean(port_rets_today))
```

**Impact on AlphaSeeker**:
| Metric | Quarterly 2-point | Daily M2M |
|--------|-------------------|-----------|
| Max Drawdown | 0% (fake) | -12.82% (real) |
| Sharpe | 4.330 (inflated) | 2.281 (real) |

New metrics available: Sortino, Calmar, drawdown duration, daily win rate.

## Out-of-Sample Validation: Honest Results

**AlphaSeeker OOS** (scored 2024-12-31, tracked 15 months):
- Top 10%: +26.4% | All stocks: **+34.7%** | Bottom 10%: +13.9% | Spread: +12.6%
- Quintile returns NOT monotonic (Q3 beat Q1)
- Top 10% underperformed equal-weight all stocks

**Interpretation**: Ranking ability exists (IC > 0, spread positive), but Top 10% concentration doesn't beat equal-weight. Honest, defensible conclusion.
