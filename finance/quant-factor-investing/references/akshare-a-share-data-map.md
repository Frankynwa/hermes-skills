# akshare A-Share Quantitative Data Availability Map

Verified 2026-06-09 with akshare in AlphaSeeker project venv.

## Macro Data (All Monthly)

| Data | akshare Interface | Rows | Key Columns | Notes |
|------|-------------------|------|-------------|-------|
| M2 Money Supply | `macro_china_money_supply()` | 220 | 月份, M2-数量(亿元), M2-同比增长 | Since 2008 |
| Social Financing | `macro_china_shrzgm()` | 136 | 月份, 社会融资规模增量 | |
| PMI | `macro_china_pmi()` | 221 | 月, 制造业-指数, 非制造业-指数 | |
| PPI | `macro_china_ppi_yearly()` | 363 | | |
| Industrial Value-Added | `macro_china_gyzjz()` | 201 | 月份, 同比增长, 累计增长, 发布时间 | |
| Bond Yield | `bond_china_yield(start_date, end_date)` | ~57/mo | 曲线名称, 日期, 3月, 6月, 1年, 10年 | Need date range |

## Market Data (Daily)

| Data | akshare Interface | Notes |
|------|-------------------|-------|
| Northbound Flow (Shanghai) | `stock_hsgt_hist_em(symbol="沪股通")` | 2685 rows, cols: 日期, 当日成交净买额, 买入/卖出成交额, 历史累计净买额 |
| Northbound Flow (Shenzhen) | `stock_hsgt_hist_em(symbol="深股通")` | 2209 rows, same columns |
| Margin Balance (SSE) | `stock_margin_sse(start_date, end_date)` | 信用交易日期, 融资余额, 融资买入额, 融券余量 |
| Industry Board Summary | `stock_board_industry_summary_ths()` | 90 industries, cols: 板块, 涨跌幅, 净流入, 上涨/下跌家数 |

**Note**: `stock_hsgt_north_net_flow_in_em` does NOT exist. Use `stock_hsgt_hist_em` instead.

## Individual Stock Financial Data

| Data | akshare Interface | Notes |
|------|-------------------|-------|
| Financial Summary | `stock_financial_abstract_ths(symbol, indicator="按报告期")` | 40 rows typical. Cols: 净利润, 净利润同比增长率, 营业总收入, 营业总收入同比增长率 |
| Income Statement | `stock_financial_report_sina(stock, symbol="利润表")` | Full P&L |
| Balance Sheet | `stock_financial_report_sina(stock, symbol="资产负债表")` | Full BS |
| Cash Flow Statement | `stock_financial_report_sina(stock, symbol="现金流量表")` | Full CF |
| Earnings Forecast (THS) | `stock_profit_forecast_ths(symbol, indicator="预测年报每股收益")` | 3 rows (next 3 years). Cols: 年度, 预测机构数, 最小值, 均值, 最大值, 行业平均数 |
| Institutional Holdings | `stock_institute_hold_detail(stock)` | May return 0 rows for some stocks |

## Risk / Governance Data

| Data | akshare Interface | Notes |
|------|-------------------|-------|
| Pledge Ratio | `stock_gpzy_pledge_ratio_em()` | 2294 stocks. Cols: 股票代码, 股票简称, 质押比例, 质押股数, 质押市值 |
| Pledge Detail (Individual) | `stock_gpzy_individual_pledge_ratio_detail_em(symbol)` | Per-stock pledge detail |
| Shareholder Changes | `stock_shareholder_change_ths(symbol)` | No `indicator` parameter — just call with symbol |

## Broken / Unavailable Interfaces

| Interface | Issue | Workaround |
|-----------|-------|------------|
| `stock_a_indicator_lg` | Does not exist | Calculate PE/PB from financial statements + market cap |
| `stock_a_lg_indicator` | Does not exist | Same as above |
| `stock_profit_forecast_em` | Returns None | Use `stock_profit_forecast_ths` instead |
| `index_value_hist_funddb` | Does not exist | Use board-level historical data or calculate from constituent stocks |
| `stock_financial_analysis_indicator_em` | Returns None | Use `stock_financial_report_sina` for raw financials |
| `stock_board_industry_hist_em` | Intermittent ConnectionError | Retry with backoff; data source rate-limits |

## Derived Metrics (Calculate from Raw Data)

```python
# Remaining Liquidity (中金核心指标)
remaining_liquidity = m2_yoy - social_financing_yoy

# PB (from balance sheet + market cap)
pb = market_cap / net_assets

# ROE (from income statement + balance sheet)
roe = net_profit / shareholder_equity

# Altman Z-Score
z = 1.2*(working_capital/total_assets) + 1.2*(retained_earnings/total_assets) + \
    3.3*(ebit/total_assets) + 0.6*(market_cap/total_liabilities) + 1.0*(revenue/total_assets)

# PEG
peg = current_pe / earnings_forecast_growth_rate
```
