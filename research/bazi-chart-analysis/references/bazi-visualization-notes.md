# BaZi Visualization Technical Notes

## Chart.js Rendering

### CDN Loading in Chrome Headless
Chart.js loads from CDN (`https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`). Chrome headless can fetch it if network is available. Charts render as canvas elements.

### Window Size for Full-Page Screenshot
- Use `--window-size=1100,<height>` where height = page content height
- Page height varies by content: 2700px for basic 6-chart, 4200px for full report with text analysis
- Check actual height with `document.body.scrollHeight` in browser console

### Chart Colors (Dark Theme)
```
水(blue): #38bdf8 | 木(green): #4ade80 | 火(red): #f87171
土(yellow): #fbbf24 | 金(purple): #a5b4fc
Background: #0a0a0f | Cards: linear-gradient(145deg, #1a1a2e, #16213e)
Accent: #8b5cf6 (purple) / #fc5c7d (pink for highlights)
```

## Markdown → PDF Workflow

1. Write markdown report
2. Convert to HTML with `python3 -c "import markdown; ..."`
3. Wrap in styled HTML template (PingFang SC font, A4 margins, dark table headers)
4. Chrome headless `--print-to-pdf` with `--no-margins --no-pdf-header-footer`

### PDF Styling (Chinese Content)
- Font: `-apple-system, "PingFang SC", "Noto Sans SC", sans-serif`
- Font size: 13px body, 22px h1, 17px h2, 14px h3
- Table headers: background #2c2c2c, color white
- Code blocks: background #1e1e1e, color #d4d4d4
- Page breaks: `page-break-after: avoid` on h2/h3, `page-break-inside: avoid` on tables/pre

## sxtwl API Reference

### Key Methods
```python
d = sxtwl.fromSolar(year, month, day)  # Returns Day object
d.getYearGZ()   # Returns GZ object with .tg and .dz (index into TIAN_GAN/DI_ZHI)
d.getMonthGZ()
d.getDayGZ()
d.getHourGZ(hour)  # 24h format: 0=子, 1=丑, ..., 23=亥
d.getLunarYear()
d.getLunarMonth()  # Returns int, negative for leap month
d.getLunarDay()
```

### Ten Gods Calculation
```python
def get_ss(day_tg, other_tg):
    tg_yin = {"甲":"阳","乙":"阴","丙":"阳","丁":"阴","戊":"阳","己":"阴","庚":"阳","辛":"阴","壬":"阳","癸":"阴"}
    twx = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
    same = tg_yin[day_tg] == tg_yin[other_tg]
    wx = ["木","火","土","金","水"]
    diff = (wx.index(twx[other_tg]) - wx.index(twx[day_tg])) % 5
    return ["比肩" if same else "劫财","食神" if not same else "伤官","偏财" if same else "正财","七杀" if same else "正官","偏印" if same else "正印"][diff]
```

### Weighted Five Elements
```python
# Heavenly stems: weight 1.0 each
# Earthly branches (base): weight 0.7 each
# Hidden stems (藏干): weight 0.3 each
# This gives a more accurate picture than counting raw occurrences
```

### Twelve Longevity (十二长生) Lookup
Each day master has a specific longevity state in each earthly branch. Use the full CS_MAP dict (10 day masters × 12 branches = 120 entries). See the complete map in the analysis scripts.

## Common Special Patterns

### 从旺格 (Following Strength)
- Fire+Earth > 80%, Metal = 0% or near 0%
- Day master at 帝旺 or near-peak strength
- Follow the dominant element, don't try to balance
- Favorable: the dominant element + elements that generate it
- Unfavorable: elements that drain or control it

### 伤官佩印格 (Injury Officer with Seal)
- 食伤 (output/creativity) + 印星 (learning/protection)
- Talent channel + knowledge backing
- Good for: technical, academic, creative careers

### 食神生财 (Food God Generates Wealth)
- 食神 (I generate) → 正财/偏财 (I control)
- Creativity → monetization pathway
- Indicates: skills can be directly converted to income
