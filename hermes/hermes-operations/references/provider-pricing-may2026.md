# Provider Pricing Reference — May 27, 2026

All prices in CNY (¥) per million tokens, for domestic (China) use.

## MiMo V2.5 Series (effective May 27, 2026)

| Model | Input (cache miss) | Input (cache hit) | Output | Cache Discount |
|---|---|---|---|---|
| mimo-v2.5-pro | ¥3.00 | ¥0.025 | ¥6.00 | 120x |
| mimo-v2.5 | ¥1.00 | ¥0.02 | ¥2.00 | 50x |

**Price reduction announcement**: V2.5 series had a permanent price reduction effective 2026-05-27 00:00 GMT+8. Cache hit price dropped from ¥1.40 to ¥0.025 (56x). Source: platform.xiaomimimo.com/static/docs/news/v2.5-price-update.md

## DeepSeek V4 Series

| Model | Input (cache miss) | Input (cache hit) | Output | Cache Discount |
|---|---|---|---|---|
| deepseek-v4-pro | ¥12.00 | ¥1.00 | ¥24.00 | 12x |
| deepseek-v4-flash | ¥1.00 | ¥0.20 | ¥2.00 | 5x |

Source: api-docs.deepseek.com

## Qwen / DashScope (Alibaba Cloud)

| Model | Input (≤32K) | Input (≤128K) | Input (≤252K) | Output | Cache |
|---|---|---|---|---|---|
| qwen3-max | ¥1.20 | ¥2.40 | ¥3.00 | ¥6.00 (≤32K) / ¥12.00 / ¥15.00 | N/A |
| qwen-max | ¥1.60 | — | — | ¥6.40 | N/A |

Qwen does not offer explicit cached input pricing (CacheReadPrice=0).
Source: Alibaba Cloud Model Studio pricing page via GitHub mirror (caidaoli/ccLoad)

## Hermes Session Cost Comparison

Typical Hermes session: ~14,500 tokens cached system prompt + tools, ~100 new input tokens/turn, ~200 output tokens/turn.

**Per-turn cost (after cache warmup):**

| Model | Cache Input | New Input | Output | **Per-turn** |
|---|---|---|---|---|
| MiMo V2.5 Pro | 14,500 × ¥0.025/M = ¥0.00036 | 100 × ¥3/M = ¥0.0003 | 200 × ¥6/M = ¥0.0012 | **¥0.00186** |
| Qwen3-max | 14,500 × ¥1.20/M = ¥0.0174 | 100 × ¥1.20/M = ¥0.00012 | 200 × ¥6/M = ¥0.0012 | **¥0.0187** |
| DeepSeek V4 Pro | 14,500 × ¥1/M = ¥0.0145 | 100 × ¥12/M = ¥0.0012 | 200 × ¥24/M = ¥0.0048 | **¥0.0205** |

**50-turn session total**: MiMo ¥0.093 | Qwen ¥0.94 | DeepSeek ¥1.03

MiMo is ~11x cheaper than DeepSeek and ~10x cheaper than Qwen with caching.
