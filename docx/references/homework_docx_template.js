/**
 * Homework/Solution DOCX Template — docx-js (Node.js)
 * Copy this file, replace content in the `questions` array or `story` sections, and run.
 * Produces professional academic Word documents with styled tables, colored sections.
 *
 * Usage: NODE_PATH=$(npm root -g) node homework_docx_template.js
 */
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, LevelFormat
} = require("docx");

const OUTPUT = "homework_output.docx";

// ── Shared table helpers ───────────────────────────────────────
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellPad = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: "1A365D", type: ShadingType.CLEAR },
    margins: cellPad, verticalAlign: "center",
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })
    ]})]
  });
}

function dataCell(text, width, opts = {}) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: opts.shade ? { fill: "F7FAFC", type: ShadingType.CLEAR } : undefined,
    margins: cellPad, verticalAlign: "center",
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({
        text, bold: opts.bold || false, color: opts.color || "000000",
        font: "Arial", size: 20
      })]
    })]
  });
}

// ── Document content (replace this section) ─────────────────────
const story = [];

// Title — ALWAYS include student name and ID below the title
story.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [
  new TextRun({ text: "Homework Title", bold: true, size: 36, color: "1A365D", font: "Arial" })
]}));
story.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [
  new TextRun({ text: "Name: Wang Ruifan          Student ID: 1230027498", bold: true, size: 24, color: "2B6CB0", font: "Arial" })
]}));
story.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [
  new TextRun({ text: "Subtitle or description", size: 20, color: "4A5568", font: "Arial", italics: true })
]}));

// Section heading
story.push(new Paragraph({ spacing: { before: 300, after: 150 }, children: [
  new TextRun({ text: "Q1: Question Title", bold: true, size: 24, color: "1A365D", font: "Arial" })
]}));

// Body text
story.push(new Paragraph({ spacing: { after: 150 }, children: [
  new TextRun({ text: "Body text goes here. Add explanations and calculations.", size: 21, font: "Arial" })
]}));

// Indented math (use Courier for monospaced alignment)
story.push(new Paragraph({ spacing: { after: 80 }, indent: { left: 360 }, children: [
  new TextRun({ text: "formula = value", font: "Courier", size: 20 })
]}));

// Highlighted result (green)
story.push(new Paragraph({ spacing: { after: 80 }, indent: { left: 360 }, children: [
  new TextRun({ text: "result = 42", font: "Courier-Bold", size: 20, color: "276749" })
]}));

// Answer line (green bold)
story.push(new Paragraph({ spacing: { before: 200, after: 100 }, children: [
  new TextRun({ text: "Answer: the result is 42.", bold: true, size: 22, color: "276749", font: "Arial" })
]}));

// Separator line
story.push(new Paragraph({
  spacing: { before: 200, after: 100 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CBD5E0", space: 1 } },
  children: []
}));

// Summary table example
story.push(new Paragraph({ spacing: { before: 300, after: 200 }, children: [
  new TextRun({ text: "Summary Table", bold: true, size: 28, color: "1A365D", font: "Arial" })
]}));

story.push(new Table({
  width: { size: 9026, type: WidthType.DXA },  // A4 with 2cm margins
  columnWidths: [3000, 2000, 4026],
  rows: [
    new TableRow({ children: [
      headerCell("Column 1", 3000), headerCell("Column 2", 2000), headerCell("Column 3", 4026)
    ]}),
    new TableRow({ children: [
      dataCell("Value A", 3000, { center: true }),
      dataCell("42", 2000, { center: true, bold: true, color: "1A365D" }),
      dataCell("Description", 4026)
    ]}),
    new TableRow({ children: [
      dataCell("Value B", 3000, { center: true, shade: true }),
      dataCell("99", 2000, { center: true, bold: true, color: "1A365D", shade: true }),
      dataCell("Another description", 4026, { shade: true })
    ]}),
  ]
}));

// ── Build document ──────────────────────────────────────────────
const doc = new Document({
  styles: { default: { document: { run: { font: "Arial", size: 24 } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },  // A4
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "Homework Header", size: 16, color: "999999", font: "Arial", italics: true })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "Page ", size: 16, color: "999999", font: "Arial" }),
          new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "999999", font: "Arial" })
        ]
      })] })
    },
    children: story
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT, buffer);
  console.log("DOCX generated: " + OUTPUT);
});
