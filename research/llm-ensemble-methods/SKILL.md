---
name: llm-ensemble-methods
description: Methods for combining multiple LLM outputs to improve reasoning quality — MoA, self-consistency, ModelSwitch, multi-temperature sampling, and aggregation strategies. Use when evaluating or implementing multi-model reasoning pipelines, comparing model outputs, or debugging ensemble quality.
---

# LLM Ensemble Methods

Combining multiple LLM outputs to achieve higher reasoning quality than any single model.

## Core Taxonomy

Three paradigms, from simple to complex:

| Paradigm | Mechanism | Cost | Best For |
|----------|-----------|------|----------|
| Self-Consistency | Same model, N samples (vary temperature), majority vote | N× | Factual QA, math |
| Multi-Model Ensemble | Different models, one sample each, aggregator synthesizes | M× | Diverse-perspective tasks |
| Iterative Debate (MoA) | Proposers ↔ Aggregator, multiple rounds | M×R× | Deep reasoning, ambiguity resolution |

## Key Finding: Reasoning-Path Diversity > Model Diversity

**Beyond Consensus** (arxiv:2605.29116, 2026-05): Single-model multi-temperature sampling can outperform heterogeneous model pools. The diversity that matters is in reasoning paths, not training data.

**When Agents Disagree** (arxiv:2603.20324, 2026-03): Identifies a "selection bottleneck" — a crossover threshold in aggregation quality. Homogeneous Self-MoA teams consistently win under synthesis-based aggregation.

**Practical implication**: Before adding more models, add more temperature variance to existing models.

## Optimal Practical Configuration

Based on ModelSwitch (arxiv:2504.00762) + Beyond Consensus:

- **2 proposer models × 2 temperatures each = 4 samples** (ModelSwitch sweet spot)
- **Minimum viable**: 1 model × 3 temperatures (0.3, 0.7, 1.0) — backed by Beyond Consensus
- **Aggregator**: Use strongest available model, feed full reasoning chains (not just final answers)
- **Rounds**: 1-2 rounds max. ReM-MoA (arxiv:2606, 2026-06) shows depth > 2 causes degradation

## Aggregation Strategy

**Beyond Majority Voting** (arxiv:2510.01499, 2025-10): Simple majority voting discards information. Use:
- **OW (Optimal Weight)**: Weight models by historical accuracy
- **ISP (Inverse Surprising Popularity)**: Down-weight answers that are "too consensus"
- **Synthesis aggregation**: Feed all proposer outputs to aggregator for reasoning-chain-level synthesis

## MoA (Mixture of Agents) in Hermes

Hermes bundles a MoA implementation, but with hard constraints:

- **Aggregator**: Hardcoded to `AnthropicBedrock` + `claude-sonnet-4-20250514-v1:0` — requires AWS Bedrock credentials
- **Proposers**: Route through OpenRouter API — requires `OPENROUTER_API_KEY`
- **No provider override**: `moa.provider` config does not exist; provider is injected via `provider_dependency("anthropic_bedrock")`
- **No cost optimization**: No RouteMoA-style pre-screening (RouteMoA reduces cost 89.8%, arxiv:2601)

**Conclusion**: Hermes MoA requires both AWS Bedrock AND OpenRouter. Neither is bypassable via config.

## Research References

See `references/paper-index.md` for full paper catalog with abstracts, findings, arxiv IDs, and community implementations. Covers 10+ papers organized by category: Core, Optimization, Selection/Aggregation, Surveys, and Community.
