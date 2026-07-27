# Model Complementarity Analysis

How to determine if two models are truly complementary — not just different.
Based on survey of 8 papers + 3 benchmark frameworks (2026.07).

## Core Insight

"Ensembles of heterogeneous model families achieve better performance scaling than those
formed within a single model family." — The Law of Multi-Model Collaboration (2025.12)

MiMo (Xiaomi) and DeepSeek are different model families → baseline complementary assumption
is valid without further verification. But actual complementarity depends on task domain.

---

## Four Methods for Measuring Complementarity

### Method 1: Error Overlap Matrix (CORE paper, 2026.01)

Mishra et al., "Collaborative Reasoning via Cross Teaching" (arxiv:2601.21600)

Simplest and most actionable. Requires 20-50 test questions from your actual task domains.
Score each model's answer correct/incorrect, then fill:

| | DeepSeek correct | DeepSeek wrong |
|---|---|---|
| MiMo correct | Both right | MiMo-only right |
| MiMo wrong | DS-only right | Both wrong |

Complementarity score = (MiMo-only + DS-only) / total questions

- >20%: strong complementarity, MoA valuable
- 5-20%: weak complementarity, MoA marginal
- <5%: redundant, single model sufficient

CORE paper uses a DPP-inspired diversity term to explicitly penalize error overlap
during training, but the raw matrix is enough for analysis.

### Method 2: Response Fingerprint Clustering (DFPE paper, 2025.01)

Cohen et al., "Diverse Fingerprint Ensemble" (arxiv:2501.17479)

Instead of scoring correctness, compare response STRUCTURE:
- Answer length and verbosity
- Structured vs free-form (bullets vs prose)
- Reasoning chain depth (how many inferential steps)
- Knowledge source type (docs, code, empirical experience)

If responses are structurally similar → same reasoning path → low complementarity.
If structurally different → different reasoning paths → high complementarity.

DFPE clusters model responses into fingerprint patterns, weights by per-subject accuracy.
Adapted for 2-model comparison: just compare response styles manually.

### Method 3: Per-Domain Accuracy Profiling (LLMRouterBench, ACL 2026)

Li et al., "LLMRouterBench" (arxiv:2601.07206)

33 models × 21 datasets. Core finding: "No single model rules every domain; models
exhibit complementary strengths." Split test questions by domain:

| Domain | MiMo | DeepSeek | Complementary? |
|--------|------|----------|----------------|
| Code | ? | ? | ? |
| Math | ? | ? | ? |
| Reasoning | ? | ? | ? |

Strong complementarity = different models excel in different domains.
Weak complementarity = one model dominates all domains.

### Method 4: Question Interpretation Diversity (Diverse LLMs paper, 2025.07)

Rosales & Miret, "Diverse LLMs or Diverse Question Interpretations?" (arxiv:2507.21168)

Core finding on binary QA: "question interpretation diversity consistently leads to
better ensemble accuracy compared to model diversity." Model diversity produced results
"between the best and worst ensemble members without clear improvement."

Implication: If you have only one model, try different prompt framings rather than
adding a second model. Different models may simply give mid-range results.

---

## Key Papers Summary

| Paper | Year | Venue | Core Contribution |
|-------|------|-------|-------------------|
| MoA (Together AI) | 2024.06 | - | Multi-layer iterative aggregation, AlpacaEval 65.1% |
| Beyond Consensus | 2026.05 | - | Single-model temperature perturbation > heterogeneous model pool |
| ModelSwitch | 2025.04 | - | Multi-LLM repeated sampling + consistency-gated switching |
| RouteMoA | 2026.01 | ACL 2026 | Cost reduction 89.8%, latency -63.6% via pre-screening |
| CORE | 2026.01 | - | Error overlap matrix + DPP diversity + cross-teaching |
| DFPE | 2025.01 | - | Response fingerprint clustering + per-subject weighting |
| LLMRouterBench | 2026.01 | ACL 2026 | 33 models × 400K instances, complementary strengths confirmed |
| Law of Multi-Model Collab | 2025.12 | - | Heterogeneous families outperform homogeneous ensembles |

---

## Engineering Reality

LLMRouterBench, RouterBench, and RouterEval are post-hoc evaluation tools — they require
pre-computed scores from all models on all test instances. Not usable for upfront
model selection.

Only actionable pre-hoc signal: model family difference. MiMo (Xiaomi/Huanfang) and
DeepSeek are from different model families → baseline complementarity is assumed.

---

## Empirical Results (2026.07.20)

15 questions × 4 models. DeepSeek as anonymous judge. Actual complementarity matrix:

### Per-Model Win Rate (out of 15 questions)

| Model | Win | Tie | Loss | Net |
|-------|:---:|:---:|:----:|:---:|
| qwen3.8-max-preview | 5 | 6 | 4 | +1 |
| deepseek-v4-pro | 5 | 4 | 6 | -1 |
| MiniMax-M3 | 4 | 8 | 3 | +1 |
| mimo-v2.5-pro | 3 | 8 | 4 | -1 |

### Pairwise Complementarity

| Pair | Rate | Verdict |
|------|:----:|---------|
| deepseek-v4-pro + MiniMax-M3 | 40.0% | Strong |
| qwen3.8-max + MiniMax-M3 | 33.3% | Strong |
| qwen3.8-max + deepseek-v4-pro | 26.7% | Strong |
| deepseek + mimo | 20.0% | Moderate |
| MiniMax + mimo | 20.0% | Moderate |
| qwen + mimo | 6.7% | Weak |

### Optimal Trio: deepseek-v4-pro + MiniMax-M3 + qwen3.8-max-preview

MiMo excluded — quality adequate but near 100% overlap with other models (no blind-spot coverage).

### Model Endpoints Discovered

| Model | Base URL | Quirks |
|-------|----------|--------|
| qwen3.8-max-preview | `https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1` | Has `reasoning_tokens` in output |
| MiniMax-M3 | `https://api.minimax.chat/v1` | Model name is `MiniMax-M3` (not M1 or M2) |
| kimi-k3 | `https://api.moonshot.cn/v1` | Requires `reasoning_effort` param; persistent 429 engine overload (new release, 2026.07) |
| mimo-v2.5-pro | `https://token-plan-cn.xiaomimimo.com/v1` | Pay-per-use API, separate from subscription key |
