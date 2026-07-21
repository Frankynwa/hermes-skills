# Reportlab Technical Document with Embedded Matplotlib Figures

Pattern for generating professional technical PDFs with CJK text, math formulas, tables, and embedded charts.

## CJK Font Registration

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

CJK_FONT_PATH = '/Library/Fonts/Arial Unicode.ttf'
CJK_BOLD_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'

pdfmetrics.registerFont(TTFont('CJK', CJK_FONT_PATH))
try:
    pdfmetrics.registerFont(TTFont('CJKBold', CJK_BOLD_PATH, subfontIndex=0))
except:
    pdfmetrics.registerFont(TTFont('CJKBold', CJK_FONT_PATH))
pdfmetrics.registerFontFamily('CJK', normal='CJK', bold='CJKBold')
```

## Matplotlib Figure Generation

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 200
plt.rcParams['savefig.dpi'] = 200
plt.rcParams['savefig.bbox'] = 'tight'

# Dark theme palette
C_BG    = '#0d1117'
C_PANEL = '#161b22'
C_TEXT  = '#e6edf3'

fig, ax = plt.subplots(figsize=(12, 5), facecolor=C_BG)
ax.set_facecolor(C_PANEL)
plt.savefig('figure.png', facecolor=C_BG)
plt.close()
```

## Embed Figure in PDF

```python
from reportlab.platypus import Image as RLImage, Table, TableStyle

img = RLImage('figure.png', width=CONTENT_W - 4*mm, height=(CONTENT_W - 4*mm) * 0.55)
img.hAlign = 'CENTER'
fig_table = Table([[img]], colWidths=[CONTENT_W])
fig_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), HexColor('#f5f7fa')),
    ('BOX', (0,0), (-1,-1), 1, HexColor('#dee2e6')),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
]))
```

## Pitfalls

- `axhline()` does NOT accept `transform` kwarg. Use `Line2D` instead.
- Never use Unicode subscript chars in reportlab. Use `<sub>`/`<super>` tags.
- `vision_analyze` cannot read .pdf files. Use `sips` to convert to .png first.
- LaTeX math must be converted to plain text (reportlab has no LaTeX renderer).

### Math font: Courier cannot render Greek/Unicode characters

When converting LaTeX to plain text for display (e.g., `\alpha` → `α`, `\sigma` → `σ`), do **NOT** use `Courier` font for the math style or inline math `<font>` tag. Courier is a pure ASCII Type1 font — it has no glyphs for Greek letters, mathematical symbols, or any non-ASCII Unicode. They render as solid boxes (■■■■ "tofu").

**Fix**: Use the CJK font (Arial Unicode MS) for math styles when the content contains Unicode characters from LaTeX conversion:
```python
# WRONG — Courier has no Greek glyphs
s['math'] = ParagraphStyle('Math', fontName='Courier', ...)
text = re.sub(r'\$([^$]+?)\$',
              lambda m: '<font face="Courier">' + clean_latex(m.group(1)) + '</font>', text)

# RIGHT — Arial Unicode covers full Unicode including Greek
s['math'] = ParagraphStyle('Math', fontName='CJK', ...)
text = re.sub(r'\$([^$]+?)\$',
              lambda m: '<font face="CJK">' + clean_latex(m.group(1)) + '</font>', text)
```

Verified: Arial Unicode.ttf contains proper glyphs for α(U+03B1), β(U+03B2), γ(U+03B3), σ(U+03C3), μ(U+03BC), π(U+03C0), λ(U+03BB), ω(U+03C9) etc. with correct widths.

**Scope of Courier failure**: Courier cannot render ANY non-ASCII Unicode, including:
- Greek letters (α β γ σ μ π λ ω) from LaTeX conversion
- Unicode box-drawing characters (┌ ─ ┐ │ └ ┘ ┬ ▼ ┴ ┤ ├) used in ASCII art
- Mathematical operators (− · × ÷ ≈ ≠ ≤ ≥)
- Arrow symbols (→ ← ↑ ↓ ⇒)

All of these render as solid boxes (■■■■ "tofu") in Courier.

**Trade-off**: Math formulas will lose monospace alignment. For pure ASCII formulas (no Greek), Courier is fine. For mixed content, always use CJK.

### ASCII art flowcharts in ReportLab — use vector Canvas instead

Do NOT use Unicode box-drawing characters (┌─┐│└┘┬▼) in code blocks to draw flowcharts. Courier can't render them, and even with CJK font the monospace alignment will break.

**Better approach**: Use ReportLab's Canvas API to draw a vector flowchart as a custom Flowable:

```python
from reportlab.platypus import Flowable  # NOT auto-imported — must add explicitly

class FlowchartDrawing(Flowable):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        box_w, box_h = 180, 36
        cx = self.width / 2
        arrow_gap = 16
        steps = [
            ('输入 x[n]  (ADC采样)', HexColor('#1565c0')),
            ('减去基线 B:  d[n] = x[n] − B', HexColor('#1565c0')),
            # ... more steps
            ('输出 y[n]  (滤波结果)', HexColor('#2e7d32')),
        ]
        y = self.height - box_h / 2 - 4
        for i, (label, color) in enumerate(steps):
            x0 = cx - box_w / 2
            # Shadow
            c.setFillColor(HexColor('#e0e0e0'))
            c.roundRect(x0 + 1.5, y - 1.5, box_w, box_h, 5, fill=1, stroke=0)
            # Box border
            c.setFillColor(color)
            c.setStrokeColor(color)
            c.setLineWidth(1.2)
            c.roundRect(x0, y, box_w, box_h, 5, fill=0, stroke=1)
            # Label text (CJK font for Unicode support)
            c.setFillColor(HexColor('#212121'))
            c.setFont('CJK', 8.5)
            c.drawCentredString(cx, y + box_h / 2 - 4, label)
            # Arrow to next step
            if i < len(steps) - 1:
                ax = cx
                ay1 = y - 2
                ay2 = y - arrow_gap + 2
                c.setStrokeColor(HexColor('#455a64'))
                c.setFillColor(HexColor('#455a64'))
                c.setLineWidth(1.2)
                c.line(ax, ay1, ax, ay2)
                # Arrowhead — Canvas has NO drawPolygon, use beginPath/drawPath
                p = c.beginPath()
                p.moveTo(ax - 3, ay2 + 4)
                p.lineTo(ax + 3, ay2 + 4)
                p.lineTo(ax, ay2)
                p.close()
                c.drawPath(p, fill=1, stroke=0)
            y -= box_h + arrow_gap

# Usage:
fc_w = CONTENT_W - 10*mm
fc_h = 7 * 36 + 6 * 16 + 20  # num_steps * box_h + (num_steps-1) * gap + margin
elements.append(FlowchartDrawing(fc_w, fc_h))
```

### Canvas API pitfall: no `drawPolygon`

ReportLab Canvas does NOT have `drawPolygon()`. To draw filled polygons (e.g., arrowheads), use:
```python
p = c.beginPath()
p.moveTo(x1, y1)
p.lineTo(x2, y2)
p.lineTo(x3, y3)
p.close()
c.drawPath(p, fill=1, stroke=0)
```

### Flowable import

`Flowable` is NOT auto-imported with `from reportlab.platypus import ...`. You must add it explicitly:
```python
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, Image as RLImage,
    Flowable  # must be explicit
)
```

### TA_JUSTIFY causes phantom spacing in Chinese/English/number mixed text

ReportLab's `TA_JUSTIFY` alignment fills the full line width by distributing extra space between words. With CJK text mixed with English and numbers, this creates visible gaps — the justification algorithm treats CJK character boundaries as word breaks and inserts space between them.

**Fix**: Use `TA_LEFT` for body text containing Chinese:
```python
# WRONG — inserts phantom spaces in mixed CJK text
s['body'] = ParagraphStyle('Body', fontName='CJK', alignment=TA_JUSTIFY, ...)

# RIGHT — natural spacing
s['body'] = ParagraphStyle('Body', fontName='CJK', alignment=TA_LEFT, ...)
```
