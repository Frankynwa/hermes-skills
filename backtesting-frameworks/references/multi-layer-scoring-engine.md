# Multi-Layer Scoring Engine Design

When building a quantitative stock selection system, a single-factor or flat multi-factor model often misses critical dimensions (macro timing, industry rotation, risk screening). This reference documents a 5-layer architecture that combines human investment frameworks (like V3.1 top-down analysis) with quantitative scoring.

## Architecture

```
Layer 1: Macro Regime     → Position sizing (50%-100%)
Layer 2: Industry Momentum → Per-stock adjustment (±8 points)
Layer 3: Risk Veto         → Hard exclusions + penalty (0-25 points)
Layer 4: Expectation       → Overpricing penalty (0-25 points)
Layer 5: Base Scoring      → Multi-factor score (0-100)
```

**Combination formula (additive, NOT multiplicative):**
```
final_score = base_score + industry_adj - risk_penalty - expectation_penalty
```

## Critical Design Rule: Use Additive Adjustments

**NEVER multiply adjustments** — multiplication causes ceiling effects:
```
# WRONG: multiplicative
score = 92 × 1.15 = 105.8 → capped at 100
score = 88 × 1.15 = 101.2 → also capped at 100
# Result: two different stocks both at 100, no differentiation

# RIGHT: additive
score = 92 + 8 = 100 (only the best hits ceiling)
score = 88 + 8 = 96 (clear differentiation preserved)
```

## Layer Details

### Layer 1: Macro Regime
- **Inputs**: Market breadth (% above 20d MA), 60d volatility, 3M/6M momentum
- **Output**: regime (BULL/NEUTRAL/BEAR) + position_pct (0.5-1.0)
- **Key**: In bear market, raise the bar for "recommend" rating (higher threshold)

### Layer 2: Industry Momentum
- **Inputs**: Industry-level ROE trend (current vs prior period), industry PE percentile
- **Output**: Additive adjustment: +8 (inflection point), +3 (warm), 0 (neutral), -3 (cooling), -8 (declining)
- **Prerequisite**: Must populate industry_metrics table first (aggregate stock-level data by industry×quarter)

### Layer 3: Risk Veto
- **Checks**: Negative ROE + high PE, extreme debt (>150%), collapsing profit (<-50%), negative margin, micro-cap (<2B), extreme PE (>300x), value trap (low PB + weak ROE)
- **Output**: penalty 0-25 points, veto flag if ≥20

### Layer 4: Expectation Progress
- **Inputs**: Current PE vs historical median, PE + growth combination
- **Logic**: Low PE + high growth = bonus; high PE + low growth = penalty
- **Output**: progress_pct (0-100), stage (early/mid/late/overpriced), penalty 0-25

### Layer 5: Base Scoring
- The existing multi-factor engine (ROE, growth, debt, PE, PB, margin)
- Unchanged — this layer is the foundation

## Comparing Two Scoring Engines Side-by-Side
When you have an enhanced version of a scoring engine and need objective evidence of improvement, see `references/comparison-backtest-pattern.md`. Covers the "same data, same periods, same methodology" comparison pattern, macro proxy computation from price data, and pitfall avoidance (especially anti-overfitting).

## Implementation File
See `backend/app/services/enhanced_scoring_service.py` in the AlphaSeeker project for the full implementation.
