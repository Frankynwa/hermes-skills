# Three-Judge Cross-Validation Methodology

## Problem

When using LLM-as-Judge to evaluate model complementarity, the judge model has inherent self-preference bias. A model judging "me vs other" will systematically favor its own outputs or its own reasoning style.

## Solution

Use at least 2 independent judge models (ideally 3) and average their verdicts.

## Empirical Evidence (this project)

15 questions × 4 models × 3 judges:

| Judge | Self-bias (net win rate) | Pattern |
|-------|------------------------|---------|
| DeepSeek V4 Pro | -1 | Self-critical, favors others |
| Qwen 3.8-Max | +4 | Strong self-preference |
| MiMo v2.5 Pro | +1 | Mild self-preference |

Judge self-bias ranges from -1 to +4. If only one judge were used, complementarity rankings would shift dramatically.

## Complementarity Stability Analysis

| Model Pair | DS score | Qwen score | MiMo score | Range | Stable? |
|-----------|:--------:|:---------:|:---------:|:-----:|:-------:|
| MiniMax + MiMo | 20.0% | 20.0% | 20.0% | 0.0 | ✓ All agree |
| Qwen + MiniMax | 33.3% | 40.0% | 6.7% | 33.3 | ✗ MiMo disagrees |
| Qwen + DS | 26.7% | 53.3% | 13.3% | 40.0 | ✗ Qwen favors self-pair |

Only MiniMax + MiMo shows consistent low complementarity across all three judges — confirming it's a real signal, not a judge artifact.

## Protocol

1. Run all model pairs through each judge
2. Anonymize answers (label "Answer A" / "Answer B", don't reveal which model)
3. Use structured verdict format: `VERDICT: A更好` / `B更好` / `等价` / `都不好`
4. Compute complementarity = (model_A_only_correct + model_B_only_correct) / total
5. Average across judges for final score
6. Flag pairs with high variance (>20% range) as "unstable — judge-dependent"

## Tool Integration

Script: `scripts/model_complementarity.py`
Usage: `python3 model_complementarity.py --judge --judge-model <model>`
