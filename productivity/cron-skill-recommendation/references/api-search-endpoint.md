# skills.sh API Search Endpoint (confirmed working 2026-07-02)

## Endpoint

```
GET https://skills.sh/api/search?q=<search_term>&limit=<N>
```

**⚠️ Correct path is `/api/search`** — NOT `/api/skills/search`, `/api/v1/search`, or `/api/skills`. Those all return 404.

## Response Format

```json
{
  "query": "hermes",
  "searchType": "fuzzy",
  "skills": [
    {
      "id": "nousresearch/hermes-agent/dogfood",
      "skillId": "dogfood",
      "name": "dogfood",
      "installs": 4069,
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
- **API is unstable**: was down 2026-06-29, back up 2026-07-02. Always test one query first

## Getting Descriptions

The API does NOT return descriptions. To get them, fetch individual skill pages:

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
