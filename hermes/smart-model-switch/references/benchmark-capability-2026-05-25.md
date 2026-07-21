# Hermes Model Capability Benchmark (2026-05-25)

Full results in `~/projects/hermes-model-bench/results/capability_*.json`.

## Methodology

10 tasks across 5 dimensions. Each task runs via `hermes chat -q --profile <model>` with tool access (file, terminal, search, skills). Measured: elapsed time, returncode, stdout, and API-level success detection (402, 401, 429, etc.).

Dimensions:
- Coding: LRU Cache implementation + code refactoring
- Reasoning: 5-person logic puzzle + tech architecture planning
- Chinese: workplace reply + AI-flavor rewrite
- Text: creative writing + long-form summarization
- Context: cross-turn memory + long-document retrieval

## Results

| Model | Pass Rate | Avg Time | Best Dimension | Worst Dimension |
|-------|-----------|----------|----------------|-----------------|
| DeepSeek V4 Pro | 8/10 | ~78s | Code (320-line LRU, 12 refactor points) | Chinese (both tasks timeout) |
| Qwen3.7 Max | 10/10 | 29.7s | Chinese (natural, idiomatic) | Code (functional but less thorough) |
| MiMo 2.5 Pro | 0/10 | N/A | N/A | ALL tasks: HTTP 402 balance exhausted |

## Critical Finding: MiMo False Positive

MiMo showed 10/10 "success" in the first benchmark because `hermes chat -q` returns returncode=0 even when the API returns 402 balance errors. The script treated returncode=0 as success. Lesson: always check stdout for API failure patterns.

## Dimension Details

### Coding
- Winner: DeepSeek V4 Pro
- DeepSeek: 320-line LRU Cache (doubly-linked list + hash, `__slots__`, sentinel node, 10 test scenarios). 12 refactor improvements with before/after comparison.
- Qwen: 8 test scenarios on LRU, 9 refactor improvements, more Pythonic (`set` over `dict.fromkeys`), extracted helper functions.

### Reasoning
- Winner: DeepSeek V4 Pro
- DeepSeek: Correctly found 3 valid solutions to 5-person logic puzzle. Python brute-force verification of 120 permutations.
- Qwen: Found only 2 solutions, one of which violated constraint 4. Claimed problem might have multiple valid answers instead of iterating.
- Both: Solid architecture planning (Meilisearch vs ES tradeoffs, permission models).

### Chinese
- Winner: Qwen3.7 Max
- Qwen: Natural idiom usage ("温水煮青蛙"), proper emotional resonance, 290 chars within limit, smooth AI-flavor removal.
- DeepSeek: Both Chinese tasks timed out.

### Text
- Winner: Qwen3.7 Max
- Qwen: 5-sense creative writing, proper emotional arc, open ending. Structured summary with glossary.
- DeepSeek: creative-text completed (good quality), summarization timed out.

### Context
- Tie
- Both correctly recalled secret_number across turns without re-reading. Both extracted SECRET_SALT, 13 microservices, P99 reduction from long doc.

## Cache Hit Rate (from `hermes chat -v`)

| Model | Call #1 Cache Hit | Call #2 Cache Hit | Mechanism |
|-------|-------------------|-------------------|-----------|
| DeepSeek V4 Pro | 14336/14411 (99%) | 14336/14553 (99%) | Persistent prefix cache, cross-session reuse |
| Qwen3.7 Max | 0/14436 (0%) | 14430/14562 (99%) | Ephemeral cache, 5-min TTL, session-scoped |

DeepSeek's persistent caching means even a fresh session's first API call gets 99% cache hit on the system prompt + tool definitions. This slashes effective input cost by 120x (0.025 vs 3 yuan/M for cached vs uncached).

Qwen's ephemeral cache means first call of each session pays full input price, but subsequent calls within 5 minutes get 99% hit.

## Benchmarking Pitfalls

1. hermes chat -q returns returncode=0 on API errors (402, 401, 429). Must grep stdout for failure patterns.
2. -v flag required to see token usage + cache hit data.
3. Single-run benchmark needs per-task timeout (600s) for models that can stall on complex chains.
4. hermes profiles need their own .env symlink; they don't inherit from ~/.hermes/.env.
5. MiMo API key format: base URL `https://token-plan-cn.xiaomimimo.com/v1` with XIAOMI_API_KEY in .env.

## Project

~/projects/hermes-model-bench/
GitHub: https://github.com/Frankynwa/hermes-model-bench
