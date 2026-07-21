# A-Share & HK Market Data Sources for Quantitative Research

> Reference for `backtesting-frameworks`. Captures free data sources suitable for undergraduate quant thesis work.

## Primary Data Sources

### AKShare (Recommended)
```bash
pip install akshare
```
- **Coverage**: A-share daily/weekly/monthly, financial statements, industry classification, macro indicators, HK stock, futures, fund NAV
- **Cost**: Free, no API key required
- **Rate limit**: Moderate — batch downloads need delay
- **Best for**: A-share factor research, backtesting

Key functions:
```python
import akshare as ak

# A-share daily data (all stocks)
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20200101", end_date="20241231")

# Financial indicators (PE, PB, ROE, etc.)
df = ak.stock_financial_abstract(symbol="000001")

# Industry classification
df = ak.stock_board_industry_name_em()  # 东方财富行业分类
```

### yfinance
```bash
pip install yfinance
```
- **Coverage**: Global markets including HK stocks, US stocks, ETFs
- **Cost**: Free
- **Best for**: HK stock data, global market comparison, benchmark indices

```python
import yfinance as yf
# HK stock (add .HK suffix)
data = yf.download("0700.HK", start="2020-01-01", end="2024-12-31")
# HSI index
hsi = yf.download("^HSI", start="2020-01-01")
```

### Tushare (Backup)
```bash
pip install tushare
```
- **Coverage**: A-share, financials, factor data, index weights
- **Cost**: Free tier available (120 points/day, student can apply for more)
- **Note**: Requires registration + token

## Eastmoney Direct API (AKShare Fallback)

When AKShare network requests fail (common in restricted networks), use Eastmoney's HTTP API directly:

```python
import urllib.request, json

# Real-time quotes for multiple stocks
# Format: 1.XXXXXX for SH, 0.XXXXXX for SZ
codes_em = ",".join([f"1.{c}" if c.startswith("6") else f"0.{c}" for c in stock_codes])
url = f"https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f12,f14&secids={codes_em}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=15)
result = json.loads(resp.read())
# result["data"]["diff"] is a list of {f12: code, f14: name, f2: price, f3: change_pct/100}
```

**When to use**: AKShare throws `RemoteDisconnected` or `Connection aborted` errors. This has been observed on university networks and VPN-restricted environments.

## Common Pitfalls for A-Share Data

1. **复权问题**: AKShare's `stock_zh_a_hist` returns 前复权 by default (`adjust="qfq"`). Always verify this — unadjusted prices will produce wildly wrong backtest results.
2. **停牌处理**: Suspended stocks have flat price lines. Filter out stocks with `volume=0` or price unchanged for N consecutive days.
3. **ST股票**: Special Treatment stocks have different trading rules (±5% limit). Filter out or handle separately.
4. **新股效应**: IPO stocks often have extreme returns in first month. Exclude first 20-60 trading days.
5. **涨跌停**: A-share has ±10% (±20% for 科创板/创业板) daily limits. If your strategy buys at a limit-up price, the order won't fill — your backtest must account for this.

## Research Platforms (for comparison/validation)

| Platform | Use Case | Cost |
|----------|----------|------|
| 聚宽 (JoinQuant) | Online backtesting, strategy validation | Free tier |
| 米筐 (RiceQuant) | Factor data, industry standard | Student free |
| 优矿 (UQER) | Factor research, community strategies | Free tier |

These platforms have pre-built factor libraries — use them to validate your own factor calculations.

## MUST-Specific Advantage

MUST is in Macau → natural advantage for **HK stock / Greater Bay Area** research angle:
- HK stock data via yfinance (free, no VPN needed)
- 港股通 (Stock Connect) flows data via AKShare
- Cross-market arbitrage or A-H premium research as differentiation

## Thesis-Ready Factor Pool

For a multi-factor stock selection thesis, these factors are well-documented and easy to compute:

| Category | Factors | Data Source |
|----------|---------|-------------|
| Value | PE, PB, PS, PCF, EV/EBITDA | AKShare financial |
| Momentum | 1M/3M/6M/12M return, 12-1M momentum | AKShare daily |
| Quality | ROE, ROA, gross margin, accruals | AKShare financial |
| Volatility | Daily std (1M/3M), beta, downside deviation | AKShare daily |
| Size | Ln(market_cap) | AKShare daily |
| Liquidity | Turnover rate, Amihud illiquidity | AKShare daily |
| Growth | Revenue growth YoY, earnings growth YoY | AKShare financial |
