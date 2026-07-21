# RSC Data Parsing for skills.sh

Skills.sh is built on Next.js with React Server Components (RSC). The RSC stream contains serialized skill paths that can be parsed without a browser — faster, more comprehensive, and works in headless/cron environments.

## Why This Exists

- Browser-based DOM scraping requires the browser tool stack (browser_navigate → browser_scroll → browser_console), which is slow and yields only ~30 entries per page scroll
- RSC data is served as `text/x-component` and contains ALL skill paths embedded in the page payload
- Combined Hot + Trending + Main leaderboard pages yield ~250 unique skills
- No authentication required — works with plain `urllib.request`

## Complete Extraction Script

```python
import urllib.request
import json
import ssl, re

ctx = ssl.create_default_context()
headers = {"User-Agent": "HermesAgent/1.0"}

def get_skills_from_rsc(url):
    """Parse RSC stream from a skills.sh page and extract skill paths."""
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        body = resp.read().decode('utf-8', errors='replace')
        
        skills = []
        # Skill paths appear as JSON-encoded href values in the RSC stream
        # Pattern: "/owner/repo" or "/owner/repo/skill-name"
        path_pattern = re.findall(
            r'"(/[a-zA-Z0-9_.\\-]+/[a-zA-Z0-9_.\\-]+(?:/[a-zA-Z0-9_.\\-]+)*)"',
            body
        )
        
        for path in path_pattern:
            parts = path.strip('/').split('/')
            if len(parts) < 2:
                continue
            # Skip known non-skill paths
            skip_prefixes = [
                'topic', 'agent', 'docs', '_next', 'api', 'search',
                'hot', 'trending', 'official', 'audits', 'about',
                'contact', 'privacy', 'terms', 'package', 'site',
                'sitemap', 'picks', 'internal'
            ]
            if parts[0] in skip_prefixes:
                continue
            
            owner = parts[0]
            repo = parts[1]
            skill_name = parts[-1] if len(parts) >= 3 else repo
            
            skills.append({
                'name': skill_name,
                'owner': owner,
                'repo': repo,
                'path': path,
                'url': f"https://www.skills.sh{path}"
            })
        
        return skills
    except Exception as e:
        return []

# Gather from multiple pages for comprehensive coverage
hot_skills = get_skills_from_rsc("https://www.skills.sh/hot")
trending_skills = get_skills_from_rsc("https://www.skills.sh/trending")
main_skills = get_skills_from_rsc("https://www.skills.sh")

# Also search specific terms for targeted discovery
search_terms = ["hermes", "claude", "frontend", "design", "devops", 
                "github", "mcp", "testing", "research", "react"]

all_skills = {}
for s in hot_skills + trending_skills + main_skills:
    key = s['name'].lower()
    if key not in all_skills:
        all_skills[key] = s

# Deduplicate against existing recommendations
existing_names_lower = {...}  # from Step 0
new_candidates = {
    k: v for k, v in all_skills.items() if k not in existing_names_lower
}
```

## Getting Skill Descriptions

RSC data only provides skill names and paths (not descriptions). For descriptions:

1. **Visit individual skill pages** on skills.sh and extract SUMMARY sections:
   ```python
   url = f"https://www.skills.sh/{repo_path}/{skill_name}"
   req = urllib.request.Request(url, headers=headers)
   resp = urllib.request.urlopen(req, context=ctx, timeout=15)
   body = resp.read().decode('utf-8', errors='replace')
   
   # Extract SUMMARY paragraph
   summary_match = re.search(r'SUMMARY.*?<p[^>]*>(.*?)</p>', body, re.DOTALL)
   if summary_match:
       summary = re.sub(r'<[^>]+>', '', summary_match.group(1)).strip()
   ```

2. **Use the browser** for interactive exploration of top candidates

3. **Check GitHub repos** for README content when skills.sh page is sparse

## Limitations

- RSC parsing extracts PATHS, not install counts or descriptions — you need to visit individual pages for those
- The regex pattern may need updating if skills.sh changes its RSC serialization format
- Some skill paths may be duplicated across pages — always deduplicate by lowercase name
- Search pages return limited results per term; use multiple search terms for breadth
