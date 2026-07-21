# OpenAlex API Patterns

## Institution Discovery (ALWAYS do this first)

```python
# Step 1: Find institution ROR and OpenAlex ID
# GET https://api.openalex.org/institutions?search=Macau+University+of+Science+and+Technology
# Returns:
#   - display_name: "Macau University of Science and Technology"
#   - ror: "https://ror.org/03jqs2n27"
#   - id: "https://openalex.org/I111950717"
```

**CRITICAL:** The ROR filter requires the FULL URL, not the short ID.

## Institution-Based Author Search (Two Filter Options)

### Option A: ROR filter (requires full URL + URL-encoding)
```python
MUST_ROR = "https://ror.org/03jqs2n27"  # Full URL, NOT just "03jqs2n27"
encoded_ror = urllib.parse.quote(MUST_ROR, safe='')
url = f"https://api.openalex.org/authors?filter=last_known_institutions.ror:{encoded_ror}&per_page=100&cursor=*"
```

### Option B: OpenAlex institution ID (simpler, recommended)
```python
MUST_INST_ID = "I111950717"  # The ID portion of the institution's OpenAlex URL
url = f"https://api.openalex.org/authors?filter=last_known_institutions.id:{MUST_INST_ID}&per_page=100&cursor=*"
```

**Prefer Option B** — no URL-encoding issues, no `://` to confuse query parsing.

### Common mistakes that return 0 results:
| Mistake | Correct |
|---------|---------|
| `ror:03jqs2n27` | `ror:https%3A%2F%2Fror.org%2F03jqs2n27` (URL-encoded full URL) |
| `ror:https://ror.org/03jqs2n27` (not encoded) | The `:` in `https://` breaks query parsing |

## Select Field Restrictions

Not all fields are valid in `/authors` endpoint `select` parameter:

| Field | Valid on /authors? |
|-------|-------------------|
| `id`, `display_name`, `works_count` | ✅ |
| `cited_by_count`, `summary_stats` | ✅ |
| `orcid`, `topics`, `last_known_institutions` | ✅ |
| **`authorships`** | ❌ Causes HTTP 400 |

**Debugging tip:** When pagination mysteriously returns 0 results with no error, test `select` fields one-by-one. The `authorships` field is valid on `/works` but not `/authors`.

## Rate Limiting (429) and Retry Pattern

**Do NOT silently swallow 429 errors.** A naive `try/except: return None` makes it look like there are 0 results when the real issue is rate-limiting.

### Correct retry pattern:
```python
def api_get(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "myapp/1.0 (mailto:user@example.com)"
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status == 429:
                    wait = min(30 * (2 ** attempt), 90)
                    print(f"Rate limited, waiting {wait}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = min(30 * (2 ** attempt), 90)
                time.sleep(wait)
                continue
            return None
    return None
```

**Key rules:**
- Include a mailto in User-Agent to enter the "polite pool" (~10 req/s instead of daily cap)
- Use exponential backoff: 30s → 60s → 120s (not 60→120→300 — too slow for cron jobs)
- Cap max retries at 3-5
- Never exceed 0.5s delay between pagination requests (10 req/s polite pool limit)

## Disk Caching for Paginated Author Lists

Paginating ~6000+ authors takes 60+ API calls. Cache to disk:

```python
def load_all_authors(self):
    cache_file = "must_authors_cache.json"
    
    # Try disk cache first
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)
    
    # Paginate from API
    all_authors = []
    cursor = "*"
    while cursor:
        data = api_get(url)
        if not data:
            break
        all_authors.extend(data["results"])
        cursor = data.get("meta", {}).get("next_cursor")
        time.sleep(0.35)  # ~3 req/s, well within 10 req/s limit
    
    # Save to disk
    with open(cache_file, "w") as f:
        json.dump(all_authors, f)
    
    return all_authors
```

## Key API Endpoints

| Endpoint | Use |
|----------|-----|
| `/authors?search={name}` | Search by name |
| `/authors?filter=display_name.search:{name},last_known_institutions.id:{id}` | **Name + institution combined search (recommended)** |
| `/authors?filter=last_known_institutions.id:{id}` | All authors from institution |
| `/works?filter=authorships.author.id:{id}` | Author's publications |
| `/works?filter=title.search:{title},authorships.institutions.lineage:{inst_id}` | **Find MUST authors from paper title (reverse-lookup)** |
| `/works?filter=raw_author_name.search:{name},authorships.institutions.lineage:{inst_id}` | Find by raw byline (CJK variant) |
| `/institutions?search={name}` | Find institution ROR and OpenAlex ID |

### Critical: `display_name.search` does NOT work with Chinese characters
Searching `display_name.search:趙慶林` returns 0 results silently (no error). Always convert to English name first.

### Critical: Abbreviated names (Z.C. Cai) fail with `display_name.search`
OpenAlex stores full names (Zhanchuan Cai), not abbreviations. Use works reverse-lookup (Phase 4) to get full names from paper authorships.

### Critical: URL-encode names with spaces
`display_name.search:Ling Zhou` fails with "URL can't contain control characters". Always encode:
```python
encoded = urllib.parse.quote("Ling Zhou")  # → "Ling%20Zhou"
url = f"...?filter=display_name.search:{encoded},last_known_institutions.id:{MUST_INST_ID}"
```

### Disambiguation: when multiple same-name candidates exist at one institution
- `works_count` is the strongest signal (professors typically 20+, students 1-5)
- `topics` field cross-validated against known research areas
- Reject implausibly high h-index for the professor's title level
- If no disambiguating signal, return the one with highest works_count as "best guess" with low confidence

## Data Format Auto-Detection

```json
{
  "id": "https://openalex.org/A5090615044",
  "display_name": "Xiaoping Lu",
  "works_count": 153,
  "cited_by_count": 2367,
  "summary_stats": {
    "h_index": 27,
    "i10_index": 61,
    "2yr_mean_citedness": 2.675
  },
  "topics": [{"display_name": "Machine Learning"}],
  "last_known_institutions": [{"display_name": "Macau University..."}]
}
```

## Common Surname Pinyin (Traditional Chinese)

Must handle traditional characters (used in Macau/HK) — **missing traditional forms causes silent 0% hit rate** for half the professors:
- 盧→Lu, 趙→Zhao, 劉→Liu, 陳→Chen, 楊→Yang, 黃→Huang, 葉→Ye
- 梁→Liang, 羅→Luo, 謝→Xie, 鄭→Zheng, 蔡→Cai, 萬→Wan, 麥→Mai
- 張→Zhang, 鄒→Zou, 錢→Qian, 鄧→Deng, 蕭→Xiao, 聶→Nie, 閔→Min
- 項→Xiang, 賈→Jia, 鄔→Wu, 顏→Yan, 龔→Gong, 華→Hua, 賀→He
- 齊→Qi, 龐→Pang, 蘇→Su, 蔣→Jiang, 韓→Han, 鐘→Zhong, 譚→Tan
- 權→Quan, 邊→Bian, 竇→Dou, 簡→Jian, 範→Fan, 關→Guan, 蘭→Lan
- 龍→Long, 衛→Wei, 歐→Ou, 賴→Lai, 閻→Yan, 應→Ying, 叢→Cong

Full mapping needed: 400+ entries. Store as a Python dict constant in the script.
Source: `find_quant_supervisor_v4.py` in must-prof-eval project has the complete dict.

## Works Reverse-Lookup (Finding Full Author Names from Papers)

When you only have abbreviated names (e.g., "Z.C. Cai") from paper titles, use works search to get full names:

```python
def get_full_name_from_paper(paper_title: str, institution_id: str) -> list:
    """Search for a paper by title, return MUST-affiliated authors with full names."""
    safe = re.sub(r'[^\w\s]', '', paper_title[:60]).strip()
    safe = re.sub(r'\s+', ' ', safe)
    encoded = urllib.parse.quote(safe)
    url = (f"https://api.openalex.org/works?"
           f"filter=title.search:{encoded},"
           f"authorships.institutions.lineage:{institution_id}"
           f"&per_page=1&mailto=student@must.edu.mo")
    data = api_get(url)
    must_authors = []
    for work in data.get("results", []):
        for auth in work.get("authorships", []):
            insts = [i.get("display_name", "") for i in auth.get("institutions", [])]
            if any("Macau" in i for i in insts):  # Adjust for your institution
                must_authors.append({
                    "name": auth["author"]["display_name"],  # Full name like "Zhanchuan Cai"
                    "id": auth["author"]["id"],
                })
    return must_authors
```

**Title cleaning for works reverse-lookup (tested on 62 professors):**

Paper titles from Chinese faculty pages come in multiple formats — use a multi-strategy extractor:

```python
def extract_pure_title(raw: str) -> str:
    """Extract the actual paper title from various faculty-page formats."""
    pure = ""

    # Strategy A: Quoted titles — "Title" or \u201cTitle\u201d
    m = re.search(r'["\u201c](.+?)["\u201d]', raw)
    if m:
        return m.group(1).strip()

    # Strategy B: Split by ", " and find the first non-author segment
    parts = re.split(r',\s+', raw)
    for j, part in enumerate(parts):
        part = part.strip()
        # Skip author names (contain dots like "Z.C."), short fragments, numbers
        if re.match(r'^[A-Z]\.', part) or len(part) < 5 or re.match(r'^\d', part):
            continue
        # Skip venue names
        if re.match(r'^(IEEE|ACM|Springer|Elsevier|Journal|Proc|Trans)', part, re.I):
            continue
        # Handle "(Year). Title." format
        if re.match(r'^\(\d{4}\)', part):
            after = re.sub(r'^\(\d{4}\)\.\s*', '', part)
            if len(after) > 10:
                return after
            continue
        # This segment is likely the title (first capital-letter word after authors)
        if re.match(r'^[A-Z][a-z]', part) and j > 0:
            pure = re.split(r',\s+(?:IEEE|ACM|Springer|Elsevier|Journal|Proceedings|Trans)', part)[0]
            break

    return pure

# Then clean and search:
pure = extract_pure_title(raw_title)
safe = re.sub(r'[^\w\s]', '', pure[:60]).strip()
safe = re.sub(r'\s+', ' ', safe)
```

**Common pitfalls:**
- APA format (`Wang, W., Wang, W., Yu, H. (2024). Title.`) — the `(Year)` marker is the best split point
- Chinese faculty pages sometimes include author lists with `*` (corresponding author) — strip `*` before processing
- Some entries are just venue metadata (`(JCR Q1)`, `(CCF-A)`, `Early Access.`) — skip if pure title < 8 chars
- URL-encode the final title search string — spaces and special chars break the URL

## Semantic Scholar as Fallback

When OpenAlex misses an author:
```python
# By name
GET https://api.semanticscholar.org/graph/v1/author/search?query={name}&fields=name,hIndex,citationCount,affiliations

# By paper title (if you know one)
GET https://api.semanticscholar.org/graph/v1/paper/search?query={title}&fields=authors
```

Rate limit: 100 requests per 5 minutes (free tier).
