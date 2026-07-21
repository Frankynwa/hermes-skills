---
name: quant-factor-investing
description: Multi-factor stock selection models, alpha factor construction, market regime adaptive weighting, and ML-based factor optimization for A-share and global markets. Use when building, evaluating, or improving quantitative stock selection engines.
tags: [quant, finance, factor-investing, alpha, a-share, multi-factor, stock-selection]
---

# Quantitative Factor Investing

Design, evaluate, and optimize multi-factor stock selection strategies. Covers factor construction, combination methods, market regime adaptation, and ML-based optimization.

## When to Use

- Building or improving a stock scoring/rating engine
- Evaluating which factors predict stock returns
- Optimizing factor weights (beyond manual assignment)
- Adapting strategy to bull/bear/flat markets
- Researching state-of-the-art quant techniques

## AlphaSeeker (AS) — The User's System

User abbreviation: **AS** = AlphaSeeker. The user's own quantitative stock selection system with a local MySQL database (`mysql -u root alphaseeker`).

### Project Directory Locations (Verified 2026-07-02)

| Location | What's There | When to Use |
|----------|-------------|-------------|
| `~/course-project-ex2-team-6/` ⭐ | **FULL version** — enhanced scoring, backtest engine, AI committee, Vue3 frontend, risk models, macro/industry/expectation engines | Main development; resume verification; feature analysis |
| `~/Documents/定时任务/` | **Simplified version** — 8-dim scoring + recommendation + Feishu push only | Daily cron job / Feishu推送版 |
| `~/.trae-cn/worktrees/course-project-ex2-team-6/` | Trae IDE worktree (mirror of full version) | Trae development sessions |

**⚠️ PITFALL**: When verifying project features, ALWAYS check `~/course-project-ex2-team-6/` FIRST. The `~/Documents/定时任务/` directory is a stripped-down version missing the backtest engine, enhanced scoring, and AI committee. Searching only the simplified version will incorrectly conclude features don't exist.

### 9-Dimension Real Engine (满分100)

The real engine `QuantitativeBaselineEngine` uses 9 weighted dimensions:

| 维度 | English | Core Metric | Weight | Scoring |
|------|---------|-------------|--------|---------|
| 盈利能力 | Profitability | ROE | 20% | ≥20%→100, <0%→0, linear |
| 成长性 | Growth | 净利润增长率 | 18% | ≥30%→100, <0%→0, linear |
| 估值 | Valuation | PE(60%)+PB(40%) | 18% | PE≤15→100, ≥60→0; PB≤1.5→100, ≥10→0 |
| 安全性 | Safety | 资产负债率 | 14% | A-share percentile calibrated |
| 护城河 | Moat | 毛利率 | 12% | ≥60%→100, ≤10%→0, linear |
| 现金流 | Cashflow | 经营现金流/净利 | 8% | A-share distribution calibrated |
| 运营效率 | Efficiency | 资产周转率 | 5% | A-share distribution calibrated |
| 股东回报 | Shareholder | 股息率 | 5% | ≥6%→100, ≤0%→0, linear |
| 透明度扣分 | Opacity | 数据缺失率 | deduction | Missing >40% deducts 0-15pts |

**Key insight**: Valuation dimension has 18% weight, PE≥60 → 0 points. This is why Maotai (PE~25x, PB~8x) doesn't rank in Top50.

### 5-Layer Enhanced Engine

Layer 1-4 are overlays on the base score:
1. **宏观择时** → position sizing (50%-100%)
2. **行业景气** → industry weight (0.8-1.2x)
3. **一票否决** → ST/loss/high-debt exclusion
4. **预期进度** → analyst expectation deviation penalty
5. **基础9维评分** → the base 9-dimension score

### Backtest: Quintile + IC Decay (CRITICAL RULES)

When user says "回测" they mean: **五分位分组(Q1-Q5) + IC衰减曲线**, not simple Top50 comparison.

**Mandatory rules (user explicitly corrected):**
1. Must use real engine code: `from app.services.scoring_service import QuantitativeBaselineEngine`
2. Must use quintile grouping Q1-Q5, each equal-weighted
3. Must show IC decay curve (weekly RankIC over time)
4. Cannot show only start/end — must show intermediate periods
5. Holding period cannot exceed IC effective window (~6 months, reverses at ~9 months)

### Data Sources (Priority Order)

1. **东方财富 datacenter API** ⭐ — bulk financial data, no rate limit
2. **腾讯财经 gtimg.cn** ⭐ — historical daily prices (forward-adjusted), no rate limit
3. **akshare** — convenient but macOS proxy issues
4. **东方财富 push2 API** — real-time prices, strict rate limit (~800 stocks)
5. **Yahoo Finance** — backup

### Local MySQL Database

**Connection**: `mysql -u root alphaseeker` (localhost:3306, no password)

| Table | Purpose |
|-------|---------|
| `stocks_info` | Stock basics (5,666 stocks) |
| `financial_indicators` | Multi-period financials |
| `stock_prices` | Daily prices (6.48M+ rows) |
| `industry_metrics` | Industry metrics |

**"更新数据库" = update local MySQL, not pull API to /tmp.**

### Mac Proxy Debugging (Clash Verge)

akshare and requests on macOS blocked by Clash Verge (127.0.0.1:7897):
```bash
networksetup -getwebproxy Wi-Fi  # diagnose
networksetup -setwebproxystate Wi-Fi off  # fix
```
Even if Clash crashes, macOS proxy settings remain pointing to 127.0.0.1:7897.

### Percentile-Based Scoring

Full A-share scoring uses percentile method (not fixed thresholds):
```python
def pct_rank(vals, higher=True):
    valid = [(i,v) for i,v in enumerate(vals) if v is not None]
    sv = sorted(v for _,v in valid)
    n = len(sv)
    scores = [50.0]*len(vals)
    for i,v in valid:
        r = sum(1 for x in sv if x<=v)/n*100
        scores[i] = round(r if higher else 100-r, 1)
    return scores
```

## Factor Categories (Standard Pool)

| Category | Factors | Typical IC | Best Regime |
|----------|---------|-----------|-------------|
| **Value** | PE, PB, PS, EV/EBITDA | 0.02-0.05 | Bear (mean reversion) |
| **Momentum** | 12-1M return, 6M return | 0.03-0.06 | Bull (trend following) |
| **Quality** | ROE, ROA, gross margin, earnings stability | 0.02-0.04 | All regimes |
| **Growth** | Revenue/earnings growth YoY | 0.02-0.04 | Bull |
| **Low Volatility** | 60-day std, downside deviation | 0.01-0.03 | Bear (defensive) |
| **Liquidity** | Turnover rate, Amihud illiquidity | 0.01-0.02 | Varies |
| **Size** | Ln(market_cap), free-float cap | -0.02 to +0.02 | Varies (small-cap premium) |

## Factor Combination Methods (Ranked by Sophistication)

### 1. Equal Weight (Baseline)
```python
score = (factor1_rank + factor2_rank + factor3_rank) / 3
```

### 2. IC-Weighted (Better)
Weight each factor by its historical IC:
```python
weights = {f: abs(ic[f]) / sum(abs(ic.values())) for f in factors}
score = sum(weights[f] * zscore[f] for f in factors)
```

### 3. IC_IR Weighted (Better)
Weight by IC/IC_std — favors consistent factors over volatile ones:
```python
ir = {f: mean(ic_history[f]) / std(ic_history[f]) for f in factors}
```

### 4. Machine Learning (Best)
```python
import lightgbm as lgb
model = lgb.LGBMRegressor(n_estimators=200, max_depth=5)
model.fit(X_train, y_train)  # X = factor values, y = forward returns
score = model.predict(X_test)
```

IC typically improves 30-50% vs linear models. LightGBM/XGBoost are the industry standard for factor combination.

### 5. Neural Network (Research Frontier)
TabNet, FT-Transformer for tabular factor data. See Microsoft Qlib for implementation.

## Market Regime Detection

### Simple Rule-Based (Sufficient for Most Cases)
```python
def classify_regime(benchmark_return):
    if benchmark_return > 10: return "BULL"
    elif benchmark_return < -10: return "BEAR"
    else: return "FLAT"
```

### Adaptive Weights
```python
REGIME_WEIGHTS = {
    "BULL":  {"value": 0.10, "momentum": 0.35, "quality": 0.25, "growth": 0.30},
    "FLAT":  {"value": 0.25, "momentum": 0.20, "quality": 0.35, "growth": 0.20},
    "BEAR":  {"value": 0.40, "momentum": 0.05, "quality": 0.40, "growth": 0.15},
}
```

### EVT-Based (Advanced)
Use Extreme Value Theory with Generalized Pareto Distribution to classify market states based on tail behavior. See `tg12/2025-trading-automation-scripts` on GitHub for implementation.

### HMM (Advanced)
Hidden Markov Model with 2-3 states. Use `hmmlearn` library.

## Alpha Factor Mining (Automated)

### RL-Based (AlphaGen, KDD 2023)
Reinforcement learning agent generates symbolic alpha expressions:
```python
# Generated factor: rank(ts_corr(close, volume, 20))
# IC = 0.04, turnover = 15%
```
Code: https://github.com/RL-MLDM/alphagen

### LLM + MCTS (MCTS-LLM Alpha, 2024)
GPT-4 + Monte Carlo Tree Search to discover formulaic alpha factors.
Code: https://github.com/dtbtc/mcts-llm-alpha

## Key Open-Source Projects (2024-2026)

| Project | Stars | Focus | URL |
|---------|-------|-------|-----|
| **microsoft/qlib** | ~16k | ML factor research platform, A-share support | github.com/microsoft/qlib |
| **AI4Finance/FinGPT** | ~14k | LLM for financial sentiment/prediction | github.com/AI4Finance-Foundation/FinGPT |
| **AI4Finance/FinRL** | ~10k | Reinforcement learning for trading | github.com/AI4Finance-Foundation/FinRL |
| **aiagents-stock** | ~300 | Multi-AI-agent A-share analysis (2025) | github.com/oficcejo/aiagents-stock |
| **RL-MLDM/alphagen** | - | RL-based alpha factor generation | github.com/RL-MLDM/alphagen |
| **OSkhQuant** | ~500 | Visual A-share backtesting (2025) | github.com/khscience/OSkhQuant |

## Key Papers (2024-2025, Top Venues)

| Paper | Venue | Key Idea |
|-------|-------|----------|
| **MASTER** (SJTU-Quant) | AAAI 2024 | Transformer for cross-stock attention, tested on A-share |
| **StockMixer** (SJTU-Quant) | AAAI 2024 | Simple MLP beats Transformer for stock prediction |
| **UMI** (Market Irrationality) | KDD 2025 | Multi-level irrationality factors for return prediction |
| **AlphaGen** | KDD 2023 | RL generates synergistic alpha factor collections |
| **MCTS-LLM Alpha** | 2024 | GPT-4 + MCTS for formulaic alpha discovery |
| **MERA** (MoE) | WWW 2025 | Mixture of Experts for regime-adaptive stock modeling |
| **AlphaFin** | COLING 2024 | RAG + LLM for financial analysis |

## A-Share Specific Considerations

| Issue | Solution |
|-------|----------|
| T+1 settlement | Compute signal EOD, trade next day open |
| ±10% daily limit (涨跌停) | Skip stocks near limits |
| Retail-dominated sentiment | Add turnover rate, bid-ask imbalance factors |
| Policy-driven rallies | Regime detection + policy event flags |
| Short selling restricted | Long-only optimization; use CSI 800/1000 as universe |
| Stamp tax (0.05%) | Factor into transaction costs; monthly rebalancing max |
| Factor crowding | Monitor IC decay; reduce exposure when IC drops sharply |
| **PE/PB positive correlation** | In A-shares, HIGH PE/PB = HIGH returns (growth premium). Low PE/PB = value traps. This is OPPOSITE to Western value investing. Scoring functions must reverse direction. See `quant-factor-backtest` skill reference. |
| **Asset turnover negative** | High turnover = low-margin retail/manufacturing. Low turnover = high-margin tech/pharma. Reverse the scoring direction. |
| **High dividend = low growth** | A-share high-dividend stocks underperform (mature companies). Reverse dividend yield scoring. |

## Optimization Roadmap (Priority Order)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| P0 | Market-cap + liquidity filter (>50B, daily vol > 5M) | Low | Avoid micro-cap blowups |
| P0 | Add 12-1M momentum factor | Low | Fix bull-market weakness |
| P1 | LightGBM for non-linear factor combination | Medium | IC +30-50% |
| P1 | Market regime adaptive weights | Medium | Bear: defensive, Bull: offensive |
| P2 | Industry-neutral Z-scoring | Low | Remove sector bias |
| P2 | IC decay analysis → optimal rebalancing | Low | Maximize signal capture |
8. **A-share scoring reversal** — Asset turnover, dividend yield are NEGATIVELY correlated with returns in A-shares (opposite intuition). Growth (net_profit_growth) is the strongest factor (IC≈0.12). Always run raw IC diagnostic before coding scoring functions.
9. **Resume/project verification**: When user asks "is this feature implemented?", search `~/course-project-ex2-team-6/` (full version) FIRST, not `~/Documents/定时任务/` (simplified version). User was extremely frustrated when I searched the wrong directory and incorrectly concluded features didn't exist. Use `find ~ -name "*.py" -exec grep -l "keyword" {} \;` as a broad fallback.
10. **Decimal vs float**: MySQL returns Decimal for numeric columns. Always convert with `float(v) if hasattr(v, 'as_integer_ratio') else v`.
11. **akshare date parsing**: Social financing uses YYYYMM format (e.g. "201501"), not "2024年01月份". M2/PMI use "2024年01月份". PPI uses ISO date.
12. **akshare interface changes**: `stock_hsgt_north_net_flow_in_em` doesn't exist; use `stock_hsgt_hist_em(symbol='沪股通')`. `stock_pledge_stat_em` doesn't exist; use `stock_gpzy_pledge_ratio_em()`.
13. **math.exp overflow**: Always clamp input to [-20, 20] before `math.exp()` in sigmoid.
14. **ST股必须排除**: ST/*ST stocks in Top50 cause -50% losses. Must add veto.
15. **push2 vs datacenter are independent services**: push2 rate limit doesn't affect datacenter, and vice versa.
16. **亏损股 PE 为负/None**: Score as neutral (50), don't exclude or give 0.
17. **Industry factor amplification**: Adjustments of +8 to +20 can dominate final score. Safe bounds: total ±12 (not ±20).
18. **先检查代理再调API**: macOS Clash Verge often runs in background. Check `networksetup -getwebproxy Wi-Fi` first.

## Critical Rules (User Corrected)

1. **回测必须用真实引擎代码** — `scoring_service.py` 的 `QuantitativeBaselineEngine`, never rewrite simplified version. User: "你是不是偷偷改我策略了"
2. **"更新数据库" = update local MySQL**, not pull API to /tmp
3. **"全量" = all A-shares (5000+)**, not 10 ETF holdings
4. **"回测" = quintile Q1-Q5 + IC decay**, not simple Top50 comparison
5. **Don't show only start/end** — must show intermediate IC and return changes
6. **Holding period cannot exceed IC effective window** — IC valid ~6 months, reverses at ~9 months
7. **Don't optimize weights on same data you test on** — walk-forward or train/test split
8. **Calibration fix (SAFE)** vs **directional change (DANGEROUS)** — distinguish them clearly

## Reference Files

- `references/alphaseeker-full-architecture.md` — Verified file-level architecture of the full project (24 service files, 3 scoring engine versions, backtest infrastructure, AI committee)
- `references/v31-scoring-framework-methodology.md` — Complete 5-layer framework with macro/industry/risk/expectation layers
- `references/akshare-a-share-data-map.md` — Verified akshare API interfaces (2026-06-09)
- `references/backtest-methodology.md` — Detailed implementation patterns
- `references/a-share-factor-ic-findings.md` — Empirical IC results and corrected scoring functions
- `references/akshare-macro-sync-patterns.md` — Verified akshare API calls for macro data
- `references/risk-models-implementation.md` — Altman Z-Score, O-Score, fraud detection
- `references/mysql_schema.sql` — AlphaSeeker database schema
- `scripts/fetch_financials.py` — Fetch financial data from datacenter API
- `scripts/full_backtest.py` — Full quintile backtest script
- `scripts/ic_decay_analysis.py` — IC decay curve analysis

## Backtest Methodology (from quant-factor-backtest)

### Quintile Sorting Test

Score all stocks → sort by score → split into 5 equal groups (Q5=top 20%, Q1=bottom 20%) → measure forward returns.

**Key metric: IC (Information Coefficient)** = Pearson correlation between scores and forward returns.
- IC > 0.03 = marginal, IC > 0.05 = good, IC > 0.10 = excellent
- IC IR (IC / IC_std) > 0.5 = stable signal

### IC Decay Curve

Score once, measure IC at each subsequent week (1-52):
- **Short-term reversal**: IC may go negative in weeks 5-10
- **Sweet spot**: IC peaks at weeks 13-40
- **Signal decay**: IC drops below 0.03 after ~50 weeks
- **Optimal rebalancing**: every 3-6 months

### Anti-Bias Rules

| Bias | Mitigation |
|------|-----------|
| Look-ahead | Use only data published BEFORE scoring date |
| Survivorship | Include all stocks (delisted, ST, etc.) |
| Overfitting | Reserve out-of-sample period |
| Transaction costs | Model commission (0.1%) + slippage (0.1%) + stamp tax (0.05%) |

### Factor IC Diagnostic Methodology

When multiple dimensions show negative IC, diagnose three root causes:

| Raw IC | Scored IC | Diagnosis | Fix |
|--------|-----------|-----------|-----|
| Positive | Positive | Working | Keep |
| Positive | **Negative** | **Scoring inverts valid signal** | Fix scoring direction |
| Negative | Negative | **Factor reverse in this market** | Flip or remove |
| ≈ 0 | ≈ 0 | No predictive power | Reduce weight to 0 |

**Calibration Fix (SAFE)**: Adjust thresholds to match data distribution, keep direction.
**Directional Change (DANGEROUS)**: Never optimize direction based on historical returns then validate on same data (先射箭后画靶).

### Tencent gtimg.cn Historical Kline API (Best — no rate limit)

```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?
  param={prefix}{code},day,{start_date},{end_date},{limit},qfq
```
- Prefix: sz for 000/002/300, sh for 600/601/603/688
- Returns: `[[date, open, close, high, low, vol], ...]`
- No rate limit (tested 150 requests with 0.3s interval)
- Use `urllib.request` with `Referer: https://finance.qq.com/`

### 东方财富 datacenter API (Bulk financial data)

**Endpoint**: `https://datacenter.eastmoney.com/securities/api/data/v1/get`

```
reportName=RPT_F10_FINANCE_MAINFINADATA
columns=SECURITY_CODE,SECURITY_NAME_ABBR,REPORT_DATE,ROEJQ,TOTALOPERATEREVETZ,PARENTNETPROFITTZ,XSMLL,XSJLL,ZCFZL,LD,SD,EPSJB,BPS
filter=(REPORT_DATE='2025-12-31')
pageSize=500&pageNumber=1&sortColumns=SECURITY_CODE&sortTypes=1&source=HSF10&client=PC
```

| API Field | Meaning |
|-----------|---------|
| ROEJQ | ROE (weighted) |
| TOTALOPERATEREVETZ | Revenue YoY growth |
| PARENTNETPROFITTZ | Net profit YoY growth |
| XSMLL | Gross margin |
| XSJLL | Net margin |
| ZCFZL | Debt-to-asset ratio |

Total ~13,546 records (2025 annual), 28 pages × 500/page. 0.5s/request is safe.

## Enhanced Scoring Engine Architecture (from quant-scoring-engine)

### 5-Layer Scoring Pipeline

```
Layer 1: Macro Regime    → position sizing (50%-100%)
Layer 2: Industry Factor → industry adjustment (-20 to +20 pts)
Layer 3: Risk Veto       → hard exclusions + penalty (0-30 pts)
Layer 4: Expectation     → valuation progress penalty (0-25 pts)
Layer 5: Base Scoring    → fundamental score (0-100)
Final = (Base + L2 - L3 - L4) × L1 position
```

### Layer 1: Macro Regime Engine

**Data sources** (akshare):
- `macro_china_money_supply()` → M2 YoY
- `macro_china_shrzgm()` → Social financing (YYYYMM format!)
- `macro_china_pmi()` → PMI
- `bond_china_yield()` → 10Y bond yield
- `stock_hsgt_hist_em(symbol='沪股通')` → Northbound flow
- `stock_margin_sse()` → Margin balance

Remaining Liquidity = M2 YoY% - Social Financing YoY%. RL > 2% → bullish.

### Layer 2: Industry Factor Engine

**PB-ROE Quadrant**:
```
         High ROE              Low ROE
    ┌──────────┬──────────┐
    │  VALUE   │  GROWTH  │
Low │  (+10)   │  (0)     │ High
PB  ├──────────┼──────────┤ PB
    │  TRAP    │  BUBBLE  │
    │  (-10)   │  (-15)   │
    └──────────┴──────────┘
```

**Inflection detection**: ROE declined 2+ quarters then rises → +12. Peak reversal → -10.

### Layer 3: Risk Veto Engine

- **Altman Z-Score**: Z < 1.81 → DISTRESS (veto)
- **Ohlson O-Score**: O > 0.38 → HIGH_RISK (+12 penalty)
- **Fraud detection**: 8 binary factors (ROE anomaly, high debt + low margin, etc.)
- **Pledge check**: >70% → hard veto, >50% → +8 penalty

### Layer 4: Expectation Progress Engine

PE/PB historical percentile + PEG + analyst consensus vs actual EPS.

### Empirical Finding: Value Factors in Speculative A-share Markets

- Value factors (low PE, high ROE) have **negative IC** in momentum markets
- Risk veto has **positive IC** — correctly excludes distressed stocks
- Growth (net_profit_growth) is the strongest factor (IC≈0.12)
- PE/PB are **POSITIVELY** correlated with returns in A-shares (opposite to Western value investing)
- Asset turnover and dividend yield are **NEGATIVELY** correlated with returns

## Pitfalls

1. **Don't optimize weights on the same data you test on** — always use walk-forward or train/test split
2. **Don't add too many factors** — 5-8 factors is the sweet spot; more leads to overfitting
3. **Factor correlation matters** — if PE and PB are 90% correlated, using both adds no information
4. **IC ≠ profitability** — IC measures rank correlation, not economic significance. Always check Q5-Q1 spread
5. **Turnover kills alpha** — a factor with IC=0.05 and 80% quarterly turnover may lose all alpha to costs
6. **A-share value factor works in bear, not bull** — pure PE/PB model showed IC=0.12 in bear vs 0 in bull (5-year backtest). BUT more critically: in A-shares, PE/PB are POSITIVELY correlated with returns (high PE = growth premium). Traditional "low PE = cheap" scoring REVERSES the signal and produces negative IC. Always run raw IC diagnostic before coding scoring functions.
7. **Small-cap bias in A-share** — without market-cap filter, scoring engines pick up micro-caps with extreme financials that are unreliable
8. **A-share scoring reversal** — Asset turnover, dividend yield are NEGATIVELY correlated with returns in A-shares (opposite intuition). Growth (net_profit_growth) is the strongest factor (IC≈0.12). See `quant-factor-backtest` skill `references/a-share-factor-ic-findings.md` for empirical data.
