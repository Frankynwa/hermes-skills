# akshare API Quirks for A-Share Quantitative Data

## Macro Data

### M2 Money Supply
```python
df = ak.macro_china_money_supply()
# Month format: "2024年01月份"
# Key column: '货币和准货币(M2)-同比增长' (YoY %)
```

### Social Financing (社融)
```python
df = ak.macro_china_shrzgm()
# Month format: "201501" (YYYYMM, NOT "2024年01月份")
# Key column: '社会融资规模增量' (absolute value, not YoY)
# Need to compute YoY manually
```

### PMI
```python
df = ak.macro_china_pmi()
# Month format: "2024年01月份"
# Key column: '制造业-指数'
```

### PPI
```python
df = ak.macro_china_ppi_yearly()
# Columns: '商品', '日期', '今值', '预测值', '前值'
# Date format: "1995-08-01" (ISO)
# '今值' is the PPI value
```

### Industrial Production (工业增加值)
```python
df = ak.macro_china_gyzjz()
# Month format: "2024年01月份"
# Key column: '同比增长'
```

### Bond Yield
```python
df = ak.bond_china_yield(start_date="20250101", end_date="20250131")
# Columns: '曲线名称', '日期', '3月', '6月', '1年', '10年'
# Must iterate month by month (no bulk download)
# Rate limit: ~0.3s between requests
```

## Market Data

### Northbound Capital Flow
```python
# DOES NOT EXIST: stock_hsgt_north_net_flow_in_em
# USE INSTEAD:
df = ak.stock_hsgt_hist_em(symbol="沪股通")  # or "深股通"
# Columns: '日期', '当日成交净买额', '买入成交额', '卖出成交额', '历史累计净买额'
# No '北上合计' - must aggregate manually from 沪+深
```

### Margin Trading
```python
df = ak.stock_margin_sse(start_date="20250101", end_date="20250131")
# Columns: '信用交易日期', '融资余额', '融资买入额', '融券余量金额'
# Iterate month by month
```

### Pledge Ratio
```python
# DOES NOT EXIST: stock_pledge_stat_em
# USE INSTEAD:
df = ak.stock_gpzy_pledge_ratio_em()
# Columns: '股票代码', '股票简称', '交易日期', '质押比例', '质押股数', '质押市值'
# Returns all stocks at once (2294 rows)
```

## Financial Data

### Earnings Forecast
```python
# East Money version often returns None:
df = ak.stock_profit_forecast_em(symbol="300750")  # → None

# USE Tonghuashun version:
df = ak.stock_profit_forecast_ths(symbol="300750", indicator="预测年报每股收益")
# Columns: '年度', '预测机构数', '最小值', '均值', '最大值', '行业平均数'
# Rate limit: ~0.2s between requests
```

### Individual Stock PE/PB History
```python
# DOES NOT EXIST: stock_a_indicator_lg, stock_a_lg_indicator
# USE INSTEAD: stock_prices table in local DB
# Columns: trade_date, pe_ratio, pb_ratio (daily, 5+ years of data)
```

### Financial Statements
```python
df = ak.stock_financial_report_sina(stock="300750", symbol="利润表")
df = ak.stock_financial_report_sina(stock="300750", symbol="资产负债表")
df = ak.stock_financial_report_sina(stock="300750", symbol="现金流量表")
# Works reliably for all stocks

df = ak.stock_financial_abstract_ths(symbol="300750", indicator="按报告期")
# Columns: '报告期', '净利润', '净利润同比增长率', '营业总收入', '营业总收入同比增长率', '基本每股收益'
```

## Industry Data

### Industry Board Summary
```python
df = ak.stock_board_industry_summary_ths()
# 90 industries, columns: '板块', '涨跌幅', '总成交量', '总成交额', '净流入'
```

### Industry Historical Data
```python
# Often fails with ConnectionError (remote server issues)
df = ak.stock_board_industry_hist_em(symbol="电池", period="周k", ...)
# Unreliable - use local DB industry_metrics table instead
```

## Date Parsing Helper

```python
import re
from datetime import date

def parse_month(s: str):
    """Parse '2024年01月份', '201501', or ISO dates."""
    # Format 1: "2024年01月份"
    m = re.search(r"(\d{4})\D+(\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), 1)
    # Format 2: "201501" (YYYYMM)
    m = re.match(r"^(\d{4})(\d{2})$", s.strip())
    if m:
        return date(int(m.group(1)), int(m.group(2)), 1)
    return None
```
