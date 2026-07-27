---
name: academic-literature-review
category: research
description: Rigorous academic literature search and quality verification. Multi-source search (OpenAlex, arXiv, Semantic Scholar, browser for IEEE Xplore/IET/SpringerLink/ScienceDirect), DOI cross-validation, predatory journal detection, citation/reference analysis. Use when the user asks to find academic papers, do a literature review, or verify paper quality — especially when domain match alone is not enough.
---

# Academic Literature Review — Rigorous Search & Verification

## Trigger
When the user asks to find academic papers, do a literature review, survey a research area, or verify whether specific papers are credible. Also applies when the user requests "deep research" into a technical topic that requires academic backing.

## Core Principle
**Domain match is NOT quality.** A paper whose title matches the topic is worthless if it's from a predatory journal with zero references and no peer review. The user has explicitly corrected the agent for recommending such papers. Verify quality BEFORE presenting results.

## Search Strategy

### Phase 1: Multi-Source Discovery
Search ALL of the following, not just one:

1. **OpenAlex API** (preferred for automated search, 2.5B+ papers):
   ```python
   import json, urllib.request, urllib.parse, time
   url = f"https://api.openalex.org/works?search={urllib.parse.quote(query)}&per_page=10&sort=cited_by_count:desc"
   req = urllib.request.Request(url, headers={"User-Agent": "mailto:research@example.com"})
   ```
   - Rate limit: 0.3-0.5s between calls
   - Abstract reconstruction from `abstract_inverted_index` field
   - Use `filter=type:article` to exclude preprints/conference papers initially

2. **arXiv API** (for preprints and CS/EE papers):
   ```python
   url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results=10"
   ```
   - Caution: arXiv papers have NOT been peer-reviewed. Always check if they later appeared in a journal/conference.

3. **Semantic Scholar API** (for citation context):
   ```python
   url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit=10"
   ```
   - Rate limited more aggressively than OpenAlex. Add 1-2s delays.

4. **Browser-based** (for IEEE Xplore, IET Digital Library, ScienceDirect, SpringerLink):
   - IEEE Xplore: `https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={query}`
   - IET Digital Library: `https://ietresearch.onlinelibrary.wiley.com/action/doSearch?AllField={query}`
   - ScienceDirect: `https://www.sciencedirect.com/search?qs={query}`
   - Note: These platforms often have anti-bot protections. If blocked, rely on OpenAlex which indexes most of their papers.

### Phase 2: DOI Cross-Validation
Every paper MUST be verified by DOI lookup. Do NOT trust search result titles alone — DOI-based queries often return WRONG papers if the DOI is guessed rather than found.

Correct pattern:
```python
# AFTER finding a paper by search, verify with its actual DOI
url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
```

Wrong pattern — DO NOT use:
```python
# Guessing DOIs by incrementing numbers (e.g., "10.1049/gtd2.12933", "10.1049/gtd2.12934")
# IET GTD DOIs are NOT sequential — they returned completely unrelated papers.
```

## Quality Verification — Mandatory Checklist

For EVERY paper before including it in results, verify ALL of:

### 1. Journal / Venue Quality
- **Acceptable**: IEEE Transactions (all series), IET Generation Transmission & Distribution, IEEE Access, Protection and Control of Modern Power Systems, Renewable and Sustainable Energy Reviews, Electric Power Systems Research, IEEE PES General Meeting, IEEE IECON, IEEE ISGT
- **Finance/Economics acceptable**: Journal of Finance (JF), Journal of Financial Economics (JFE), Review of Financial Studies (RFS), Journal of Political Economy (JPE), Econometrica, Journal of Econometrics, Journal of Applied Econometrics (JAE), Journal of Business & Economic Statistics (JBES), Journal of Financial Econometrics, Journal of Financial Markets, Review of Economics and Statistics, American Economic Review
- **Warning signs**: Journal not indexed in Scopus/Web of Science, created after 2020 with no track record, ISSN not in any major database
- **REJECT immediately**: JAIGS (Journal of Artificial Intelligence General science) — predatory, 0 references typical, no peer review, ISSN 3006-4023 not indexed anywhere
- Use OpenAlex's `primary_location.source.display_name` to identify the journal

### 2. References Count
- **Minimum: 20 references** for journal articles
- **0 references = REJECT** (means no literature review was done, cannot be peer-reviewed)
- Conference papers may have fewer (10-15 acceptable for 4-6 page formats)
- References count via OpenAlex: `len(work.get('referenced_works', []))`

### 3. Citation Count
- Not a hard filter (new papers have low citations), but check:
- Review papers with < 5 citations after 1+ years = likely low impact
- Cited by count via OpenAlex: `work.get('cited_by_count', 0)`

### 4. Author Institution Background
- Are the authors from institutions with established power systems / signal processing research programs?
- Example good institutions: TU Dresden, NTNU, QUT, CNRS/Paris-Saclay, ASELSAN/Gazi, EPRI, Aalborg, TU Delft, IEEE Fellows
- Single-author papers from unknown institutions with no publication history = red flag

### 5. Abstract Coherence
- Does the abstract describe actual methodology (not just buzzwords)?
- Signs of AI-generated abstracts: vague claims, no specific numbers, excessive adjectives
- Use OpenAlex's `abstract_inverted_index` to reconstruct and read the abstract

## Output Format

Present papers in tiered format:

**A+ Tier (7/7)**: IEEE/IET flagship journal, peer-reviewed, ≥20 refs, verified DOI, strong author institutions
**A Tier (6/7)**: Elsevier/Springer mainstream journal, peer-reviewed, ≥20 refs
**B Tier**: Conference paper or preprint with formal publication record but quality metrics below thresholds
**Rejected**: Predatory journals, 0 refs, unverifiable — do NOT present in results

For each accepted paper, always include:
- Full title
- All authors with institutions
- Journal/conference name + year
- DOI (verified)
- Citation count + reference count
- Whether open access
- 1-2 paragraph methodology summary
- Explicit relevance mapping to the user's project

## Pitfalls

### OpenAlex search returns noise
Broad queries (e.g., "deep learning volatility") return papers from physics, medicine, astronomy, etc. **Always filter results by journal** — only keep papers from finance/economics/statistics journals. Use `primary_location.source.display_name` to check.

### Crossref DOI verification: search by title first
Don't guess DOIs. The most reliable workflow:
1. Search by exact title in OpenAlex → get the correct DOI
2. Verify that DOI in Crossref → get exact citation count and journal
3. Cross-check both sources agree on title, authors, year

This two-step pattern catches cases where OpenAlex indexes a different version (preprint vs published) than Crossref.
OpenAlex counts `referenced_works` from its database. A paper with 0 is almost certainly either a predatory journal publication or a preprint without a bibliography. Do NOT assume "metadata might be incomplete" — verify via another source or reject.

### Conference papers often not indexed
CIGRE, CIRED, and some regional IEEE conferences are NOT indexed in OpenAlex or Scopus. If a paper claims CIGRE publication but has no OpenAlex record, flag it as "unverifiable" and explain why.

### PPT/office file text extraction failures
When the standard text extraction pipeline truncates or misses slides (especially last slides of a PPT), use python-pptx directly in terminal:
```bash
python3 -c "
from pptx import Presentation
prs = Presentation('file.pptx')
for i, slide in enumerate(prs.slides):
    print(f'=== Slide {i+1} ===')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                text = p.text.strip()
                if text: print(text)
    print()
"
```
See `references/office-file-extraction.md` for full details.

### Researcher evaluation (not literature search)
When the task is to evaluate a specific researcher's publication record (not find papers on a topic), use the Crossref + OpenAlex combo documented in `references/researcher-evaluation.md`. This covers journal quality tiering, per-paper citation lookup via Crossref, and synthesis into an overall assessment.

For MUST (Macau University of Science and Technology) faculty specifically, start with the MUST Scholar database first (see `references/must-scholar-navigation.md` for navigation quirks), then cross-verify with OpenAlex/ORCID. MUST Scholar typically has the most complete publication list for MUST faculty — more than OpenAlex for recent (2025-2026) and regional-journal papers.

### Browser anti-bot blocking
IEEE Xplore, ScienceDirect, and Google Scholar frequently return 403 or CAPTCHA challenges. When blocked:
1. Try the site with browser_navigate first
2. If blocked, fall back to OpenAlex API which indexes these papers
3. If a specific PDF is needed, search for it on the author's institutional repository or ResearchGate
