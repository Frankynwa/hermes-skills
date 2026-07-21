# Round 1 Benchmark Results — May 24, 2026

> **⚠️ Pricing in this table is outdated.** MiMo V2.5 had a permanent price reduction on May 27, 2026. See `references/provider-pricing-may2026.md` for current pricing.

## Models Tested

| Model | Provider | Context | Input Price | Output Price | Cache Read |
|---|---|---|---|---|---|
| DeepSeek V4 Pro | deepseek | 1M | $0.435/M | $0.87/M | $0.0036/M |
| MiMo 2.5 Pro | xiaomi | 1M | $1.0/M | $3.0/M | $0.2/M |
| Qwen3.7 Max | dashscope | 1M | $2.5/M | $7.5/M | N/A |

## Results

| Task | DeepSeek | MiMo | Qwen |
|---|---|---|---|
| simple-tools | 61.8s ✅ | 47.5s ✅ | 44.9s ✅ |
| chained-tools | 141.9s ✅ | 56.6s ✅ | 49.7s ✅ |
| error-recovery | 46.5s ✅ | 38.3s ✅ | 26.5s ✅ |
| coding | 109.5s ✅ | 55.1s ✅ | 43.5s ✅ |
| instruction | 46.0s ✅ | 47.7s ✅ | 27.7s ✅ |
| skill-usage | 222.0s ⏱️ timeout | 102.8s ✅ | 74.5s ✅ |
| **Pass Rate** | **5/6** | **6/6** | **6/6** |
| **Avg Time** | **79.8s** | **58.0s** | **44.5s** |
| **Est. Total Cost** | **$0.061** | **$0.149** | **$0.470** |

## Key Findings

1. **Qwen fastest** (44.5s avg), ~1.3x faster than MiMo, ~1.8x faster than DeepSeek
2. **DeepSeek cheapest** ($0.061/run), ~2.4x cheaper than MiMo, ~7.7x cheaper than Qwen
3. **MiMo best balance**: 6/6 pass, reasonable speed, reasonable cost
4. **DeepSeek stuck on skill-usage** (timeout at 222s) — complex multi-skill chains are a weakness
5. **Qwen consistently ~3.15x more expensive than MiMo** across all tasks (stable ratio)
6. All three models correctly identified bugs in coding task (floating-point + off-by-one)
7. DeepSeek produced most detailed output (markdown tables, 9 test cases) but slowest

## Recommendation

- **Primary**: MiMo 2.5 Pro ($15/mo est, 100% pass)
- **Fallback**: DeepSeek V4 Pro (simple tasks, cost savings)
- **Speed-critical**: Qwen3.7 Max (fastest, but 3x cost of MiMo)
