# Benchmark Landscape (2026-07)

Condensed from LMSys Chatbot Arena, MT-Bench, AlpacaEval 2.0, Arena-Hard, LiveBench, GAIA, SWE-bench, BFCL, C-Eval, CMMLU, SuperCLUE.

---

## 1. Human Preference (Crowdsourced ELO)

**LMSys Chatbot Arena:** Anonymous side-by-side chat, Bradley-Terry model, bootstrapped CIs. Anti-gaming: random pairing, IP rate limits.
- Gold standard but expensive/infeasible for fast iteration.

---

## 2. LLM-as-Judge

**MT-Bench:** 80 multi-turn questions, 8 categories. Two modes:
- Single: judge rates 1-10 against reference answer
- Pairwise: judge picks [[A]]/[[B]]/[[C]]
- Position bias fix: runs each pairwise twice (swap A/B), requires agreement
- Tie delta = 0.1

**AlpacaEval 2.0:** 805 instructions, pairwise vs GPT-4 Turbo. LC Win Rates: logistic regression controls length bias. Spearman = 0.98 with Arena.
- Key insight: length bias is #1 confound. Randomize order, control statistically.

**Arena-Hard:** 500 hardest Arena prompts. Better discrimination at top. GPT-4 judge.

---

## 3. Objective/Verifiable (No Judge)

**LiveBench:** 18 tasks, 6 categories. Fresh questions monthly from recent arXiv/news/IMDb. ALL verifiable ground truth — no LLM judge. Temp: creative=0.7, factual=0.0.
- Gold standard for contamination-free evaluation.

**GAIA:** 466 multi-step agentic questions. 3 difficulty levels. Exact match only.

**SWE-bench:** 2294 real GitHub issues. Model generates patch passing repo tests. pass@1. Docker sandbox.

**BFCL (Berkeley Function Calling):** V1-V4 evolution: single-turn → enterprise → multi-turn state-based → agentic. AST-based static analysis + execution-based.

---

## 4. Chinese Benchmarks

- C-Eval: 13,948 MC, 52 subjects
- CMMLU: 11,528 MC, 67 topics
- SuperCLUE: multi-dimensional rubric (accuracy, fluency, relevance, safety), human+LLM hybrid

---

## 5. Scoring Best Practices (10 Rules)

1. Position swap: always run pairwise twice (swap), require agreement
2. Length control: statistically (LC regression) or prompt the judge
3. Reference answers: provide gold answers for math/coding
4. Tie threshold: use delta for close scores
5. Chain of thought: explain before verdict
6. Consistency check: flag inconsistent double-pass results
7. Ensemble judges: multiple models for high-stakes
8. Calibration: 10% human spot-check
9. Avoid self-enhancement: different model family as judge
10. Parseable output: [[A]], [[B]], [[C]]

## 6. Anti-Cheating

- Rotate 20-30% of prompts monthly
- Time-bound tasks from recent events
- SHA256 pre-published hashes
- Joint evaluation window
- Detect: refusals, identical outputs, length gaming
