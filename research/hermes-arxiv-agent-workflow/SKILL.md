---
name: hermes-arxiv-agent-workflow
description: >
  Execute the hermes-arxiv-agent daily workflow: run monitor.py, extract affiliations from PDFs,
  generate Chinese summaries, update Excel, rebuild viewer data, and sync pending state.
  Use when running the arxiv agent cron job or processing new papers manually.
  Complements hermes-arxiv-agent-deploy (which covers initial setup).
tags: [arxiv, pdf, affiliation-extraction, academic-papers, cron-workflow]
triggers:
  - "run arxiv agent"
  - "process new papers"
  - "extract affiliations from PDF"
  - "arxiv daily workflow"
  - "monitor.py"
---

# hermes-arxiv-agent Workflow Execution

## Overview

This skill covers the daily execution workflow for hermes-arxiv-agent. For initial deployment/setup, see `hermes-arxiv-agent-deploy`.

## Workflow Steps

### Step 1: Run monitor.py

```bash
cd /Users/wangruifan/projects/hermes-arxiv-agent && python3 monitor.py
```

**Timeout**: Use 300s+ timeout. arXiv API frequently returns 429 (rate limit) and may need multiple retries. The script's built-in retry logic handles this, but the overall command can take 2-3 minutes.

**Expected output patterns**:
- `No new papers` → No action needed, report "✅ 今日（YYYY-MM-DD）未发现新的论文。"
- `LLM_SUMMARIZATION_REQUIRED` → Proceed to Step 2

### Step 2: Read new_papers.json

```python
import json
with open('/Users/wangruifan/projects/hermes-arxiv-agent/new_papers.json') as f:
    data = json.load(f)
```

Key fields:
- `new_count`: papers newly crawled this run
- `pending_count`: papers still needing LLM completion
- `papers_to_process`: list of papers to process (preferred over `new_papers`)

### Step 3: Extract Affiliations from PDFs

**Critical technique**: Do NOT rely on regex pattern matching for affiliation extraction. Academic PDFs have complex layouts that defeat simple regex.

**Correct approach**:

1. Use PyMuPDF (`fitz`) to read first page text:
```python
import fitz
doc = fitz.open(pdf_path)
text = doc[0].get_text()
doc.close()
```

2. Parse the structured author-affiliation block. Academic papers typically have this layout:
```
Author Name1, Author Name2
email1@university.edu
University Name1
email2@institute.edu
Institute Name2
```

3. **Key insight**: Look for email addresses and their surrounding context. The institution name is usually on the line immediately after or before the email. Extract by:
   - Splitting text into lines
   - Finding lines with `@` (email addresses)
   - The institution is typically the line containing "University", "Institute", "College", "Department", etc.
   - Also check the line immediately above/below the email

4. **Fallback**: If no emails found, look for known institution patterns in the first 50 lines:
```python
known_institutions = [
    'MIT', 'Stanford', 'Google', 'Microsoft', 'Meta',
    'University of', 'Institute of', 'KU Leuven',
    'Tsinghua', 'Peking', 'Zhejiang', 'KAIST',
    # ... expand as needed
]
```

5. **Cleaning rules**:
   - Remove URLs, email addresses
   - Remove footnote markers (†, ‡, §, ¶, *)
   - Remove superscript numbers (1, 2, 3)
   - Fix CamelCase: "DepartmentofCS" → "Department of CS"
   - Merge hyphenated line breaks: "Repub-" + "lic of Korea" → "Republic of Korea"
   - Remove consecutive 18+ char strings without spaces (likely noise)
   - Join multiple affiliations with `; `

6. **Quality check**: If result contains words like "memory", "computational", "quantization", "method", "performance" → it's extracting abstract text, not affiliations. Retry with different line range.

### Step 4: Generate Chinese Summary (summary_cn)

For each paper's abstract, generate 90-150 Chinese characters covering:
- Method core (what technique/approach)
- Main contribution (what's new)
- Key results (what benchmarks, what improvement)

**Anti-patterns to avoid**:
- Template phrases like "提出新型方法" without specifics
- Copy-pasting English abstract fragments
- Generic statements that could apply to any paper

### Step 5: Update Excel

```python
import openpyxl

wb = openpyxl.load_workbook(excel_path)
ws = wb.active
header = [cell.value for cell in ws[1]]

# Find columns by name
arxiv_id_col = next(i+1 for i, h in enumerate(header) if h and 'arxiv_id' in str(h).lower())
affiliations_col = next(i+1 for i, h in enumerate(header) if h and 'affiliations' in str(h).lower())
summary_cn_col = next(i+1 for i, h in enumerate(header) if h and 'summary_cn' in str(h).lower())

# Update by matching arxiv_id
for row in ws.iter_rows(min_row=2):
    if str(row[arxiv_id_col-1].value).strip() == arxiv_id:
        row[affiliations_col-1].value = affiliations
        row[summary_cn_col-1].value = summary_cn

wb.save(excel_path)
```

### Step 6: Rebuild Viewer Data

```bash
cd /Users/wangruifan/projects/hermes-arxiv-agent && python3 viewer/build_data.py
```

Expected: `[OK] Wrote N papers to viewer/papers_data.json`

### Step 7: Sync Pending State

```bash
cd /Users/wangruifan/projects/hermes-arxiv-agent && python3 monitor.py --sync-pending-state
```

**Important**: Must run AFTER Excel update. This refreshes `pending_llm_ids.txt` and `new_papers.json`.

Expected: `[INFO] Pending LLM state synced from Excel | remaining=0`

### Step 8: Build Feishu Message

Format:
```
📚 **论文日报** | YYYY-MM-DD
共发现 **N** 篇新论文

---
**N. Title**
- arXiv ID: XXXXX.XXXXX
- 日期: YYYY-MM-DD
- 作者: Author1, Author2
- 单位: Institution1; Institution2
- PDF: https://arxiv.org/pdf/XXXXX.XXXXX

[90-150字中文摘要]

---
PDF 已下载至 papers/，记录已更新至 papers_record.xlsx，网站数据已更新至 viewer/papers_data.json。
```

## Pitfalls

1. **arXiv API 429 errors**: Common. Set timeout to 300s+. The script retries automatically but overall execution may take 2-3 minutes.

2. **PDF affiliation extraction**: Regex-based extraction is unreliable. Always use the structured parsing approach (Step 3).

3. **Summary length**: Must be 90-150 Chinese characters. Count characters after generation. Too short = missing key details; too long = verbose.

4. **Order matters**: Excel update → viewer rebuild → sync pending state. Running sync before update will lose pending papers.

5. **CamelCase in affiliations**: Academic PDFs often merge words in author blocks. Always apply CamelCase splitting.

## File Locations

- Project root: `/Users/wangruifan/projects/hermes-arxiv-agent`
- PDFs: `papers/`
- Excel: `papers_record.xlsx`
- Intermediate JSON: `new_papers.json`
- Pending IDs: `pending_llm_ids.txt`
- Viewer data: `viewer/papers_data.json`

## Skill Files

- `scripts/extract_affiliations.py` — Reusable affiliation extraction script
- `references/pdf-patterns.md` — Real examples of PDF affiliation patterns
