# PDF Affiliation Extraction — Working Approach

## Reliable Method

arXiv papers typically have affiliations on the first page, directly below author names.
Common patterns:

- Superscript numbers: `1 Harvard University`, `2 Google DeepMind`
- Daggers/carets: `† University of Macau`, `‡ Guangdong Institute of Intelligence Science and Technology`
- Plain text after author block (no markers): all authors share one affiliation
- Numbered footnotes with full sentences: `1Author X and Author Y are with Institution Z, City, Country.`

## Tools

### PyMuPDF (fitz) — preferred
```bash
pip3 install pymupdf
```
```python
import fitz
doc = fitz.open(pdf_path)
text = ""
for i in range(min(2, len(doc))):
    text += doc[i].get_text()
doc.close()
```

### pdfplumber — alternative
```bash
pip3 install pdfplumber
```
```python
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    text = "\n".join(page.extract_text() or "" for page in pdf.pages[:2])
```

## Script Template

Write this to a temp `.py` file and run via `terminal`:

```python
import fitz
import re

def extract_affiliations(pdf_path):
    """Read first 2 pages, look for affiliation patterns."""
    doc = fitz.open(pdf_path)
    text = ""
    for i in range(min(2, len(doc))):
        text += doc[i].get_text()
    doc.close()

    # Merge hyphenated line breaks
    text = re.sub(r'-\s*\n\s*', '', text)
    lines = text.split('\n')

    # Strategy 1: Look for footnote-style affiliations
    # Pattern: "1Author X and Author Y are with Institution Z"
    footnote_pattern = re.compile(r'^\s*(\d+)\s+(.+?)(?:,\s*|$)')

    aff_lines = []
    abstract_idx = len(lines)

    # Find abstract start
    for i, line in enumerate(lines):
        if re.match(r'^\s*abstract', line.strip(), re.IGNORECASE):
            abstract_idx = i
            break

    # Scan between title and abstract
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped or i < 3:
            continue
        if i >= abstract_idx:
            break

        # Skip non-affiliation lines
        if re.match(r'^(arXiv:|http|www\.|email|@|\d{4}\.)', line_stripped):
            continue
        if len(line_stripped) > 200:
            continue

        # Match footnote-style: "1Institution name"
        fm = footnote_pattern.match(line_stripped)
        if fm:
            aff_text = fm.group(2).strip()
            # Check if it looks like an affiliation
            if any(kw in aff_text.lower() for kw in [
                'university', 'institute', 'research', 'lab', 'school',
                'department', 'college', 'center', 'centre', 'faculty',
                'google', 'microsoft', 'meta', 'nvidia', 'intel', 'huawei',
                 'samsung', 'qualcomm', 'sk hyn', 'etri', 'academy',
+                'mit', 'uiuc', 'hust', 'cas', 'iit', 'eth', 'epfl',
             ]):
                aff_lines.append(aff_text)
                continue

        # Match institution keyword lines
        if any(kw in line_stripped.lower() for kw in [
            'university', 'institute', 'research', 'lab', 'school',
            'department', 'college', 'center', 'centre', 'faculty',
            'google', 'microsoft', 'meta', 'nvidia', 'intel', 'huawei',
            'samsung', 'qualcomm', 'sk hyn', 'etri', 'academy',
            'openai', 'anthropic', 'deepmind', 'baidu', 'alibaba',
             'tencent', 'bytedance', 'kaist', 'postech',
+            'mit', 'uiuc', 'hust', 'cas', 'iit', 'eth', 'epfl',
         ]):
            cleaned = re.sub(r'^\s*\d+\s*', '', line_stripped)
            cleaned = re.sub(r'^\*+\s*', '', cleaned)
            cleaned = re.sub(r'^[†‡§]\s*', '', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned and len(cleaned) > 5:
                aff_lines.append(cleaned)

    if aff_lines:
        # Clean and deduplicate
        seen = set()
        result = []
        for aff in aff_lines:
            aff = re.sub(r'[,\s]+$', '', aff)
            # CamelCase splitting
            aff = re.sub(r'([a-z])([A-Z])', r'\1 \2', aff)
            if aff and aff not in seen and len(aff) > 5:
                seen.add(aff)
                result.append(aff)
        return "; ".join(result) if result else "未找到单位信息"

    return "未找到单位信息"
```

## Edge Cases Encountered

| Paper ID | Issue | Resolution |
|----------|-------|------------|
| 2607.01579 | Superscript "1" before affiliation | Stripped number prefix, got "Kempner Institute..." |
| 2607.01607 | Daggers († ‡) marking affiliations | Manual read: † = Macau, ‡ = Guangdong Institute |
| 2607.01831 | Mixed affiliations (UCL + Huawei) | Each author had affiliation inline after name |
| 2607.02371 | Single affiliation, no marker | Plain text after authors: "The Military Technical Academy..." |
| 2607.03652 | CamelCase no-space PDF rendering | `VictorAgostinelli`, `OregonStateUniversity` — split on uppercase boundaries |
| 2606.27205 | Asterisk/dagger markers (∗ †) | ∗ = Simula Research Laboratory, † = University of L'Aquila |
| 2607.05475 | Many authors, mixed affiliations | Each author inline with affiliation and city below; Tsinghua + BJTU |
| 2607.05832 | Clean layout, email-based anchoring | Author emails confirm Duke University and University of Waterloo |
| 2607.08029 | Korean research institute (ETRI) | Footnote "1ETRI, Republic of Korea" — not a university keyword, needed `etri` in match list |
| 2607.08643 | Multi-institution numbered footnotes | Full sentences: "1Author X and Author Y are with Nanjing Univ..."; "2...Institute of Automation, CAS"; "3...Huawei, China" |
| 2607.10137 | Single author, no affiliation visible | First 2 pages had no affiliation text; filled "未找到单位信息" |
| 2607.08734 | Multiple departments, same university | "AI Initiative, UCF; Applied Computer Education Dept; Dept of CS" — all valid, kept all |
| 2607.09999 | Affiliation as city+state line | "College Park, MD, USA" + "University of Maryland" — merged to single entry |
| 2607.14181 | Inline author block with dept+uni on separate lines | Each author: "AURA Lab / Department of Computer Science / William & Mary" — institution spread across 3 lines per author, all same affiliation |
| 2607.14506 | Asterisk/dagger inline markers (∗UIUC, †MIT, ‡Bridgewater) | Multi-institution with acronyms — needed to map ∗→UIUC, †→MIT, ‡→Bridgewater manually; acronyms not in keyword list |
| 2607.14630 | Single author, no institution anywhere | Independent researcher — only a gmail address; legitimate "未找到单位信息" |
| 2607.14661 | Superscript numbers concatenated to institution name (1Nanjing, 2HUST) | No space between digit and name broke the `^\s*\d+\s*(.+)` regex; also "HUST" (acronym) not matched by keyword list |

## Common Pitfalls

- **ETRI and other non-university institutes**: Add `etri`, `sk hyn`, `academy` to keyword list
- **Multi-institution papers**: All affiliations should be kept, separated by `; `
- **Footnote sentences**: "1Author X and Author Y are with Institution Z, City, Country" — extract the institution part, strip the author preamble
- **City/country only lines**: "College Park, MD, USA" alone is not an affiliation; pair with the institution name from the next/previous line
- **Abstract leakage**: Always check `i < abstract_idx` to avoid matching institution names mentioned in the abstract text
- **Concatenated number-institution**: Some PDFs render superscript numbers joined to institution names without a space (e.g., `1Nanjing`, `2HUST`). The regex `^\s*\d+\s*(.+)` fails because there's no whitespace after the digit. Handle with `re.sub(r'^\d+', '', line)` first, then match keywords.
- **Acronym-only institutions**: MIT, UIUC, HUST, CAS, KAIST, ETH, IIT, etc. are valid institutions but won't match keyword-based patterns. When the abstract-index-constrained scan yields nothing, fall back to scanning the first ~800 chars of the full text for known acronyms or email domain hints (e.g., `@illinois.edu` → UIUC, `@mit.edu` → MIT, `@hust.edu.cn` → HUST).
- **Independent researchers**: Some papers have no institution — only a personal email (e.g., gmail). This is a legitimate case for "未找到单位信息".
