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
- AlpacaEval / MT-Bench wins may reflect judge model bias, not genuine quality improvement
- Academic benchmarks do not equal user's actual task domain. Always flag this gap explicitly.
- GitHub star count can be inflated by HN launches; weight maintenance activity and issues more.
- Always use APIs (arXiv, GitHub) for search, not just web_search, to get structured queryable data.

## Reference Files
- `references/moa-research.md` — Condensed MoA paper findings and practical conclusions (July 2026)

## Anti-Patterns
- Do not stop at the seminal paper's abstract. Read at least 3 papers (original + critique + improvement).
- Do not claim "it works" without noting the domain gap between benchmarks and user's tasks.
- Do not ignore cost. If the paper does not discuss it, flag it as a gap.
- Do not give a binary yes/no. The truth is usually domain-dependent.
