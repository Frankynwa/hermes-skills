# Professor Research & Outreach Template

## Professor Background Research Checklist

For each potential supervisor, collect:

### Academic Profile
- [ ] Full name (Chinese + English)
- [ ] Title (Assistant/Associate/Full Professor)
- [ ] University & Department
- [ ] Email
- [ ] ORCID (if available)
- [ ] OpenAlex ID

### Research Metrics (via OpenAlex API)
```bash
# Author profile
curl -s "https://api.openalex.org/authors/{OPENALEX_ID}" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'Name: {d[\"display_name\"]}')
print(f'Works: {d[\"works_count\"]}')
print(f'Citations: {d[\"cited_by_count\"]}')
print(f'h-index: {d[\"summary_stats\"][\"h_index\"]}')
for t in d.get('topics', []):
    print(f'  Topic: {t[\"display_name\"]}')
"

# Recent works
curl -s "https://api.openalex.org/works?filter=author.id:{ID}&sort=publication_date:desc&per-page=10" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for w in d['results']:
    print(f'[{w[\"publication_year\"]}] {w[\"title\"]}')
    print(f'  Cited: {w[\"cited_by_count\"]}')
"
```

### Assessment Questions
1. Is the professor active? (publications in last 2 years)
2. Research alignment with user's interests?
3. New professor (eager for students) vs established (harder to get attention)?
4. Supervision capacity? (check group size if visible)
5. Does their university have professor discretion for admission?

## Outreach Email Template

```
Subject: Prospective [MPhil/PhD] Student — [Your Research Area] Background

Dear Professor [Name],

I am [Name], a senior BSAI (Artificial Intelligence) student at Macau University of Science and Technology. I am writing to express my interest in your research on [specific topic from their paper], and to inquire about [MPhil/PhD] supervision opportunities.

My background includes:
- [Project 1]: [1-2 sentence description with concrete results]
- [Project 2]: [1-2 sentence description with concrete results]
- Technical skills: Python, [ML framework], [relevant tools]

I have been following your work on [specific paper title or topic], and I believe my experience in [specific skill] aligns well with your research direction.

I have attached my CV and would be grateful for the opportunity to discuss potential research directions. I am flexible on start date and can begin as early as [date].

Thank you for your time.

Best regards,
[Name]
[Email]
[GitHub link]
```

### Email Rules
1. **300 words max** — professors skim
2. **Reference specific paper** — shows genuine interest
3. **Lead with projects** — not GPA or courses
4. **DO NOT mention GPA** — if they ask, be honest; don't volunteer it
5. **Attach CV + GitHub link** — let the work speak
6. **One email per professor** — never mass-send templates
7. **Follow up once** after 1-2 weeks if no response, then stop

## MUST Professor 王黎 (Li Wang) — Reference
- **Title**: 助理教授 (Assistant Professor)
- **Email**: liwang-fi@must.edu.mo
- **ORCID**: 0000-0001-8565-9477
- **OpenAlex**: A5029511797
- **h-index**: 1, Works: 2, Citations: 4
- **Previous**: University of Macau (2018), MUST (2023)
- **Research**: Financial Risk & Volatility Modeling, Stochastic Processes, Econometrics
- **Key papers**:
  - [2023] GMM Estimation of Realized Stochastic Volatility Model (J Risk & Financial Mgmt)
  - [2018] Realized Laplace transforms for pure jump semimartingales (Soft Computing)
- **Assessment**: New professor, limited output but direction aligns with quantitative finance. Good for building math foundation, limited weight for recommendation letters.
