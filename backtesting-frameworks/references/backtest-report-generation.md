# Generating Academic Backtest Reports

> Reference for `backtesting-frameworks`. Pattern validated in the AlphaSeeker project.

## When to Use

You've completed a backtest and need to produce a polished report (PDF/HTML) for academic submission, professor review, or stakeholder presentation.

## Architecture: Charts First, Report Second

1. Generate all charts as PNG files via a dedicated Python script
2. Write HTML report referencing charts as relative paths
3. Convert to PDF via Chrome headless

```
backtest_report/
├── report.html              ← main report
├── report.pdf               ← converted via Chrome
├── chart1_score_distribution.png
├── chart2_quintile_returns.png
├── chart3_ic_by_period.png
├── chart4_spread.png
├── chart5_monotonicity.png
├── chart6_equity_curve.png
├── chart7_ic_heatmap.png    ← optional: IC by date × horizon
├── chart8_ic_by_regime.png  ← optional: bull/bear/flat
└── summary.json             ← machine-readable metrics
```

## Chart Script Pattern (matplotlib, headless)

```python
import matplotlib
matplotlib.use('Agg')  # MUST be before pyplot import
import matplotlib.pyplot as plt

# Font: on macOS, default fonts work for English labels.
# Chinese labels require PingFang/Heiti — often broken in venv matplotlib.
# Solution: use all English labels for portability.

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x, y, color='#4CAF50')
ax.set_title('Title Here', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('chart.png', dpi=150)
plt.close()
```

## Essential Charts for Factor Validation

| # | Chart | What It Shows |
|---|-------|--------------|
| 1 | Score Distribution | Histogram of all scores — should be roughly normal, not clustered |
| 2 | Quintile Returns (grouped bar) | Average return per quintile across multiple holding periods |
| 3 | IC by Holding Period | Bar chart of IC at 3M/6M/9M/12M — find the sweet spot |
| 4 | Q5-Q1 Spread | Long-short spread by holding period |
| 5 | Monotonicity Test | Line chart with error bars: Q5>Q4>Q3>Q2>Q1? |
| 6 | Equity Curve | Q5 vs Q1 vs benchmark, quarterly rebalancing |
| 7 | IC Heatmap | Scoring date × holding period — shows stability over time |
| 8 | IC by Regime | Line chart: IC in bull vs bear vs flat markets |

## HTML Report Structure

Use a clean, professional layout with these sections:

1. **Executive Summary** — metric cards (IC, IR, Spread, sample size)
2. **Methodology** — scoring → quintile sort → forward return → IC calculation
3. **Data Description** — stock count, date range, indicator coverage
4. **Results** — tables + charts for each analysis
5. **Detailed Analysis** — individual stock verification (input→output coherence)
6. **Limitations** — honest caveats (this actually IMPROVES credibility)
7. **Conclusion** — verdict with comparison to industry standards

CSS: Use a single-file HTML with inline styles. No external dependencies.

## PDF Conversion (macOS, Chrome headless)

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf=output.pdf \
  --no-pdf-header-footer \
  --print-to-pdf-no-header \
  file://$(pwd)/report.html
```

Chrome must be installed. SSL errors in stderr are harmless — check for "bytes written" in output.

## Pitfalls

1. **matplotlib Chinese fonts**: Often broken in venv. Use English labels or install fonts system-wide.
2. **Chart DPI**: 150 is good for PDF, 100 for web. Don't use 300+ (file too large).
3. **Report should be self-contained**: All data in charts/tables, no external references needed.
4. **Limitations section builds credibility**: Professors appreciate honest caveats more than overselling.
5. **Metric cards in executive summary**: Use a CSS grid of 6 cards for the key metrics — instant visual impact.
