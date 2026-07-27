---
name: ai-technique-evaluation
description: "Deep-validate whether an AI technique or product claim is real and worth adopting. 4-layer protocol. Use when the user asks 'is X really effective?' or 'should I adopt Y?'."
---

# AI Technique Evaluation Protocol

When the user questions whether an AI technique, product, or claim is genuinely effective, do a structured 4-layer investigation before giving conclusions.

## Trigger Phrases
- "这个真的真实可靠有效吗？"
- "should I adopt X?"
- "is X worth it?"
- "does X actually work?"
- Any skepticism about a tech claim

## Prerequisite: Paper Quality Screening (ALWAYS run first)

Before citing ANY academic paper as evidence, verify its credibility. Domain/title match alone is NOT enough — predatory journals publish keyword-matched junk with 0 references and 0 peer review.

Hard reject criteria:
- References < 20 (0 references = automatic rejection regardless of topic match)
- Venue not indexed in Scopus/WoS/IEEE Xplore
- Journal created < 2 years ago with no established track record
- Non-specialist author institutions with no prior publications in the domain

See `references/paper-quality-screening.md` for full protocol, OpenAlex verification script, and pre-vetted venue lists.

When a paper fails screening, tell the user explicitly WHY and offer to find legitimate alternatives. Never present a flagged paper as credible evidence.

## 4-Layer Investigation Protocol

### Layer 1: Academic Papers
- Search arXiv API (export.arxiv.org/api/query) for the seminal paper and follow-up work
- Look for: original paper, independent replications, critical follow-ups that point out limitations
- Red flags: only one group's papers, no independent validation, benchmark-only claims
- Key question: "Did anyone NOT on the original team validate this?"

### Layer 2: Open-Source Implementations
- Search GitHub API for repos implementing the technique
- Check: star count, fork count, last update date, open issues
- Red flags: dead repos, no community adoption, only demo-quality code
- Also search for forks/alternatives that fix original limitations

### Layer 3: Community and Industry
- Hacker News discussions (hn.algolia.com/api)
- Red flags: community consensus that benchmarks are gamed, cost hidden
- Industry: look for SaaS products built on the technique (commercialization is a weak signal)

### Layer 4: Cross-Reference and Synthesis
- Map claims from each layer against each other
- Identify: contradictions between academic claims and community experience
- Identify: cost gaps (paper does not discuss cost but implementations reveal it)
- Identify: domain gaps (paper tested on benchmark X, user needs task Y)

## Output Format
Structure findings as:
1. Core claim and evidence strength (strong/moderate/weak)
2. Independent validation (exists / does not exist)
3. Known limitations the paper did not emphasize
4. Cost-benefit for THIS user's specific use cases (not generic)
5. Practical next step (if applicable)

## Pitfalls
- **Keyword-matched predatory papers:** A paper whose title perfectly matches the user's domain can still be junk. Always screen venue, citations, and references BEFORE presenting the paper as evidence. The user explicitly corrected this: "不是看到领域符合就行，随便搜一个野鸡注水造价论文". See `references/paper-quality-screening.md`.
- AlpacaEval / MT-Bench wins may reflect judge model bias, not genuine quality improvement
- Academic benchmarks do not equal user's actual task domain. Always flag this gap explicitly.
- GitHub star count can be inflated by HN launches; weight maintenance activity and issues more.
- Always use APIs (arXiv, GitHub) for search, not just web_search, to get structured queryable data.

## Reference Files
- `references/moa-research.md` — Condensed MoA paper findings and practical conclusions (July 2026)
- `references/paper-quality-screening.md` — Academic paper credibility verification protocol: venue checks, citation/reference thresholds, OpenAlex screening script, pre-vetted journal lists (July 2026)

## Anti-Patterns
- Do NOT recommend a paper based on title/domain keyword match without running the full quality screening protocol. A perfect title match on a predatory-journal paper (0 references, 0 peer review) is worse than silence.
- Do not stop at the seminal paper's abstract. Read at least 3 papers (original + critique + improvement).
- Do not claim "it works" without noting the domain gap between benchmarks and user's tasks.
- Do not ignore cost. If the paper does not discuss it, flag it as a gap.
- Do not give a binary yes/no. The truth is usually domain-dependent.
