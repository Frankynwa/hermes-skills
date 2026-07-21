# Browser Scraping Fallback for skills.sh

When the skills.sh REST API is inaccessible (requires Vercel OIDC auth), use browser-based DOM scraping.

## Why This Exists

- The REST API (`https://skills.sh/api/v1/skills`) requires `Authorization: Bearer <VERCEL_OIDC_TOKEN>` 
- Without a Vercel OIDC token (typical for cron environments), the API returns `{"error":"authentication_required"}`
- The previously documented `/api/search` endpoint returns 404
- Browser-based scraping of `https://www.skills.sh/` works without authentication

## DOM Extraction Pattern

### Step 1: Navigate to the leaderboard

```
browser_navigate(url="https://www.skills.sh/?sort=installs&page=1")
```

### Step 2: Scroll for more entries (optional)

```
browser_scroll(direction="down")
```

Repeat 1-2 times to capture 60-90 entries.

### Step 3: Extract with browser_console

```javascript
(() => {
  const results = [];
  const mainEl = document.querySelector('main');
  if (!mainEl) return [];
  
  const allLinks = mainEl.querySelectorAll('a');
  allLinks.forEach(a => {
    const href = a.getAttribute('href') || '';
    const text = (a.textContent || '').trim();
    
    // Leaderboard entries have install counts like "2.2M", "591.2K"
    if (text.match(/\d+[KMB]$/) && text.length > 20 && text.length < 500) {
      results.push({
        fullText: text,
        href
      });
    }
  });
  
  return results;
})()
```

### Step 4: Parse extracted data

Each `fullText` has the format: `"RANKskill-nameowner/repoINSTALLS"`
Example: `"1find-skillsvercel-labs/skills2.2M"`

Parse with regex:
```python
import re
for entry in scraped_data:
    text = entry["fullText"]
    # Extract: rank, name, repo, installs
    m = re.match(r'^(\d+)([a-z][a-z0-9-]*?)([\w.-]+/[\w.-]+)([\d.]+[KMB])$', text)
    if m:
        rank = m.group(1)
        name = m.group(2)
        repo = m.group(3)
        installs = m.group(4)
```

The `href` field gives the skills.sh page: `/owner/repo/skill-name`

### Step 5: Get more detail

For richer descriptions, the URLs from the leaderboard can be used to construct GitHub links:
- `https://github.com/owner/repo` — the source repo
- Individual skill pages on skills.sh can be navigated for descriptions

## Complete extraction script (recommended)

```javascript
// Returns structured array with name, repo, installs, skillsUrl
(() => {
  const results = [];
  document.querySelectorAll('main a[href*="/skills/"]').forEach(a => {
    const text = (a.textContent || '').trim();
    if (!text.match(/\d+[KMB]$/)) return;
    
    // Parse: RANK name repo INSTALLS
    const match = text.match(/^(\d+)(.+?)([\w.-]+\/[\w.-]+)([\d.]+[KMB])$/);
    if (!match) return;
    
    results.push({
      rank: match[1],
      name: match[2].trim(),
      repo: match[3],
      installs: match[4],
      url: 'https://skills.sh' + a.getAttribute('href')
    });
  });
  return results;
})()
```

## Caveats

- Page structure may change — update the selectors if skills.sh redesigns
- Only shows ~30 entries per scroll — for 100+ skills, scroll 3-4 times
- Descriptions may not be available directly; supplement with GitHub repo READMEs
- The page lazy-loads; entries below the fold won't appear until scrolled into view
