#!/usr/bin/env python3
"""
东方财富 datacenter API 批量拉取A股财务数据
用法: python3 fetch_financials.py [报告日期，默认2025-12-31]

输出: /tmp/a_share_financial_{year}.json

注意: push2.eastmoney.com 限频严格（~800只后被封），但 datacenter 不限频。
如果遇到系统代理问题，先运行:
  networksetup -setwebproxystate Wi-Fi off
  networksetup -setsecurewebproxystate Wi-Fi off
"""

import subprocess
import json
import time
import sys

REPORT_DATE = sys.argv[1] if len(sys.argv) > 1 else "2025-12-31"
YEAR = REPORT_DATE[:4]
OUTPUT = f"/tmp/a_share_financial_{YEAR}.json"
PAGE_SIZE = 500
DELAY = 0.5  # 秒/请求

COLUMNS = (
    "SECURITY_CODE,SECURITY_NAME_ABBR,REPORT_DATE,"
    "ROEJQ,TOTALOPERATEREVETZ,PARENTNETPROFITTZ,"
    "XSMLL,XSJLL,ZCFZL,LD,SD,EPSJB,BPS"
)

all_data = []
page = 1

while True:
    url = (
        f"https://datacenter.eastmoney.com/securities/api/data/v1/get?"
        f"reportName=RPT_F10_FINANCE_MAINFINADATA&columns={COLUMNS}"
        f"&filter=(REPORT_DATE=%27{REPORT_DATE}%27)"
        f"&pageSize={PAGE_SIZE}&pageNumber={page}"
        f"&sortColumns=SECURITY_CODE&sortTypes=1&source=HSF10&client=PC"
    )

    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl", "-s", "--connect-timeout", "10", "--max-time", "20", url],
                capture_output=True, text=True, timeout=25,
            )
            raw = json.loads(r.stdout)
            result = raw.get("result", {})
            data = result.get("data", [])
            total = result.get("count", 0)
            pages = result.get("pages", 0)
            all_data.extend(data)
            print(f"Page {page}/{pages}: +{len(data)} (total={len(all_data)}/{total})")
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                print(f"Page {page} FAILED: {e}")
                sys.exit(1)

    if len(all_data) >= (total if 'total' in dir() else 99999):
        break
    page += 1
    time.sleep(DELAY)

with open(OUTPUT, "w") as f:
    json.dump({"update_date": time.strftime("%Y-%m-%d"), "report": f"{YEAR}年报", "total": len(all_data), "data": all_data}, f, ensure_ascii=False)

print(f"\nDone: {len(all_data)} stocks -> {OUTPUT}")
