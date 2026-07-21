# MUST Scholar Database API Reference

Base URL: `https://scholar.must.edu.mo`

## Endpoints

### Scholar List (paginated)
```
GET /scholar/page?nameAcronym=&realName={name}&departmentsCode={code}&page={N}
```
Returns HTML with scholar cards. Parse with regex:
```python
scholars = re.findall(r'href="/scholar/(\d+)"[^>]*title="([^"]+)"', html)
total = re.search(r'totalCount\s*=\s*"(\d+)"', html)
```

### Individual Scholar Profile
```
GET /scholar/{id}
```
Returns HTML with tabs: 論文, 著作, 科研項目, 專利

Parse stats:
```python
# Key patterns in text:
# "WOS核心合集引用：3043 | H Index：17 | WOS收錄：80"
# "CNKI收錄：4 | SCOPUS收錄：103"
# "論文: 107"
# "科研項目：5"
# "專利：11"
```

### Unpublished Profiles
Professors without published profiles have:
```html
<a href="javascript:tiaozhuan();" class="thumbnail" title="王黎">
```
The `tiaozhuan()` function shows: "資訊確認中，待發佈！"

## Department Codes
| Code | Department | Scholars |
|------|-----------|----------|
| 672339 | Computer Science & Engineering | 51 |
| 672340 | Unknown (smaller dept) | 18 |
| 672342 | Unknown | 13 |
| (empty) | All departments | 552 |

## OpenAlex API for MUST Professors

### Search by name + institution
```
GET https://api.openalex.org/authors?search={name}&filter=last_known_institutions.country_code:MO&per_page=5&fields=id,display_name,works_count,cited_by_count,summary_stats,last_known_institutions
```

### Get professor's papers
```
GET https://api.openalex.org/works?filter=author.id:{openalex_id}&sort=cited_by_count:desc&per_page=10&select=title,publication_year,cited_by_count,concepts
```

### Pitfalls
- Common names (Wang Li, Li Xiaodong) merge multiple authors
- Rate limit: HTTP 429 if too fast. Add 1s delay.
- Use `country_code:MO` to filter to Macau institutions
- Semantic Scholar also rate-limited (429) as fallback

## Verified Scholar IDs (from 2026-06-16 session)
| ID | Name | h-index | WOS Citations | Core Area |
|----|------|---------|---------------|-----------|
| 100243 | 李曉東 | 17 | 3043 | Power Electronics |
| 101102 | 盧曉平 | 12 | 461 | Astronomy + ML |
| 107860 | 宋家陽 | — | — | LLM Uncertainty |
