#!/usr/bin/env python3
"""
AlphaSeeker 全量A股评分回测脚本
用法: python3 full_backtest.py

前置数据:
  /tmp/a_share_financial_2025.json — datacenter API 拉取的财务数据
  /tmp/a_share_quotes.json — push2 API 拉取的行情数据（可能不全）

输出:
  /tmp/as_backtest_result.json — Top50 + 分组对比 + ETF持仓评分
"""

import json
import math

# ─── 加载 ─────────────────────────────────────
FIN_PATH = "/tmp/a_share_financial_2025.json"
QUOTE_PATH = "/tmp/a_share_quotes.json"
OUTPUT_PATH = "/tmp/as_backtest_result.json"

with open(FIN_PATH) as f:
    fin_db = json.load(f)
with open(QUOTE_PATH) as f:
    quote_db = json.load(f)

quotes = quote_db.get("data", {})
print(f"财务: {len(fin_db['data'])} | 行情: {len(quotes)}")

# ─── 合并 + 过滤 ──────────────────────────────
stocks = {}
for d in fin_db["data"]:
    code = d["SECURITY_CODE"]
    # 只要沪深主板+创业板+科创板
    if not (code.startswith("0") or code.startswith("3") or code.startswith("6")):
        continue
    roe = d.get("ROEJQ")
    npm = d.get("XSJLL")
    if roe is None or npm is None:
        continue

    entry = {
        "code": code, "name": d.get("SECURITY_NAME_ABBR", ""),
        "roe": roe, "rev_yoy": d.get("TOTALOPERATEREVETZ") or 0,
        "np_yoy": d.get("PARENTNETPROFITTZ") or 0,
        "gpm": d.get("XSMLL") or 0, "npm": npm,
        "debt": d.get("ZCFZL") or 0,
        "eps": d.get("EPSJB") or 0, "bps": d.get("BPS") or 0,
    }

    if code in quotes:
        q = quotes[code]
        for key, api_key in [("price","price"),("pe_ttm","pe_ttm"),("pb","pb"),("total_mv","total_mv")]:
            try:
                v = q.get(api_key)
                entry[key] = float(v) if v and v != "-" else None
            except:
                entry[key] = None

    stocks[code] = entry

print(f"合并: {len(stocks)} 只 | 有行情: {sum(1 for s in stocks.values() if s.get('price'))} 只")

# ─── 百分位评分 ────────────────────────────────
codes = list(stocks.keys())

def pct_rank(vals, higher=True):
    valid = [(i,v) for i,v in enumerate(vals) if v is not None and not (isinstance(v,float) and math.isnan(v))]
    if not valid:
        return [50.0]*len(vals)
    sv = sorted(v for _,v in valid)
    n = len(sv)
    scores = [50.0]*len(vals)
    for i,v in valid:
        r = sum(1 for x in sv if x<=v)/n*100
        scores[i] = round(r if higher else 100-r, 1)
    return scores

roe_s = pct_rank([stocks[c]["roe"] for c in codes])
rev_s = pct_rank([stocks[c]["rev_yoy"] for c in codes])
np_s  = pct_rank([stocks[c]["np_yoy"] for c in codes])
npm_s = pct_rank([stocks[c]["npm"] for c in codes])
debt_s = pct_rank([stocks[c]["debt"] for c in codes], higher=False)
gpm_s = pct_rank([stocks[c]["gpm"] for c in codes])

for idx, code in enumerate(codes):
    s = stocks[code]
    prof = roe_s[idx]*0.4 + npm_s[idx]*0.3 + gpm_s[idx]*0.3
    grow = rev_s[idx]*0.4 + np_s[idx]*0.6
    safe = debt_s[idx]

    pe, pb = s.get("pe_ttm"), s.get("pb")
    if pe and pe > 0 and pb and pb > 0:
        val = max(0, 100-pe)*0.5 + max(0, 100-pb*10)*0.5
    else:
        val = 50  # 无数据或亏损给中性分

    effi = gpm_s[idx]*0.5 + npm_s[idx]*0.5
    total = prof*0.30 + grow*0.25 + safe*0.20 + val*0.15 + effi*0.10

    # 一票否决
    if s["npm"] < -20 or s["roe"] < -30 or s["debt"] > 95:
        total *= 0.3

    s["sc"] = {
        "prof": round(prof,1), "grow": round(grow,1), "safe": round(safe,1),
        "val": round(val,1), "effi": round(effi,1), "total": round(total,1),
    }

ranked = sorted(stocks.values(), key=lambda x: x["sc"]["total"], reverse=True)

# ─── 输出 ──────────────────────────────────────
print(f"\n{'='*90}")
print(f"AS Top 30 / {len(ranked)} 只")
print(f"{'='*90}")
print(f"{'#':<3} {'股票':<8} {'代码':<7} {'总分':>5} {'盈利':>5} {'成长':>5} {'安全':>5} {'估值':>5} {'ROE':>6} {'净利YoY':>8} {'负债率':>5}")
for i, s in enumerate(ranked[:30]):
    sc = s["sc"]
    print(f"{i+1:<3} {s['name']:<8} {s['code']:<7} {sc['total']:>5.1f} {sc['prof']:>5.1f} {sc['grow']:>5.1f} {sc['safe']:>5.1f} {sc['val']:>5.1f} {s['roe']:>5.1f}% {s['np_yoy']:>7.1f}% {s['debt']:>4.1f}%")

# 分组对比
priced = [s for s in ranked if s.get("price")]
if len(priced) >= 50:
    top50 = priced[:50]
    bot50 = priced[-50:]
    mid = priced[len(priced)//2-25:len(priced)//2+25]

    print(f"\n{'-'*70}")
    for label, grp in [("Top50",top50),("Mid50",mid),("Bot50",bot50)]:
        n = len(grp)
        a = lambda k: sum(s[k] for s in grp)/n
        hp = [s for s in grp if s.get("pe_ttm") and s["pe_ttm"]>0]
        a_pe = sum(s["pe_ttm"] for s in hp)/len(hp) if hp else 0
        print(f"  {label}: score={a('sc')['total']:.1f} ROE={a('roe'):.1f}% RevYoY={a('rev_yoy'):.1f}% NPM={a('npm'):.1f}% Debt={a('debt'):.1f}% PE={a_pe:.0f}x")

# 保存
out = {
    "update_date": fin_db.get("update_date",""),
    "total": len(ranked),
    "top50": [{"rank":i+1,"code":s["code"],"name":s["name"],"score":s["sc"]["total"],
               "roe":s["roe"],"np_yoy":s["np_yoy"],"debt":s["debt"]}
              for i,s in enumerate(ranked[:50])],
}
with open(OUTPUT_PATH, "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\nSaved: {OUTPUT_PATH}")
