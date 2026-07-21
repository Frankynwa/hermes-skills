# Agent Benchmark Data — Cloud-OpsBench Findings

Source: Tracer-Cloud/opensre issue #2074, citing Wang et al. "Cloud-OpsBench" (arXiv:2603.00468v1, Feb 2026).

Cloud-OpsBench tests 452 fault cases across 40 fault types in Kubernetes environments using a deterministic State Snapshot Paradigm (no live cluster needed).

## Key Model Findings (from paper, reproduced in opensre issue)

| Model | A@1 Score | Failure Mode |
|---|---|---|
| DeepSeek-V3.2 | 0.73 | Best overall; wins via exploration depth (avg 10 steps, RAR=0.11 self-correction) |
| GPT-5 | 0.67 | Relevance-centric |
| Claude-4-Sonnet | 0.50 | Speculative shortcuts (ZTDR=0.32) |
| GPT-4o | 0.49 | Premature convergence (avg 5.67 steps) |
| Qwen3-14B | 0.34 | Improves to 0.71 with 3-shot ICL (in-context learning) |

## Relevance to Hermes Agent

The benchmark's findings align with what matters for Hermes:
- **Exploration depth matters for agent tasks.** DeepSeek's strength (10-step exploration) maps directly to Hermes multi-turn tool calling patterns.
- **ICL capability matters for skill loading.** Qwen3's dramatic improvement with few-shot examples (0.34 → 0.71) suggests it benefits significantly from Hermes skill injection (skills are essentially structured in-context examples).
- **Premature convergence kills agent performance.** GPT-4o's 5.67-step average is a warning sign — models that "jump to conclusions" fail at multi-step agent workflows.

## Caveats

- Cloud-OpsBench tests cloud SRE tasks, not general agent use. Extrapolate cautiously.
- DeepSeek-V3.2 was tested, not V4 Pro. V4 Pro may perform differently.
- Qwen3-14B (small model) was tested, not Qwen3.7 Max (frontier model). Frontier Qwen likely performs much better.
- MiMo was NOT included in this benchmark. No direct comparison data available.
