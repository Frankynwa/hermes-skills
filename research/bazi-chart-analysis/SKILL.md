---
name: bazi-chart-analysis
description: Chinese BaZi (八字) chart calculation, analysis, visualization, and celebrity comparison. Use when user asks about birth chart, destiny analysis, personality from birth date/time, or Chinese astrology.
tags: [chinese-metaphysics, bazi, astrology, personality, visualization]
triggers: ["八字", "命盘", "排盘", "命理", "五行", "十神", "大运", "日主", "生辰八字", "命运", "算命", "命格", "流年", "fortune telling", "birth chart", "BaZi", "八字分析报告", "命盘量化分析", "量化分析报告"]
---

# BaZi (八字) Chart Analysis

## When to use
- User provides birth date/time and asks for BaZi chart
- User asks about personality, career, health from birth info
- User wants celebrity comparison or rarity calculation
- User asks about 大运 (major luck periods), 流年 (annual luck)

## Prerequisites
- Birth year, month, day, hour (地支时辰)
- Birth location (for 真太阳时 adjustment if needed)

## Calculation Method

### PREFERRED: sxtwl Library (accurate, handles lunar calendar)

```python
import sxtwl
TIAN_GAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DI_ZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

# Convert lunar date to solar first (use sxtwl to verify)
d = sxtwl.fromSolar(year, month, day)  # solar date
yTG = d.getYearGZ()
mTG = d.getMonthGZ()
dTG = d.getDayGZ()
hTG = d.getHourGZ(hour)  # 24h format, e.g. 15 for 申时

print(f"年柱：{TIAN_GAN[yTG.tg]}{DI_ZHI[yTG.dz]}")
print(f"月柱：{TIAN_GAN[mTG.tg]}{DI_ZHI[mTG.dz]}")
print(f"日柱：{TIAN_GAN[dTG.tg]}{DI_ZHI[dTG.dz]}")
print(f"时柱：{TIAN_GAN[hTG.tg]}{DI_ZHI[hTG.dz]}")
```

**Always use sxtwl for production** — manual formulas have off-by-one errors on edge cases (leap months, 节气 boundaries). Install: `pip install sxtwl`

### Fallback: Manual Calculation (reference only)

#### Year Pillar (年柱)
Base: 1984 = 甲子年
`year_tg = tg[(year - 1984) % 10]` and `year_dz = dz[(year - 1984) % 12]`

#### Month Pillar (月柱)
Month stem determined by year stem (五虎遁):
- 甲己年: 丙寅起 | 乙庚年: 戊寅起 | 丙辛年: 庚寅起 | 丁壬年: 壬寅起 | 戊癸年: 甲寅起

Month branch: 寅(1月)→卯→辰→巳→午→未→申→酉→戌→亥→子(11月)→丑(12月)
子月 = 大雪 to 小寒 (roughly Dec 7 - Jan 5)

#### Day Pillar (日柱)
⚠️ Manual calculation is error-prone. Use sxtwl or verified万年历.
Base date: 2000-01-07 = 甲子日 (reference only, verify with sxtwl)

#### Hour Pillar (时柱)
Hour stem determined by day stem (日上起时法):
- 甲己日: 甲子起 | 乙庚日: 丙子起 | 丙辛日: 戊子起 | 丁壬日: 庚子起 | 戊癸日: 壬子起

12时辰: 子(23-1), 丑(1-3), 寅(3-5), 卯(5-7), 辰(7-9), 巳(9-11), 午(11-13), 未(13-15), 申(15-17), 酉(17-19), 戌(19-21), 亥(21-23)

## Analysis Framework

### 1. Day Master Strength (日主强弱)
- 得令: born in season that supports day master
- 得地: earth branches contain supporting elements
- 得势: heavenly stems support day master
- Result: 身强 / 身弱 / 中和

### 2. Ten Gods (十神)
For each stem/branch, determine relationship to day master:
- Same element: 比肩(同性)/劫财(异性)
- I generate: 食神(同性)/伤官(异性)
- I克: 偏财(同性)/正财(异性)
-克me: 七杀(同性)/正官(异性)
- Generate me: 偏印(同性)/正印(异性)

### 3. 用神忌神 (Favorable/Unfavorable elements)
- 身强: need 泄(食伤)/克(官杀)/耗(财) → 喜木火土 (varies)
- 身弱: need 生(印)/帮(比劫) → 喜金水 (varies)

### 4. Luck Periods (大运)
- 阳年男/阴年女: forward (顺排)
- 阴年男/阳年女: backward (逆排)
- Count days to next/previous 节气, 3 days = 1 year

### 5. Rarity Calculation
Total combinations = 60 × 12 × 60 × 12 = 518,400
Each specific BaZi = 1/518,400 ≈ 0.000193%
World population / 518,400 ≈ 15,432 people share same chart

## Visualization Approach (6-chart standard)

Create HTML dashboard with Chart.js (dark theme). The authoritative template is at `~/Desktop/八字命盘全景量化.html` — always read it first to match style. Also see `references/visualization-template.md` for chart configs.

### Required 6 Charts:
1. **五行力量** — doughnut chart (water/wood/fire/earth/metal % with weighted scoring)
2. **十神力量** — horizontal bar chart (10 gods strength index)
3. **性格维度** — radar chart (8 personality dimensions: 创造力/稳定性/叛逆性/洞察力/执行力/社交力/学习力/共情力)
4. **十二长生状态** — vertical bar chart (日主在四柱地支的长生/沐浴/冠带/临官/帝旺/衰/病/死/墓/绝/胎/养)
5. **大运五行变化** — line chart (fire/wood/water strength across luck periods)
6. **核心维度评分** — grouped bar chart (原局 vs 当前流年: 事业/财运/学业/健康/感情/贵人/抗压/创造)

### Additional Sections (non-chart, all required):
- 四柱排盘 cards (年/月/日/时 with 天干地支 + 十神 + 纳音)
- 喜用忌神 colored cards (with reason for each)
- 日主深度分析 (4-5 items: 本质/格局优势/特殊配置/核心矛盾)
- 大运时间线 (colored segments with age ranges, highlight current, + 逐阶段详解cards)
- 流年分析 box (当前年份的天干地支合化分析 + 有利/注意 + 行动建议)
- 配偶适配分析 (最适合日主 + 性格画像 + 建议婚龄)
- 格局总结 grid (主格局/特殊配置/核心矛盾/关键时间)
- 八字稀有度 badge (1/518,400 base, with global population estimate)
- Footer with date and disclaimer

### Color scheme (dark theme)
- 水(blue): #38bdf8 | 木(green): #4ade80 | 火(red): #f87171
- 土(yellow): #fbbf24 | 金(purple): #a5b4fc
- Background: #0a0a0f | Cards: linear-gradient(145deg, #1a1a2e, #16213e)
- Accent: #8b5cf6 (purple) / #fc5c7d (pink for highlights)

## Celebrity Comparison
Search for famous people with:
1. Same year pillar (同年柱)
2. Same month (同月)
3. Same day master (同日主)
4. Same chart pattern (同格局)
5. Same day pillar (同日柱) - rarest

Use `delegate_task` with web search for celebrity BaZi data.

## Output Format & Delivery

### Workflow (standard):
1. **Calculate** — execute_code for precise四柱 + 十神 + 五行 + 大运 (see `references/calculation_code.py`)
2. **Find existing template** — search Desktop for `*八字*.html` files first. The authoritative working template is at `~/Desktop/八字命盘全景量化.html`. Read it to match style exactly.
3. **Report** — write comprehensive FULL-SPEC markdown report (see depth requirements below), convert to HTML, generate PDF via Chrome headless
4. **Visualize** — create HTML with Chart.js 6-chart dashboard, based on existing template style
5. **Screenshot** — Chrome headless `--screenshot` to PNG (NOT PDF for charts — canvas rendering is blurry in PDF). Alternatively, open in browser with `open` command and use `browser_vision` to verify rendering.
6. **Deliver** — **ALWAYS send BOTH files together** in a single batch: PDF report + PNG chart image via lark-cli. Never send one without the other.

### When user says "像我之前一样" (like before):
1. Search `~/Desktop/` for existing `*.html` files with 八字/命盘 in the name
2. Read the existing template with `read_file` to extract exact CSS, layout, chart configs
3. Create new report matching the same structure and style
4. Save to Desktop with a descriptive name (e.g., `癸卯日主八字量化分析.html`)

### Report Depth Requirements (MANDATORY)

Every BaZi report MUST match the full template depth. Minimum 12 chapters:

1. 四柱排盘 (table)
2. 日主深度分析 (性格特质 + 五行本质)
3. 十神格局详解 (天干十神 + 藏干十神 + 格局判定 + 核心矛盾)
4. 五行力量分析 (加权计算 + 失衡诊断 + 喜用神)
5. 十二长生分析 (四柱长生状态 + 旺衰指数 + 关键洞察)
6. 性格深度剖析 (核心矩阵 + 优势/风险评分 + 内心冲突)
7. 大运详排 (总表 + 逐阶段详解：天干地支 + 核心主题)
8. 流年详析 (天干地支 + 合化冲 + 行动建议)
9. 感情婚姻 (特质 + 时间线)
10. 事业方向 (适合/不适合行业 + 发展节奏)
11. 健康提醒 (五行对应器官 + 具体建议)
12. 总结 (核心画像 + 关键节点 + 一句话概括)

⚠️ **NEVER give a summary version when user asks for a report.** If user says "帮我出一份", give the FULL 12-chapter version. If upgrading an existing file, compare with the most comprehensive version you've done and match its depth — ADD missing chapters, don't create a shorter replacement.

### Upgrade Workflow

When user says "升级一下" or "按照以前那个来":
1. **Find the reference version** — check session_search for the most comprehensive past version
2. **Compare chapter by chapter** — identify what the old version had that the new one is missing
3. **Add missing sections** — don't rewrite from scratch, add the gaps
4. **Verify file size** — if the new version is significantly smaller than the reference, something is wrong

### Batch Delivery (multiple people)

When analyzing multiple people in one session:
- Generate ALL files first (PDF + PNG for each person)
- Then send ALL files in sequence
- Label clearly: "汪瑞凡·报告.pdf", "汪瑞凡·图表.png", "苗果·报告.pdf", etc.
- Use `cd /path && lark-cli im +messages-send --file "name" --user-id <id> --as bot` for each

### iCloud File Locking

Files on Desktop may be locked by iCloud sync. Standard tools (read_file, cp, dd) will fail with "Resource deadlock avoided".

**Workaround**: Use Perl to force-read:
```perl
perl -e 'open(F, "<:utf8", "/path/to/file") or die $!;
local $/; $_ = <F>; close F;
print length($_);'
```

Do NOT attempt to overwrite iCloud-locked files — copy to /tmp first, work on the copy, then write back.

### ⚠️ PNG over PDF for chart visualizations
**User preference**: Chart.js canvas charts render blurry in PDF. Always use PNG screenshot for the visualization dashboard:
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --screenshot="/path/to/output.png" \
  --window-size=1100,2700 \
  "file:///path/to/visualization.html"
```

PDF is fine for text-only reports (markdown→HTML→Chrome --print-to-pdf).

### Delivery commands:
```bash
cd /path/to/files && lark-cli im +messages-send --file "report.pdf" --user-id <id> --as bot
cd /path/to/files && lark-cli im +messages-send --file "chart.png" --user-id <id> --as bot
```

### Pitfalls
- 飞书消息长度限制：超过约4000字符会被静默截断，必须保存为文件再发送
- lark-cli --file 不支持绝对路径，必须cd到文件目录用相对路径
- sxtwl getHourGZ() 参数是24小时制（如15=申时），不是时辰index
- 古代名人八字多为推定，需要标注"推定/传说"
- Chrome headless --screenshot的--device-scale-factor参数可能不生效，直接用--window-size控制分辨率
- sxtwl的农历转公历方法：`sxtwl.fromSolar(year, month, day)` 返回Day对象，用 `getLunarMonth()/getLunarDay()` 读取农历
- PDF中的Chart.js canvas会模糊，必须用PNG截图
- `chinese-astrology-bazi` skill与本skill有重叠，本skill更偏分析和可视化，那个更偏排盘计算
- **icloud文件锁**: Desktop文件可能被iCloud锁定，read_file/cp/dd都会报"Resource deadlock"。用Perl的`open(F, "<:utf8", path)`强制读取。不要直接覆盖iCloud锁定的文件。
- **升级时不要缩短**: 用户说"升级"=在现有基础上加内容，不是重新做一个更短的版本。先对比旧版有哪些章节，缺的补上，已有的保留。
- **多人分析时批量发送**: 一次会话分析多人时，先全部生成完再逐个发送，不要分析一个发一个。
- **起运年龄计算**: 阳年男/阴年女顺排，从生日到下一个节气天数/3=起运年龄。阴年男/阳年女逆排，从生日到前一个节气天数/3。
- **十二长生状态必须交叉验证**: 计算十二长生时不要凭记忆，必须用 changsheng-table.md 查表。常见错误：把"病"和"死"搞混，或把"长生"和"冠带"的顺序记反。每次生成图表前，用 Python 打印完整的十二长生状态列表确认。
- **纳音计算需要六十甲子序号**: 纳音表按 sexagenary index 分组（每2个一组），计算时先算出天干地支的六十甲子序号再查表。不要直接用天干或地支单独查。
- **五行权重计算**: 天干各1.0分，地支本气1.0分、中气0.3分、余气0.1分。总分归一化为百分比。八字完全缺某五行时，用0.1%代替0%以避免图表显示问题。
- **配偶适配分析是标配**: 每份报告都应包含配偶适配分析板块（最适合日主、配偶性格画像、建议婚龄），用户多次单独问过这个问题。
- **稀有度计算**: 基础稀有度 1/518,400，但实际要考虑性别（×2）和时辰不确定性（×12），给出合理估计范围。

## Support Files
- `references/bazi-visualization-notes.md` — Chart.js rendering, PDF styling, sxtwl API reference, weighted five elements calculation, special patterns (从旺格/伤官佩印格/食神生财)
- `references/visualization-template.md` — 6-chart HTML template structure, Chart.js configs, color scheme
- `references/bazi-report-structure.md` — Full 12-section report outline
- `references/bazi-report-template.html` — Complete HTML report template (authoritative source also at `~/Desktop/八字命盘全景量化.html`)
- `references/changsheng-table.md` — 十二长生 lookup table (all 10 stems × 12 states)
- `references/feishu_sending_workflow.md` — Feishu file sending workflow
- `references/calculation_code.py` — Python calculation code with pillars, ten gods, changsheng (十二长生), nayin (纳音), and wuxing weighting
- `references/celebrity-bazi-data.md` — Celebrity BaZi data for comparison
- `templates/bazi-dashboard-template.html` — Complete HTML/CSS dark-theme template with all component classes (copy and fill in data)
