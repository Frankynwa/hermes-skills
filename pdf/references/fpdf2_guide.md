# fpdf2 Guide for Academic PDF Generation

fpdf2 is a lightweight alternative to reportlab for generating homework/solution PDFs. Best for: math solutions, step-by-step computations, tables with monospace code. Falls short for: complex layouts, charts, heavy formatting.

## Critical API Pitfalls

### 1. Deprecated `ln` parameter (v2.5.2+)

The `ln` parameter in `cell()` is deprecated. Use `new_x` and `new_y` instead.

```python
# OLD (deprecated, generates DeprecationWarning)
pdf.cell(0, 10, 'Hello', ln=1)
pdf.cell(0, 10, 'World', ln=1, align='C')

# NEW (correct)
from fpdf.enums import XPos, YPos
pdf.cell(0, 10, 'Hello', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.cell(0, 10, 'World', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
```

### 2. multi_cell width=0 cursor failure

After `cell()` calls, the x-cursor may shift. `multi_cell(0, ...)` with width=0 then fails with:
```
FPDFException: Not enough horizontal space to render a single character
```

**Fix**: Always reset x-position and use explicit width:
```python
pdf.set_x(pdf.l_margin)
pdf.multi_cell(pdf.epw, 5, 'text')
```

### 3. multi_cell with indented text

Lines with leading spaces (e.g. `'    Found: ...'`) can overflow when using font size 9 after size 10. Keep annotation lines short or remove indentation.

## Helper Method Pattern

Define wrapper methods in a PDF subclass to avoid repetitive cursor management:

```python
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class AcademicPDF(FPDF):
    def section_title(self, text):
        self.set_font('Helvetica', 'B', 13)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 8, '  ' + text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(3)

    def mono_line(self, text, size=10):
        """Monospace line for equations/code — safe cursor reset."""
        self.set_font('Courier', '', size)
        self.set_x(self.l_margin)
        self.cell(self.epw, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def text_line(self, text, bold=False, italic=False, size=10):
        style = 'B' if bold else '' + 'I' if italic else ''
        self.set_font('Helvetica', style or '', size)
        self.set_x(self.l_margin)
        self.cell(self.epw, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def text_block(self, text, size=10):
        """Multi-line text block — safe cursor reset."""
        self.set_font('Helvetica', '', size)
        self.set_x(self.l_margin)
        self.multi_cell(self.epw, 5, text)

    def section_box(self, text, fill_color=(245, 245, 220)):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(*fill_color)
        self.set_x(self.l_margin)
        self.cell(self.epw, 7, '  ' + text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(2)
```

## Table Generation

```python
col_w = [20, 28, 28, 28]
headers = ['Col1', 'Col2', 'Col3', 'Col4']

# Header row
pdf.set_font('Helvetica', 'B', 9)
pdf.set_fill_color(70, 100, 160)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(headers):
    pdf.cell(col_w[i], 7, h, border=1, align='C', fill=True)
pdf.ln()
pdf.set_text_color(0, 0, 0)

# Data rows with alternating colors
pdf.set_font('Courier', '', 9)
for idx, row_data in enumerate(data):
    fill_color = (245, 245, 255) if idx % 2 == 0 else (255, 255, 255)
    pdf.set_fill_color(*fill_color)
    for i, val in enumerate(row_data):
        pdf.cell(col_w[i], 6, str(val), border=1, align='C', fill=True)
    pdf.ln()
```

## Answer Highlighting

```python
pdf.set_font('Helvetica', 'B', 14)
pdf.set_fill_color(220, 255, 220)
pdf.set_draw_color(0, 150, 0)
pdf.set_x(pdf.l_margin)
pdf.cell(pdf.epw, 12, f'  Answer: Loss = {value:.4f}', border=1, align='C', fill=True)
```

## When to Use fpdf2 vs reportlab

| Criterion | fpdf2 | reportlab |
|-----------|-------|-----------|
| Install size | ~200KB | ~5MB |
| Math/code output | Excellent (Courier inline) | Good (needs Paragraph markup) |
| Complex layouts | Limited | Full Platypus framework |
| Tables | Manual cell-by-cell | Table + TableStyle objects |
| Unicode/subscripts | Native support | Needs XML tags (<sub>/<super>) |
| Speed | Fast | Moderate |

Use fpdf2 for: homework solutions, code output, simple reports.
Use reportlab for: formal reports, complex multi-column layouts, fillable forms.
