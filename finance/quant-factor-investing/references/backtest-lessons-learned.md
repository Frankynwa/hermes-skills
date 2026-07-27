# AlphaSeeker V3.4 Backtest: Empirical Lessons

Extracted 2026-07-22 from actual V3.4 full backtest results, diagnostic scripts, and factor IC analysis.

## Key Numbers (5-quarter backtest, 2025Q1-2026Q1, CSI all-stocks)

| Strategy | Cumulative | Annualized | Max DD | Win Rate |
|----------|:----------:|:----------:|:------:|:--------:|
| Baseline (6-dim factor score) | +86.6% | +51.5% | -5.6% | 4/5 |
| Enhanced (5-layer framework) | +61.8% | +37.8% | -4.6% | 3/5 |
| Benchmark (equal-weight all) | +43.4% | — | — | — |

## Lesson 1: Adding Layers Reduced Performance

The Enhanced framework added 4 layers on top of the baseline 6-dimension score:
1. Macro regime detection → position sizing
2. Industry factor → sector adjustment
3. Risk veto → hard exclusion + penalty
4. Expectation progress → valuation penalty

All five quarters: Enhanced < Baseline. Every extra layer added noise, not signal.

Diagnostic (`deep_diagnostic.py`):
- Enhanced IC < Baseline IC (information coefficient between scores and forward returns)
- Risk veto excluded stocks that later rose 10%+
- Expectation penalty: "Penalty HURT — penalized stocks actually did better!"
- Macro regime engine returned "ERROR" in 2/5 periods, couldn't provide valid position sizing

**Rule**: Start with the simplest model as baseline. Each added layer must demonstrate incremental IC/return significantly >0 before inclusion.

## Lesson 2: A-Share Factors Invert Western Logic

`factor_diagnostic.py` ran Spearman correlation (raw factor value vs 6M forward return) on 5,000+ stocks:

- Low PE: NEGATIVE signal in A-shares (PE 0-10 zone had LOWEST returns; PE 20-50 had HIGHEST). Classic "low PE value" strategy backfired.
- Low debt-to-equity: not safer (D/E < 0.3 underperformed moderate-leverage companies)
- High gross margin: not a moat signal (manufacturing/cyclical stocks with lower margins outperformed in bull markets)
- Cash-to-income: data almost entirely missing

**Rule**: Never port US/HK factor logic directly. Validate every factor's IC direction on A-share data before coding scoring functions.

## Lesson 3: Data Quality Defines the Ceiling

| Metric | Coverage |
|--------|:--------:|
| ROE / Net profit growth / Gross margin | >97% |
| PE / PB | ~37% |
| Cash flow / Cash-to-income | near-zero |
| Historical depth | ~5 quarters (2024Q4-2026Q1) |

PE/PB missing for 63% of stocks means the valuation dimension (18% weight) was mostly absent. Cash flow dimension was entirely non-functional.

**Rule**: Run factor coverage reports BEFORE modeling. Don't assume "data is complete."

## Lesson 4: 5 Quarters Is Too Short

The backtest period (2024Q4-2026Q1) captured only a post-bear-market recovery. Key problems:
- Equal-weight benchmark itself returned +43.4% — much of the "alpha" was market beta
- No bear market test — unknown if factors provide downside protection
- Final quarter (2026Q1): Baseline -5.6%, Enhanced -4.6% — strategies showed limited drawdown control

**Rule**: Backtest needs at least one full bull-bear cycle (A-share: 3-5 years). Shorter periods risk beta-masquerading-as-alpha.

## Lesson 5: Missing Risk-Adjusted Metrics

The V3.4 report included cumulative return, annualized return, max drawdown, and win rate. Missing:
- Sharpe ratio (especially rolling Sharpe)
- Information Ratio
- Calmar ratio
- Monthly return standard deviation
- Max drawdown duration
- Turnover rate

Without risk adjustment, +86.6% could be driven by high volatility and concentrated sector bets.

**Rule**: Never present backtest results without risk-adjusted metrics (Sharpe minimum).

## Lesson 6: Over-Engineering Isly a Real Hazard

Enhanced framework: 5 layers × multiple sub-components each. Total complexity was high, but each layer's contribution was never validated in isolation.

`deep_diagnostic.py` layer-by-layer IC analysis showed:
- base_score IC > final_score IC (industry_adj, risk_penalty, expect_penalty all degraded IC)
- Among Baseline top-100 stocks, Enhanced re-ranking through extra layers REDUCED predictive accuracy

**Rule**: Simpler models are more robust with limited data. Don't add layers without isolating and validating their incremental contribution.

## Lesson 7: AKShare Anti-Crawling Killed Automation

AKShare frequently hit port bans and anti-crawling measures. The planned automated daily data sync was impossible. This cascaded into insufficient historical data for the scoring engine.

Workaround: local MySQL caching of all fetched data. System could function offline but data was always stale.

**Rule**: External data dependencies must have fallback strategies and caching from day one. Plan for API unreliability, not against it.

## Diagnostic Methodology (for reuse)

When backtest shows unexpected underperformance, run three diagnostics in order:

1. **Factor-level IC**: Raw factor value vs forward return (Spearman). Is the factor itself predictive?
2. **Score-level IC**: Scored value vs forward return. Does the scoring function preserve or invert the raw signal?
3. **Layer-by-layer IC**: For multi-layer frameworks, compute IC at each layer to isolate which layers add/remove signal.
4. **Quintile returns**: By both raw factor value AND scored value. Reveals non-monotonic relationships.
5. **Missed-bulls and false-positives**: What did each layer exclude that it shouldn't have?

Diagnostic scripts: `deep_diagnostic.py`, `factor_diagnostic.py`, `ic_diagnostic_v2.py` in `~/course-project-ex2-team-6/backend/scripts/`.
