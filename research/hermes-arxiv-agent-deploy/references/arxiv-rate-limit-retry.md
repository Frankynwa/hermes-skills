# arXiv API Rate Limiting & Retry Pattern

## Problem

arXiv's API endpoint `https://export.arxiv.org/api/query` frequently returns two error types:

1. **Read Timeout**: After 30s, `requests.exceptions.ReadTimeout` fires — the API never responds in time.
2. **HTTP 429 Too Many Requests**: Rate limiting kicks in, especially during peak hours or for bulk queries with many keyword groups.

Without retry logic, `monitor.py` fails immediately and the daily cron produces no results.

## The Fix

Replace the single request in `monitor.py` `search_arxiv_papers()` with retry logic. The function already imports `time` at module level.

### Location: `monitor.py` line ~114

Replace:
```python
    print(f"[INFO] Searching arxiv: {keywords}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
```

With:
```python
    print(f"[INFO] Searching arxiv: {keywords}")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            break
        except (requests.exceptions.ReadTimeout, requests.exceptions.HTTPError) as e:
            if attempt + 1 == max_retries:
                raise
            wait = min(2 ** attempt * 5, 60)
            print(f"[RETRY] Attempt {attempt+1}/{max_retries} failed ({e}), waiting {wait}s...")
            time.sleep(wait)
```

### Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Max retries | 5 | Rides out typical 30-60s rate-limit windows |
| Base delay | 5s | Conservative starting point, respects arXiv rate limits |
| Backoff | Exponential ×2 | 5→10→20→40→60s (capped at 60) |
| Catch exception | `ReadTimeout` + `HTTPError` | Covers both timeout and 429 scenarios |

### Real-world performance

- June 28, 2026: 3 retries needed (5+10+20s = 35s total) before success.
- July 16, 2026: 5 retries all failed (timeouts + 429) on first attempt. Second attempt 30min later succeeded on first try. The multi-line `search_keywords.txt` may have contributed — see below.

## Multi-line search_keywords.txt Issue

`load_search_keywords()` reads the entire file with `f.read().strip()`. When the file has multiple keyword lines:

```
all:large+AND+all:language+AND+all:model+AND+all:quantization
all:psychological+AND+all:NLP+AND+all:mental+AND+all:health
```

The newlines become `%0A` in the URL:
```
search_query=all:large+AND+...%0Aall:psychological+AND+...
```

This makes the arXiv API treat the query as malformed or overly broad, increasing the chance of timeouts and 429s. The 5-retry backoff usually recovers, but on heavy traffic days all5 may fail.

**Workarounds**:
1. Keep `search_keywords.txt` to a single line
2. If multiple keyword groups are needed, run `monitor.py` once per keyword line (not currently implemented)
3. Simply retry the cron job — the API recovers within ~30 minutes

## Re-application

If the repo is re-cloned or the upstream changes, re-apply this patch. The `time` module is already imported — no new imports needed. Search for `search_arxiv_papers` and replace the bare `requests.get` + `raise_for_status` block.
