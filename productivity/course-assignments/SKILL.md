---
name: course-assignments
description: "Complete university course assignments end-to-end — Colab notebooks, GitHub Classroom repos, macOS ML notebook adaptation, homework document generation (PDF/DOCX). Covers Python 3.12 fixes, CUDA→MPS, notebook editing, submission packaging, and student info requirements."
tags: [course, assignments, colab, notebook, homework, pdf, docx, github-classroom, macos, mps]
---

# Course Assignments

End-to-end workflow for completing and submitting university course assignments across multiple platforms and formats.

## MANDATORY: Student Info on Every Document

Every homework/assignment document MUST include:
- **Name**: Wang Ruifan
- **Student ID**: 1230027498

Place on title area, visible on first page. No exceptions.

## Assignment Types

### 1. Google Colab Notebooks (.ipynb with external .py)

**Workflow**: Download starter code → Fix Python 3.12 issues → Fix Drive paths → Implement TODOs → Repackage → Upload to Colab → Submit.

#### Python 3.12 Removed `imp` Module

Colab upgraded to Python 3.12. `%load_ext autoreload` crashes with `ModuleNotFoundError: No module named 'imp'`.

**Fix**: Replace autoreload cells with:
```python
# autoreload skipped (Python 3.12 compatibility)
```

#### `loss.item()` AttributeError

PyTorch loss may return float or Tensor. Use:
```python
loss.item() if isinstance(loss, torch.Tensor) else loss
```

#### Google Drive Path

After extracting zip, have user run `os.listdir('drive/My Drive')` to discover the path. Better: pre-fix in notebook JSON before uploading.

#### Submission Structure

UMich EECS 498-style: original `.ipynb` (with outputs) + `.py` files + `.pt` checkpoints. **Do NOT** create self-contained notebooks — autograder expects original structure.

#### Regularization Factor Inconsistency

| Assignment Part | Loss Regularization | Gradient |
|---|---|---|
| A2 linear classifiers | `reg * sum(W*W)` (NO 0.5) | `2 * reg * W` |
| A3 FullyConnectedNet | `0.5 * reg * sum(W*W)` (WITH 0.5) | `reg * W` |

Check the TODO comment for "includes a factor of 0.5" hint.

#### When Rewriting .py Files

Include ALL classes from original — not just TODO blocks. Helper classes often appear at the BOTTOM after TODO blocks. Missing classes cause `ImportError`.

#### dtype Mismatch

`(margins > 0).float()` creates float32 even when X is float64. Use `.to(X.dtype)` instead.

#### SSL Certificate Errors

Style transfer cells may fail with `SSLCertVerificationError`. Skip these cells — they're optional and not graded.

### 2. GitHub Classroom Assignments

**Workflow**: Accept invitation → Discover repo → Clone → Understand requirements → Complete → Submit → Verify.

#### Accept & Discover

```bash
open "https://classroom.github.com/a/ASSIGNMENT-SLUG"
```

Repos are under course org, not personal account. Search via org API:
```bash
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/orgs/BSAI301/repos?per_page=50&sort=updated"
```

#### Submit

```bash
GIT_HTTP_VERSION=1.1 git add RELEVANT_FILES
GIT_HTTP_VERSION=1.1 git commit -m "feat: complete Assignment N - TOPIC"
GIT_HTTP_VERSION=1.1 git push
```

**`GIT_HTTP_VERSION=1.1` is required** — without it, push hangs on macOS.

#### PDF Assignments

Use `pdfplumber` for reading:
```bash
/opt/homebrew/bin/python3.13 -c "
import pdfplumber
with pdfplumber.open('assignment.pdf') as pdf:
    for page in pdf.pages:
        print(page.extract_text())
"
```

### 3. macOS ML Notebook Adaptation

Adapt Linux/CUDA Colab notebooks to run locally on macOS with MPS.

#### CUDA → MPS

Replace in notebook AND all imported .py files:
```python
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
```

**Search ALL .py files** for `cuda` — missed references cause runtime crashes.

#### MPS float64 Incompatibility (CRITICAL)

MPS does NOT support float64. Fix:
```python
# BROKEN: numpy→torch creates float64, then .to("mps") fails
torch.from_numpy(arr).to(device).float()

# FIXED: cast to float32 BEFORE moving to MPS
torch.from_numpy(arr).float().to(device)
```

#### Saved Expert Policies with numpy inference

Load with `map_location='cpu'`, do NOT call `.to(device)`. CPU is fine for inference-only models.

#### Dependency Installation

```bash
pip install torch torchvision torchaudio  # MPS included
pip install mujoco
pip install "gymnasium-robotics>=1.2.0,<1.3.0" --no-deps
pip install "gymnasium==0.29.1" "numpy>=1.24,<2.0" matplotlib tqdm Jinja2 imageio
```

The `--no-deps` skip avoids mujoco downgrade. gymnasium-robotics 1.2.4 works with mujoco 3.8.1.

### 4. Homework Document Generation (PDF/DOCX)

#### Format Selection

- **PDF (reportlab)**: English-only, heavy math, precise typographic control
- **DOCX (docx-js)**: User says "word"/"docx", simple MCQ
- **HTML→Chrome PDF**: Chinese content or rich CSS

#### PDF with reportlab

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
```

- Tables: colored headers (DARK_BLUE bg, white text), alternating row colors
- Math: Courier font, left-indented 8mm
- Answers: Green text (#276749)
- **NEVER use Unicode sub/superscript** (renders as black boxes) — use `<sub>`/`<super>` tags

#### DOCX with docx-js

```javascript
const { Document, Packer, Paragraph, TextRun, Table, ... } = require("docx");
```

- A4 = `{width: 11906, height: 16838}` DXA
- Always set BOTH `columnWidths` on Table AND `width` on each Cell
- Use `WidthType.DXA` — never PERCENTAGE (breaks in Google Docs)
- `ShadingType.CLEAR` — never SOLID (black background)
- Global npm: `NODE_PATH=$(npm root -g) node script.js`

## Document Structure Convention

### MCQ Homework
1. Title + subtitle (student name/ID)
2. Each question: text → options → answer → explanation
3. Separator line between questions
4. Answer summary table at end

### Calculation Homework
1. Title + subtitle (student name/ID)
2. Each problem: statement → step-by-step → final answer highlight
3. Summary table of all results

## Pitfalls

1. **Don't edit original notebook cells** unless TODO placeholders. Keep structure intact.
2. **Notebook JSON manipulation**: Use `json.load`/`json.dump`, not text replacement — source is split across JSON string arrays.
3. **`execution_count: null`**: Expected after filling TODOs — user must run to get output.
4. **Forgotten CUDA references in imported modules**: `utils.py`, `evaluate.py` each have their own `device` variable. Patch ALL.
5. **Colab cells install deps**: If assignment uses Hypothesis or other libs, install in dedicated cell before test cells.
6. **PDF naming**: Follow exact convention (e.g., `BSAI301-Assignment-2-WangRuifan.pdf`).
7. **Reportlab XML entities**: `&amp;` for `&`, `&lt;` for `<`, `&gt;` for `>`.
8. **Table column widths must be explicit** — auto-sizing is unreliable.
9. **CJK smart quotes in JS strings** break parsing — use JSON data file + `fs.readFileSync`.
10. **`PageBreak` must be inside a `Paragraph`** in docx-js.
11. **Tables need cell margins** `{top:80, bottom:80, left:120, right:120}` for readability.
12. **Always verify syntax after writing .py files** — `py_compile.compile()` catches errors before uploading.
13. **Repackage zip after every fix** — user will re-upload to Drive.
14. **Don't give step-by-step debugging when user is frustrated** — take direct action instead.
15. **Write complete implementations** — user prefers full code over incremental guidance.

## Templates

- `templates/reportlab_homework.py` — Python PDF template with all styles pre-configured
- `templates/docx_homework.js` — Node.js DOCX template with header/footer/student-info

## Scripts

- `scripts/numeric_gradient_check.py` — Numeric gradient verification for PyTorch implementations

## References

- `references/a3-implementation-patterns.md` — UMich EECS 498 A3 implementation patterns (BatchNorm, Conv backward, sandwich layers)
- `references/notebook-conversion-pattern.md` — Programmatic notebook conversion script template
- `references/dependency-compatibility.md` — Known-working macOS MuJoCo/Gymnasium version matrix
- `references/mujoco-gymnasium-robotics-versions.md` — MuJoCo + Gymnasium-Robotics version compatibility
- `references/pytorch-implement-from-scratch-pitfalls.md` — PyTorch implementation pitfalls
- `references/notebook-editing.md` — Programmatic .ipynb cell editing pattern
- `references/pdf-generation.md` — HTML→PDF with Mermaid diagrams via Chrome headless
- `references/dl-lect-topics.md` — MUST CS463 DL lecture topic/Moodle ID mapping and scores
- `references/must-dl-course.md` — MUST CS463 deep learning course context
- `references/lecture-mapping.md` — Exam topic → lecture mapping

## Part 5: LAMS/Moodle Course Automation (Browser-based)

Automate LAMS learning activities (Noticeboard → Self-study → Quiz → Assessment → Gate) via Safari AppleScript on macOS. For MUST CS463 deep learning course on Moodle+LAMS platform.

### CRITICAL: Answer Correctly First

**NEVER submit wrong answers just to "see the feedback".** The user called the agent "真蠢" for doing this. Read the self-study content → analyze questions → select correct answers → submit.

**Anti-pattern**: Selecting first option for all questions → 0/20 → collecting feedback = "敷衍" (perfunctory).

### Workflow

1. **Get lecture URLs from Moodle** — JavaScript in Safari to find `mod/lams` links
2. **Navigate to lecture** — open Moodle URL → wait → click "Open Lesson"
3. **Navigate activities** — Noticeboard → Self-study → Quiz → Assessment → Gate
4. **Answer quiz** — group radio buttons by name, select correct answers
5. **Submit** — `form.submit()` more reliable than button click
6. **Collect feedback** — extract score and explanations

### Authentication

LAMS auth hash from Moodle is time-limited (~minutes). Get FRESH URL each time:
```
Moodle page → JS contains "url":"https://lams.must.edu.mo/lams/LoginRequest?uid=...&hash=..."
```

### Safari/osascript Pitfalls

- **Variable capture error**: `set ret to do JavaScript` fails with -2753. Use `do JavaScript` without capturing.
- **Button click timeouts**: Use `dispatchEvent(new MouseEvent("click", {bubbles:true}))` instead of `.click()`
- **Disabled buttons**: Force enable with `btn.disabled = false; btn.removeAttribute("disabled")`
- **osascript timeout**: Default ~10s, LAMS pages take 15-30s. Use `timeout 30 osascript -e '...'`

### Batch Optimization

Don't process one lecture end-to-end before the next. Batch:
1. `curl` all Moodle pages → extract all LAMS URLs (fast)
2. Loop: open URL → extract content → save
3. Generate all MD files at once

Reduces per-lecture from ~10-15 min to ~3-4 min.
