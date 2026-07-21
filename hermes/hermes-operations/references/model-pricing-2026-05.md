# Model Pricing Comparison (2026-05-24)

Raw data from OpenRouter API for the three models compared. Pricing in USD per token.

## Qwen3.7 Max
- Provider ID: `qwen/qwen3.7-max`
- Context window: 1,000,000 tokens
- Input: $0.0000025/token
- Output: $0.0000075/token
- Input cache write: $0.000003125/token (no cache read support)
- Hermes provider: DashScope (百炼), env var: DASHSCOPE_API_KEY

## MiMo 2.5 Pro
- Provider ID: `xiaomi/mimo-v2.5-pro`
- Context window: 1,048,576 tokens
- Input: $0.000001/token
- Output: $0.000003/token
- Input cache read: $0.0000002/token
- Hermes provider: Xiaomi MiMo, env var: XIAOMI_API_KEY

## DeepSeek V4 Pro
- Provider ID: `deepseek/deepseek-v4-pro`
- Context window: 1,048,576 tokens
- Input: $0.000000435/token
- Output: $0.00000087/token
- Input cache read: $0.000000003625/token (near-free)
- Hermes provider: DeepSeek, env var: DEEPSEEK_API_KEY
- Special: CNY pricing (2.5折至2026/05/31): flash input=1元/M output=2元/M, pro input=3元/M output=6元/M

## Cost Comparison (10K input + 5K output conversation)

| Model | Cost per conversation | Relative |
|---|---|---|
| Qwen3.7 Max | ~$0.0625 | 7.2x |
| MiMo 2.5 Pro | ~$0.025 | 2.9x |
| DeepSeek V4 Pro | ~$0.0087 | 1.0x (baseline) |

DeepSeek V4 Pro's cache read pricing ($0.000000003625/token) means Hermes context compression delivers near-zero additional cost for repeated context — a massive advantage for long-running agent sessions.
