# LLM Ensemble: Paper Index

Key papers discovered during MoA deep-dive (2026-07-20).

---

## Core Papers

### Beyond Consensus: Trace-Level Synthesis in Mixture of Agents
- **arxiv**: 2605.29116
- **Date**: 2026-05
- **Key finding**: Single-model multi-temperature sampling can outperform heterogeneous model pools. Reasoning-path diversity matters more than model diversity. Aggregator reading full reasoning chains (not just final answers) can correct errors even when models unanimously agree.
- **Implication**: Before adding more models, add more temperature variance.

### ModelSwitch: Multi-LLM Repeated Sampling
- **arxiv**: 2504.00762
- **Date**: 2025-04
- **Key finding**: Combines repeated-sampling-then-voting with multiple models. Uses consistency as signal to dynamically switch between models. Outperforms both self-consistency AND multi-agent debate, while reducing costs. "Even weaker models" contribute complementary value.
- **Implication**: This is the direct implementation of "multi-temperature × multi-model" — the optimal practical configuration.

### When Agents Disagree: The Selection Bottleneck
- **arxiv**: 2603.20324
- **Date**: 2026-03
- **Key finding**: Identifies a crossover threshold s* in aggregation quality. Below threshold, heterogeneous diversity helps; above it, homogeneous Self-MoA wins. Explains contradictory findings in prior MoA literature.
- **Implication**: The aggregator model's quality is the limiting factor. Weak aggregator = diversity hurts.

### MoA (Original): Mixture-of-Agents
- **arxiv**: 2406.04692
- **Date**: 2024-06
- **Authors**: Together AI (Wang et al., incl. James Zou, Stanford)
- **Key finding**: Pure open-source models in multi-layer architecture achieve 65.1% AlpacaEval 2.0, beating GPT-4 Omni's 57.5%. GitHub: 2955 stars.
- **Limitation**: Only addresses model diversity, not reasoning-path diversity. No cost optimization.

---

## Optimization & Cost

### RouteMoA
- **arxiv**: 2601 (ACL 2026)
- **Key finding**: Lightweight scorer pre-screens models, calling only high-potential subset. Cost -89.8%, latency -63.6%. This is what makes MoA practically usable.

### ReM-MoA (Reasoning Memory MoA)
- **arxiv**: 2606 (2026-06)
- **Key finding**: Vanilla MoA variants degrade with depth (degeneration, early stopping, saturation). Reasoning memory mechanism fixes this. Deeper is NOT better without architectural guardrails.

### CTTS: Collective Test-Time Scaling
- **arxiv**: 2508.03333
- **Date**: 2025-08
- **Authors**: Song et al.
- **Key finding**: Systematically compares SA-MR, MA-SR, MA-MR paradigms. MA-MR (multi-agent multi-reward) consistently superior. +4.82% over Best-of-N, +7.06% over GPT-4.1.
- **Code**: github.com/magent4aci/CTTS-MM (2 stars, code pending release)

---

## Selection & Aggregation

### MCA: Mixture of Complementary Agents
- **arxiv**: 2605.24048
- **Date**: 2026-05
- **Key finding**: Proposer selection as combinatorial feature selection. Value = complementarity, not individual strength. Strongest models ≠ best combination.

### Beyond Majority Voting
- **arxiv**: 2510.01499
- **Date**: 2025-10
- **Authors**: Ai et al.
- **Key finding**: Majority voting discards latent heterogeneity and inter-model correlation. OW (Optimal Weight) and ISP (Inverse Surprising Popularity) provably improve collective decisions. Validated on MMLU, UltraFeedback, real healthcare setting.

### ME: Rethinking LLM Ensembling as Mixture Models
- **arxiv**: 2605.00419
- **Date**: 2026-05
- **Key finding**: Stochastic single-model selection at each token step. Mathematically equivalent to sampling from full ensemble distribution, but avoids separate forward pass per model.

---

## Surveys

### Awesome-LLM-Ensemble
- **arxiv**: 2502.18036 (survey paper)
- **GitHub**: junchenzhi/Awesome-LLM-Ensemble (251 stars)
- **Taxonomy**: Ensemble-before-inference, ensemble-during-inference, ensemble-after-inference

---

## Community Implementations

- **ensemble** (raiyanyahya/ensemble, 9★): Multi-model consensus debate via filesystem. LLMs propose → peer-review → rebut → vote → synthesize. CLI + MCP.
- **V-BReE** (MiladEbrahimiAbyzandi/V-BReE-test-time-scaling, 1★): Variance-thresholded Blinded Refinement Ensemble for MMLU-Pro.
- **Tiny-MoA**: CPU-level MoA with 1.2B + 600M + 90M models. Proof that small models can ensemble.
