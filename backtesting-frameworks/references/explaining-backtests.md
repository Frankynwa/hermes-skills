# Explaining Backtests to Non-Technical Stakeholders

> How to present backtest methodology and results to professors, teammates, or investors who don't know quant jargon.

## The Core Analogy

> "If our scoring system is good, then in the past, stocks we scored high should have gone up more than stocks we scored low."

## Step-by-Step Explanation (Use This Sequence)

### Step 1: Scoring
"We use financial data (ROE, PE, growth rate, etc.) to give every stock a score from 0 to 100."

### Step 2: Sorting
"We rank all stocks by score and split them into 5 equal groups: the top 20%, next 20%, ..., bottom 20%."

### Step 3: Measuring Real Returns
"Then we look at what ACTUALLY happened — how much did each group's stocks go up or down over the next N months?"

### Step 4: Comparing
"If the scoring system works, the top group should make more money than the bottom group. If they're the same, the scoring is useless."

### Step 5: IC (Information Coefficient)
"IC is just a correlation number: does a higher score correlate with higher returns?
- IC > 0 means yes, the scoring works
- IC ≈ 0 means no, the scoring is random
- IC < 0 means the scoring is backwards"

## Key Metrics to Present

| Metric | Plain English | Good Value |
|--------|--------------|------------|
| IC | "Does our score predict returns?" | > 0.05 |
| IC IR | "Is the prediction consistent across time periods?" | > 0.5 |
| Q5-Q1 Spread | "How much more does the top group earn vs bottom?" | > 5% |
| Monotonicity | "Is each group better than the one below it?" | All 5 ordered |

## What NOT to Say

- ❌ "The Sharpe ratio is 1.2 with a Sortino of 1.8" → too technical
- ❌ "We ran a vectorized backtest with walk-forward optimization" → jargon soup
- ✅ "We tested across 3,364 stocks over 5 different time periods. The top-scored stocks beat the bottom-scored stocks in every single test."

## Presentation Structure

1. **What we built** (1 slide): "A scoring engine that rates stocks 0-100 based on financial health"
2. **How we tested it** (1 slide): "Scored 3,364 stocks, split into 5 groups, measured real returns over 3-15 months"
3. **Results** (2 slides): Bar chart of quintile returns + IC chart
4. **Honest limitations** (1 slide): What doesn't work and what we'd improve
