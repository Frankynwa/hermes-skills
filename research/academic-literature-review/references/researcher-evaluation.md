# Researcher Publication Record Evaluation

When asked to assess a specific researcher's publication quality (not search for papers on a topic), use this two-API workflow.

## API Combination

### Crossref API — per-paper citation counts
```
GET https://api.crossref.org/works?query.title={URL-encoded title}&rows=3
```
Returns `is-referenced-by-count` (citation count), `container-title`, `publisher`, `DOI`.
More reliable for citation counts than OpenAlex for older papers.
Rate limit: no auth needed, ~1 req/sec is fine.

### OpenAlex Sources API — journal-level metrics
```
GET https://api.openalex.org/sources?search={journal name}&per-page=3
```
Returns `summary_stats.h_index`, `summary_stats.2yr_mean_citedness`, `works_count`, `cited_by_count`, `type` (journal/conference/etc).

For a specific known journal, filter by ISSN:
```
GET https://api.openalex.org/sources?filter=issn:{issn}&per-page=3
```

## Journal Quality Tiers (domain-agnostic)

### Top-tier (A+)
- Flagship society journals (e.g., Annals of Statistics, JASA, JRSS-B in statistics; Journal of Finance, Review of Financial Studies in finance)
- h-index typically 100+, SCI/SSCI Q1, decades of history
- Publisher: Wiley, Oxford, Cambridge, University presses, major societies

### Solid mainstream (A)
- Well-established Q1-Q2 SCI/SSCI journals
- h-index 80-150, publisher: Elsevier, Springer, Taylor & Francis, Wiley
- Examples: Scandinavian Journal of Statistics, North American J. Economics & Finance

### Mid-tier (B)
- Q2-Q3 journals, h-index 50-100
- Includes newer journals from reputable publishers, some MDPI OA journals with Scopus indexing
- Acceptable for teaching-focused university faculty

### Weak / Borderline (C)
- Q3-Q4 or unranked, h-index < 50, often OA-only
- No DOI registration, not in Scopus/WoS
- Includes predatory-adjacent journals (Scienpress, some obscure publishers)

## Synthesis

When evaluating a researcher, calculate:
1. Total citations across all papers
2. Publication timeline (years of activity, papers per year)
3. Best venue (which is the strongest journal they published in?)
4. Journal tier distribution (how many A+/A/B/C papers?)
5. Collaboration network (consistent co-authors? same institution?)
6. Research trajectory (are they moving up/down in journal quality over time?)

## ORCID-Based Author Disambiguation (Critical for Common Names)

When evaluating researchers with common names (Li Wang, Wei Zhang, Jing Li, etc.), OpenAlex frequently merges papers from different people into a single profile. This produces wildly inflated metrics (e.g., a 5-paper finance professor appearing to have h-index 80 and 38,000+ citations from a medical researcher with the same name).

### Detection Pattern

1. After finding any paper by the researcher via DOI lookup, extract ALL author OpenAlex IDs and ORCIDs from the authorships array.
2. If the researcher appears with different OpenAlex IDs across papers, profile splitting has occurred.
3. Check each OpenAlex author ID against the researcher's known profile:
   - Does the `last_known_institutions` match?
   - Do the `topics` match the researcher's field?
   - Is `works_count` plausible? (A 5-paper professor shouldn't have 2,031 works)

**Strong diagnostic — co-author network consistency:** If all papers in question share the identical co-author set but the target researcher has different OpenAlex IDs across them, it confirms the same person has been split. Same co-authors + same topic + overlapping years = disambiguation failure. This is more reliable than institution matching alone, since researchers may move institutions over time (e.g., UM → MUST).

**Weak diagnostic — ORCID field mismatch:** If an OpenAlex author ID maps to an ORCID whose works are in a completely unrelated field (e.g., the ORCID owner is an influenza vaccine researcher at CDC, but the paper is about stochastic volatility), OpenAlex assigned the wrong ORCID during ingest. This is a secondary confirmation signal, not a standalone detection method.

### Resolution: ORCID as Ground Truth

ORCID is the definitive disambiguation anchor. Use the ORCID public API:

```python
orcid = "0000-0001-8565-9477"
url = f"https://pub.orcid.org/v3.0/{orcid}"
headers = {"Accept": "application/json"}
# Returns: person (name, emails, keywords, researcher-urls) +
#          activities-summary (educations, employments, fundings, works, peer-reviews)

# For works specifically:
url = f"https://pub.orcid.org/v3.0/{orcid}/works"
```

ORCID profiles reveal what OpenAlex can't:
- Education history and employment timeline
- Research grants/funding (amount, source, dates)
- Peer review activities (which journals they review for)
- Complete publication list curated by the researcher themselves

### Red Flag: Sparse ORCID Profile

A researcher with 5+ years in academia but:
- 2 or fewer works on ORCID
- No employment history
- No funding/grants
- No peer review record
- Education entry exists but has no details

...indicates either a teaching-focused academic who doesn't maintain their profile, or a very junior researcher. Either way, the ORCID is a reliable upper bound — their actual achievements are unlikely to exceed what's on ORCID.

### When ORCID Shows Split Profiles

If a researcher's papers appear on TWO different ORCIDs (common when they moved institutions and created a new ORCID without linking), note this in the evaluation. The other ORCID may be a completely different person (verify by checking works — if they're in an unrelated field like virology vs finance, it's a different person).

## MUST-Specific Workflow

For evaluating faculty at Macau University of Science and Technology, use a two-phase approach:

**Phase 1 — MUST Scholar Database** (primary source, most complete):
- See `references/must-scholar-navigation.md` for the navigation quirks (keyword search doesn't filter, pages return 48 results, pinyin-ordered pagination)
- Extract: publication count, WOS citations, h-index, SCOPUS count, CNKI count, journal list with impact factors
- MUST Scholar typically has MORE papers listed than OpenAlex (indexing lag, regional journals)

**Phase 2 — OpenAlex + ORCID Cross-Verification** (identity confirmation):
- Use paper titles from MUST Scholar to find the researcher's OpenAlex author ID
- Check for false positives: papers from completely different fields/institutions merged by OpenAlex's disambiguation
- Verify ORCID profile completeness — many MUST faculty have empty ORCID profiles
- Cross-check citation counts (OpenAlex typically lower than WOS)

**Compare to establish a range**: MUST Scholar = upper bound (most complete), OpenAlex = lower bound (only indexed papers). Reality is usually closer to MUST Scholar's numbers.

## Pitfalls

- Crossref doesn't index all journals. If a paper isn't found there, try OpenAlex works search.
- OpenAlex source search can match wrong journals with similar names — always verify ISSN.
- Citation counts in Crossref (`is-referenced-by-count`) tend to be lower than Google Scholar but more reliable.
- A researcher at a teaching-focused university (like MUST) with any SCI/SSCI publications is above average for that context — calibrate expectations to institution type.
- **OpenAlex author disambiguation is unreliable for common Chinese names.** Always cross-verify with ORCID. A tiny profile merged into a mega-profile (or vice versa) will produce completely wrong h-index and citation metrics.
- **ORCID public API v3.0** is always available without authentication — prefer it over web scraping ORCID.org (which requires JavaScript).
- **Same-name different-person misattribution**: When OpenAlex assigns an author ID to a paper, check if that ID's profile (topics, institution, works_count) matches the researcher you're evaluating. If a finance professor's paper is assigned to an oncology researcher's profile, all downstream metrics are contaminated.
- **MUST Scholar keyword search is broken**: It returns all scholars regardless of query. Paginate through pinyin order to find specific scholars. See `references/must-scholar-navigation.md`.
- **OpenAlex indexing gap for recent MUST papers**: 2025-2026 papers frequently absent from OpenAlex. Pull the full publication list from MUST Scholar first, then use OpenAlex only for author identity disambiguation.
