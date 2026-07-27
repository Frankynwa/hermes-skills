# Sitemap-Based Skill Discovery

**Status: Primary method (2026-07-21)** — confirmed working when REST API is down.

## Overview

Skills.sh publishes XML sitemap files that list every skill on the platform:
- `https://www.skills.sh/sitemap-skills-1.xml` — first ~10,000 skills
- `https://www.skills.sh/sitemap-skills-2.xml` — second ~10,000 skills
- Total: ~20,000 unique skills across both files

Each entry is a simple `<url><loc>https://www.skills.sh/{owner}/{repo}/{skill-name}</loc></url>`.

## Advantages over other methods

| Method | Speed | Coverage | Rate Limits | Notes |
|--------|-------|----------|-------------|-------|
| Sitemap XML | ⚡ 2 HTTP requests | 20K skills | None | **Best choice** — 2 files, all skills |
| RSC parsing | Medium (15 requests) | ~250 skills | None | Fragile to Next.js changes |
| Browser scraping | Slow (GUI) | ~100 skills | None | Virtual DOM limits extraction |
| GitHub API | Slow (rate-limited) | ~40 skills | ~10 req/min | Need auth for scale |

## Complete Python extraction

```python
import urllib.request, json, xml.etree.ElementTree as ET, re, time

# Step 1: Parse sitemaps for all skill URLs
all_skills = []
for i in [1, 2]:
    url = f"https://www.skills.sh/sitemap-skills-{i}.xml"
    req = urllib.request.Request(url, headers={'User-Agent': 'Hermes-Agent/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        tree = ET.parse(resp)
        root = tree.getroot()
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for url_elem in root.findall('.//ns:url/ns:loc', ns):
            loc = url_elem.text.strip()
            parts = loc.replace('https://www.skills.sh/', '').split('/')
            if len(parts) >= 3:
                all_skills.append({
                    'url': loc,
                    'owner': parts[0],
                    'repo': parts[1],
                    'name': parts[2],
                })

# Step 2: Filter against existing_names (from Feishu base)
def normalize(name):
    n = name.lower().strip()
    n = re.sub(r'[（(][^)）]*[)）]', '', n)
    if ' - ' in n:
        n = n.split(' - ')[0].strip()
    return n.replace('-', ' ').replace('_', ' ')

existing_norm = {normalize(n) for n in existing_names}
# Also add collapsed variant (no spaces/hyphens)
existing_collapsed = {n.replace('-','').replace('_','').replace(' ','') for n in existing_norm}

def is_existing(name):
    n = normalize(name)
    return n in existing_norm or n.replace(' ','') in existing_collapsed

new_skills = [s for s in all_skills if not is_existing(s['name'])]

# Step 3: Pick candidates (prioritize well-known authors)
priority_authors = {
    'mattpocock', 'vercel-labs', 'anthropics', 'microsoft', 'stripe',
    'supabase', 'agentspace-so', 'larksuite', 'stablyai', 'getpaperclipai',
    'firebase', 'browser-act', 'remotion-dev', 'xixu-me', 'halt-catch-fire',
    'lllllllama', 'wind-information-co-ltd', 'soultrace-ai', 'juliusbrussee',
}

priority = [s for s in new_skills if s['owner'] in priority_authors]
others = [s for s in new_skills if s['owner'] not in priority_authors]

# Step 4: Fetch descriptions for priority candidates (~0.3s each)
candidates = []
for s in priority[:25]:  # Limit to ~8 seconds of fetching
    try:
        req = urllib.request.Request(s['url'], headers={'User-Agent': 'Hermes-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE)
            s['description'] = desc_match.group(1) if desc_match else ""
            candidates.append(s)
        time.sleep(0.3)
    except Exception as e:
        pass  # Skip unreachable pages

# Step 5: Select 10 with category diversity (manual curation after this point)
```

## Category assignment

Since the sitemap provides no metadata beyond URL, assign categories manually:
- **AI/ML**: agent orchestration, model hosting, ML workflows
- **开发工具**: code review, testing, dev workflows, git, CLI tools
- **创意设计**: image/video generation, animation, design systems, UI
- **生产力**: docs, slides, calendar, notes, office automation
- **DevOps**: deployment, security, infrastructure, CI/CD
- **数据科学**: databases, analytics, finance, data processing
- **研究**: academic, search, literature, monitoring
- **通信**: messaging, social media, email
- **其他**: education, niche domains

## Pitfalls

1. **Author name variations**: Same org may appear under different names (e.g., `halt-catch-fire` = `agentspace-so` backend). Check the URL carefully.
2. **20K skills is too many to fetch descriptions for**: Only fetch descriptions for the ~25 most promising candidates.
3. **Sitemap doesn't include installs/stars**: You need to visit individual pages or use the leaderboard page for ranking data. Prioritize known-author skills when selecting.
4. **XML namespace**: Always use the `http://www.sitemaps.org/schemas/sitemap/0.9` namespace — ElementTree requires explicit namespace for XPath queries.
