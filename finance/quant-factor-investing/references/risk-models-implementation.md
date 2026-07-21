# Financial Risk Models for A-Share Stocks

Implementation patterns for Z-Score, O-Score, and fraud detection using limited financial data.

## Altman Z-Score (Adapted for Available Fields)

Standard Z-Score requires full balance sheet data. With only `financial_indicators` fields (roe, pe, pb, debt_to_equity, gross_margin, market_cap), use these approximations:

```
X1 = Working Capital / Total Assets ≈ 0.3 - debt_to_equity/300  (clamped to [-0.5, 0.3])
X2 = Retained Earnings / Total Assets ≈ roe/100 * 0.5  (assume 50% retention)
X3 = EBIT / Total Assets ≈ gross_margin/100 * 0.8  (assume 0.8x asset turnover)
X4 = Market Cap / Total Liabilities ≈ 100 / debt_to_equity  (capped at 8.0)
X5 = Sales / Total Assets ≈ 0.8  (default asset turnover)

Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
Z < 1.81 → DISTRESS (penalty +15)
1.81 ≤ Z ≤ 2.99 → GREY (penalty +5)
Z > 2.99 → SAFE
```

**Empirical validation (2026 A-share)**: Z-Score correctly excluded most distressed stocks (vetoed avg -3.98% vs benchmark +3.13%). False negatives included turnaround plays (科翔股份 +285%, 昀冢科技 +205%).

## Ohlson O-Score (Simplified)

Requires `math.exp` — **clamp input to [-20, 20] to avoid overflow**:
```python
o_clamped = max(-20, min(20, o_raw))
o_normalized = 1 / (1 + math.exp(-o_clamped))
```

O > 0.38 → HIGH_RISK (penalty +12)

**Pitfall**: Without clamping, stocks with extreme financial metrics cause `math.exp` overflow → `math range error` crash. Always clamp before sigmoid.

## Fraud Detection (8 Factors)

Check each factor independently, count suspicious flags:
1. ROE anomaly: roe > 30% or roe < -50%
2. Debt + low margin: debt_to_equity > 100 AND gross_margin < 10
3. Cash quality: cash_to_income < 0.5 (poor cash flow vs profit)
4. Extreme PE: pe > 300 or pe < -50
5. Value trap: pb < 0.5 AND roe < 3
6. Negative gross margin: gross_margin < 0
7. Profit collapse: net_profit_growth < -80
8. Micro-cap speculation: market_cap < 2B AND pe > 100

Score ≥ 3 flags → penalty +15, ≥ 2 → penalty +8

## Pledge Check

```python
# From stock_pledge table (latest per stock)
if pledge_ratio > 70: penalty += 15, HARD VETO
elif pledge_ratio > 50: penalty += 8
```

## Combining Models

Total penalty = min(Z_penalty + O_penalty + fraud_penalty + pledge_penalty, 30)
Vetoed = total_penalty ≥ 25 OR Z < 1.81 OR pledge > 70%

## Key Pitfall: Decimal vs Float

MySQL `DECIMAL` columns return `decimal.Decimal` in Python. Arithmetic with `float` fails:
```python
TypeError: unsupported operand type(s) for /: 'decimal.Decimal' and 'float'
```

**Fix**: Convert all DB values to float when building stock_data dicts:
```python
sd[k] = float(v) if hasattr(v, 'as_integer_ratio') else v
```
