# Chinese A-Share Data Fetching Playbook

## Data Source Priority (best → worst)

| Priority | Source | Coverage | Auth | Notes |
|----------|--------|----------|------|-------|
| 1 | **akshare** (`pip install akshare`) | Full fundamentals, real-time quotes, financials | None | Wraps eastmoney/ths/sina. Best for A-shares. |
| 2 | **eastmoney API direct** | Real-time quotes, PE/PB/ROE, financials | None | `push2.eastmoney.com` (quotes), `datacenter.eastmoney.com` (financials) |
| 3 | **Yahoo Finance** (stocks skill) | Price, change, 52w high/low only | None | Use `.SZ`/`.SS` suffixes. No fundamentals. |
| 4 | **GitHub analysis repos** | Historical snapshots of fundamentals | GitHub token optional | `yangdingshan/stock-chose`, `kavenGw/GSStock`, `sinbawang/stock` |

## akshare Quick Start

```python
import akshare as ak

# Real-time quote
df = ak.stock_individual_info_em(symbol="300750")

# Financial summary (annual)
fin = ak.stock_financial_abstract_ths(symbol="300750", indicator="按年度")

# Bulk A-share spot data
df = ak.stock_zh_a_spot_em()  # All A-shares
```

## macOS System Proxy Issue (CRITICAL)

**Problem**: macOS apps like Clash/Surge set a **system-level** HTTP/HTTPS proxy
via SystemConfiguration (not just env vars). Python's `requests` and akshare
read this proxy automatically, causing eastmoney API calls to fail with:
```
RemoteDisconnected: Remote end closed connection without response
```

**What does NOT work**:
- `export NO_PROXY="*"` — macOS proxy is deeper than env vars
- `export HTTP_PROXY=""` — same reason
- Monkey-patching `requests.Session.proxies` — akshare creates sessions internally
- `requests.get(url, proxies={"http": None})` — still picks up system proxy

**What DOES work**:

### Option 1: Clash Verge rule (permanent fix)

**Clash Verge config path** (macOS):
```
~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml
```

Add DIRECT rules **before** the `GEOIP,CN,DIRECT` line:
```yaml
rules:
  - DOMAIN-SUFFIX,eastmoney.com,DIRECT
  - DOMAIN-SUFFIX,eastmoney.com.cn,DIRECT
  - DOMAIN-SUFFIX,emsec.com.cn,DIRECT
  - DOMAIN-SUFFIX,qq.com,DIRECT
  - DOMAIN-SUFFIX,sina.com,DIRECT
  # ... then existing GEOIP,CN,DIRECT rules
```

Reload: send `USR1` to the mihomo process, or restart Clash Verge app.

**Pitfall**: If Clash Verge crashes or mihomo process dies, macOS system proxy
settings at `127.0.0.1:7897` **persist**. Python requests and akshare will
still fail even though the proxy process is dead. Fix: `networksetup
-setwebproxystate Wi-Fi off && networksetup -setsecurewebproxystate Wi-Fi off`.

**Pitfall**: `networksetup` disables the proxy at OS level, but macOS caches
the settings in SystemConfiguration framework. You may need to wait ~30s or
toggle Wi-Fi off/on for the change to fully propagate to all processes.

### Option 2: urllib with ProxyHandler bypass (code-level fix)
```python
import urllib.request, json

proxy_handler = urllib.request.ProxyHandler({})  # Empty = no proxy
opener = urllib.request.build_opener(proxy_handler)

url = "https://push2.eastmoney.com/api/qt/stock/get?fltt=2&fields=f57,f58,f43,f162,f167&secid=0.300750"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with opener.open(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
```

**Caveat**: eastmoney rate-limits aggressively (~1 req/sec). Use 1-2s delays
between requests. After ~5 rapid requests, connections get dropped for minutes.

### Option 3: curl from terminal (works, no Python proxy interference)
```bash
curl -s "https://push2.eastmoney.com/api/qt/stock/get?fltt=2&fields=f57,f58,f43,f162,f167&secid=0.300750"
```

## eastmoney API Reference

### Real-time Quote
```
GET https://push2.eastmoney.com/api/qt/stock/get?fltt=2&fields=<FIELDS>&secid=<MARKET.CODE>
```
- `secid`: `0.300750` (SZ prefix=0), `1.600519` (SH prefix=1)
- Key fields: `f43`(price), `f57`(code), `f58`(name), `f116`(total_mv), `f162`(PE_TTM), `f167`(PB), `f173`(ROE), `f183`(revenue_yoy), `f185`(net_profit_yoy), `f186`(gross_margin), `f187`(net_margin), `f188`(debt_ratio)

### Financial Reports (datacenter API — PREFERRED for bulk data)
```
GET https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_FINANCE_MAINFINADATA&columns=ALL&filter=(SECURITY_CODE="300750")&pageSize=2&sortColumns=REPORT_DATE&sortTypes=-1&source=HSF10&client=PC
```

**Key advantage**: datacenter API is **NOT rate-limited** like push2. After push2
blocks your IP (happens after ~5 rapid requests), datacenter still works. Use
datacenter for financial data, push2 only for real-time prices.

**Field mapping** (discovered 2026-06-09, `columns=ALL` response):

| API Field | Meaning | Example |
|-----------|---------|---------|
| `ROEJQ` | ROE (加权) | 24.91 |
| `TOTALOPERATEREVETZ` | 营收同比增长率 (%) | 17.04 |
| `PARENTNETPROFITTZ` | 归母净利润同比增长率 (%) | 42.28 |
| `XSMLL` | 销售毛利率 (%) | 26.27 |
| `XSJLL` | 销售净利率 (%) | 18.12 |
| `ZCFZL` | 资产负债率 (%) | 61.94 |
| `LD` | 流动比率 | 1.60 |
| `SD` | 速动比率 | 1.34 |
| `REPORT_DATE_NAME` | 报告期名称 | "2025年报" / "2026一季报" |
| `SECURITY_NAME_ABBR` | 股票简称 | "宁德时代" |
| `EPSJB` | 基本每股收益 | 4.58 |
| `BPS` | 每股净资产 | 78.28 |
| `TOTALOPERATEREVE` | 营业总收入 (元) | 129131041000 |
| `PARENTNETPROFIT` | 归母净利润 (元) | 20737710000 |

**Tip**: Use `pageSize=2` and filter for `REPORT_DATE_NAME` containing "年报" to
get the latest annual report (Q1 data has different base rates). If only Q1
exists, use it but note the YoY is Q1-vs-Q1 not full-year.

### Market Code Mapping
| Exchange | Prefix | Examples |
|----------|--------|----------|
| Shenzhen (SZ) | `0` | 000xxx, 002xxx, 300xxx |
| Shanghai (SH) | `1` | 600xxx, 601xxx, 688xxx |

## Yahoo Finance Suffixes
- Shenzhen: `300750.SZ`
- Shanghai: `600519.SS`
- Returns: price, change, volume, 52w levels only (no fundamentals)

## GitHub Fallback Data Sources

When APIs are blocked, search GitHub for recent analysis reports:
```
site:github.com "300750" "ROE" "2025年报"
site:github.com stock-chose 300750
```
Repos with structured financial data:
- `yangdingshan/stock-chose` — AI-generated deep analysis with full financials
- `kavenGw/GSStock` — Buffett-style analysis reports
- `sinbawang/stock` — Structured JSON with financial metrics
