---
name: academic-data-enrichment
description: Enrich professor/author lists with external academic APIs (OpenAlex, Semantic Scholar). Chinese name matching, institution-based search, rate limiting, data format handling. Use when building professor evaluation systems, finding supervisors, or doing bibliometric analysis.
---

# Academic Data Enrichment

## When to Use
- Building professor/author evaluation or ranking systems
- Finding supervisors by research direction
- Enriching scraped personnel data with citation counts, h-index, topics
- Bibliometric analysis of an institution or department

## Core Pattern: Institution-First Search

**Problem:** Searching Chinese names (e.g., "趙慶林") directly in English academic databases yields near-zero hits.

**Solution:** Pre-load ALL authors from the institution, then match locally:

```python
# 1. Load all institution authors (one bulk request, cached)
# OpenAlex: filter by ROR ID
url = f"{OPENALEX_BASE}/authors?filter=last_known_institutions.ror:{ROR_ID}&per_page=200&cursor=*"

# 2. Match by name locally (no more API calls)
for author in cached_authors:
    if name_similarity(chinese_name, author.display_name) > 0.7:
        return author
```

This changes hit rate from ~5% to 60%+.

## Name Matching Strategy (Publication-First)

When matching Chinese professor names to English academic records, **do NOT use surname-pinyin-matching or email-prefix inference** — both cause 30%+ false match rates (tested on 62 MUST professors). Instead:

### Phase 1: Extract English names from the professor's own publication data

Scraped personnel data always includes representative publications. The author list in each paper title contains the professor's full English name:

```
# Paper title format (common in Chinese university faculty pages):
# "X.X. Surname, Fullname Surname , Paper Title, Venue, Volume: Pages (Year)"
# Example: "F.L. Sun, Z.C. Cai , A Family of Generalized Cardinal Polishing Splines, IEEE TIP, 33: 1952-1964 (2024)"
```

```python
import re

SURNAME_PINYIN = {"趙": "Zhao", "盧": "Lu", "李": "Li", ...}  # 400+ entries, include traditional

def extract_authors_from_title(raw: str) -> list:
    """Extract all author names from a paper title. Handles 4 formats."""
    authors = []

    # Format 1: X.X. Surname (abbreviated, e.g., "Z.C. Cai", "F.L. Sun")
    for m in re.finditer(r'([A-Z]\.(?:[A-Z]\.)?\s*[A-Z][a-z]+(?:\s*-\s*[A-Z][a-z]+)?)', raw):
        authors.append(m.group(1).strip())

    # Format 2: GivenName Surname (full name, e.g., "Jianqing Li", "Jun Wan")
    # ⚠️ MUST use [a-z]+ NOT [a-z]{2,} — the {2,} variant EXCLUDES 2-letter
    # surnames (Li, Lu, Wu, Yu, He, Ma, Xu, Hu, Gu, Du, Fu, Su, ...), which
    # caused 7+ professors to be missed in testing.
    for m in re.finditer(r'(?<![A-Z.])([A-Z][a-z]+\s+[A-Z][a-z]+)(?![a-z])', raw):
        name = m.group(1).strip()
        if not any(kw in name.lower() for kw in [
            'transactions', 'ieee', 'journal', 'proceedings', 'international',
            'university', 'science', 'technology', 'engineering', 'processing',
            'information', 'systems', 'computer', 'analysis', 'learning',
            'networks', 'advanced', 'based', 'novel', 'model', 'methods',
        ]):
            authors.append(name)

    # Format 3: Surname GivenName (surname-first, e.g., "Lu Xiao-Ping", "Li Feng")
    # Common in Chinese faculty pages that follow Chinese name order.
    for m in re.finditer(r'(?<![A-Z])([A-Z][a-z]+)\s+([A-Z][a-z]+(?:\s*-\s*[A-Z][a-z]+)?)', raw):
        surname, given = m.group(1), m.group(2)
        if not any(kw in (surname + given).lower() for kw in [
            'ieee', 'acm', 'springer', 'elsevier', 'transactions', 'journal',
            'proceedings', 'university', 'processing', 'based', 'novel',
        ]):
            full = f"{surname} {given}"
            if full not in authors:
                authors.append(full)

    # Format 4: APA format "Surname, Initial." (e.g., "Wang, W.", "Li, J.")
    for m in re.finditer(r'([A-Z][a-z]+),\s*([A-Z]\.(?:[A-Z]\.)?)', raw):
        surname, initials = m.group(1), m.group(2)
        full = f"{initials} {surname}"
        if full not in authors:
            authors.append(full)

    return list(dict.fromkeys(authors))  # dedupe preserving order


def extract_english_names(chinese_name: str, publications: list) -> list:
    """Extract professor's English name from their own paper titles."""
    surname_pinyin = SURNAME_PINYIN.get(chinese_name[0], "")
    if not surname_pinyin:
        return []

    name_counts = {}
    for pub in publications[:15]:
        title = pub.get("title", "")
        for author in extract_authors_from_title(title):
            if surname_pinyin.lower() in author.lower().split():
                name_counts[author] = name_counts.get(author, 0) + 1

    # Prioritize full names over initials (X.X. Surname)
    full = {k: v for k, v in name_counts.items() if not re.search(r'\b[A-Z]\b', k)}
    if full:
        return [n for n, _ in sorted(full.items(), key=lambda x: x[1], reverse=True)]
    return [n for n, _ in sorted(name_counts.items(), key=lambda x: x[1], reverse=True)]
```

This achieved **47/62 extraction rate** on MUST professors (up from 40/62 with the older regex).

**Critical pitfall discovered:** Using `[a-z]{2,}` in the regex silently excludes all 2-letter surnames — Li, Lu, Wu, Yu, He, Ma, Xu, Hu, Gu, Du, Fu, Su, An, Ou, Yin, etc. This caused 7+ professors to be completely missed. Always use `[a-z]+` (at least 1 lowercase letter after the initial capital).

### Phase 2: Search OpenAlex with name + institution filter

```python
# Combine display_name.search with institution filter — eliminates cross-institution false matches
encoded = urllib.parse.quote(english_name)
url = (f"https://api.openalex.org/authors?"
       f"filter=display_name.search:{encoded},"
       f"last_known_institutions.id:{MUST_INST_ID}"
       f"&per_page=5&mailto=student@must.edu.mo")
```

### Phase 3: Disambiguate multiple candidates

When multiple same-name authors exist at the same institution:
- Sort by `works_count` descending (professors typically have 20+ papers)
- Cross-validate with `topics` against the professor's known research areas
- Reject implausibly high metrics (e.g., h-index > 80 for an assistant professor)

### Phase 4: For abbreviated names — works reverse-lookup

If Phase 1 only extracts initials (e.g., "Z.C. Cai" instead of "Zhanchuan Cai"):
- Use the paper title to search OpenAlex works endpoint
- Extract the full name from the authorships array

```python
# Search works by title, filter by institution lineage
safe_title = re.sub(r'[^\w\s]', '', paper_title[:60]).strip()
encoded = urllib.parse.quote(safe_title)
url = (f"https://api.openalex.org/works?"
       f"filter=title.search:{encoded},"
       f"authorships.institutions.lineage:{MUST_INST_ID}"
       f"&per_page=1&mailto=student@must.edu.mo")
# From results[0].authorships, find entries where institution contains "Macau"
# → Those authors' display_name are the full English names
```

See `references/openalex-patterns.md` for complete implementation details and pitfalls.

## Data Format Auto-Detection

Scraped data often comes in two formats:
- **Flat list**: `[{"name": ...}, ...]`
- **Nested dict**: `{"教研團隊": [...], "行政團隊": [...]}`

Always handle both:
```python
raw_list = []
if isinstance(data, dict):
    for key, val in data.items():
        if isinstance(val, list):
            raw_list.extend(val)
elif isinstance(data, list):
    raw_list = data
```

## Rate Limiting

| API | Limit | Strategy |
|-----|-------|----------|
| OpenAlex | ~10 req/s (unauthenticated) | 100-150ms delay between requests |
| Semantic Scholar | 100 req/5min (free) | 3s delay, exponential backoff on 429 |
| Google Scholar | Aggressive blocking | Use SerpAPI or scholarly library |

**When hit with 429:**
- Do NOT retry immediately
- Schedule a delayed job (15-30 min) to resume
- Cache partial results to avoid re-doing completed work

## FYP / Advisor Evaluation Workflow

When helping users choose FYP topics or evaluate potential advisors:

1. **Parse the topic list PDF** — extract project IDs, advisor names, topics, types (Faculty/Industry)
2. **Match to user background** — compare topic keywords against user's known projects, skills, and interests
3. **Check local project databases first** — if the user has a professor evaluation project (e.g., `must-prof-eval`), load existing rankings/scores before making API calls. This saves time and reveals what data the user already has.
4. **Evaluate advisors** — search OpenAlex for each candidate advisor's publication record, h-index, recent topics
5. **Detect scoring system biases** — when reviewing a user's existing ranking system, check if the methodology creates blind spots. Common bias: direction-match keywords overweighted vs. raw academic output (papers, citations, h-index) underweighted. A professor ranked #2 by direction match but with only 2 papers may be weaker than one ranked #20 with 150+ papers and high citations.
6. **Rank by fit** — consider: topic alignment with user strengths, advisor's research focus depth (single-topic vs scattered), publication venue quality, and supervision history
7. **Highlight deadlines** — FYP bidding systems often have strict deadlines; always flag the nearest one

**Practical tip:** When web tools are unavailable (subagent limitation), use `terminal` + `curl` to query OpenAlex directly:
```bash
# Search by name + institution
curl -s "https://api.openalex.org/authors?filter=display_name.search:Jiayang%20Song,last_known_institutions.id:I111950717&per_page=5&mailto=student@must.edu.mo"
```

**Red flags when evaluating advisors:**
- Advisor's topics span completely unrelated fields (e.g., finance + energy storage) → finance may not be their core expertise
- Only 1 topic in a field vs 2+ topics → less committed to that direction
- Industry topics with "TBA" advisor → cannot evaluate until advisor is announced

## Same-Advisor FYP Comparison

When a professor offers 2+ FYP topics and the user wants to choose between them:

1. **Identify the core difference** — frame it in one sentence (e.g., "024 = modeling asset variance/covariance; 108 = modeling inter-asset correlation")
2. **Map technical difficulty** — which topic requires more math/ML the user doesn't already know?
3. **Check evaluation framework maturity** — topics with standard metrics (VaR backtest, accuracy, F1) are easier to validate than open-ended research
4. **Assess advisor's own expertise gap** — if the advisor has no publications in the DL method the FYP requires, the student must be self-sufficient in that area. The advisor provides domain theory; the student provides the technical method.
5. **Align with user's existing projects** — choose the topic that forms a coherent narrative with prior work (e.g., stock selection engine → risk management = natural extension)

## FYP Advisor Inquiry Email Writing

When the user asks to draft inquiry emails to FYP advisors:

1. **Email topic must match user's DESIRED direction, not the professor's listed FYP topics.** If the user says "I want to do quant finance with Professor X" and Professor X's listed FYP topics are about robotics, write the email asking about quant finance — reference the professor's PUBLISHED research in that area as justification. Do NOT default to the listed FYP topics.
2. **Reference specific papers** — citing a professor's actual publication (title, year) shows the student has done homework and dramatically increases response rate.
3. **Lead with student's relevant project experience** — professors care about what the student has BUILT, not just courses taken. Include concrete metrics (excess returns, model accuracy, dataset sizes).
4. **Include student ID** — MUST requires student ID on all academic communications.
5. **One email per professor, tailored** — never use a generic template. Each email should reference different papers and emphasize different aspects of the student's background that match that professor.
6. **When professor's core research ≠ user's desired direction** — be transparent with the user. Example: "李曉東's published work is in power systems, not finance. His FYP-2026-009 on quant trading has no backing publications." Let the user decide whether to still inquire.

## MUST Scholar Database (Institution-Specific Source)

Before hitting external APIs, check MUST's own scholar database at `scholar.must.edu.mo` — it has WOS citations, h-index, SCOPUS counts, and research projects that OpenAlex may not have.

```python
# List scholars by department
GET https://scholar.must.edu.mo/scholar/page?nameAcronym=&realName={name}&departmentsCode={code}&page={N}

# Individual profile
GET https://scholar.must.edu.mo/scholar/{id}
```

**Department codes**: 672339=CS(51 scholars), 672340(18), 672342(13), empty=all(552).

**Pitfall**: Unpublished profiles use `javascript:tiaozhuan()` links — professor too new or profile pending.

See `references/must-scholar-api.md` for complete API reference and verified scholar IDs.
See `scripts/must_scholar_scraper.py` for a ready-to-use scraper that cross-references with OpenAlex.

## Domain Knowledge Banks

- **`references/llm-uncertainty-quantification.md`** — Methods, benchmarks, decomposition techniques, key papers, and evaluation pipeline for LLM UQ research (updated 2026-06).
- **`references/must-fyp-advisors-2026.md`** — MUST 2026/2027 FYP advisor profiles: publication records, research focus, OpenAlex data, and fit analysis for quantitative/RL/finance students.
- **`references/must-scholar-api.md`** — MUST Scholar database API endpoints, parsing patterns, and verified scholar IDs.
- **`templates/fyp-inquiry-email.md`** — Structured FYP advisor inquiry email template (Chinese/English).
- **`scripts/must_scholar_scraper.py`** — Python scraper for MUST Scholar DB with OpenAlex cross-reference.

## Quick Single-Professor Lookup (No Bulk Enrichment Needed)

When the user asks about ONE specific professor (e.g., "tell me about Prof. X"), skip the full institution-scan pipeline and use a direct OpenAlex query:

```python
import urllib.request, json, urllib.parse

def quick_lookup(english_name: str, institution_hint: str = "Macau"):
    """Fast single-professor search. Returns best match or None."""
    encoded = urllib.parse.quote(english_name)
    url = (f"https://api.openalex.org/authors?"
           f"search={encoded}&per_page=10"
           f"&select=id,display_name,works_count,cited_by_count,summary_stats,last_known_institutions")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    for a in data.get("results", []):
        insts = [i.get("display_name", "") for i in (a.get("last_known_institutions") or [])]
        if any(institution_hint.lower() in i.lower() for i in insts):
            return a  # Institution match found
    return None  # No institution match — name too common
```

**When this works:** Unique-ish names like "Xiaoping Lu", "Jiayang Song", "Zhanchuan Cai" — returns clean results in 1 API call.

**When this FAILS:** Extremely common names like "Wang Li", "Li Wei", "Zhang Jing" — OpenAlex merges hundreds of same-name authors into a single profile with 1000+ works spanning unrelated fields. The institution filter in the results doesn't help because the MERGED profile lists many institutions. **Fallback:** Use the full institution-first pipeline (bulk scan + local matching) described above.

### Quick Profiling from FYP Topic Descriptions

When OpenAlex lookup fails for a professor, analyze their FYP topic descriptions instead:

1. **Count topics per field** — 2+ topics in the same area = core research focus; 1 topic = possibly opportunistic
2. **Check topic field consistency** — Topics spanning unrelated fields (e.g., finance + energy storage + robotics) suggest the advisor may not specialize in any single area
3. **Look for domain-specific keywords** — Factor-GARCH, multi-agent RL, spectral decomposition etc. indicate depth; generic terms like "AI-based system" indicate breadth
4. **Cross-reference with co-authors** — If a professor's topic overlaps with a known professor's papers, they may be collaborators

**Red flags when evaluating advisors:**
- Advisor's topics span completely unrelated fields → none may be their core expertise
- Only 1 topic in a field vs 2+ topics → less committed to that direction
- Industry topics with "TBA" advisor → cannot evaluate until advisor is announced
- Very generic topic titles ("AI-based XX system") → may be course-project-level, not research-level

## Pitfalls
- **OpenAlex ROR filter format:** The `last_known_institutions.ror` filter requires the FULL ROR URL (`https://ror.org/03jqs2n27`), NOT the short ID (`03jqs2n27`). The short ID returns 0 results with no error. Always verify the institution via `/institutions?search=...` first to get the correct ROR.
- **Alternative filter:** Use `last_known_institutions.id:{OPENALEX_ID}` (e.g., `I111950717`) as a more robust alternative — it doesn't need the `https://` prefix and avoids URL-encoding issues.
- **URL-encode filter values:** When the filter value contains special characters (like `://` in ROR URLs), call `urllib.parse.quote(value, safe='')` before interpolating into the URL.
- **Invalid select fields cause silent 400:** The `authorships` field is NOT valid on `/authors` endpoint selects — it causes HTTP 400. Test select fields one-by-one when pagination mysteriously returns 0 results.
- **429 rate-limiting is silent with naive error handling:** Always check HTTP status codes explicitly. A `try/except Exception: pass` pattern will silently return `None` on 429, making pagination appear to return 0 total authors when the real issue is rate-limiting. Use exponential backoff: 30s → 60s → 120s with max 3-5 retries.
- **Disk caching paginated results:** Paginating ~6000+ authors takes 60+ API calls. Save the full cache to a JSON file and reload it on subsequent runs. Check file existence before paginating.
- Common Chinese names produce garbage results on OpenAlex: Names like "Wang Li", "Li Wei", "Zhang Jing" get merged into mega-profiles with 1000+ works across unrelated fields and institutions. The `search=` parameter returns these merged profiles even with institution hints. **Solution:** Do NOT rely on name-only search for common names. Use the full publication-based name extraction pipeline (Phase 1 → Phase 2 above), or fall back to topic-description analysis.
- **A professor's listed FYP topics may NOT reflect their core expertise.** Always cross-check with their actual publication record. Example: 李曉東 lists "AI Quantitative Trading" as FYP topic but his 11 papers are ALL in power systems/energy engineering. A professor with an unrelated FYP topic is likely offering it as a side interest, not as deep domain expertise. **Signal:** If a professor's FYP topics span completely unrelated fields (e.g., finance + energy storage), the topic outside their core research area is the opportunistic one.
- **Academic rank matters for supervision quality.** An assistant professor (助理教授) with 2 papers in the right direction vs a professor (教授) + program director with 150+ papers in an adjacent direction — the senior professor often provides better supervision even if their topic alignment is weaker. Factor in: lab resources, network, co-author connections, and experience advising students.
- **Subagent delegation is unreliable for academic web research:** Even with `toolsets=["web", "search", "browser"]` explicitly passed, subagents frequently report having "only GitHub tools" and cannot fetch external URLs. This is a consistent pattern across multiple delegation attempts in the same session. **Reliable fallback:** Do all OpenAlex/academic API calls yourself using `execute_code` + `urllib.request` — this always works since it runs in the parent agent's terminal with full network access. Never delegate more than 2 rounds of academic web research to subagents before switching to direct execution.
- Chinese surnames have many characters mapping to the same pinyin (e.g., 盧/卢/鲁 all → "Lu") — use full surname dictionary, not just common ones
- h-index varies by database (OpenAlex vs Scholar vs Scopus) — don't mix sources in the same ranking
- `cited_by_count` includes self-citations in OpenAlex — note this in methodology
- Some MUST professors have no English name in scraped data — extract from their publication titles instead (email prefixes are NOT reliable for inferring full names)
- **OpenAlex severely undercounts early-career professors:** An assistant professor with 5 verified publications on their MUST FIE page may show only 2 works in OpenAlex. Always cross-check with the professor's own faculty page publication list before concluding they have a thin record. OpenAlex coverage is biased toward well-indexed English-language journals; Chinese university faculty pages are more complete for their full publication history.
- **`fie_personnel_data.json` has two separate entries for the same professor:** One in `教研團隊` (teaching staff) and one in `碩士及博士學位導師` (graduate supervisors). Both contain the same core info but the supervisor entry has `是否博導` field. When looking up a professor, search all sections and merge.
