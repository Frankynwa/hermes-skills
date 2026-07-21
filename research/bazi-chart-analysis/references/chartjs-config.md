# Chart.js Configuration Reference for BaZi Reports

## Chart 1: 五行力量分布 (Doughnut)
```js
type: 'doughnut',
labels: ['木 51.8%', '水 24.1%', '金 12.0%', '火 12.0%', '土 0%'],
data: [51.8, 24.1, 12.0, 12.0, 0.1],  // 0.1 for zero to show slice
backgroundColor: ['#4ade80', '#38bdf8', '#a5b4fc', '#f87171', '#fbbf24']
```

## Chart 2: 十神力量对比 (Horizontal Bar)
```js
type: 'bar', indexAxis: 'y',
// Score each 十神 0-100 based on how many positions it occupies and its strength
// 食神主导=95, 偏财=50, 劫财=30, etc.
backgroundColor: ['#4ade80','#fb923c','#38bdf8','#34d399','#818cf8','#60a5fa']
```

## Chart 3: 性格维度雷达 (Radar)
```js
type: 'radar',
labels: ['创造力', '稳定性', '叛逆性', '洞察力', '执行力', '社交力', '学习力', '共情力'],
// Score each 0-100 based on chart analysis
// 食伤旺→创造力高/叛逆性高; 缺土→稳定性/执行力低; 癸水→洞察力/共情力高
r: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.08)' } }
```

## Chart 4: 十二长生状态 (Bar)
```js
type: 'bar',
// Calculate 十二长生 for day master in each of the 4 branches
// 癸水: 长生在卯, 帝旺在亥, 病在酉, etc.
// Score: 长生=70, 帝旺=95, 病=20, 死=15, 冠带=65, 临官=90, 墓=25, etc.
```

## Chart 5: 大运五行变化 (Multi-line)
```js
type: 'line',
datasets: [
  { label: '火(财星)', borderColor: '#f87171', fill: true, tension: 0.3 },
  { label: '木(食伤)', borderColor: '#4ade80', fill: true, tension: 0.3 },
  { label: '土(官杀)', borderColor: '#fbbf24', fill: true, tension: 0.3 }
]
// Score each element 0-80 per major period based on 大运 stems/branches
```

## Chart 6: 核心维度评分 (Grouped Bar)
```js
type: 'bar',
labels: ['事业潜力', '财运指数', '学业运', '健康指数', '感情运', '贵人运', '抗压力', '创造力'],
datasets: [
  { label: '原局评分', backgroundColor: 'rgba(192,132,252,0.4)' },  // purple
  { label: '2026年评分', backgroundColor: 'rgba(252,92,125,0.4)' }  // pink
]
```

## Dark Theme Defaults
```js
// All charts: grid color, tick color, legend color
grid: { color: 'rgba(255,255,255,0.05)' }
ticks: { color: '#888' }
legend: { labels: { color: '#aaa' } }
```

## Scoring Guidelines
- 五行 weights: 本气=1.0, 中气=0.3, 余气=0.1 per branch
- 十神 scores: count positions × weight (天干 full, 藏干 reduced)
- 性格雷达: map from 五行/十神/格局 characteristics
- 评分: base on 喜用神 alignment, 大运 support, 流年 interaction
