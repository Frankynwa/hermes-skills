# V3.1 Quantitative Scoring Framework — Implementation Methodology

Source: AlphaSeeker project research report (2026-06-09). Synthesizes academic papers + Chinese broker research (中金, 光大, 天风, 国海, 东方证券).

## Architecture: 5-Layer Scoring Pipeline

```
Stock Universe
    ↓
Layer 1: Macro Regime → Position Sizing (50%-100%)
    ↓
Layer 2: Industry Momentum → Industry Weight Adjustment
    ↓
Layer 3: Risk Veto → Hard Exclusions (一票否决)
    ↓
Layer 4: Expectation Progress → Overpricing Penalty
    ↓
Layer 5: Base 6-Dimension Score → Final Rating
```

## Layer 1: Macro Regime (宏观择时)

### Method A: Remaining Liquidity Index (中金模型)
- **Core signal**: `剩余流动性 = M2同比增速 - 社融存量同比增速`
  - M2 = total liquidity supply, 社融 = real economy liquidity demand
  - Difference = excess liquidity available for financial markets
  - Positive → BULL, Negative → BEAR
- **Enhancement**: Use 2nd-order difference (环比加速度) for early signals
- **Supporting signals**:
  - DR007 deviation from policy rate (interbank liquidity)
  - Northbound capital 20-day cumulative flow (foreign sentiment)
  - Margin balance change rate (leverage appetite)
  - PMI direction (economic momentum)

### Method B: HMM State Classification (高级方法)
- 2-3 hidden states (Bull/Bear/Flat)
- Each state has different return distribution N(μ_k, σ_k²)
- Transition matrix: Bull persistence ~0.97 (33 days avg), Bear ~0.92 (12 days)
- Signal: P(Bear|t) > 0.7 → reduce position
- Library: `hmmlearn.hmm.GaussianHMM`

### Scoring Formula (0-100)
```
macro_score = (
    liquidity_signal * 0.35 +    # M2-社融
    dr007_signal * 0.15 +         # interbank rate
    northbound_signal * 0.20 +    # foreign flow
    margin_signal * 0.15 +        # leverage
    pmi_signal * 0.15             # economy
)
# >60: BULL (100% position), 40-60: NEUTRAL (75%), <40: BEAR (50%)
```

## Layer 2: Industry Inflection (行业景气拐点)

### Method A: Three-Factor Model (光大证券)
1. **Supply-Demand**: 工业增加值增速 × PPI增速 (z-score over 3Y rolling)
   - Price z-score > 66.7%: +2, >33.3%: 0, else: -2
   - Volume z-score > 66.7%: +1, >33.3%: 0, else: -1
   - Combined: +3/+2 = boom, +1/0 = recovery, -1 = depression, -2/-3 = recession

2. **Profitability**: Industry revenue growth + operating margin historical percentile
   - Margin change weighted 2x vs revenue change 1x
   - Profitability inflection LAGS supply-demand by 1-2 quarters (leading indicator!)

3. **Inventory**: Industrial enterprise finished goods inventory growth rate
   - Inventory destocking from high → inflection signal
   - Inventory restocking from low → confirmation signal

### Method B: PB-ROE Quadrant (PB-ROE象限)
Based on Wilcox (1984): `ln(PB) = a + b × ROE`

| Quadrant | ROE | PB | Action | Score |
|----------|-----|-----|--------|-------|
| Value Zone | High (>15%) | Low (<30th pctile) | Core allocation | +10 |
| Stable Growth | High | High | Hold, don't add | 0 |
| Value Trap | Low | Low | Wait for inflection | -10 |
| Bubble | Low | High | Avoid | -15 |

**Inflection detection for Quadrant 4 (value trap → value zone)**:
- ROE declining 2 quarters then first uptick → +12
- PB at historical 10th percentile + ROE stabilizing → +8
- ROE rising 2 quarters then first decline → -10 (top inflection)

### Scoring Formula
```
industry_score = supply_demand_score + profitability_score + inventory_score + pb_roe_score
# Range: -30 to +30, mapped to adjustment multiplier
```

## Layer 3: Risk Veto (一票否决)

### Tier 1: Bankruptcy Models
- **Altman Z-Score**: Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 0.999X₅
  - Z < 1.81 → VETO, 1.81-2.99 → gray zone, >2.99 → safe
- **Ohlson O-Score**: Logistic regression with 9 financial variables
  - O > 0.38 → VETO

### Tier 2: Fraud Detection (8 Key Factors)
From Gibbs random search on 3500+ A-share companies:
1. ROE anomaly
2. Construction-in-progress growth anomaly
3. Prepayment growth anomaly
4. Interest expense / revenue anomaly
5. Investment income / revenue anomaly
6. Other income / revenue anomaly
7. Other receivables / total assets anomaly
8. Long-term loans / total assets anomaly

### Tier 3: Hard Thresholds
| Check | Threshold | Action |
|-------|-----------|--------|
| Pledge ratio | >70% | VETO |
| Goodwill / Net assets | >20% | VETO |
| Operating CF / Net profit | <0.5 for 3+ years | VETO |
| Accounts receivable growth > revenue growth AND AR/revenue > 40% | Both | VETO |
| Large shareholder sells > 5% in 1 year | | VETO |
| Cash > 30% of assets AND interest-bearing debt > 30% | Both (存贷双高) | VETO |
| Frequent auditor changes | | FLAG |

## Layer 4: Expectation Progress (预期兑现进度)

### Multi-Dimensional Scoring (0-100)

| Dimension | Metric | Early Signal | Late Signal |
|-----------|--------|-------------|-------------|
| Valuation | PE/PB 5Y percentile | <30% | >70% |
| Valuation | Consensus PEG | <1 | >2 |
| Catalyst | Already-announced / expected catalysts | <30% | >70% |
| Institutional | Quarterly institutional position change | +5% | -5% |
| Coverage | Broker reports in 30 days | <5 | >20 |
| Leverage | Margin buy / total volume | <8% | >15% |
| Target price | Upside to consensus target | >30% | <10% |

### Behavioral Validation
- **Underreaction** (early stage): Low retail participation, few broker reports, institutional accumulation
- **Overreaction** (late stage): High margin buying, excessive broker coverage, retail FOMO
- Cubic relationship: price trend positive effect peaks then reverses (nonlinear mean reversion)
- A-share specific: reversal effect > momentum effect (retail overreaction)

### Stage Classification
```
progress_pct < 30  → early  (重点配置, penalty=0)
progress_pct 30-60 → mid    (持有控仓, penalty=0)
progress_pct 60-80 → late   (只减不增, penalty=0-10)
progress_pct > 80  → overpriced (坚决回避, penalty=10-25)
```

## Implementation Priority

| Phase | Module | Data Dependency | Effort |
|-------|--------|----------------|--------|
| 1 | Risk Veto (Z-Score + O-Score + fraud) | 3 financial statements + pledge data | Low |
| 1 | PB-ROE Quadrant | Financials + market cap | Low |
| 2 | Macro Regime (remaining liquidity) | M2, 社融, northbound, margin | Medium |
| 2 | Industry Three-Factor | Industrial VA, PPI, inventory | Medium |
| 3 | Expectation Progress | Earnings forecast, margin data | High |

## Key References

- 中金公司 "股市宏观驱动力轮动" (2021) — remaining liquidity model
- 光大证券 "从宏观政策到行业景气度" (2022) — three-factor industry model
- 天风证券 "行业景气度量化前瞻系列" (2018) — industry driver identification
- 国海证券 "半月效应和宏观流动性择时策略" (2023) — liquidity timing
- 东方证券 "质优股量化投资" — governance factors (executive pay IC=0.026, IR=2.6)
- Altman Z-Score (1968), Ohlson O-Score (1980) — bankruptcy prediction
- Wilcox PB-ROE model (1984) — valuation-fundamental matching
- BSV model (Barberis, Shleifer, Vishny 1998) — behavioral over/underreaction
- DHS model (Daniel, Hirshleifer, Subrahmanyam 1998) — overconfidence + self-attribution
