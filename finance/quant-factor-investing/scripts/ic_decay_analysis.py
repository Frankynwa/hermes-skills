#!/usr/bin/env python3
"""
IC Decay Curve Analysis for AlphaSeeker.
Score stocks once, measure RankIC at each subsequent week to find optimal rebalancing frequency.

Usage: cd ~/course-project-ex2-team-6/backend && python3 scripts/ic_decay_analysis.py
Requires: MySQL alphaseeker with financial_indicators + stock_prices
"""
import sys, json
import numpy as np
from scipy.stats import spearmanr
import pymysql

sys.path.insert(0, ".")
from app.services.scoring_service import QuantitativeBaselineEngine

engine = QuantitativeBaselineEngine()
DB = pymysql.connect(host="localhost", user="root", password="", database="alphaseeker",
                     cursorclass=pymysql.cursors.DictCursor)
cur = DB.cursor()

# Step 1: Score from 2024 annual report
print("Step 1: Scoring stocks from 2024Q4...")
cur.execute("""
    SELECT fi.stock_code, fi.roe, fi.net_profit_growth,
           fi.debt_to_equity, fi.gross_margin, fi.pe, fi.pb
    FROM financial_indicators fi
    JOIN stocks_info si ON fi.stock_code = si.stock_code
    WHERE fi.report_date >= '2024-12-01' AND fi.report_date <= '2024-12-31'
      AND fi.roe IS NOT NULL AND fi.stock_code NOT LIKE '920%%'
""")
rows = cur.fetchall()
latest = {}
for r in rows:
    c = r["stock_code"]
    if c not in latest:
        latest[c] = r

scored = []
for code, d in latest.items():
    sd = {
        "roe": float(d["roe"]) if d["roe"] else None,
        "net_profit_growth": float(d["net_profit_growth"]) if d["net_profit_growth"] else None,
        "debt_to_equity": float(d["debt_to_equity"]) if d["debt_to_equity"] else None,
        "pe": float(d["pe"]) if d["pe"] and float(d["pe"]) > 0 else None,
        "pb": float(d["pb"]) if d["pb"] and float(d["pb"]) > 0 else None,
        "gross_margin": float(d["gross_margin"]) if d["gross_margin"] else None,
    }
    try:
        res = engine.compute_baseline(stock_data=sd, apply_opacity_penalty=True)
        scored.append({"code": code, "score": res.total_score})
    except:
        pass

scored.sort(key=lambda x: x["score"], reverse=True)
codes = [s["code"] for s in scored]
scores = np.array([s["score"] for s in scored])
print(f"  Scored {len(codes)} stocks")

# Step 2: Load daily prices
print("Step 2: Loading daily prices...")
codes_str = ",".join(f"'{c}'" for c in codes)
cur.execute(f"""
    SELECT stock_code, trade_date, close_price FROM stock_prices
    WHERE stock_code IN ({codes_str}) AND trade_date >= '2025-01-02'
      AND trade_date <= '2026-06-09' AND close_price IS NOT NULL
    ORDER BY stock_code, trade_date
""")
all_rows = cur.fetchall()
price_by_code = {}
dates_set = set()
for r in all_rows:
    c, d, p = r["stock_code"], str(r["trade_date"]), float(r["close_price"])
    price_by_code.setdefault(c, {})[d] = p
    dates_set.add(d)
trade_dates = sorted(dates_set)
print(f"  {len(price_by_code)} stocks, {len(trade_dates)} days")

# Step 3: IC at each week
print("\nStep 3: IC decay...")
entry_prices = {}
for c in codes:
    if c in price_by_code:
        for d in trade_dates:
            if d in price_by_code[c]:
                entry_prices[c] = price_by_code[c][d]
                break

ic_results = []
for week in range(1, min(70, len(trade_dates) // 5) + 1):
    day_idx = min(week * 5 - 1, len(trade_dates) - 1)
    target_date = trade_dates[day_idx]
    returns, slist = [], []
    for i, code in enumerate(codes):
        if code in entry_prices and code in price_by_code and target_date in price_by_code[code]:
            returns.append((price_by_code[code][target_date] / entry_prices[code] - 1) * 100)
            slist.append(scores[i])
    if len(returns) < 100: continue
    returns, slist = np.array(returns), np.array(slist)
    ric, pval = spearmanr(slist, returns)
    idx = np.argsort(-slist)
    q = len(slist) // 5
    q1m, q5m = np.mean(returns[idx[:q]]), np.mean(returns[idx[-q:]])
    ic_results.append({"week": week, "date": target_date, "n": len(returns),
                       "ric": round(ric, 4), "pval": round(pval, 6),
                       "spread": round(q1m - q5m, 2), "q1": round(q1m, 2), "q5": round(q5m, 2)})

print(f"\n{'Wk':>3} {'Date':<12} {'RankIC':>8} {'p':>8} {'Q1%':>8} {'Q5%':>8} {'Sprd':>8} {'OK':>3}")
print("-" * 60)
for r in ic_results:
    w = r["week"]
    if w in [1,2,4,8,12,16,20,26,30,35,39,45,52,60,65] or w == ic_results[-1]["week"]:
        ok = "Y" if r["pval"] < 0.05 and r["ric"] > 0 else "N"
        print(f"{w:>3} {r['date']:<12} {r['ric']:>+8.4f} {r['pval']:>8.4f} {r['q1']:>+8.2f} {r['q5']:>+8.2f} {r['spread']:>+8.2f} {ok:>3}")

last = max((r["week"] for r in ic_results if r["pval"] < 0.05 and r["ric"] > 0), default=0)
print(f"\nLast valid week: {last} (~{last/4:.1f} months). Rebalance every 3-6 months.")
DB.close()
