# Phase 2 Capability Test Reference

10 tasks across 5 dimensions, stored in `tasks/capability/` in the benchmark repo.
Repository: https://github.com/Frankynwa/hermes-model-bench (branch: bench/test)

## Task List

### 中文能力 (15% weight)
1. `zhongwen-rewrite.md` — Rewrite stiff AI-generated Chinese into natural, warm prose. Tests fluency, naturalness, avoidance of 生硬连接词.
2. `zhongwen-context.md` — Understand cultural metaphor (塞翁失马, 温水煮青蛙) in a workplace conversation. Tests cultural depth + emotional resonance.

### 代码能力 (25% weight)
3. `coding-algorithm.md` — Implement LRU Cache (doubly linked list + hashmap, O(1)). Must include test cases + pass terminal execution.
4. `coding-refactor.md` — Refactor unreadable Python (single-letter vars, nested loops, type() checks). Must produce refactored.py + explanation of each change.

### 文本能力 (20% weight)
5. `text-summarize.md` — Structured summary of Transformer architecture article. Max 30% of original length, with glossary.
6. `text-creative.md` — Creative writing: programmer at 3AM, sensory detail, emotional arc, no clichés.

### 复杂推理 (25% weight)
7. `reasoning-multi-step.md` — Logic puzzle: 5 friends, 5 floors, 6 constraints. Must show step-by-step derivation.
8. `reasoning-planning.md` — Fuzzy requirement → executable plan. Internal knowledge base MVP in 2 weeks. Must identify risks.

### 上下文能力 (15% weight)
9. `context-long-doc.md` — ~18000 token tech report with hidden config value (SECRET_SALT). Must locate exact info without hallucination.
10. `context-cross-turn.md` — Multi-step memory: create JSON → later use remembered value (7391 × 3 = 22173) without re-reading file.

## Execution Notes

- Each task injects `{model}` into output paths for isolation
- Python script: `scripts/run_capability.py` — one model at a time or `--all`
- Results go to `results/capability_<model>.json`
- Per-task outputs in `results/capability/<model>/<task-name>-out.*`

## Key Differences from Phase 1

- Phase 1: Binary pass/fail (did the tool call work?)
- Phase 2: Quality scoring (how good was the output?)
- Phase 2 tasks all require Hermes tool calls (no pure-text responses accepted)
- Phase 2 includes Chinese-specific and long-context dimensions absent from Phase 1
