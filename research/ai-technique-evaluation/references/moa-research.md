# Mixture of Agents (MoA) Research Summary

Condensed findings from July 2026 deep investigation.

## Key Papers

| Paper | Date | Key Finding |
|-------|------|-------------|
| Wang et al. "Mixture-of-Agents Enhances LLM Capabilities" (2406.04692) | 2024-06 | Seminal: layered MoA achieves 65.1% on AlpacaEval 2.0 vs GPT-4 Omni 57.5%, using only open-source models. |
| Schoenegger et al. "Wisdom of the Silicon Crowd" | 2024-02 | Independent validation: 12-LLM ensemble = 925-human crowd accuracy. Not statistically different. |
| Fadnavis et al. "Beyond Consensus: Trace-Level Synthesis in MoA" (2605.29116) | 2026-05 | Aggregation paradox: aggregator reading full reasoning traces corrects errors even when agents unanimously agree. Single model with perturbation outperforms heterogeneous model pools. |
| Wang et al. "RouteMoA" (2601.18130) | 2026-01 | ACL 2026. Reduces MoA cost by 89.8% and latency by 63.6% via dynamic routing. |
| Ping et al. "ReM-MoA" (2606.24437) | 2026-06 | Existing MoA variants fail with depth scaling (degradation, plateauing, saturation). Memory-augmented framework needed. |
| Li et al. "SMoA" (2411.03284) | 2024-11 | Sparse MoA reduces dense interaction overhead while preserving diversity. |

## Practical Conclusions for Local Implementation

### Minimal Viable Configuration
- 2 proposers + 1 aggregator = 3 models minimum
- 2 iteration rounds is the sweet spot (1 = no debate value, 3+ = diminishing returns)
- Beyond Consensus finding: same model at different temperatures (0.3/0.7/1.0) can outperform heterogeneous pools

### Where MoA Helps (domain-dependent)
- High: complex debugging (multi-model trace-level reasoning catches missed paths)
- Medium-High: strategy/method evaluation (multiple perspectives on factor effectiveness)
- Medium: paper interpretation (different models catch different nuances)
- Zero: simple instructions, subjective interpretation tasks

### Where MoA's Evidence is Weak
- All benchmarks are chatbot quality (AlpacaEval, MT-Bench) — not code debugging or domain reasoning
- GPT-4 as judge may introduce bias favoring outputs that "look good" to GPT-4
- No published studies on MoA for embedded/C development tasks

### Hermes Implementation
- Hardcoded: AnthropicBedrock (aggregator) + OpenRouter (proposers)
- No configurable provider for aggregator
- No cost optimization (no RouteMoA-style routing)
- Correctly implements layered architecture from original paper

## Cost Reality
- MoA is 5-15x single-model cost per query
- RouteMoA reduces this but from that elevated baseline
- Local approach (same model, different temperatures) costs ~4x single run (3 proposer calls + 1 aggregator)
