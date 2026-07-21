# Integrating Backtest with an Existing Scoring Engine (A-Share)

> Reference for `backtesting-frameworks`. Pattern validated in the AlphaSeeker project (BSAI301/course-project-ex2-team-6).

## When to Use

You have a stock scoring/rating engine (multi-factor, rule-based, or ML) and need to validate its predictive power via historical backtest. Common in university quant projects and capstone courses.

## Architecture Pattern

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Data Service    │────▶│  Backtest Engine  │────▶│  Metrics Calc   │
│  (AKShare/DB)    │     │  (Scoring Loop)   │     │  (Sharpe/DD/α)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  Price Cache     │     │  Rebalance Log   │
│  (parquet)       │     │  (JSON history)  │
└─────────────────┘     └──────────────────┘
```

**Key principle**: The backtest engine wraps the existing scoring engine — it calls it at each rebalance date with point-in-time data. Do NOT rewrite scoring logic inside the backtest.

## Rebalance Loop (Pseudocode)

```python
for rebalance_date in rebalance_dates:
    # 1. Get point-in-time financial data (published before this date)
    financials = get_financials_as_of(rebalance_date)
    
    # 2. Score all stocks using existing engine
    scored = [(code, scoring_engine.score(financials[code])) for code in universe]
    
    # 3. Select top N%
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:n_select]
    
    # 4. Track portfolio for this period
    portfolio_history.append({date, holdings, weights})
```

## AKShare Data for Backtesting

### Price Data (Daily Close, Forward-Adjusted)
```python
import akshare as ak
df = ak.stock_zh_a_hist(symbol="000001", period="daily",
                         start_date="20230101", end_date="20260101",
                         adjust="qfq")  # 前复权
```

### Financial Indicators
```python
# Returns latest financials (ROE, growth, debt ratio, gross margin)
df = ak.stock_financial_abstract_ths(symbol="000001")
# Columns: 净资产收益率, 净利润同比增长率, 资产负债率, 销售毛利率
```

### Benchmark Index
```python
# CSI 300 index
df = ak.index_zh_a_hist(symbol="000300", period="daily", ...)
# Or: ak.stock_zh_index_daily(symbol="sh000300")
```

### Stock Universe
```python
# CSI 300 components
df = ak.index_stock_cons_csindex(symbol="000300")
codes = df["成分券代码"].tolist()
```

## Anti-Bias Checklist

| Bias | How It Appears | Mitigation |
|------|---------------|------------|
| **Look-ahead** | Using Q2 report data for a March rebalance | Only use reports published ≥ 45 days before rebalance date |
| **Survivorship** | Only testing stocks that still exist | Use index constituent lists (they include delisted stocks historically) |
| **Cost-blind** | Ignoring commission + slippage | Model 0.1% commission + 0.1% slippage per trade (A-share standard) |
| **IPO bias** | New stocks with extreme first-month returns | Exclude first 60 trading days |
| **ST bias** | ST stocks have ±5% limits | Filter out stocks with ST prefix |

## Performance Metrics Checklist

For a course project / thesis, these metrics are expected:

- **Sharpe Ratio** (>1.0 = good for A-share)
- **Sortino Ratio** (downside risk only)
- **Max Drawdown** (peak-to-trough)
- **Annual Excess Return** (vs CSI 300 benchmark)
- **Information Ratio** (excess return / tracking error)
- **Alpha / Beta** (CAPM regression)
- **Win Rate** (% of positive-return days)
- **Up/Down Capture** (how strategy performs in up/down markets)

## Paper Trading (Forward Validation)

After historical backtest, run paper trading to validate out-of-sample:

1. Score stocks TODAY using the engine
2. Select top N, create virtual portfolio
3. Update daily with real prices
4. After 3-6 months, compare actual vs predicted

Store state in JSON so it survives restarts:
```json
{
  "created_at": "2026-06-01T00:00:00",
  "initial_capital": 1000000,
  "positions": [{"code": "600519", "entry_price": 1800, "shares": 55.56, "score": 92}],
  "equity_history": [{"date": "...", "equity": 1005000}]
}
```

## Market Regime Analysis (Essential for Factor Validation)

A factor's predictive power often depends on market conditions. **Always segment results by market regime** when presenting backtest results, especially for academic/thesis work.

**Classification rule:**
```python
if benchmark_return > 10%: regime = "BULL"
elif benchmark_return < -10%: regime = "BEAR"
else: regime = "FLAT"
```

**Real-world finding (AlphaSeeker, A-share PE/PB value factor):**

| Regime | 12M IC | 12M Spread | Interpretation |
|--------|--------|-----------|----------------|
| BEAR    | +0.120 | +12.7%   | Excellent — cheap stocks massively outperform in downturns |
| FLAT    | +0.031 | -1.2%    | Weak — modest signal, inconsistent direction |
| BULL    | +0.032 | -0.2%    | None — growth/momentum dominates, value irrelevant |

This is the classic **value factor lifecycle**: strong in bear markets (mean reversion), weak in bull markets (growth/momentum dominance). A multi-factor engine that adds ROE/growth/margin on top of pure PE/PB can maintain positive IC even in bull markets — this is the key selling point for multi-factor over single-factor approaches.

**For the report/presentation:** Show the regime breakdown table. It demonstrates sophisticated understanding of factor dynamics and explains WHY some test periods show negative IC.

## Pitfalls

1. **`stock_financial_abstract_ths` only returns LATEST data** — not historical quarters. For multi-year backtests, you need to either cache historical snapshots or use alternative APIs (`stock_financial_analysis_indicator` for historical ROE). **Fallback**: The `stock_prices` table often contains `pe_ratio`, `pb_ratio`, and `market_cap` columns with much longer history (e.g., 2021+). Build a simplified PE/PB-based value scoring function to extend the backtest to 5+ years when `financial_indicators` only has recent data. This is less complete than the full multi-factor engine but enables regime analysis.
2. **AKShare rate limits**: batch downloads need `time.sleep(0.15)` between calls. Downloading 300 stocks × 3 years of daily prices takes ~5 minutes.
3. **Parquet caching is essential** — first run downloads everything, subsequent runs load from cache. Use `CACHE_DIR / f"prices_{start}_{end}.parquet"`.
4. **Forward-fill gaps** — A-share stocks have holidays and suspensions. Use `df.ffill(limit=5).bfill(limit=5)` to handle short gaps.
5. **The scoring engine doesn't need to be perfect** — even weak predictive power (IC > 0.03) is meaningful if consistent over time.
6. **AKShare network failures**: On university/restricted networks, AKShare often fails with `RemoteDisconnected`. Fallback: use Eastmoney's direct HTTP API (`push2.eastmoney.com/api/qt/ulist.np/get`). See `references/a-share-data-sources.md` for the exact curl/Python code.
7. **Small-sample short-period tests are MISLEADING**: A 15-stock × 5-week test showed the engine "failed" (avg -3%), but a 3364-stock × 9-month test showed it was "valid" (IC=0.09). Always test with N > 500 stocks and holding period > 3 months.
8. **Q1 may not be the worst quintile**: Fundamental scoring engines often identify "good" companies better than "bad" ones. If Q1 > Q2, the engine has asymmetric skill — still useful, but acknowledge it.
