#!/usr/bin/env python3
"""
Homework/Solution PDF Template — reportlab Platypus
Copy this file, replace content in build_doc(), and run.
Produces professional academic PDFs with tables, math, and colored sections.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUTPUT = "output.pdf"

# ── Color palette ──────────────────────────────────────────────
DARK_BLUE    = HexColor("#1a365d")
MID_BLUE     = HexColor("#2b6cb0")
LIGHT_GRAY   = HexColor("#f7fafc")
BORDER_GRAY  = HexColor("#cbd5e0")
ACCENT_GREEN = HexColor("#276749")

# ── Styles ─────────────────────────────────────────────────────
def build_styles():
    ss = getSampleStyleSheet()
    S = {}
    S['Title'] = ParagraphStyle('T', parent=ss['Title'], fontSize=20, leading=26,
        textColor=DARK_BLUE, spaceAfter=4*mm, fontName='Helvetica-Bold', alignment=TA_CENTER)
    S['Subtitle'] = ParagraphStyle('Sub', parent=ss['Normal'], fontSize=11, leading=14,
        textColor=MID_BLUE, spaceAfter=8*mm, fontName='Helvetica', alignment=TA_CENTER)
    S['H1'] = ParagraphStyle('H1', parent=ss['Heading1'], fontSize=16, leading=20,
        textColor=DARK_BLUE, spaceBefore=10*mm, spaceAfter=4*mm, fontName='Helvetica-Bold')
    S['H2'] = ParagraphStyle('H2', parent=ss['Heading2'], fontSize=13, leading=17,
        textColor=MID_BLUE, spaceBefore=6*mm, spaceAfter=3*mm, fontName='Helvetica-Bold')
    S['H3'] = ParagraphStyle('H3', parent=ss['Heading3'], fontSize=11, leading=15,
        textColor=HexColor("#2d3748"), spaceBefore=4*mm, spaceAfter=2*mm, fontName='Helvetica-Bold')
    S['Body'] = ParagraphStyle('B', parent=ss['Normal'], fontSize=10.5, leading=15,
        textColor=black, spaceAfter=2*mm, fontName='Helvetica', alignment=TA_JUSTIFY)
    S['Bold'] = ParagraphStyle('Bd', parent=S['Body'], fontName='Helvetica-Bold')
    S['Math'] = ParagraphStyle('M', parent=ss['Normal'], fontSize=10, leading=14,
        textColor=HexColor("#1a202c"), spaceAfter=1.5*mm, fontName='Courier', leftIndent=8*mm)
    S['MathHL'] = ParagraphStyle('MH', parent=S['Math'],
        textColor=ACCENT_GREEN, fontName='Courier-Bold')  # highlighted result
    S['Answer'] = ParagraphStyle('A', parent=ss['Normal'], fontSize=11, leading=15,
        textColor=ACCENT_GREEN, spaceAfter=3*mm, fontName='Helvetica-Bold', leftIndent=4*mm)
    S['Note'] = ParagraphStyle('N', parent=ss['Normal'], fontSize=9.5, leading=13,
        textColor=HexColor("#4a5568"), spaceAfter=2*mm, fontName='Helvetica-Oblique', leftIndent=6*mm)
    # Table cell styles
    S['CellN'] = ParagraphStyle('CN', parent=ss['Normal'], fontSize=9.5, leading=13,
        fontName='Helvetica', alignment=TA_CENTER)
    S['CellB'] = ParagraphStyle('CB', parent=S['CellN'],
        fontName='Helvetica-Bold', textColor=DARK_BLUE)
    S['CellH'] = ParagraphStyle('CH', parent=S['CellN'],
        fontName='Helvetica-Bold', textColor=white)
    return S

# ── Styled table helper ────────────────────────────────────────
def make_table(data, col_widths=None, header_row=True):
    """data: list of lists of Paragraph objects. First row = header if header_row."""
    t = Table(data, colWidths=col_widths, repeatRows=1 if header_row else 0)
    cmds = [
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5), ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8), ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_GRAY),
    ]
    if header_row:
        cmds += [
            ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0,i), (-1,i), LIGHT_GRAY))
    t.setStyle(TableStyle(cmds))
    return t

# ── Document content (replace this) ────────────────────────────
def build_doc(S):
    story = []
    story.append(Paragraph("Homework Title", S['Title']))
    # ALWAYS include student name and ID below the title
    story.append(Paragraph("Name: Wang Ruifan &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Student ID: 1230027498", S['Subtitle']))
    story.append(Paragraph("Subtitle or description", S['Note']))

    story.append(Paragraph("Q1: Question Title", S['H1']))
    story.append(Paragraph("Body text goes here.", S['Body']))

    # Math block (Courier font, monospaced for alignment)
    story.append(Paragraph("Step 1: description", S['H3']))
    story.append(Paragraph("formula = value", S['Math']))
    story.append(Paragraph("result = final_value", S['MathHL']))  # green highlight

    # Table example
    story.append(Paragraph("Summary", S['H2']))
    tbl = make_table([
        [Paragraph("<b>Col1</b>", S['CellH']), Paragraph("<b>Col2</b>", S['CellH'])],
        [Paragraph("val", S['CellN']),  Paragraph("<b>42</b>", S['CellB'])],
    ], col_widths=[150, 100])
    story.append(tbl)

    # Answer highlight
    story.append(Paragraph("Answer: the result is 42.", S['Answer']))
    story.append(Paragraph("Note: explanation or caveat.", S['Note']))

    return story

# ── Main ────────────────────────────────────────────────────────
def main():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    S = build_styles()
    doc.build(build_doc(S))
    print(f"PDF generated: {OUTPUT}")

if __name__ == "__main__":
    main()
