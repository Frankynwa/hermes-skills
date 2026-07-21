---
name: hermes-arxiv-agent-deploy
description: Deploy hermes-arxiv-agent for daily arXiv paper monitoring with Feishu delivery. Covers repo setup, cron job creation, and known operational pitfalls.
category: research
tags: [arxiv, papers, monitoring, feishu, cron]
---

# Hermes arXiv Agent Deploy

Deploy the hermes-arxiv-agent project for daily arXiv paper monitoring with Feishu (飞书) delivery.

## Trigger

Use when:
- User wants to set up daily arXiv paper monitoring
- User mentions hermes-arxiv-agent, arxiv monitor, or paper monitoring cron
- User needs to fix or update the cron job for this project

## Deployment Steps

### 1. Clone and install

```bash
git clone https://github.com/genggng/hermes-arxiv-agent.git ~/projects/hermes-arxiv-agent
cd ~/projects/hermes-arxiv-agent
pip install requests openpyxl pymupdf
```

### 2. Generate cron prompt

```bash
bash prepare_deploy.sh
```

For GitHub Pages mode: `DEPLOY_MODE=pages bash prepare_deploy.sh`

### 3. Create cron job

Use the generated `cronjob_prompt.generated.txt` to create a Hermes cron job that runs daily.

## Daily Operational Flow

1. `python3 monitor.py` — searches arXiv, downloads new PDFs, writes `new_papers.json`
2. Agent reads `new_papers.json` and processes pending papers:
   - Extract author affiliations from PDF (pdfplumber/PyMuPDF on first 2 pages)
   - Generate Chinese summary (summary_cn, 90-150 chars)
3. Agent updates `papers_record.xlsx` with affiliations and summary_cn
4. `python3 viewer/build_data.py` — rebuilds `viewer/papers_data.json`
5. `python3 monitor.py --sync-pending-state` — syncs `pending_llm_ids.txt`
6. (Optional Pages mode) `bash scripts/publish_viewer.sh` — pushes to GitHub Pages

## Key Files

- `papers_record.xlsx` — source of truth for paper metadata
- `papers/` — downloaded PDFs
- `new_papers.json` — intermediate file for agent processing
- `pending_llm_ids.txt` — papers missing affiliations or summary_cn
- `viewer/papers_data.json` — static site data

## PDF Affiliation Extraction Guidance

Automated regex-based affiliation extraction from PDFs is unreliable — it produces noisy output mixing affiliation text with abstract/formula fragments. The reliable approach:

1. Read the first 2 pages of the PDF with `pdfplumber` or `PyMuPDF` (`fitz`). PyMuPDF is lighter weight and often available when pdfplumber is not: `pip3 install pymupdf`, then `import fitz; doc = fitz.open(path); text = doc[0].get_text() + doc[1].get_text()`
2. Look for the author line and the affiliation line directly beneath it — usually marked with superscript numbers (e.g., `1 Harvard University`) or daggers (e.g., `† University of Macau`)
3. **If nothing found below the author line**, check the page footer / column bottom. In IEEE/ACM two-column format, affiliations often appear as a footnote block in the left-column footer (e.g., `Ren-Yi Huang, Mingchen Li, and Morris Chang are with the Department of Electrical and Computer Engineering, University of South Florida`). Search for patterns like `are with`, `is with`, or email addresses (`@`) in the last few hundred characters of each page.
4. If no clear superscript mapping or footer block, scan for known institution names in the first ~500 characters of text
5. Join multiple affiliations with `; ` — no newlines, no footnote numbers

See `references/pdf-affiliation-extraction.md` for the script template and edge cases from real papers.

**Important**: `execute_code` runs in its own venv. On first run, it will NOT have `pdfplumber`, `pymupdf`, or `openpyxl`. Install them via `terminal(pip3 install pymupdf openpyxl)` before using `execute_code` for PDF extraction or Excel updates. Alternatively, write scripts to a temp `.py` file (via `write_file`) and run them via `terminal(command="python3 /path/to/script.py")` with the system Python.

**Heredoc pitfall**: Do NOT use heredocs (`<< 'EOF'`) in `terminal` when the script contains Chinese characters — the security scanner flags "confusable Unicode characters" and blocks execution. Always write the script to a `.py` file first with `write_file`, then run it with `terminal(command="python3 /path/to/script.py")`. Clean up the temp file after.

**execute_code + Chinese smart quotes pitfall**: `execute_code` runs Python in a sandbox where inline Chinese smart quotes (「""」`\u201c`/`\u201d`) inside string literals cause `SyntaxError`. The parser interprets the opening quote as ending the Python string. Two workarounds: (a) use unicode escapes (`\u201c` for `"`, `\u201d` for `"`) inside string literals, or (b) write the script to a `.py` file with `write_file` and run it via `terminal(command="python3 /path/to/script.py")`. Prefer (b) when the script has multiple Chinese text blocks — it's simpler and avoids escape clutter.

## Known Pitfalls

### PDF Download Failures — Retry with urllib

`monitor.py` downloads PDFs via `requests`, which can fail with `ConnectionResetError(54)` or `Connection aborted` on arXiv's servers. If a PDF is missing after `monitor.py` completes, retry the download manually with `urllib.request` (different HTTP stack, often succeeds):

```python
import urllib.request
url = 'https://arxiv.org/pdf/<paper_id>'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    with open('papers/<paper_id>.pdf', 'wb') as f:
        f.write(resp.read())
```

Always check whether each paper in `papers_to_process` actually has its PDF on disk before starting affiliation extraction.

### CamelCase PDF Text (No Spaces)

Some arXiv PDFs render text without spaces between words due to font encoding issues (e.g., `VictorAgostinelli` instead of `Victor Agostinelli`, `OregonStateUniversity` instead of `Oregon State University`). When extracting affiliations:

1. If you see concatenated CamelCase words, split them: insert space before each uppercase letter that follows a lowercase letter
2. Known institution name patterns to match even when concatenated: `University`, `Institute`, `Laboratory`, `Research`, `National`
3. Email addresses (`@`) and affiliation city/country lines can help anchor the correct institution names when the text is garbled

### arXiv API Rate Limiting (429) and Timeouts

arXiv's API frequently returns 429 (rate limit) or read timeouts. The `search_arxiv_papers()` function needs retry logic with exponential backoff. See `references/arxiv-rate-limit-retry.md` for the exact patch pattern.

### Multi-line search_keywords.txt causes malformed API queries

`load_search_keywords()` reads the entire `search_keywords.txt` as one string. If the file has multiple keyword lines (one per line), they get joined with newlines, which become `%0A` in the URL. The arXiv API may interpret this as an invalid query, causing repeated timeouts or 429 errors. The retry logic (5 attempts with exponential backoff) usually recovers, but if all5 attempts fail, check whether `search_keywords.txt` has multiple lines and consider reducing to a single-line query.

### Chinese summary (summary_cn) requirements

- 90-150 Chinese characters, one natural paragraph (no bullet points)
- Must cover: core method, main contribution, key results
- No generic filler like "提出新型方法" — be specific about what the method does
- Self-check: rewrite if under 90 chars or highly similar to other summaries

### Do NOT publish with pending papers

`scripts/publish_viewer.sh` refuses to publish when `pending_llm_ids.txt` is non-empty. Always complete affiliation extraction and summary generation before publishing.

### Do NOT push to upstream repository

Publishing must target the user's own fork, not `genggng/hermes-arxiv-agent`.

## Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 monitor.py` | Search + download |
| `python3 viewer/build_data.py` | Rebuild viewer JSON |
| `python3 monitor.py --sync-pending-state` | Sync pending queue |
| `bash scripts/publish_viewer.sh` | Publish to GitHub Pages |
| `python3 viewer/run_viewer.py` | Start local viewer |
