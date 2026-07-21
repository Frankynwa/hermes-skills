# AlphaSeeker Full Architecture (Verified 2026-07-02)

Source: `~/course-project-ex2-team-6/backend/app/services/`

## Service Layer (24 Python files)

### Scoring Engines (3 versions)
| File | Version | Description |
|------|---------|-------------|
| `scoring_service.py` | Base | 9-dimension weighted scoring (profitability 20%, growth 18%, safety 14%, moat 12%, valuation 18%, cashflow 8%, efficiency 5%, shareholder 5%, opacity deduction) |
| `scoring_service_v31.py` | V3.1 | Enhanced with industry/macro/risk/expectation layers |
| `enhanced_scoring_service.py` | V3.4 | Full 5-layer pipeline: macro → industry → risk veto → expectation → base scoring |

### 5-Layer Engine Sub-Components
| File | Layer | Function |
|------|-------|----------|
| `macro_regime_engine.py` | L1 | Macro regime (M2, social financing, PMI, bond yield, northbound, margin). Classifies BULL/BEAR/NEUTRAL |
| `industry_factor_engine.py` | L2 | Industry factor (PB-ROE quadrant, inflection detection, lifecycle stage) |
| `risk_models.py` | L3 | Risk veto (Altman Z-Score, Ohlson O-Score, fraud detection 8-factor, pledge check) |
| `expectation_engine.py` | L4 | Expectation progress (PE/PB percentile, PEG, analyst consensus vs actual) |

### Backtest Infrastructure
| File | Function |
|------|----------|
| `backtest_engine.py` | Core backtest logic: slippage (0.1%) + commission (0.1%), rebalancing, paper portfolio |
| `backtest_metrics.py` | Performance metrics: Sharpe, max drawdown, excess return, IC/IR |
| `backtest_data_service.py` | Data service for backtest: AKShare + Parquet file cache |
| `app/api/backtest.py` | REST API endpoints for backtest |

### Backtest Scripts (Version History)
| Script | Version | Focus |
|--------|---------|-------|
| `v3_1_backtest.py` | V3.1 | Initial enhanced backtest |
| `v3_2_daily_backtest.py` | V3.2 | Daily rebalancing |
| `v3_3_comparison_backtest.py` | V3.3 | Comparison across strategies |
| `v3_4_full_backtest.py` | V3.4 | Full backtest: Enhanced +61.75% vs Benchmark +43.39% = **excess +18.36%** |
| `multi_period_backtest.py` | Multi | Multi-period analysis |
| `extended_backtest.py` | Extended | Extended time range |
| `regime_and_oos.py` | OOS | Out-of-sample + regime analysis |
| `ic_decay_analysis.py` | IC | IC decay curve analysis |

### AI & Context
| File | Function |
|------|----------|
| `ai_committee_service.py` | Multi-agent decision: TechnicalAgent, FundamentalAgent, SentimentAgent. Committee voting. |
| `context_builder_service.py` | Build context for AI agents (30-second TTL cache) |
| `ai_service.py` | LLM integration (DeepSeek/MiMo) for natural language signal interpretation |

### Data & Sync
| File | Function |
|------|----------|
| `akshare_service.py` | Multi-source data: 东方财富 → EM估值 → 新浪实时 → 百度估值 → 新浪日线 |
| `stock_history_service.py` | Historical data sync (300s failure cache) |
| `background_sync_service.py` | Background data synchronization |
| `data_sync_service.py` | Data sync orchestration |
| `history_sync_service.py` | History sync |
| `sync_scheduler.py` | Sync scheduling |

### Other
| File | Function |
|------|----------|
| `auth_service.py` | JWT authentication |
| `http_client.py` | HTTP client with retry |
| `mock_data_service.py` | Mock data for testing |

## Frontend
- **Vue3 + Vite** (NOT Bootstrap)
- Ports: 5173-5177 (defined in `main.py:62-73`)

## Signal Levels (Verified)
- **Enhanced engine**: 5 levels — 强烈推荐 / 推荐 / 中立 / 不推荐 / 回避
- Thresholds vary by macro regime: BEAR (75/50/30), BULL (65/35/20), NEUTRAL (70/40/25)
- Vetoed stocks → 回避 regardless of score

## Data Sources (Priority Order)
1. 东方财富 datacenter API — bulk financial data
2. 腾讯财经 gtimg.cn — historical daily prices (referenced in skill, may be in full version)
3. AKShare — convenience wrapper
4. 东方财富 push2 API — real-time prices
5. Yahoo Finance — backup

## NOT Found in Codebase (as of 2026-07-02)
- Tencent gtimg real-time quotes (data comes from 东方财富/AKShare)
- 30min + 8h dual-layer cache (actual: 30s TTL context cache)
- Multi-level stop-loss / take-profit
- Smart 套牢 (trapped-position) protection
- Bootstrap + AJAX frontend (actually Vue3 + Vite)
- Manual position management / stock blacklist / auto README generation

## V3.4 Backtest Results
- Enhanced strategy total return: **+61.75%**
- Benchmark total return: **+43.39%**
- Excess return: **+18.36%**
- Note: Benchmark was POSITIVE (+43.39%), not negative (-1.43% as previously claimed on resume)
