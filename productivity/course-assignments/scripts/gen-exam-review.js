/** gen-exam-review.js
 *  Generate CS463 exam review Word document from curated JSON question bank.
 *  Usage: NODE_PATH=$(npm root -g) node gen-exam-review.js /path/to/questions.json output.docx
 */

const fs = require('fs');
const { Document, Packer, Paragraph, TextRun,
        Header, Footer, AlignmentType, LevelFormat,
        HeadingLevel, BorderStyle, WidthType, ShadingType,
        PageNumber, PageBreak } = require('docx');

const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outputPath = process.argv[3] || 'DL_Final_Exam_Review.docx';

// Build children array from data.sections
const children = [];
const accentColor = "2E75B6";

// Title
children.push(new Paragraph({ spacing: { before: 1200 }, children: [] }));
children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: data.title, font: "Arial", size: 44, bold: true, color: "1A3A5C" })]
}));
children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
    children: [new TextRun({ text: data.subtitle || "", font: "Arial", size: 24, color: "666666" })]
}));
children.push(new Paragraph({
    spacing: { after: 400 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: accentColor, space: 1 } },
    children: []
}));

// Sections
data.sections.forEach((section, si) => {
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: section.name, font: "Arial", size: 28, bold: true })]
    }));
    if (section.description) {
        children.push(new Paragraph({
            spacing: { after: 200 },
            children: [new TextRun({ text: section.description, font: "Arial", size: 20, italics: true, color: "555555" })]
        }));
    }

    section.questions.forEach((q, qi) => {
        children.push(new Paragraph({
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 240, after: 80 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: accentColor, space: 4 } },
            children: [new TextRun({ text: q.topic || `Q${qi+1}`, font: "Arial", size: 22, bold: true, color: accentColor })]
        }));
        children.push(new Paragraph({
            spacing: { before: 80, after: 80 },
            children: [new TextRun({ text: (q.q || "").substring(0, 500), font: "Arial", size: 20 })]
        }));

        if (q.options && q.options.length > 0) {
            q.options.forEach(opt => {
                const isCorrect = q.answer && opt === q.answer;
                children.push(new Paragraph({
                    spacing: { after: 30 }, indent: { left: 360 },
                    children: [new TextRun({
                        text: isCorrect ? `${opt} ✅` : opt,
                        font: "Arial", size: 19,
                        bold: isCorrect, color: isCorrect ? "2E7D32" : "333333"
                    })]
                }));
            });
        }

        if (q.answer) {
            children.push(new Paragraph({
                spacing: { before: 40, after: 60 }, indent: { left: 200 },
                children: [
                    new TextRun({ text: "✅ ", font: "Arial", size: 19, bold: true, color: "2E7D32" }),
                    new TextRun({ text: q.answer.substring(0, 800), font: "Arial", size: 19 })
                ]
            }));
        }

        if (q.explanation) {
            children.push(new Paragraph({
                spacing: { before: 20, after: 80 }, indent: { left: 200 },
                children: [new TextRun({ text: "💡 " + q.explanation.substring(0, 400), font: "Arial", size: 18, italics: true, color: "666666" })]
            }));
        }
    });

    if (si < data.sections.length - 1) {
        children.push(new Paragraph({ children: [new PageBreak()] }));
    }
});

const doc = new Document({
    styles: {
        default: { document: { run: { font: "Arial", size: 22 } } },
        paragraphStyles: [
            { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
              run: { size: 28, bold: true, font: "Arial", color: "1A3A5C" },
              paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 0 } },
            { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
              run: { size: 22, bold: true, font: "Arial", color: accentColor },
              paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
        ]
    },
    sections: [{
        properties: {
            page: {
                size: { width: 12240, height: 15840 },
                margin: { top: 1200, right: 1200, bottom: 1200, left: 1200 }
            }
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC", space: 4 } },
                    children: [new TextRun({ text: "CS463 Deep Learning — Final Exam Review", font: "Arial", size: 16, color: "999999", italics: true })]
                })]
            })
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    alignment: AlignmentType.CENTER,
                    border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC", space: 4 } },
                    children: [new TextRun({ text: "Page ", font: "Arial", size: 16, color: "999999" }),
                              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" })]
                })]
            })
        },
        children
    }]
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(outputPath, buffer);
    console.log(`Written ${(buffer.length/1024).toFixed(1)}KB to ${outputPath}`);
});
