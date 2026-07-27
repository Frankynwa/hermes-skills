# Academic Search Methodology — Multi-Platform Strategy & Anti-Bot Workarounds

## Platform Reliability Ranking (as of July 2026)

| Platform | Reliability | Anti-Bot | Best For |
|----------|------------|----------|----------|
| OpenAlex API | HIGH — no restrictions | None | Bulk discovery, DOI verification, venue/citation checks |
| arXiv API | MEDIUM — keyword matching too broad | None | Searching known IDs, confirming preprint publication status |
| Semantic Scholar API | MEDIUM — rate-limit 429 after ~5 calls | Moderate | Supplementary search when OpenAlex is insufficient |
| SpringerLink (browser) | MEDIUM — works after cookie consent | Accept-cookies gate | Finding papers in Springer journals |
| IEEE Xplore (browser) | LOW — request rejected | Aggressive | Expect failure; use OpenAlex filter workaround |
| IET Digital Library | LOW — stuck on Cloudflare verify | Aggressive | Expect failure; use OpenAlex filter workaround |
| ScienceDirect | LOW — reference number error | Aggressive | Expect failure; use OpenAlex filter workaround |
| Google Scholar | LOW — "We're sorry" captcha | Aggressive | Expect failure |
| DuckDuckGo/web_search | LOW — returns noise, not structured results | N/A | Not recommended for academic search |

## Multi-Platform Search Strategy

### Primary: OpenAlex API (always start here)

```python
import urllib.request, json, time

def search_openalex(query, max_papers=15):
    url = f"https://api.openalex.org/works?search={urllib.request.quote(query)}&sort=cited_by_count:desc&per_page={max_papers}&filter=publication_year:2023-2025,type:article"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "mailto:research@example.com")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read()).get("results", [])
```

**PITFALL**: OpenAlex keyword search uses semantic matching, which is too broad for niche domains. "power quality deep learning" returns cardiology papers (higher citation count). Use short, specific queries and always filter results by domain keywords in the title.

### Secondary: DOI Verification (exact match, always reliable)

```python
def lookup_by_doi(doi):
    url = f"https://api.openalex.org/works/doi:{urllib.request.quote(doi, safe='')}"
    req = urllib.request.Request(url, headers={"User-Agent": "mailto:research@example.com"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())
```

### Tertiary: arXiv API for Specific IDs

arxiv API `search_query` with multi-word queries returns noise (splits "power quality" into individual terms). Better approach: search by specific arXiv IDs found through other means, or use very specific quoted phrases.

```python
# Good: lookup specific papers
url = "http://export.arxiv.org/api/query?id_list=2503.13566,2409.00025"

# Bad: broad keyword search (returns unrelated physics papers)
url = "http://export.arxiv.org/api/query?search_query=all:power+quality+disturbance+classification"
```

### Fallback: SpringerLink via Browser

SpringerLink works when you:
1. Navigate to the search page
2. Click "Accept all cookies" (ref is usually @e4 on the cookie dialog)
3. Apply domain filters (e.g., "Electrical power engineering")
4. Narrow date range to 2023-2025

### When All Else Fails

If OpenAlex, arXiv, Semantic Scholar, and SpringerLink all fail to find a paper:
1. The paper may be too recent for indexing (< 3 months old)
2. The paper may be behind a paywall on a platform with aggressive anti-bot
3. **Tell the user honestly that the paper cannot be accessed**, don't fabricate content

## PPT/Office Document Extraction — Always Use python-pptx

### PITFALL: Upper-layer text extraction pipeline unreliable

The built-in text extraction for uploaded pptx files can silently drop slides (observed: Slide 57-62 of a 62-slide PPT completely missing from context). This caused a critical information loss — the project team table (Slide 61) and development timeline (Slide 62) were invisible, leading to incorrect conclusions about algorithm ownership.

### Correct Approach: python-pptx in terminal

Always bypass the extraction pipeline and use python-pptx directly:

```bash
python3 -c "
from pptx import Presentation
prs = Presentation('/path/to/file.pptx')
for i, slide in enumerate(prs.slides, 1):
    print(f'\n=== Slide {i} ===')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.strip()
                if text:
                    print(text)
"
```

This extracts 100% of slide content, every slide, every text element. No silent drops.

### File Location on macOS

Uploaded files are typically saved to `~/Desktop/` (user drags to Desktop). Check for .pptx, .xls, .xlsx extensions. Use `search_files` with `target='files'` and `path='~/Desktop/'` to locate.

### Excel Extraction

For .xls/.xlsx files, use openpyxl or pandas:

```bash
python3 -c "
import pandas as pd
df = pd.read_excel('/path/to/file.xls', sheet_name=None)
for name, sheet in df.items():
    print(f'\n=== Sheet: {name} ===')
    print(sheet.to_string())
"
```

## Quality Screening — ALWAYS Before Presenting a Paper

Before citing any paper, run the `ai-technique-evaluation/references/paper-quality-screening.md` protocol:

1. DOI lookup on OpenAlex → check venue (indexed in Scopus/WoS/IEEE?)
2. References count: < 20 → flag, 0 → automatic rejection
3. Citation count: 0 after 1+ year → flag
4. Author institutions: research university with domain lab? or teaching-only college?

**The JAIGS lesson**: A paper with perfect title/domain match can still be predatory junk.
"0 references" alone disqualified it — never skip the screening.
