# MoA Research: Paper Details & Session Methodology

Source: arxiv search + analysis, 2026-07-20 session.

## Paper 1: Beyond Consensus (Fadnavis et al., 2026)

- **Title**: Beyond Consensus: Trace-Level Synthesis in Mixture of Agents
- **Authors**: Shreyas Fadnavis, Praitayini Kanakaraj, Felix Wyss
- **Published**: 2026-05-27
- **arxiv**: 2605.29116
- **URL**: https://arxiv.org/abs/2605.29116

**Full abstract:**

"When multiple LLM agents solve the same problem, standard practice compresses each agent's reasoning into a majority vote or layered synthesis, treating agreement as the finish line. We show this is unnecessarily lossy: an LLM aggregator that reads complete reasoning traces recovers correct solutions even when agents unanimously agree, with beneficial corrections consistently outweighing harmful ones -- the aggregation paradox. Majority voting has a ceiling that perturbation diversity does not raise (error correlations are identical); the aggregator's gain comes from trace-level complementarity, assembling correct intermediate steps from minority chains that voting discards. These findings motivate Self-Consistent Mixture of Agents which generates trace diversity through semantic-preserving input perturbations, safeguards the majority via anchored refinement with provable non-degradation guarantees, and always synthesizes -- never gates on consensus. A single model with perturbation-induced trace variation outperforms heterogeneous model pools across structured reasoning, PhD-level science, competition mathematics, and competitive programming. The unit of aggregation should be the reasoning trace, not the answer."

**Key terms:**
- "aggregation paradox" — aggregator corrects errors even during unanimous agreement
- "trace-level complementarity" — value comes from intermediate reasoning steps, not final answers
- "semantic-preserving input perturbations" — the diversity generation method (NOT just temperature)
- "anchored refinement with provable non-degradation" — mathematical guarantee that output >= best proposer
- SC-MoA — the proposed method name

**Relevance to local setup:**
The paper's core finding directly supports using a single model with perturbations rather than paying for multiple different models. The perturbation method is "semantic-preserving input perturbations" — rephrasing the prompt while preserving meaning. Temperature alone provides weaker diversity. A practical local implementation should combine both: input perturbation variants × temperature variants.

## Paper 2: Self-Consistency (Wang et al., Google, 2022)

- **Title**: Self-Consistency Improves Chain of Thought Reasoning in Language Models
- **Authors**: Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, Sharan Narang, Aakanksha Chowdhery, Denny Zhou
- **Published**: 2022-03-21
- **arxiv**: 2203.11171
- **URL**: https://arxiv.org/abs/2203.11171

**Abstract excerpt:**

"Chain-of-thought prompting combined with pre-trained large language models has achieved encouraging results on complex reasoning tasks. In this paper, we propose a new decoding strategy, self-consistency, to replace the naive greedy decoding used in chain-of-thought prompting. It first samples a diverse set of reasoning paths instead of only taking the greedy one, and then selects the most consistent answer by marginalizing out the sampled reasoning paths."

**What it proves:**
- Sampling multiple reasoning paths from SAME model (temperature > 0) beats greedy decoding
- Method: sample N times → majority vote on final answer
- Does NOT compare against heterogeneous model pools
- Foundation for the "single model diversity" paradigm

## Paper 3: LLM Ensemble Survey (Chen et al., 2025)

- **Title**: Harnessing Multiple Large Language Models: A Survey on LLM Ensemble
- **Authors**: Zhijun Chen, Xiaodong Lu, Jingzheng Li, et al. (14 authors)
- **arxiv**: 2502.18036
- **URL**: https://arxiv.org/abs/2502.18036

**Taxonomy:**
- ensemble-before-inference
- ensemble-during-inference
- ensemble-after-inference

**Note**: Published before Beyond Consensus (May 2026), so does not include SC-MoA findings.

## Paper 4: Original MoA (Together AI, 2024)

- **Title**: Mixture-of-Agents Enhances Large Language Model Capabilities
- **arxiv**: 2406.04692
- **URL**: https://arxiv.org/abs/2406.04692
- **GitHub**: 2955 stars, 385 forks

Open-source models in layered proposal-aggregation architecture. AlpacaEval 2.0: 65.1% (GPT-4 Omni: 57.5%). This is what Hermes Agent's /moa implements.

## Paper 5: RouteMoA (ACL 2026)

Cost optimization for MoA. 89.8% cost reduction, 63.6% latency reduction. Lightweight scoring router pre-screens models.

## Paper 6: ReM-MoA (2026-06)

Fixes depth degradation in MoA. Reasoning memory mechanism. Key insight: more layers ≠ better, existing variants degrade.

## Session Methodology

1. Searched arxiv API programmatically for MoA-related papers
2. Verified author names: Fadnavis → found correct paper ID (2605.29116)
3. Retrieved full abstracts via arxiv export API
4. Cross-referenced Hermes source code (`agent/moa.py`) for implementation details
5. Analyzed Hermes config (`config.yaml` moa section) for configuration options
6. Mapped research findings to user's specific use cases (LVGL, AlphaSeeker, psych-nlp)

## Important Correction Made During Session

Initial claim: paper titled "Beyond Consensus: Surpassing the Limits of LLM Ensembles with Perturbation-Driven Diversity"
Actual title: "Beyond Consensus: Trace-Level Synthesis in Mixture of Agents"
Correction triggered by user pressing for exact citations. Lesson: verify paper titles against arxiv API, don't rely on memory or LLM-generated titles.
