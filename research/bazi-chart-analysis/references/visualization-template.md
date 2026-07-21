# BaZi Quantified Visualization — HTML Template Structure

Standard dark-themed Chart.js dashboard for BaZi analysis. All 6 charts required.

## Page Structure (top to bottom)

```
1. Title + subtitle (name, birth date/time, place, gender)
2. 四柱排盘 grid (4 cards, color-coded by element)
3. 喜用忌神 row (5 emoji cards)
4. Chart row 1: 五行 doughnut + 十神 horizontal bar
5. Chart row 2: 性格 radar + 十二长生 vertical bar
6. 大运时间线 (segmented bar with active highlight)
7. 流年分析 box (purple gradient, 有利/注意 split)
8. Chart row 3: 大运趋势 line + 核心评分 grouped bar
9. 格局总结 card (2x2 grid: 主格局/矛盾/优势/关键时间)
10. Footer
```

## CSS Constants

```css
body { background: #0a0a0f; color: #e0e0e0; font: -apple-system, "PingFang SC" }
.card { background: linear-gradient(145deg, #1a1a2e, #16213e); border-radius: 14px; border: 1px solid rgba(255,255,255,0.06) }
```

## Element Colors

| Element | Color | Hex |
|---------|-------|-----|
| 水 Water | Cyan | #38bdf8 |
| 木 Wood | Green | #4ade80 |
| 火 Fire | Red | #f87171 |
| 土 Earth | Gold | #fbbf24 |
| 金 Metal | Indigo | #a5b4fc |

## Chart.js Config

CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`

### Chart 1: 五行 Doughnut
```js
type: 'doughnut'
data: [water%, earth%, metal%, wood%, fire%]
colors: ['#38bdf8', '#fbbf24', '#a5b4fc', '#4ade80', '#f87171']
legend: bottom, labels show "五行 XX%"
```

### Chart 2: 十神 Horizontal Bar
```js
type: 'bar', indexAxis: 'y'
labels: ten gods sorted by strength
colors: unique per bar
scales.x: 0-max, scales.y: no grid
```

### Chart 3: 性格 Radar
```js
type: 'radar'
labels: ['创造力','稳定性','叛逆性','洞察力','执行力','社交力','学习力','共情力']
max: 100, ticks hidden
```

### Chart 4: 十二长生 Vertical Bar
```js
type: 'bar'
labels: "地支(柱名)\n长生状态"
data: strength index from changsheng-table.md
title: "X水/火/土/金/木在四柱地支的长生状态"
```

### Chart 5: 大运趋势 Line
```js
type: 'line'
labels: all major luck periods (name + age range)
datasets: 3 key elements (e.g. 财星/食伤/官杀)
fill: true, tension: 0.3
```

### Chart 6: 核心评分 Grouped Bar
```js
type: 'bar'
labels: ['事业潜力','财运指数','学业运','健康指数','感情运','贵人运','抗压力','创造力']
datasets: [原局评分, 当前流年评分]
two colors: rgba(56,189,248,0.4) blue + rgba(252,92,125,0.4) pink
```

## Ten Gods Strength Index (reference values)

Approximate strength based on position + root:
- 天干透出+地支有根: 80-90
- 天干透出无根: 50-60
- 地支藏干本气: 50-60
- 地支藏干中气: 30-40
- 地支藏干余气: 15-25
- 比肩/劫财帮身: 70-80 (multiple sources)

## Personality Radar Scoring Guide

| Dimension | High (70+) | Low (30-) |
|-----------|-----------|-----------|
| 创造力 | 食伤旺 | 食伤弱 |
| 稳定性 | 身旺+印旺 | 身弱+冲多 |
| 叛逆性 | 伤官旺 | 正官旺 |
| 洞察力 | 偏印/七杀 | 无特殊 |
| 执行力 | 正官+比肩 | 食伤过旺 |
| 社交力 | 财星+食神 | 偏印+七杀 |
| 学习力 | 印星旺 | 印星弱 |
| 共情力 | 正财/正官 | 伤官+比肩 |

## Chrome Headless Screenshot

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --screenshot="/tmp/output.png" \
  --window-size=1100,2700 \
  "file:///tmp/visualization.html"
```

2700px height fits standard 6-chart layout. Always verify with vision_analyze before sending.
