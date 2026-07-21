# AKShare Macro Data Sync Patterns

Verified working patterns for syncing macro economic data to MySQL (as of 2026-06).

## Date Parsing Pitfall

AKShare returns dates in inconsistent formats:
- `macro_china_money_supply()`: column `月份` format `"2024年01月份"` 
- `macro_china_shrzgm()`: column `月份` format `"201501"` (YYYYMM, no separator)
- `macro_china_ppi_yearly()`: column `日期` format `"1995-08-01"` (ISO date)
- `bond_china_yield()`: column `日期` as datetime object

**Universal parser** (handles all formats):
```python
import re
from datetime import date

def parse_month(s: str):
    s = str(s)
    # Format: "2024年01月份" or "2024年12月份"
    m = re.search(r"(\d{4})\D+(\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), 1)
    # Format: "201501" (YYYYMM)
    m = re.match(r"^(\d{4})(\d{2})$", s.strip())
    if m:
        return date(int(m.group(1)), int(m.group(2)), 1)
    return None
```

## Verified API Functions

| Function | Returns | Key Columns | Notes |
|----------|---------|-------------|-------|
| `macro_china_money_supply()` | DataFrame, 220 rows | `货币和准货币(M2)-同比增长` | M2 YoY growth |
| `macro_china_shrzgm()` | DataFrame, 136 rows | `社会融资规模增量` | Monthly social financing |
| `macro_china_pmi()` | DataFrame, 221 rows | `制造业-指数` | Manufacturing PMI |
| `macro_china_ppi_yearly()` | DataFrame, 361 rows | `日期`, `今值` | PPI year-over-year |
| `macro_china_gyzjz()` | DataFrame, 189 rows | `同比增长` | Industrial production YoY |
| `bond_china_yield(start_date, end_date)` | DataFrame | `10年` | 10Y gov bond yield. Must iterate month-by-month for range. |
| `stock_hsgt_hist_em(symbol="沪股通")` | DataFrame | `当日成交净买额` | Northbound flow. Use "沪股通" and "深股通" separately, then aggregate. |
| `stock_margin_sse(start_date, end_date)` | DataFrame | `融资余额`, `融资买入额` | Margin trading. Iterate month-by-month. |
| `stock_gpzy_pledge_ratio_em()` | DataFrame | `质押比例`, `股票代码` | Pledge ratio. One-shot, not time-series. |
| `stock_profit_forecast_ths(symbol, indicator)` | DataFrame | `均值`, `最小值`, `最大值`, `预测机构数` | Earnings forecast. Per-stock call. |

## Northbound Flow Aggregation

`stock_hsgt_hist_em` only returns one channel at a time. To get "北上合计":
```python
# Fetch both channels
df_sh = ak.stock_hsgt_hist_em(symbol="沪股通")
df_sz = ak.stock_hsgt_hist_em(symbol="深股通")
# Insert both, then aggregate in SQL:
# INSERT INTO northbound_flow (trade_date, channel, net_buy, ...)
# SELECT trade_date, '北上合计', SUM(net_buy), ...
# FROM northbound_flow WHERE channel IN ('沪股通', '深股通')
# GROUP BY trade_date
# ON DUPLICATE KEY UPDATE ...
```

## Remaining Liquidity Calculation

Core macro timing signal: **剩余流动性 = M2同比增速 - 社融同比增速**

- Positive (M2 > 社融): liquidity flowing into financial markets → bullish
- Negative (M2 < 社融): liquidity absorbed by real economy → bearish

Normalize social financing to YoY% for comparison (raw values are in 亿元).

## Bond Yield Iteration

`bond_china_yield` requires explicit date range. Fetch month-by-month for reliability:
```python
for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        start = f"{year}{month:02d}01"
        end = f"{year}{month:02d}28"  # or 30/31
        try:
            df = ak.bond_china_yield(start_date=start, end_date=end)
        except:
            pass  # some months may fail
        time.sleep(0.3)  # rate limit
```

## MySQL Schema for Macro Data

```sql
CREATE TABLE macro_indicators (
  id INT AUTO_INCREMENT PRIMARY KEY,
  indicator_type VARCHAR(40) NOT NULL,  -- 'M2', 'SOCIAL_FINANCING', 'PMI', 'PPI', 'IP', 'BOND_10Y'
  data_date DATE NOT NULL,
  value DECIMAL(16,4),
  yoy_change DECIMAL(12,4),
  UNIQUE KEY (indicator_type, data_date)
);

CREATE TABLE northbound_flow (
  id INT AUTO_INCREMENT PRIMARY KEY,
  trade_date DATE NOT NULL,
  channel VARCHAR(20) NOT NULL,  -- '沪股通', '深股通', '北上合计'
  net_buy DECIMAL(16,4),
  UNIQUE KEY (trade_date, channel)
);

CREATE TABLE macro_regime_cache (
  id INT AUTO_INCREMENT PRIMARY KEY,
  eval_date DATE NOT NULL UNIQUE,
  regime VARCHAR(20),  -- 'BULL', 'BEAR', 'NEUTRAL'
  position_pct DECIMAL(4,2),
  score DECIMAL(6,2),
  remaining_liquidity DECIMAL(12,4)
);
```
