# MUST Scholar Database Navigation

The Macau University of Science and Technology scholar database (`scholar.must.edu.mo`) is the primary source for evaluating MUST faculty. It provides WOS citation counts, h-index, SCOPUS counts, and publication lists — often more complete than OpenAlex for Chinese-named researchers in Macau.

## Site Structure

- Scholar list: `https://scholar.must.edu.mo/scholar/page?page={N}&size=20`
- Scholar profile: `https://scholar.must.edu.mo/scholar/{id}`
- Department filter: `https://scholar.must.edu.mo/scholar/page?departmentsCode={code}` (e.g., `672339` = Computer Science, 51 scholars)

## Critical Quirk: Search Does NOT Filter

**The keyword search on the MUST scholar site returns ALL 537 scholars in the database, regardless of the search term.** The `totalCount` is always "537" and the results are always pinyin-ordered. This means:

- **Do NOT rely on keyword search** — it will mislead you into thinking no results match
- Instead, paginate through the list in pinyin order to find a specific scholar
- Each page returns **48 results** (NOT the 20 requested in the URL)

## Pinyin Order Reference (approx page numbers, 48/page)

| Pinyin Range | Approx Page |
|---|---|
| A-F (安–傅) | 1–3 |
| G-L (高–羅) | 4–7 |
| M-T (馬–田) | ~8 |
| W (王) | 8–9 |
| W (吳–伍) | 9 |
| X (夏–許) | 9 |
| Y (閆–楊) | 9 |
| Y (楊泱–陽洋) | 10 |
| Z (張–朱) | 10–11 |

## Extracting Scholar Data

### Find a scholar by Chinese name
```python
import urllib.request, re

for page in range(1, 12):
    url = f"https://scholar.must.edu.mo/scholar/page?page={page}&size=20"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req).read().decode()
    
    # Extract all scholar blocks: title attr + href
    blocks = re.findall(r'<a href="([^"]+)"[^>]*title="([^"]+)"', raw)
    for href, name in blocks:
        if 'TARGET_NAME' in name:
            print(f"FOUND: {name} -> {href}")
```

### Unpublished profiles
Scholars whose profiles haven't been published by MUST use `javascript:tiaozhuan()` as the href. These pages show a "资讯确认中，待发布" (info pending) notification and cannot be viewed directly. However, the scholar ID can sometimes still be inferred from surrounding entries.

### Extract profile metrics
```python
# Key metrics appear as plain text after scraping
# WOS核心合集引用：266 | H Index：8 | WOS收錄：35
# CNKI收錄：0 | SCOPUS收錄：36
# 成果：36件
```

The profile page lists all publications with:
- Title, authors (abbreviated), journal name with ISSN, year/volume/pages
- WOS/SCOPUS indexing status
- WOS citation count
- Journal impact factor (2024 IF)

## MUST Scholar vs OpenAlex Discrepancy

MUST Scholar typically shows MORE publications than OpenAlex because:
1. OpenAlex indexing lags 6-12 months behind publication
2. 2025-2026 papers frequently missing from OpenAlex
3. Some regional Chinese journals indexed in WOS but not OpenAlex

**Use MUST Scholar for the most complete publication list.** Use OpenAlex/ORCID for author identity verification and cross-referencing.

## Scholar ID Pattern

IDs are numeric (e.g., `100987` for 杨蕾, `100987` for others). The IDs appear to be assigned sequentially — lower IDs generally indicate earlier entry into the system, not necessarily seniority.
