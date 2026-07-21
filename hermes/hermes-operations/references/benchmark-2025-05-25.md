# Benchmark Results — 2025-05-25

Three models tested: DeepSeek V4 Pro, MiMo 2.5 Pro, Qwen3.7 Max.

## Tier 1: Tool-Calling Stability

| Model | Pass Rate | Avg Time | Failures |
|-------|-----------|----------|----------|
| Qwen3.7 Max | 6/6 | 43.3s | — |
| MiMo 2.5 Pro | 6/6 | 54.0s | — |
| DeepSeek V4 Pro | 5/6 | 86.1s | skill-usage timeout |

## Tier 2: Core Capability

| Model | Tasks Passed | Avg Time | Failures |
|-------|-------------|----------|----------|
| MiMo 2.5 Pro | 10/10 | 16.4s | — |
| Qwen3.7 Max | 10/10 | 29.7s | — |
| DeepSeek V4 Pro | 8/10 | ~78s (est) | text-creative + text-summarize timeout |

## Capability Details

### Coding
- **DeepSeek**: Best. 320-line LRU Cache with __slots__, sentinel nodes, 10 tests — LeetCode editorial quality. 12 refactor improvements documented, kept original as reference.
- **Qwen**: Good but simpler. 8 test scenarios. Refactor uses set() dedup (more Pythonic than DeepSeek's dict.fromkeys). Extracted 2 helpers vs DeepSeek's 1.
- **MiMo**: Fastest (10.5s refactor). Output quality not captured (script bug).

### Reasoning
- **DeepSeek**: 3 valid solutions to logic puzzle. Systematic enumeration, 164 lines of derivation. Noted ambiguity and suggested additional constraint.
- **Qwen**: ANSWERED WRONG. Claimed 2 solutions but didn't satisfy constraint 4 (|Eve-Carol| should be 2, got 3). This is critical — returncode=0 masked the error.
- **MiMo**: Completed in 12.3s. Quality not captured.

### Chinese
- **Qwen**: Best. Accurate 成语 usage ("温水煮青蛙"), emotional resonance in workplace response, natural rhythm control. Removed AI clichés ("具体而言", "此外", "总体而言") effectively.
- **DeepSeek**: All Chinese/text tasks TIMED OUT. Critical compatibility issue with Hermes for text-heavy Chinese tasks.
- **MiMo**: Completed in ~20s. Quality not captured.

### Text
- **Qwen**: Multi-sensory creative writing (5 senses), complete emotional arc. Structured markdown summary with comparison table + glossary.
- **DeepSeek**: Timed out.
- **MiMo**: Completed in ~21s. Quality not captured.

### Context
- Both DeepSeek and Qwen passed cross-turn memory and long-document retrieval correctly.
- DeepSeek: tripled_secret=22173, SECRET_SALT='hermes-bench-2026', 13 microservices, P99 750→180ms.
- Qwen: same results, noted "didn't re-read data.json — relied on memory."

## Cost Per Run (6 tasks, estimated upper bound)

| Model | Total Cost | Monthly (20/day) |
|-------|-----------|-----------------|
| DeepSeek V4 Pro | $0.06 | ~$6 |
| MiMo 2.5 Pro | $0.15 | ~$15 |
| Qwen3.7 Max | $0.47 | ~$47 |

## Final Verdict

- **Daily driver**: MiMo 2.5 Pro (fastest, most stable, reasonable cost)
- **Coding/reasoning**: DeepSeek V4 Pro (best quality, but avoid text-heavy tasks)
- **Chinese**: Qwen3.7 Max (best cultural nuance, but most expensive)
