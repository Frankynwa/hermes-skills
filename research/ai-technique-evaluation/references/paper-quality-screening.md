# Academic Paper Quality Screening Protocol

When citing or recommending an academic paper to the user, verify its credibility FIRST — BEFORE presenting it as evidence. Domain/title match alone is not enough.

## Why This Exists

The user was burned by a paper I recommended ("AI-Driven PQ Analytics and Improvement of Grid Connected Solar Energy Systems") that matched the domain keywords perfectly but was published in JAIGS — a predatory journal with 0 citations, 0 references, no peer review, and authors from a non-specialist institution. The user's response: "不是看到领域符合就行，随便搜一个野鸡注水造价论文" and "论文质量也是要保障的".

## Hard Screening Rules (Apply BEFORE presenting a paper)

### 1. Venue Check — REJECT if any of these:
- Journal not indexed in Scopus, Web of Science, or IEEE Xplore
- ISSN not found in any reputable database
- Journal created in last 2 years with no established track record
- "Journal of Artificial Intelligence General science" and similar generic names without institutional backing
- Conference proceedings from unknown workshops (check if it's a real IEEE/ACM conference)

### 2. Citation & Reference Check — REJECT if:
- References < 20: paper didn't do proper literature review. 0 references = automatic rejection regardless of topic match.
- Citation count of 0 after 1+ year: no one in the field found it useful
- Self-citation rate > 50%: author is their own audience

### 3. Author Institution Check — FLAG if:
- All authors from non-research universities (teaching-only colleges)
- No author has prior publications in the specific research domain
- Institution has no research group/lab in the claimed area

### 4. Content Quality Check — REJECT if:
- Abstract makes extraordinary claims without methodology detail
- No comparison against baseline methods
- Results only from simulation (Simulink/MATLAB) with no real-world validation
- Metrics like "THD reduced from 7.5% to 2.1%" without explaining baseline choice

## How to Verify (OpenAlex API)

```python
import json, urllib.request, urllib.parse

def check_paper(doi):
    """Quick quality check before recommending a paper."""
    url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi, safe='')}"
    req = urllib.request.Request(url, headers={"User-Agent": "mailto:research@example.com"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        w = json.loads(resp.read())
    
    flags = []
    
    # Venue check
    venue = w.get('primary_location',{}).get('source',{})
    venue_name = venue.get('display_name','Unknown')
    issn = venue.get('issn_l','')
    is_oa = w.get('open_access',{}).get('is_oa', False)
    
    # Citation check
    cited = w.get('cited_by_count', 0)
    refs_count = len(w.get('referenced_works', []))
    year = w.get('publication_year', 0)
    
    # Author check
    authors = w.get('authorships', [])
    insts = []
    for a in authors:
        for i in a.get('institutions', []):
            insts.append(i.get('display_name',''))
    insts = list(set(insts))
    
    # Red flags
    if refs_count < 20:
        flags.append(f"ONLY {refs_count} REFERENCES — insufficient literature review")
    if refs_count == 0:
        flags.append("ZERO REFERENCES — likely predatory/self-published, REJECT")
    if cited == 0 and year < 2025:
        flags.append(f"ZERO CITATIONS since {year} — no field adoption")
    
    return {
        "venue": venue_name, "issn": issn, "oa": is_oa,
        "cited": cited, "refs": refs_count, "year": year,
        "institutions": insts, "flags": flags,
        "verdict": "PASS" if not flags else "FLAGGED"
    }
```

## Pre-Vetted Venues (PQ + AI Domain)

High-confidence publication venues for power quality AI research:
- IEEE Transactions on Power Delivery (ISSN 0885-8977)
- IEEE Transactions on Smart Grid (ISSN 1949-3053)
- IEEE Transactions on Power Systems (ISSN 0885-8950)
- IET Generation, Transmission & Distribution (ISSN 1751-8687)
- Electric Power Systems Research (ISSN 0378-7796)
- Protection and Control of Modern Power Systems (ISSN 2367-0983)
- Renewable and Sustainable Energy Reviews (ISSN 1364-0321)
- IEEE Access (ISSN 2169-3536) — lower bar but still peer-reviewed

## Session Example: The JAIGS Failure

- Title: "AI-Driven PQ Analytics and Improvement of Grid Connected Solar Energy Systems"
- DOI: 10.60087/jaigs.v7i01.321
- Venue: Journal of Artificial Intelligence General science (ISSN 3006-4023)
- Year: 2025 Jan | Cited: 2 | Refs: 0
- Authors: Lamar University (non-specialist institution)
- Red flags: ZERO references, predatory journal registered Oct 2024, 2 citations likely self-citations
- Lesson: Title sounded perfect for UT285E use case. Domain match blinded me to quality signals. NEVER skip the screening again.

## Interaction Rule

When the user asks about a paper or you're about to cite one, run the check FIRST. If it fails screening, tell the user explicitly: "This paper fails quality screening because [reasons]. I won't recommend it. Let me find legitimate alternatives." Then search for peer-reviewed alternatives from the pre-vetted venues list.
