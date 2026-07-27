# Office File Text Extraction — Fallback Patterns

## PowerPoint (.pptx)

### Problem
The standard text extraction pipeline sometimes truncates or misses slides, especially later slides in large presentations. This happened with a 62-slide PPT where slides 57-62 were missing from the extracted context.

### Solution: python-pptx direct extraction
```bash
python3 -c "
from pptx import Presentation
prs = Presentation('file.pptx')
for i, slide in enumerate(prs.slides):
    print(f'=== Slide {i+1} ===')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                text = p.text.strip()
                if text: print(text)
    print()
"
```

For tables within slides:
```python
from pptx import Presentation
prs = Presentation('file.pptx')
for i, slide in enumerate(prs.slides):
    print(f'=== Slide {i+1} ===')
    for shape in slide.shapes:
        if shape.has_table:
            table = shape.table
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                print(' | '.join(cells))
```

### Why this works
PPTX files are ZIP archives containing XML. python-pptx reads the XML directly, bypassing any rendering or text extraction pipeline that might truncate content.

## Excel (.xls / .xlsx)

### For .xlsx (modern format):
```bash
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('file.xlsx')
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    print(f'=== Sheet: {sheet_name} ===')
    for row in ws.iter_rows(values_only=True):
        print(' | '.join([str(c) if c is not None else '' for c in row]))
"
```

### For .xls (legacy format):
openpyxl cannot read .xls. Use xlrd:
```bash
pip install xlrd
python3 -c "
import xlrd
wb = xlrd.open_workbook('file.xls')
for sheet in wb.sheets():
    print(f'=== Sheet: {sheet.name} ===')
    for row_idx in range(sheet.nrows):
        print(' | '.join([str(sheet.cell_value(row_idx, c)) for c in range(sheet.ncols)]))
"
```

## When to use this
- Standard pipeline output is truncated or shows empty slides
- The file is on the local filesystem (Desktop, Downloads, project directory)
- python-pptx / openpyxl / xlrd are available in the Python environment
