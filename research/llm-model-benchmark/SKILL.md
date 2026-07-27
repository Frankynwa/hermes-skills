---
name: llm-model-benchmark
description: "Systematic evaluation and comparison of LLM performance — benchmark design, three-tier scoring, model config management, anti-contamination."
version: 1.2.0
category: research
tags: [benchmark, evaluation, llm, scoring, model-comparison, community-frameworks]
related_skills: [multi-model-strategies, ai-technique-evaluation, smart-model-switch]
---

# LLM Model Benchmarking

When designing, running, or improving a systematic evaluation of multiple LLMs — standardized task suites, objective scoring, LLM-as-judge comparisons, anti-contamination measures.

## When This Skill Activates

- User wants to benchmark/compare LLMs systematically
- User has a benchmark project and wants to upgrade scoring methodology
- User asks "which model is best for X?" and needs structured evaluation
- User wants to design tasks with verifiable ground truth

## Core Methodology: Three-Tier Scoring

### Tier 1: Objective (no LLM judge)
Verifiable answers with ground truth. Zero judge bias.

- **Code execution**: Extract code block → run with subprocess → check stdout/assertions. Template: prepend test cases to extracted code, run `python3 -c`, check for `ALL_TESTS_PASSED`.
- **Math**: Exact match or numeric tolerance (±0.01). Ground truth pre-computed and stored in task file.
- **Extraction**: JSON schema validation + field-level exact matching against reference.
- **Classification**: Exact match on expected labels.
- **Instruction following**: Constraint checking — word count, format compliance, keyword presence/absence detection.
- **Tool calling** (BFCL-style AST): JSON parse → validate schema (correct function name, required params present) → value correctness (arguments match expected types and values). For chained calls, verify both step 1 and step 2 are present. For error recovery tasks, verify the model asks for missing params rather than hallucinating defaults.

### Tier 2: LLM-as-Judge (subjective/creative)
For tasks without ground truth: writing, summarization, translation, creative text.

- **Double-pass pairwise with position swap** (MT-Bench pattern): swap model A and B positions, require agreement.
- Structured output: `[[A]]`, `[[B]]`, `[[C]]` (tie).
- Judge prompt: "impartial judge", criteria = helpfulness, relevance, accuracy, depth, creativity, detail.
- Anti-bias: "Avoid position biases", "Do not allow length to influence".
- **Length control**: Note in judge prompt; optionally apply LC regression (AlpacaEval approach).
- **Judge model**: Use a different model family to avoid self-enhancement bias.
- **Tie threshold**: Δ < 0.1 on 1-10 scale = tie.
- Flag and report inconsistent double-pass results.

### Tier 3: Human Spot-Check
Random 10% of LLM-judged results reviewed by human. Calibrates judge reliability.

## Community Frameworks (Complementary, Not Replacement)

The custom benchmark pipeline above is essential for controlled, thinking-mode-aware comparisons. But it's not enough alone — the task coverage is inherently limited (31 prompts vs. thousands in community benchmarks). Pair with these four frameworks for a complete model profile:

| Framework | What It Measures | Custom Benchmark Can't Do This |
|---|---|---|
| **OpenCompass** | Chinese knowledge: C-Eval (13.9K MC), CMMLU (11.5K), GAOKAO-Bench | Thousands of standardized Chinese questions |
| **lm-eval-harness** | Academic benchmarks: MMLU, GSM8K, HumanEval, HellaSwag, ARC, BBH | 60+ standardized datasets with exact-match scoring |
| **Arena-Hard-Auto** | Open-ended conversation quality — 500 hardest Arena prompts, GPT-4.1 pairwise judge | Conversation quality at scale with position-swap judging |
| **BFCL** | Tool/function calling — AST-based 3-stage verification (parse→schema→value), 5 call patterns | Standardized tool-calling taxonomy accepted by industry |

**Coverage gap**: No single framework covers all dimensions. Use all four for a complete model profile. The custom benchmark handles thinking-mode-aware head-to-head comparisons; community frameworks provide standardized, reproducible rankings.

### Installation Notes (China Network + Proxy)

**Proxy setup**: macOS system proxy (Clash/verge-mih on 127.0.0.1:7897) is NOT picked up by pip automatically. Must set env vars explicitly: `export HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897`. Also check `scutil --proxy` — SOCKS proxy may still be enabled even when HTTP proxies are off. Disable with `networksetup -setsocksfirewallproxystate Wi-Fi off`.

**Per-framework install**:

- **lm-eval**: `pip install "lm-eval[api]"` — installs cleanly, no Python 3.13 issues.
- **OpenCompass**: Python 3.13 has numpy ≥2.1 but OpenCompass requires numpy <2.0, and numpy 1.x has no prebuilt wheels for Python 3.13 (must build from source — 15.8MB tarball, slow on unreliable networks). **Proven workaround**: `pip download --no-deps opencompass -d /tmp/oc`, then `pip install --no-deps /tmp/oc/opencompass-*.whl`, then `pip install accelerate datasets evaluate mmengine-lite opencv-python-headless jsonlines fuzzywuzzy immutabledict func_timeout einops absl-py`. This skips the numpy<2 constraint entirely — opencompass works fine with numpy 2.x at runtime despite the metadata pin.
- **BFCL**: Same numpy==1.26.4 constraint. Use same workaround: `pip install --no-deps -e berkeley-function-call-leaderboard/` then install deps manually. Key deps: `requests tqdm pydantic python-dotenv tree_sitter tree-sitter-java tree-sitter-javascript mistralai anthropic cohere typer tabulate tenacity overrides`.
- **Arena-Hard-Auto**: NOT pip-installable (no pyproject.toml/setup.py). `git clone --depth 1 https://github.com/lm-sys/arena-hard-auto.git`. Install deps: `pip install -r requirements.txt`. Note: RPC failures during clone are transient network issues — retry with `--depth 1` (smaller transfer).

### Framework Config Files

Store per-framework model configs in `frameworks/`:
- `frameworks/opencompass_config.py` — OpenAISDK model dicts with api_base, api_key env references, rate limits
- `frameworks/lm_eval_config.py` — model args (base_url, num_concurrent, extra_body for thinking)
- `frameworks/arena_hard_config.py` — api_base + judge config (needs OPENAI_API_KEY for GPT-4.1)
- `frameworks/bfcl_config.py` — api_base + temperature (0.001 for deterministic tool calling, except Kimi locked at 1.0)

Unified runner: `run_all.py` — dry-run mode first to verify configs, then `--fast` mode for initial pass.

**Pitfall**: Arena-Hard needs its own OPENAI_API_KEY (for GPT-4.1 judge), separate from model API keys. Don't run Arena-Hard without first verifying the judge key works.

## Task Taxonomy

Design tasks across these categories for comprehensive coverage:

| Category | Sub-Tasks | Scoring | Source |
|----------|-----------|---------|--------|
| Coding | Generation, debugging, refactoring, SQL | Tier 1 (execution) | SWE-bench, HumanEval+ |
| Reasoning | Multi-step math, logic deduction, planning | Tier 1 (ground truth) | GPQA, BBH |
| Instruction Following | Format constraints, multi-constraint, length | Tier 1 (constraint check) | IFEval |
| Mathematics | Probability, calculus, linear algebra | Tier 1 (exact match) | MATH, GSM8K |
| Extraction | Resume parsing, NER, classification | Tier 1 (schema validation) | MT-Bench |
| Chinese | Rewrite, idioms, ambiguity, translation | Tier 2 (LLM judge) | C-Eval, CMMLU |
| Agentic | Data pipeline, code review, research→report | Tier 1 (file/existence check) | GAIA, BFCL V4 |
| Knowledge | STEM MC, history, culture | Tier 1 (exact match) | LiveBench |
| Creative | Writing, summarization | Tier 2 (LLM judge) | MT-Bench |
| Tool Calling | Simple, multi-select, parallel, chained, error recovery | Tier 1 (AST: parse→schema→value) | BFCL |
| Multi-turn Memory | Cross-turn reference tracking | Tier 1 (state check) | MT-Bench |

## Model Config Best Practices

### Required Fields Per Model
```yaml
model-key:
  label: "Human-readable name"
  provider: provider_name
  api_base: https://api.provider.com          # NO trailing /v1 unless provider requires it
  model_id: exact-api-model-id
  context_window: 1000000
  max_output_tokens: 131072
  capabilities: {vision, thinking, tool_calling, structured_output, streaming, system_prompt}
  thinking: {param, budget_param, budget_default}  # if supported
  recommended_params: {coding, reasoning, creative}
  notes: "..."
```

### Critical API Quirks (2026-07 status)

**DeepSeek V4 Pro:**
- api_base: `https://api.deepseek.com` (NO `/v1`)
- Thinking: `reasoning_effort` via extra_body, values: low/medium/high/max
- **CRITICAL**: V4 Pro ALWAYS produces reasoning tokens, even without explicitly setting reasoning_effort. With small max_tokens (≤50), reasoning tokens consume the entire output budget leaving `content: ""`. Always use ≥500 max_tokens for V4 Pro to leave room for both reasoning and content. The content is in `decision.reasoning_content`, not `decision.content` at low budgets.
- When thinking enabled, temperature/top_p are IGNORED by API — don't set them
- deepseek-chat/deepseek-reasoner deprecated 2026/7/24

**Qwen3.8 Max:**
- Token Plan subscription only — regular DashScope key gets 403
- model_id: `qwen3.8-max-preview` (may change on GA)
- Thinking: `enable_thinking` + `thinking_budget` (1024-8192) via extra_body
- JSON mode may not be strict when thinking enabled

**MiniMax M3:**
- 428B MoE, 22B active
- context_window: 1M (not 512K as some docs state)
- Thinking: `thinking: {type: "adaptive"}` via extra_body
- **Thinking defaults OFF** — must explicitly enable; without it, model runs in standard mode
- Dual API: OpenAI + Anthropic compatible

**Kimi K3:**
- api_base: `https://api.moonshot.cn/v1` (NOT api.moonshot.ai)
- Thinking: `reasoning_effort` as TOP-LEVEL param (not extra_body!) — **critical difference** from all other providers
- **temperature LOCKED at 1.0**, **top_p LOCKED at 0.95** — setting them causes API errors
- **Never set temperature/top_p for Kimi** — leave recommended_params empty
- Chinese-first, 1M context, vision-capable

## Anti-Contamination Measures


## Tier 2 Judge Prompt Types (MT-Bench Pattern)

Use task-type-specific judge prompts — not one generic prompt for all tasks:

| Prompt Type | Trigger | Focus |
|---|---|---|
| `math` | Tasks starting with `math/` | Correctness, step-by-step clarity, proper notation |
| `coding` | Tasks starting with `coding/` | Does code compile? Edge cases? Optimal algorithm? Clean? |
| `creative` | Tasks starting with `creative/` | Creativity, voice, originality, engagement. Do NOT favor length. |
| `chinese` | Tasks starting with `chinese/` or `zhongwen` | Grammar, naturalness, rhetoric. 简洁优先于冗长. |
| `default` | Everything else | Generic: helpfulness, relevance, accuracy, depth |

## Length Control Formula (AlpacaEval 2.0)

```
ratio = len(answer_a) / max(len(answer_b), 1)
if ratio > 1:   penalty = min(0.4, (ratio - 1) * 0.15)  # A is longer
if ratio < 1:   bonus  = min(0.4, (1 - ratio) * 0.3)    # A is shorter
```

Apply: if length_bonus > 0.2 and shorter answer "lost", adjust to tie. Prevents verbose-but-vapid from winning.

## Anti-Contamination Measures

1. **Task rotation**: Replace 20-30% of prompts monthly
2. **Temporal freshness**: Include 5+ tasks based on recent events/arXiv papers
3. **SHA256 hashing**: Publish hashes before evaluation runs
4. **Joint evaluation window**: All models tested in same time period
5. **Private held-out set**: Alongside public tasks
6. **Detection heuristics**: Refusal patterns, identical outputs, length-only strategies

## Multi-Task File Pattern

For v2 tasks, use a single markdown file per category with `## Task XX:` sections. Extract with regex:
```python
def extract_section(content, marker):
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("## ") and marker in line:
            start = i; break
    # Collect until next ## or EOF
```
Store section markers in a lookup dict mapping task_key → marker string.

## Pitfalls

- **Don't delegate API research to subagents.** Subagent summaries are too shallow — missing parameter formats, locked values, and deprecation warnings. Do the actual web scraping and doc reading yourself. The 4 models studied here (DeepSeek, Qwen, MiniMax, Kimi) all have different thinking parameter mechanisms; a subagent summary would flatten these into "they all support thinking."
- **Loading .env for subprocess scripts**: `source ~/.hermes/.env` breaks on lines containing spaces (e.g. `OBSIDIAN_VAULT_PATH="/Users/.../Obsidian Vault/"` → "bash: Vault: command not found"). Use `export $(grep -E '^(DEEPSEEK|DASHSCOPE|MINIMAX|MOONSHOT|OPENAI)_API_KEY=' ~/.hermes/.env | xargs)` to extract only API key assignments. The runner script reads from os.environ, so prepend this to any benchmark command.
- **Config mismatches are common**: api_base trailing /v1, wrong context_window, wrong api domain (.ai vs .cn). Always verify against official docs, not third-party aggregators.
- **Thinking params differ per provider**: Some use extra_body, some use top-level params. Getting this wrong = thinking silently disabled.
- **Temperature + thinking conflict**: DeepSeek ignores temp when thinking is on. Don't set both.
- **DeepSeek V4 Pro reasoning budget**: The model ALWAYS produces reasoning tokens (even without explicit reasoning_effort). With small max_tokens (≤50), reasoning consumes the entire budget and content is empty. Always use ≥500 max_tokens. In benchmarks where frameworks hardcode low max_tokens (like Arena-Hard-Auto's default 1024), this is usually fine — but test with a simple prompt first to confirm the model responds with actual content, not empty strings.
- **JSON mode + thinking**: Qwen may not produce strict JSON in thinking mode.
- **JSON mode + thinking**: Qwen may not produce strict JSON in thinking mode.
- **Length bias**: The #1 confound in LLM judging. Always control for it.
- **Position bias**: Swapping model order in pairwise and requiring agreement is mandatory, not optional.
- **Pattern-matching scoring is fragile**: `re.search(r'88[0-3]', stdout)` can false-positive on unrelated text. Prefer execution-based verification.
- **Token Plan models**: Some models (Qwen3.8 Max) require special subscription — test API access before scheduling benchmark runs.
- **China network for pip/git**: PyPI direct downloads often fail with SSL EOF errors. Use Aliyun mirror for pip. GitHub is frequently unreachable for git clone — for pip-installable repos (like BFCL via gorilla) this works because pip uses URLs differently; for manual git clone, try ghproxy or browser download. Arena-Hard-Auto is the only framework that MUST be git cloned manually and CANNOT be pip-installed.
- **Community frameworks ≠ custom benchmark**: They serve different purposes. Community = standardized ranking (thousands of questions, pre-built scoring). Custom = thinking-mode-aware head-to-head (controlled prompts, per-model parameter tuning). Don't pick one — run both.
- **OpenAI key requirement**: Arena-Hard-Auto's GPT-4.1 judge needs OPENAI_API_KEY. This is separate from the benchmarked model's API keys.
- **Arena-Hard-Auto is a script repo, not a pip package**: No pyproject.toml/setup.py. Just clone and run `gen_answer.py` (model response generation) then `gen_judgment.py` (GPT-4.1 pairwise judging). The existing `~/projects/hermes-model-bench/arena-hard-auto/` checkout is ready to use.

## Reference Files

- `references/benchmark-landscape.md` — Condensed research from LMSys Arena, MT-Bench, AlpacaEval, LiveBench, SWE-bench, BFCL, GAIA, Chinese benchmarks. Scoring best practices and anti-cheating measures.
- `references/model-thinking-params.md` — Per-model thinking parameter reference with code examples, default states, and testing checklist. Covers DeepSeek, Qwen, MiniMax, Kimi.

## Implementation Reference

The user's benchmark project lives at `~/projects/hermes-model-bench/` with:
- `config/models.yaml` — 5-model config with corrected API endpoints, thinking_params per model, Kimi locked t/p
- `scripts/run_bench.py` — v3 runner: direct API calls for thinking mode (per-model extra_body/top-level), hermes CLI fallback for agentic tasks. MODEL dict is the runtime source of truth.
- `scripts/evaluate.py` — v3 evaluator: 27 Tier 1 scorers (coding, reasoning, instruction, math, extraction, knowledge, agentic, tool-calling) + 4 task-type-specific judge prompts + length control formula
- `tasks/v2/` — 31 tasks across 10 categories (coding, reasoning, chinese, instruction, math, extraction, agentic, knowledge, tool-calling, creative)
- `config/frameworks.py` — Unified framework config generator (generates OpenCompass model configs, prints lm-eval/Arena-Hard/BFCL commands, runs connectivity tests). Loads API keys from `~/.hermes/.env` + project `.env`.
- `scripts/run_benchmarks.py` — Unified runner for all four community frameworks. Dry-run mode prints exact commands. Status mode tests API connectivity. Runs frameworks in sequence with per-model result tracking. Output: `results/frameworks/<fw>/<timestamp>/results.json`.
- `.env.template` — API key template with comments explaining where to obtain each key and known limitations (Qwen3.8 Max Token Plan, etc.)
- **Consistency rule**: Every V2_TASKS entry needs matching V2_SECTIONS + TIER1_SCORERS entries. Run the Python consistency check after any addition.
