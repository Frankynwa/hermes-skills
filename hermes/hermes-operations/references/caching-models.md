# Cache Hit Rate Findings (2025-05-25 session)

## DeepSeek V4 Pro — Persistent Prefix Caching

Tested with `hermes chat -q -v --profile bench-deepseek` (multi-turn, 3 consecutive calls):

```
Call #1 (turn 1):
  Model: deepseek-v4-pro
  Cost: $0.000204
  Cache: 14336/14411 tokens hit (99%)

Call #2 (turn 2):
  Model: deepseek-v4-pro
  Cost: $0.000256
  Cache: 14336/14553 tokens hit (99%)

Call #3 (turn 3):
  Model: deepseek-v4-pro
  Cost: $0.000325
  Cache: 14336/14573 tokens hit (99%)
```

Key finding: ~14,336 tokens are persistently cached (Hermes system prompt + tool definitions). Every call, even the first, benefits from 99% cache hit. Cross-session persistent.

Cache read pricing (DeepSeek 2.5% discount until 2026/05/31):
- Full input: ¥3/M tokens
- Cache read: ¥0.025/M tokens (120x cheaper)

Effective input cost at 99% hit: ~¥0.05/M tokens.

## Qwen3.7 Max (DashScope) — Ephemeral Caching

Tested with `hermes chat -q -v --profile bench-qwen` (multi-turn, 2 consecutive calls):

```
Call #1 (turn 1):
  Model: qwen3.7-max
  Cached tokens: 0 (cache_miss: 14430)
  Total prompt: 14436 tokens

Call #2 (turn 2):
  Model: qwen3.7-max
  Cached tokens: 14430/14562 (99%)
```

Key finding: Ephemeral cache — first call creates the cache entry (0% hit), second call reads it (99% hit). TTL is approximately 5 minutes. Cross-session: resets to 0%.

Whether DashScope charges full price for cached tokens is unverified. If yes, the 99% hit rate reduces latency but not cost — 50-turn session input cost remains ~¥1.81.

## MiMo 2.5 Pro — Not Tested

MiMo account balance was exhausted during testing. Cache behavior unknown.

## Practical Impact

For real Hermes sessions (not one-shot `chat -q`):

- DeepSeek's persistent cache makes it extremely cost-effective for deployment. The "sticker price" (¥3/M input) is misleading — actual effective price is ~¥0.05/M.
- Qwen's ephemeral cache works well within a session but provides no cross-session savings.
- Cost comparison should ALWAYS account for the provider's caching model, not just sticker pricing.
