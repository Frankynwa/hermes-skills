# skills.sh API Search Endpoint (confirmed working 2026-07-25)

## Endpoint

```
GET https://skills.sh/api/search?q=<search_term>&limit=<N>
```

**⚠️ Correct path is `/api/search`** — NOT `/api/skills/search`, `/api/v1/search`, or `/api/skills`. Those all return 404.
**⚠️ NO `www.` prefix** — `www.skills.sh/api/search` returns 404. Use `skills.sh/api/search` only.
**⚠️ Individual skill detail endpoints (`/api/skills/{id}`) return 404** — search is the ONLY available API.

## Response Format (updated 2026-07-26)

The response is a **JSON object** with a `skills` array:

```json
{
  "query": "hermes",
  "searchType": "fuzzy",
  "skills": [
    {
      "id": "nousresearch/hermes-agent/dogfood",
      "skillId": "dogfood",
      "name": "dogfood",
      "installs": 4835,
      "source": "nousresearch/hermes-agent"
    },
    {
      "id": "anthropics/skills/frontend-design",
      "skillId": "frontend-design",
      "name": "frontend-design",
      "installs": 598591,
      "source": "anthropics/skills"
    }
  ]
}
```

**Parse accordingly:**
```python
data = json.loads(resp.read().decode())
items = data.get("skills", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
```

**Note (2026-07-26):** Previous entry (2026-07-25) claimed the format changed to a "flat JSON array." This was incorrect — the wrapped format `{"skills":[...]}` is the actual response. Always use `data.get("skills", [])` with a fallback for robustness.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique skill identifier: `{owner}/{repo}/{skillId}` |
| `skillId` | string | Skill name within the source (e.g., `frontend-design`) |
| `name` | string | Display name (same as skillId in most cases) |
| `installs` | number | Installation count |
| `source` | string | Owner/repo (e.g., `anthropics/skills`) |

**Note:** Only these 5 fields are returned. No `category`, `description`, `author`, `tags`, or `url`.

## Usage Notes

- Returns up to 100 results per query (default). The `limit` parameter works: `?q=hermes&limit=20`
- Search is fuzzy — broad terms like "design" match many skills
- No authentication required
- Be polite: add `time.sleep(0.3)` between queries
- 15 search terms × 20 results (with limit=20) ≈ 250-300 unique skills after dedup by `id`
- **API stability history**: down 2026-06-29, back up 2026-07-02, down again 2026-07-23, back up 2026-07-25. Always test one query first. Sitemap XML (`sitemap-skills-{1,2}.xml`) is the reliable fallback.

## Getting Descriptions

The API does NOT return descriptions. Individual skill detail endpoints (`/api/skills/{id}`) return 404. To get descriptions, fetch individual skill pages via HTTP and parse meta tags:

```python
import urllib.request, re

def get_description(skill_url):
    req = urllib.request.Request(skill_url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=10).read().decode()
    # Try meta description first
    m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"', html, re.I)
    return m.group(1).strip() if m else ""
```

URL format: `https://skills.sh/{source}/{skillId}` (e.g., `https://skills.sh/anthropics/skills/frontend-design`)

Allow ~0.3s per skill page fetch. For 10 skills, that's ~3s total.

## Search Terms Used (2026-06-28)

```
hermes, claude, frontend, design, devops, github, mcp, testing,
research, react, data, memory, automation, ai-agent, security
```

More terms = more candidates with less overlap. 15 terms consistently yield 250+ unique skills.
