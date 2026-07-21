---
name: multi-model-strategies
description: "Strategies for using multiple AI models together — MoA, ensembles, fallback chains, cost-benefit analysis."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [multi-model, ensemble, MoA, fallback, cost-analysis]
    category: research
    related_skills: [arxiv, llm-wiki]
---

# Multi-Model Strategies

When the user wants to compare, combine, or orchestrate multiple AI models — MoA, model ensembles, fallback chains, or cost-benefit analysis of multi-model setups.

## When This Skill Activates

Use this skill when the user:
- Asks about Mixture of Agents (MoA), multi-model committees, or LLM ensembles
- Questions whether a multi-model approach is worth the cost for a specific task
- Wants to set up a local multi-model pipeline without expensive APIs (OpenRouter, AWS Bedrock)
- Asks about model diversity vs perturbation diversity in ensemble methods
- Compares single-model vs multi-model approaches for reasoning tasks

## Core Knowledge: MoA Research Landscape

### Foundational Papers

1. **Beyond Consensus: Trace-Level Synthesis in Mixture of Agents** (Fadnavis et al., 2026-05-27)
   arxiv: 2605.29116 — https://arxiv.org/abs/2605.29116
   
   Key finding: *"A single model with perturbation-induced trace variation outperforms heterogeneous model pools across structured reasoning, PhD-level science, competition mathematics, and competitive programming."*
   
   Method: SC-MoA (Self-Consistent Mixture of Agents) — semantic-preserving **input perturbations** (not just temperature) on a single model. Aggregator reads complete reasoning traces, not just final answers. "Aggregation paradox": aggregator can correct errors even when models unanimously agree.
   
   Status: May 2026, very new, not yet independently replicated.

2. **Self-Consistency Improves Chain of Thought Reasoning** (Wang et al., Google, 2022-03)
   arxiv: 2203.11171 — https://arxiv.org/abs/2203.11171
   
   Foundation: sampling multiple reasoning paths from the SAME model (temperature > 0), then majority vote. Proves single-model diversity improves reasoning. Does NOT compare against heterogeneous model pools.

3. **Harnessing Multiple Large Language Models: A Survey on LLM Ensemble** (Chen et al., 2025)
   arxiv: 2502.18036 — https://arxiv.org/abs/2502.18036
   
   Systematic taxonomy: ensemble-before-inference, ensemble-during-inference, ensemble-after-inference. Good map of the field. Does not cover Beyond Consensus (too new).

4. **Mixture-of-Agents Enhances LLM Capabilities** (Wang et al., Together AI, 2024-06)
   arxiv: 2406.04692 — https://arxiv.org/abs/2406.04692
   
   Original MoA paper. Open-source models in layered architecture beat GPT-4 Omni on AlpacaEval 2.0 (65.1% vs 57.5%). 2955 GitHub stars. Academic origin.

5. **RouteMoA** (Wang et al., ACL 2026)
   Cost optimization: light scoring router pre-screens models, only calls high-potential subset. **89.8% cost reduction, 63.6% latency reduction.** Makes MoA practical.

6. **ReM-MoA** (Ping et al., 2026-06)
   Fixes depth degradation: existing MoA variants degrade with more layers. Reasoning memory mechanism solves this.

### Hermes Agent MoA Implementation

- Hardcoded to **AnthropicBedrock** provider (`us.anthropic.claude-sonnet-4-20250514-v1:0`) for aggregator
- External proposal models via **OpenRouter** API (`moa.openrouter_api_key`)
- Config: `moa.openrouter_api_key`, `moa.external_models`, `moa.num_proposal_steps`
- Cannot use with existing MiMo/DeepSeek providers without code modification
- Provider is dependency-injected (`provider_dependency("anthropic_bedrock")`) but no config option to override

## Local Multi-Model Strategy (No OpenRouter / AWS)

### Simplest Effective Setup

Based on Beyond Consensus: same model, different perturbations.

**Proven approach (from the literature):**
- 3x same model (e.g., MiMo) with different parameters
- Mix input perturbation + temperature variation
- Strongest model as aggregator (e.g., DeepSeek V4 Pro)

**Practical implementation:**
```
[MiMo temp=0.3 + prompt variant A] ─┐
[MiMo temp=0.7 + prompt variant B] ─┼─→ DeepSeek V4 Pro (aggregator) → final output
[MiMo temp=1.0 + prompt variant C] ─┘
```

Input perturbation examples: rephrase the question, change sentence structure, add/remove context framing — all while preserving semantics.

### When This Is Worth It

| Task type | Multi-model gain | Reason |
|-----------|-----------------|--------|
| LVGL / embedded bug debugging | High | Cross-trace reasoning catches missed call chains |
| Strategy backtest analysis | Medium-High | Multiple perspectives on factor validity |
| Academic paper interpretation | Medium | Different models notice different nuances |
| Simple commands / messages | Zero | Overhead > benefit |
| Subjective interpretation | Low | Iteration can muddy clear insights |

### Cost Reality

- MoA is **5-15x** token cost of single-model call
- RouteMoA brings that down ~90%, still 1.5-3x single-model
- 2-round iteration is sweet spot; 3+ risks degradation (ReM-MoA finding)
- For local: cost = N × proposal_tokens + aggregator_tokens × rounds

## Pitfalls

- **Benchmark ≠ real task**: MoA papers measure AlpacaEval/MMLU — not LVGL debugging or strategy analysis. Your gains may differ.
- **Beyond Consensus is unverified**: May 2026, single team, no independent replication yet. The claim is strong but not settled science.
- **Temperature ≠ input perturbation**: Beyond Consensus uses semantic-preserving **input** perturbations. Temperature alone gives weaker diversity.
- **Layers don't guarantee quality**: ReM-MoA shows depth degradation. 2 rounds is safe; 3+ needs the memory mechanism.
- **MoA tool ≠ accessible on Hermes**: Requires both AWS Bedrock credentials AND OpenRouter key. Not usable with MiMo/DeepSeek-only setup.
- **AlpacaEval bias**: Some community criticism that MoA scores reflect GPT-4 judge preference, not genuine quality improvement.
