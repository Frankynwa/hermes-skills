# Comparison Backtest: Enhanced vs Original Scoring Engine

> Pattern validated in AlphaSeeker v3.3 (2026-06). Use when you have two versions of a scoring engine and need objective evidence that the new version is better.

## When to Use

- You've added layers/adjustments to a scoring engine and need to validate improvement
- You want to compare two fundamentally different scoring approaches (e.g., value vs momentum)
- You need evidence for a thesis/project that one model outperforms another
- **Anti-"先射箭后画靶子"**: Both engines run on the SAME data, SAME periods, SAME methodology — no cherry-picking favorable timeframes

## Architecture

```
                    ┌──────────────────┐
                    │   Shared Data    │
                    │ (price, fin, bm) │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────┐
     │  Engine A    │ │  Engine B    │ │ Benchmark│
     │  (Original)  │ │  (Enhanced)  │ │ (equal-w)│
     └──────┬───────┘ └──────┬───────┘ └────┬─────┘
            │                │               │
            ▼                ▼               ▼
     ┌──────────────────────────────────────────────┐
     │     Same Rebalance Schedule for ALL          │
     │     Same Selection Logic (top N%)             │
     │     Same Transaction Cost Model               │
     └───────────────────┬──────────────────────────┘
                         ▼
              ┌─────────────────────┐
              │  Side-by-Side NAV   │
              │  + Metrics Compare  │
              └─────────────────────┘
```

## Key Implementation Rules

### 1. Load Data Once, Score Twice
```python
# Load financial + price data once
fin_index, price_series, all_dates = load_data()

# For each rebalance period, score with BOTH engines using same data
for sched in REBALANCE_SCHEDULE:
    for (code, fdate), row in fin_index.items():
        if fdate != sched["fin_date"]:
            continue
        orig_score = base_engine.compute_baseline(build_stock_data(row))
        enh_score = enhanced_engine.score_stock(build_stock_data(row), macro_regime)
```

### 2. Same Selection Logic
Both engines must use identical selection: same top-N%, same min holdings, same filtering.
```python
# Both engines: sort by score, select top 10%
scored.sort(key=lambda x: x[1], reverse=True)
n_select = max(10, int(len(scored) * 0.10))
selected = scored[:n_select]
```

### 3. Daily Mark-to-Market (Not Just Entry/Exit)
Track portfolio value every trading day for real drawdown and Sharpe calculation:
```python
for date in period_dates:
    port_rets = [(find_price(code, date) - entry_p) / entry_p
                 for code in selected_codes if entry_p > 0]
    port_val = cum_port * (1 - cost) * (1 + np.mean(port_rets))
    daily_equity.append((date, port_val, bm_val))
```

### 4. Macro Layer Without External Data
When you don't have market breadth/volatility data, compute proxies from price data:
```python
# Breadth: % of stocks above 20-day MA
above_ma20 = sum(1 for code in codes if price_now > price_20d)
breadth = above_ma20 / total * 100

# Momentum: average 3M/6M returns across universe
mom_3m = np.mean([(p_now - p_3m) / p_3m for ...])

# Volatility: std of daily market returns * sqrt(252)
vol_60d = np.std(market_daily_rets[-60:]) * np.sqrt(252) * 100
```

## Metrics Comparison Table

Always present results as a head-to-head table:

| Metric | Original | Enhanced | Winner |
|--------|----------|----------|--------|
| Total Return | +72.94% | +74.53% | 🟢 |
| Excess Return | +15.03% | +16.79% | 🟢 |
| Sharpe Ratio | 2.281 | 2.265 | 🔵 |
| Max Drawdown | -12.82% | -12.87% | 🔵 |

Include per-period breakdown showing which engine won each quarter.

## Pitfalls

1. **Both engines must use the same stock universe** — if Engine A skips low-ROE stocks but Engine B doesn't, the comparison is unfair. The selection/filtering logic must be identical.

2. **Don't optimize Engine B parameters on the test data** — if you tune the enhanced engine's penalty weights using the same historical period you're backtesting, that's overfitting ("先射箭后画靶子"). Use fixed, pre-set parameters.

3. **Short data coverage ≠ failure** — if only 5 quarters have enough data, that's fine. Report honestly with the limitation. A 5-quarter comparison with consistent outperformance is still meaningful evidence.

4. **Macro regime affects comparison** — enhanced engine with macro layer may hold less in bear markets (lower position_pct). This reduces both losses AND gains. Compare risk-adjusted metrics (Sharpe, Sortino) not just raw returns.

5. **Transaction costs matter for close comparisons** — if two engines differ by <1% in total return, the comparison is meaningless after costs. Only report a "winner" when the gap exceeds ~2x total transaction costs.

6. **Industry layer needs data** — if industry metrics table isn't populated, the enhanced engine's industry layer does nothing. Document this in the report ("industry signals unavailable, contribution from layers 3-5 only").

## Report Template

Generate HTML with:
- Side-by-side cards (Original vs Enhanced) for key metrics
- Metrics comparison table with 🟢/🔵 winner indicators
- Per-period comparison table showing quarterly returns + excess
- NAV curves on log scale (both engines on same chart)
- Drawdown comparison chart
- Macro regime labels per period (if applicable)

See `scripts/v3_3_comparison_backtest.py` in AlphaSeeker for a complete implementation.
