---
name: backtesting-frameworks
description: Build robust backtesting systems for trading strategies with proper handling of look-ahead bias, survivorship bias, and transaction costs. Use when developing trading algorithms, validating strategies, or building backtesting infrastructure.
---

# Backtesting Frameworks

Build robust, production-grade backtesting systems that avoid common pitfalls and produce reliable strategy performance estimates.

## When to Use This Skill

- Developing trading strategy backtests
- Building backtesting infrastructure
- Validating strategy performance
- Avoiding common backtesting biases
- Implementing walk-forward analysis
- Comparing strategy alternatives

## Core Concepts

### 1. Backtesting Biases

| Bias             | Description               | Mitigation              |
| ---------------- | ------------------------- | ----------------------- |
| **Look-ahead**   | Using future information  | Point-in-time data      |
| **Survivorship** | Only testing on survivors | Use delisted securities |
| **Overfitting**  | Curve-fitting to history  | Out-of-sample testing   |
| **Selection**    | Cherry-picking strategies | Pre-registration        |
| **Transaction**  | Ignoring trading costs    | Realistic cost models   |

### 2. Proper Backtest Structure

```
Historical Data
      │
      ▼
┌─────────────────────────────────────────┐
│              Training Set               │
│  (Strategy Development & Optimization)  │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│             Validation Set              │
│  (Parameter Selection, No Peeking)      │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│               Test Set                  │
│  (Final Performance Evaluation)         │
└─────────────────────────────────────────┘
```

### 3. Walk-Forward Analysis

```
Window 1: [Train──────][Test]
Window 2:     [Train──────][Test]
Window 3:         [Train──────][Test]
Window 4:             [Train──────][Test]
                                     ─────▶ Time
```

## Detailed worked examples and patterns

Detailed sections (starting with `## Implementation Patterns`) live in `references/details.md`. Read that file when the navigation summary above is insufficient.

## A-Share & HK Market Data
For China A-share and Hong Kong stock quant research (especially for undergraduate theses), see `references/a-share-data-sources.md`. Covers AKShare, yfinance, Tushare, common pitfalls (复权, 停牌, ST, 涨跌停), and a thesis-ready factor pool. MUST students have a natural angle on HK stock / Greater Bay Area research.

## Integrating Backtest with Existing Scoring Engine
When you already have a multi-factor scoring/rating engine and need to validate it, see `references/a-share-scoring-engine-integration.md`. Covers the rebalance-loop pattern, AKShare data fetching for backtesting, anti-bias checklist, paper trading for forward validation, and common pitfalls (rate limits, parquet caching, financial data limitations).

## IC-Based Factor Validation (Standard Approach)

When validating a scoring/rating engine, use this methodology:

1. **Score** all stocks in the universe at time T using financial data available before T
2. **Sort** by score, divide into 5 quintiles (Q5=top 20%, Q1=bottom 20%)
3. **Measure** forward returns for each stock from T to T+horizon
4. **Compute IC** = Pearson correlation between scores and forward returns
5. **Test monotonicity**: Q5 avg > Q4 avg > Q3 avg > Q2 avg > Q1 avg

| IC Value | Interpretation |
|----------|---------------|
| > 0.10 | Excellent |
| 0.05 - 0.10 | Good |
| 0.03 - 0.05 | Weak but usable |
| 0 - 0.03 | Marginal |
| < 0 | No predictive power (or reverse) |

**IC IR** = mean(IC) / std(IC) across periods. IR > 0.5 means the signal is stable.

## Market Regime Analysis

Factor effectiveness varies by market regime (bull/bear/flat). **Always segment IC and spread results by regime** — a factor that looks weak overall may be excellent in bear markets but useless in bull markets. This is especially true for value factors (PE/PB). See `references/a-share-scoring-engine-integration.md` for the regime classification rule and real A-share findings.

For explanation to non-technical stakeholders, see `references/explaining-backtests.md`.

## Critical Pitfall: Sample Size × Holding Period

> **A short-period small-sample backtest can completely mislead you about a factor's validity.**

Real example from the AlphaSeeker project:
- **Test A** (5 weeks, 15 stocks): avg return = -3.01%, recommended stocks lost -5.98%. Conclusion: "engine is useless"
- **Test B** (9 months, 3,364 stocks): IC = 0.090, Q5-Q1 spread = +10%. Conclusion: "engine is valid"

The signal was always there, but Test A had too much noise to detect it.

**Rules of thumb:**
- Minimum ~500 stocks for IC to be meaningful (N=3000+ gives high statistical power)
- Minimum 3-month holding period for fundamental factors (they work on earnings cycles, not daily noise)
- Test at least 3 different holding periods to find the optimal horizon
- Always test across multiple scoring dates, not just one snapshot

## IC Decay Analysis (Finding Optimal Rebalancing Frequency)

Instead of testing just 3M/6M/9M/12M, measure IC at **weekly intervals** to find exactly when the signal peaks and decays:

```python
# Test IC at every 4 weeks from 4 to 52 weeks
for weeks in range(4, 53, 4):
    exit_date = scoring_date + timedelta(weeks=weeks)
    # ... compute IC at this horizon
```

Plot the IC curve. The peak tells you the optimal rebalancing frequency. If IC peaks at week 13 and decays to near-zero by week 26, you should rebalance quarterly, not annually.

## Backtest Report Generation

For creating polished academic reports (HTML → PDF) with embedded charts, see `references/backtest-report-generation.md`. Covers chart generation with matplotlib, HTML report structure, Chrome headless PDF conversion, and the essential 8 charts for factor validation.

## Multi-Layer Scoring Engine Design
When combining macro/industry/risk layers with a base scoring engine, see `references/multi-layer-scoring-engine.md`. Covers the 5-layer architecture, additive vs multiplicative adjustments (critical!), and the V3.1 framework integration pattern.

## Comparing Two Scoring Engines
When you've built an enhanced version and need objective evidence it's better, see `references/comparison-backtest-pattern.md`. Covers the "same data, same periods, same methodology" comparison backtest pattern, macro proxy computation from price data, and anti-overfitting rules.

## Critical Finding: Short-Term Reversal
Fundamental factors often show **negative IC in weeks 1-10** (short-term reversal) before becoming positive. This means:
- Don't rebalance too early (weekly rebalancing will hurt)
- Optimal holding for fundamental factors is typically 13-48 weeks
- Always test IC at weekly granularity, not just quarterly

## Best Practices

### Do's

- **Use point-in-time data** - Avoid look-ahead bias
- **Include transaction costs** - Realistic estimates
- **Test out-of-sample** - Always reserve data
- **Use walk-forward** - Not just train/test
- **Monte Carlo analysis** - Understand uncertainty
- **Test large samples** - 500+ stocks minimum for IC validity
- **Test multiple horizons** - 3M, 6M, 9M, 12M to find the sweet spot
- **Report IC + IR + Spread** - The trifecta for factor validation

### Don'ts

- **Don't overfit** - Limit parameters
- **Don't ignore survivorship** - Include delisted
- **Don't use adjusted data carelessly** - Understand adjustments
- **Don't optimize on full history** - Reserve test set
- **Don't ignore capacity** - Market impact matters
- **Don't conclude from small samples** - 15 stocks × 5 weeks proves nothing
- **Don't skip the monotonicity check** - Q5>Q4>Q3>Q2>Q1 is the gold standard
