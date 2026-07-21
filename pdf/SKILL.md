---
name: pdf
description: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see REFERENCE.md. If you need to fill out a PDF form, read FORMS.md and follow its instructions.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

#### Subscripts and Superscripts

**IMPORTANT**: Never use Unicode subscript/superscript characters (₀₁₂₃₄₅₆₇₈₉, ⁰¹²³⁴⁵⁶⁷⁸⁹) in ReportLab PDFs. The built-in fonts do not include these glyphs, causing them to render as solid black boxes.

Instead, use ReportLab's XML markup tags in Paragraph objects:
```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# Subscripts: use <sub> tag
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# Superscripts: use <super> tag
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

For canvas-drawn text (not Paragraph objects), manually adjust font the size and position rather than using Unicode subscripts/superscripts.

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Academic Homework PDF Generation (reportlab Platypus)

When generating homework/solution PDFs, use reportlab's **Platypus** framework (not canvas). Key pattern:

1. Build a `SimpleDocTemplate` with A4 pagesize and 2cm margins
2. Define custom `ParagraphStyle` objects for: Title, H1, H2, Body, Math (Courier font), Answer (green, bold), Note (gray, italic)
3. Use `Paragraph` with `<sub>` / `<super>` for math notation (never Unicode subscripts)
4. Use `Table` + `TableStyle` for data tables with header rows (dark blue bg, white text) and alternating row colors
5. Build the `story` list, then `doc.build(story)`
6. **Always verify** by extracting text with `pypdf` to confirm content rendered correctly

Color palette that works well: DARK_BLUE=#1a365d, MID_BLUE=#2b6cb0, ACCENT_GREEN=#276749, BORDER_GRAY=#cbd5e0, LIGHT_GRAY=#f7fafc.

For a complete working template, see `references/homework_pdf_template.py`.

### Technical Documents with Embedded Figures
For generating professional technical PDFs with CJK text, matplotlib charts, math blocks, styled tables, and page headers/footers, see `references/reportlab_technical_doc.md`. This covers the full pipeline: font registration, figure generation with dark themes, figure embedding, math/code/blockquote styled blocks, and common pitfalls.

### Chinese/CJK Content in Reportlab
Reportlab CAN render CJK characters with proper font registration. Register system CJK fonts:
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# macOS fonts:
pdfmetrics.registerFont(TTFont('CJK', '/Library/Fonts/Arial Unicode.ttf'))
pdfmetrics.registerFont(TTFont('CJKBold', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
pdfmetrics.registerFontFamily('CJK', normal='CJK', bold='CJKBold')
```
Then use `fontName='CJK'` / `fontName='CJKBold'` in ParagraphStyle. Works for all Chinese/Japanese/Korean text.

**Font gotcha**: Courier (ASCII-only) renders any non-ASCII Unicode as ■■■■ tofu — Greek letters, box-drawing chars, math operators, arrows all fail. Use CJK font for mixed Unicode content. Also, `TA_JUSTIFY` inserts phantom spaces in Chinese text — use `TA_LEFT`. Both pitfalls detailed in `references/reportlab_technical_doc.md`.

**Flowchart gotcha**: Don't draw flowcharts as ASCII art in code blocks (Unicode box-drawing chars break). Use Canvas vector drawing as a custom Flowable instead. Canvas has no `drawPolygon` — use `beginPath()/drawPath()`. Both pitfalls detailed in `references/reportlab_technical_doc.md`.

**Alternative: Chrome Headless** (for complex CSS layouts):
1. Write content as HTML with inline CSS
2. Run: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --print-to-pdf="output.pdf" --no-margins --no-pdf-header-footer "file:///path/to/input.html"`
Chrome uses system fonts and renders CJK perfectly, plus supports full CSS (flexbox, grid, etc.).

### Alternative: fpdf2 for Lightweight Homework PDFs

For simpler homework/solution PDFs (math step-by-step, code output, tables), fpdf2 is lighter and faster than reportlab. Key gotchas: the `ln` parameter in `cell()` is deprecated since v2.5.2 — use `new_x=XPos.LMARGIN, new_y=YPos.NEXT` instead. Always reset cursor with `pdf.set_x(pdf.l_margin)` before `multi_cell`. Full guide with helper method patterns and table templates: see `references/fpdf2_guide.md`.

### Pitfall: Always Read Referenced Materials

**Critical**: When a homework/exam problem contains a hyperlink or references a specific document (e.g., "参见讲义5", "[词向量](https://...)"), that linked material contains the course-specific terminology, formulas, and notation the instructor expects in the answer. **Always read the referenced document before answering.** The answer must incorporate course-specific content (equation numbers, slide references, specific model names from lecture), not just generic knowledge. The user will notice and explicitly call out missing references.

## When to Choose PDF vs DOCX
**When to choose PDF vs DOCX**:
- **PDF (reportlab)**: Precise math layout, formula positioning, complex tables, colored diagrams. Best for technical homework with calculations.
- **DOCX (docx-js)**: Simple text answers, MCQ with explanations, collaborative editing needed. Faster to generate for text-heavy content. See the `docx` skill's `references/homework_docx_template.js`.
- **PDF with Chinese/CJK**: Use Chrome headless (see html-to-pdf-macos skill), NOT reportlab.
- Choose automatically based on task — do not ask the user which format.

### Academic Document Requirements
**Always include student name and ID** on homework/solution documents (title area). Example: "Name: Wang Ruifan          Student ID: 1230027498". This is a hard requirement — omitting it will trigger user frustration.

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab or fpdf2 | Canvas/Platypus or cell-based (see references/fpdf2_guide.md) |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see FORMS.md) | See FORMS.md |

## Next Steps

- For advanced pypdfium2 usage, see REFERENCE.md
- For JavaScript libraries (pdf-lib), see REFERENCE.md
- If you need to fill out a PDF form, follow the instructions in FORMS.md
- For troubleshooting guides, see REFERENCE.md
