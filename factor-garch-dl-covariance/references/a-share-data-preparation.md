# A股数据准备

## 数据位置

原始数据：`~/course-project-ex2-team-6/backend/database_dump/stock_prices_YYYY.csv.gz`
- 2021-2025：完整年度数据（各约30-40MB）
- 2026：截至当前日期
- 格式：CSV gzip压缩

## 数据字段

| 字段 | 说明 |
|------|------|
| stock_code | 股票代码（数字，如1=平安银行） |
| trade_date | 交易日期 YYYY-MM-DD |
| open_price | 开盘价 |
| close_price | 收盘价 |
| high_price | 最高价 |
| low_price | 最低价 |
| volume | 成交量 |
| market_cap | 总市值（元） |
| pe_ratio | 市盈率 |
| pb_ratio | 市净率 |

## 数据规模（2021-2026）

- 总记录：6,355,896条
- 唯一股票：5,506只
- 交易日：1,236天（2021-03-24至2026-04-29）

## 准备脚本

`prepare_a_share_data.py` — 生成不同规模的收益率矩阵：

```bash
cd ~/projects/factor-garch-dl-research
/opt/anaconda3/bin/python3 prepare_a_share_data.py
```

输出文件：
- `data/returns_sample30.csv` — 30只股票样本（快速测试）
- `data/returns_top30.csv` — 526只大盘股（top 10%市值）
- `data/returns_top50.csv` — 1,055只中盘股（top 20%市值）
- `data/returns_top100.csv` — 2,614只全市场（top 50%市值）

## 使用方法

```python
import pandas as pd

# 加载30只样本
returns = pd.read_csv('data/returns_sample30.csv', index_col=0, parse_dates=True)

# 或加载大盘股
returns = pd.read_csv('data/returns_top30.csv', index_col=0, parse_dates=True)
```

## 注意事项

1. **市值过滤**：使用最新可用市值数据（2026-04-29）
2. **数据质量**：要求至少200个交易日的数据
3. **缺失值**：前向填充+后向填充
4. **收益率**：对数收益率 log(P_t/P_{t-1})
