#!/usr/bin/env python3
"""Homework PDF template — reportlab Platypus. Copy and modify."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import math, sys

OUTPUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/homework.pdf"

DARK_BLUE = HexColor("#1a365d")
MID_BLUE  = HexColor("#2b6cb0")
LIGHT_GRAY = HexColor("#f7fafc")
BORDER_GRAY = HexColor("#cbd5e0")
ACCENT_GREEN = HexColor("#276749")

def build_styles():
    ss = getSampleStyleSheet()
    S = {}
    S['Title'] = ParagraphStyle('T', parent=ss['Title'], fontSize=20, leading=26,
        textColor=DARK_BLUE, spaceAfter=4*mm, fontName='Helvetica-Bold', alignment=TA_CENTER)
    S['Subtitle'] = ParagraphStyle('Sub', parent=ss['Normal'], fontSize=11, leading=14,
        textColor=MID_BLUE, spaceAfter=2*mm, fontName='Helvetica', alignment=TA_CENTER)
    S['StudentInfo'] = ParagraphStyle('SI', parent=ss['Normal'], fontSize=12, leading=16,
        textColor=MID_BLUE, spaceAfter=8*mm, fontName='Helvetica-Bold', alignment=TA_CENTER)
    S['H1'] = ParagraphStyle('H1', parent=ss['Heading1'], fontSize=16, leading=20,
        textColor=DARK_BLUE, spaceBefore=8*mm, spaceAfter=4*mm, fontName='Helvetica-Bold')
    S['H2'] = ParagraphStyle('H2', parent=ss['Heading2'], fontSize=13, leading=17,
        textColor=MID_BLUE, spaceBefore=5*mm, spaceAfter=3*mm, fontName='Helvetica-Bold')
    S['Body'] = ParagraphStyle('B', parent=ss['Normal'], fontSize=10.5, leading=15,
        textColor=black, spaceAfter=2*mm, fontName='Helvetica', alignment=TA_JUSTIFY)
    S['Math'] = ParagraphStyle('M', parent=ss['Normal'], fontSize=10, leading=14,
        textColor=HexColor("#1a202c"), spaceAfter=1.5*mm, fontName='Courier', leftIndent=8*mm)
    S['MathHL'] = ParagraphStyle('MH', parent=S['Math'], textColor=ACCENT_GREEN, fontName='Courier-Bold')
    S['Answer'] = ParagraphStyle('A', parent=ss['Normal'], fontSize=11, leading=15,
        textColor=ACCENT_GREEN, spaceAfter=3*mm, fontName='Helvetica-Bold', leftIndent=4*mm)
    S['Note'] = ParagraphStyle('N', parent=ss['Normal'], fontSize=9.5, leading=13,
        textColor=HexColor("#4a5568"), spaceAfter=2*mm, fontName='Helvetica-Oblique', leftIndent=6*mm)
    S['CellN'] = ParagraphStyle('CN', parent=ss['Normal'], fontSize=9.5, leading=13,
        fontName='Helvetica', alignment=TA_CENTER)
    S['CellB'] = ParagraphStyle('CB', parent=S['CellN'], fontName='Helvetica-Bold', textColor=DARK_BLUE)
    S['CellH'] = ParagraphStyle('CH', parent=S['CellN'], fontName='Helvetica-Bold', textColor=white)
    return S

def make_table(data, col_widths=None, header_row=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header_row else 0)
    cmds = [
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5), ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_GRAY),
    ]
    if header_row:
        cmds += [('BACKGROUND', (0,0), (-1,0), DARK_BLUE), ('TEXTCOLOR', (0,0), (-1,0), white),
                 ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0,i), (-1,i), LIGHT_GRAY))
    t.setStyle(TableStyle(cmds))
    return t

def build_doc(S):
    story = []
    # === STUDENT INFO (MANDATORY) ===
    story.append(Paragraph("Homework Title Here", S['Title']))
    story.append(Paragraph("Course Name", S['Subtitle']))
    story.append(Paragraph("Name: Wang Ruifan &nbsp;&nbsp;&nbsp; Student ID: 1230027498", S['StudentInfo']))
    # === ADD CONTENT BELOW ===
    # story.append(Paragraph("Q1. ...", S['H1']))
    # story.append(Paragraph("content", S['Body']))
    # story.append(Paragraph("answer", S['Answer']))
    return story

def main():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    S = build_styles()
    doc.build(build_doc(S))
    print(f"PDF generated: {OUTPUT}")

if __name__ == "__main__":
    main()
