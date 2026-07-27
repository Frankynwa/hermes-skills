# Community Frameworks Integration Guide

## Why Four Frameworks

The custom benchmark (31 tasks across 10 categories) gives thinking-mode-aware, head-to-head comparisons but lacks the breadth of community benchmarks (thousands of standardized questions, pre-built scoring, public rankings).

| Dimension | Custom Benchmark | Community Frameworks |
|---|---|---|
| Chinese knowledge | None | OpenCompass: C-Eval + CMMLU (25K+ MC) |
| Academic benchmarks | None | lm-eval: MMLU, GSM8K, HumanEval, BBH, ARC |
| Conversation quality | 4 LLM-judged Chinese tasks | Arena-Hard: 500 prompts, GPT-4.1 pairwise |
| Tool calling | 5 BFCL-style AST tasks | BFCL: full taxonomy, AST 3-stage verification |

## Framework Details

### 1. OpenCompass

- **Install**: Python 3.13 ships numpy ≥2.1 but OpenCompass requires numpy <2.0, and numpy 1.x has no prebuilt wheels for Python 3.13 (must build from source — 15.8MB tarball, slow on unreliable networks). **Proven workaround**: `pip download --no-deps opencompass -d /tmp/oc`, then `pip install --no-deps /tmp/oc/opencompass-*.whl`, then install deps: `pip install accelerate datasets evaluate mmengine-lite opencv-python-headless jsonlines fuzzywuzzy immutabledict func_timeout einops absl-py`. OpenCompass works fine with numpy 2.x at runtime — the constraint is only in metadata.
- **Model config**: OpenAISDK type, `openai_api_base` + `key.env` pattern
- **Key datasets**: `ceval_gen` (13,948 MC, 52 subjects), `cmmlu_gen` (11,528 MC, 67 topics), `gsm8k_gen`, `mmlu_gen`, `bbh_gen`
- **CLI**: `python -m opencompass.cli.main --models deepseek-v4-pro --datasets ceval_gen,cmmlu_gen,gsm8k_gen`

### 2. lm-eval-harness

- **Install**: `pip install "lm-eval[api]"` — lightweight, clean install
- **Model config**: `local-chat-completions` model type with `base_url` pointing to `/chat/completions` endpoint
- **Key tasks**: `mmlu`, `gsm8k`, `bbh`, `arc_challenge`, `hellaswag`, `humaneval`, `mbpp`, `ceval`, `cmmlu`
- **CLI**: `lm_eval --model local-chat-completions --model_args model=deepseek-v4-pro,base_url=https://api.deepseek.com/v1/chat/completions --tasks mmlu,gsm8k`
- **Output**: `--output_path ./outputs/lm_eval --log_samples` for per-question results

### 3. Arena-Hard-Auto

- **Install**: `git clone https://github.com/lm-sys/arena-hard-auto.git` — NOT pip-installable (no pyproject.toml/setup.py at root)
- **Judge**: Requires OPENAI_API_KEY for GPT-4.1 judge (separate from benchmarked model keys)
- **Scripts**: Two-phase workflow — `gen_answer.py` generates model responses, `gen_judgment.py` runs GPT-4.1 pairwise judging
- **Run answer generation**: `python arena-hard-auto/gen_answer.py --model deepseek-v4-pro --api-base https://api.deepseek.com/v1 --api-key $DEEPSEEK_API_KEY --answer-dir ./data/model_answer --num-choices 1`
- **Run judgment**: `python arena-hard-auto/gen_judgment.py --model-list deepseek-v4-pro --answer-dir ./data`
- **Fast mode**: Not directly supported; reduce question count via `gen_answer.py --num-questions 100` if available
- **Output**: Win rate from judgment phase, stored in leaderboard JSON

### 4. BFCL (Berkeley Function Calling Leaderboard)

- **Install**: Clone with `git clone --depth 1 https://github.com/ShishirPatil/gorilla.git frameworks/bfcl`. BFCL has numpy==1.26.4 constraint same as OpenCompass — use same workaround: `pip install --no-deps -e frameworks/bfcl/berkeley-function-call-leaderboard/`, then install deps manually: `pip install requests tqdm pydantic python-dotenv tree_sitter tree-sitter-java tree-sitter-javascript mistralai anthropic cohere typer tabulate tenacity overrides`.
- **Heavy deps**: mistralai, anthropic, google-genai, cohere — install individually to handle failures gracefully
- **Categories**: `all` or individual: single/multiple/parallel/irrelevance/live/sql/java/js
- **Run**: `python openfunctions_evaluation.py --model deepseek-v4-pro`
- **Scoring**: AST-based 3-stage: JSON parse → schema validation (correct function, required params) → value correctness
- **Pitfall**: Requires registering custom model handler in `bfcl_eval/handler.py` with correct api_base, model_id, and auth header. Run `--dry-run` mode first to verify handler registration.

## China Network Workarounds

| Problem | Solution |
|---|---|
| macOS system proxy (Clash/verge-mih on 7897) not picked up by pip/conda | Set explicit env vars: `export HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897`. Check SOCKS too: `networksetup -setsocksfirewallproxystate Wi-Fi off` if enabled. |
| Conda proxy error ("Tunnel connection failed: 404") | Same — explicit HTTPS_PROXY env var. System proxy settings are NOT inherited by conda. |
| PyPI numpy source build hangs (15.8MB tarball) | Skip entirely via `--no-deps` workaround (see OpenCompass install notes). |
| GitHub git clone RPC failure / early EOF | Use `--depth 1` for smaller transfer. Retry if transient. |
| Qwen3.8 Max 403 access_denied | Token Plan subscription required — separate from DashScope API key. Attend to Qwen3.7 Max as fallback.

## Unified Runner (scripts/run_benchmarks.py)

Located at `~/projects/hermes-model-bench/scripts/run_benchmarks.py`. Usage:

```bash
# Check API key status and connectivity
python scripts/run_benchmarks.py --status

# Dry run — print commands without executing
python scripts/run_benchmarks.py --dry-run

# Run specific framework + models
python scripts/run_benchmarks.py --framework lm_eval --models deepseek,qwen37

# Run all four frameworks
python scripts/run_benchmarks.py --framework all --models deepseek,qwen37

# Run with specific tasks
python scripts/run_benchmarks.py -f lm_eval -m deepseek -t gsm8k,mmlu
```

Parameters:
- `--framework / -f`: opencompass, lm_eval, arena-hard, bfcl, or all
- `--models / -m`: comma-separated keys (deepseek, qwen37, qwen38, minimax, kimi)
- `--tasks / -t`: comma-separated task IDs (defaults to framework defaults)
- `--status / -s`: show API key status + connectivity test, then exit
- `--dry-run / -d`: print commands without running
- `--output / -o`: output directory (default: results/frameworks/)

Results go to `results/frameworks/<framework>/<timestamp>/results.json`.

## API Key Requirements

| Framework | Keys Needed |
|---|---|
| All | Model-specific: DEEPSEEK_API_KEY, DASHSCOPE_API_KEY, MINIMAX_API_KEY, MOONSHOT_API_KEY |
| Arena-Hard | + OPENAI_API_KEY (GPT-4.1 judge) |

Keys stored in `~/.hermes/.env`. Current status (2026-07-21 connectivity test):
- DEEPSEEK_API_KEY: ✅ working (V4 Pro responds, but needs ≥500 max_tokens — V4 Pro always produces reasoning tokens)
- DASHSCOPE_API_KEY: ✅ working for Qwen3.7 Max; ❌ Qwen3.8 Max returns 403 ("access_denied" — Token Plan subscription required, not included in standard DashScope key)
- MINIMAX_API_KEY: missing
- MOONSHOT_API_KEY: missing
- OPENAI_API_KEY: missing (needed for Arena-Hard GPT-4.1 judge)

**Loading keys for subprocesses**: Do NOT use `source ~/.hermes/.env` — it breaks on lines with spaces in values. Instead:
```bash
export $(grep -E '^(DEEPSEEK|DASHSCOPE|MINIMAX|MOONSHOT|OPENAI)_API_KEY=' ~/.hermes/.env | xargs)
```

## Run Order

1. lm-eval (fastest, most reliable) — verify models respond, get baseline numbers
2. OpenCompass (Chinese benchmarks) — adds Chinese-specific coverage
3. BFCL (tool calling) — verify agent capabilities
4. Arena-Hard (conversation quality) — last because it needs the judge key and network for git clone
5. Custom benchmark — thinking-mode-aware, controlled head-to-head
