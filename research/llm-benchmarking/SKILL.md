---
name: llm-benchmarking
description: Multi-framework LLM evaluation pipeline — install, configure, and run Arena-Hard-Auto, BFCL, lm-eval-harness for API-based models (DeepSeek, Qwen, MiniMax, Kimi). Use when setting up model benchmarks, evaluating new models, or comparing model quality.
---

# LLM Benchmarking Pipeline

Four-framework evaluation for API-based models. Each covers a distinct dimension; run all four for a complete model profile.

## Framework Coverage Matrix

| Framework | Measures | Scoring |
|---|---|---|
| lm-eval-harness | Academic benchmarks (MMLU, GSM8K, C-Eval) | Exact match / generative |
| Arena-Hard-Auto | Open-ended conversation quality | GPT-4.1 pairwise judge |
| BFCL | Function/tool calling accuracy | AST 3-stage verification |
| OpenCompass | Chinese benchmarks (C-Eval, CMMLU) | Multiple choice exact match |

## Pre-install Check

```bash
# Confirm conda base Python and pip
/opt/anaconda3/bin/python3 -c "import lm_eval; print(lm_eval.__version__)"
# Arena-Hard should be cloned at ~/projects/hermes-model-bench/frameworks/arena-hard-auto/
# BFCL should be cloned via gorilla repo
```

## 1. lm-eval-harness

```bash
pip install lm-eval[api]
```

### Critical Gotchas

1. **MUST use `openai-chat-completions` model type**, not `local-chat-completions`. The latter doesn't support `loglikelihood`, which is required for multiple-choice Chinese tasks (cmmlu, ceval).

2. **OPENAI_API_KEY env var is the ONLY way** to pass API keys. `api_key` in model_args is silently ignored by `openai-chat-completions`. Set `OPENAI_API_KEY` to the specific provider's key before each run.

3. **`--apply_chat_template` is ALWAYS required** for chat models. Without it, requests arrive as plain strings and fail assertion.

4. **`loglikelihood` is NOT supported by any chat-completions model type** (OpenAI doesn't provide prompt logprobs). This means multiple-choice tasks (cmmlu, ceval, mmlu) won't work with API-based models. Use `_generative` variants (e.g., `mmlu_anatomy_generative`, `gsm8k`) instead.

### Recommended Tasks

Generative-only (works with `openai-chat-completions`):
- `gsm8k` — grade-school math
- `mmlu_anatomy_generative` — MMLU generative variants
- `hellaswag_gen` — commonsense reasoning

Chinese tasks (multiple-choice, requires loglikelihood → NOT supported):
- `cmmlu`, `ceval-valid` — use OpenCompass instead

```bash
# Run command template
export OPENAI_API_KEY=$PROVIDER_API_KEY
/opt/anaconda3/bin/lm_eval \
  --model openai-chat-completions \
  --model_args "model=MODEL_ID,base_url=BASE_URL/v1/chat/completions" \
  --tasks gsm8k,mmlu_anatomy_generative \
  --limit 100 --batch_size 8 \
  --apply_chat_template
```

## 2. Arena-Hard-Auto

Path: `~/projects/hermes-model-bench/frameworks/arena-hard-auto/`

### Setup

```bash
git clone https://github.com/lm-sys/arena-hard-auto.git
cd arena-hard-auto
pip install -r requirements.txt
```

### Judge Cost

GPT-4.1 is required as judge. 750 questions × 4 models × 2 rounds (position swap) ≈ 6,000 pairwise judgments. Estimated $50-80 in OpenAI API costs.

### Model Config

Any OpenAI-compatible API works via the `openai` api_type. Create YAML configs for `gen_answer` and `gen_judgment` steps. See `references/arena-hard-configs.md` for templates.

### Run Pipeline

```bash
# 1. Resolve config
envsubst < config/api_config.yaml > config/api_config_resolved.yaml

# 2. Generate answers
python gen_answer.py --config-file config/gen_answer.yaml --endpoint-file config/api_config_resolved.yaml

# 3. Add markdown metadata
python utils/add_markdown_info.py --dir data/arena-hard-v2.0/model_answer --output-dir data/arena-hard-v2.0/model_answer

# 4. Generate judgments
python gen_judgment.py --setting-file config/judge.yaml --endpoint-file config/api_config_resolved.yaml

# 5. Show leaderboard
python show_result.py --benchmark arena-hard-v2.0 --judge-names gpt-4.1 --category hard_prompt
```

## 3. BFCL (Berkeley Function Calling Leaderboard)

### Installation

BFCL lives in the `ShishirPatil/gorilla` monorepo, NOT a standalone `berkeley-nest/BFCL` repo (that returns 404).

```bash
git clone --depth 1 https://github.com/ShishirPatil/gorilla.git
cd gorilla
# Install from the berkeley-function-call-leaderboard subdirectory
pip install -e berkeley-function-call-leaderboard/
```

Set env var:
```bash
export BFCL_PROJECT_ROOT=/path/to/gorilla/berkeley-function-call-leaderboard
```

### CLI Commands

```bash
bfcl models                  # list available models
bfcl test-categories         # list test categories
bfcl generate --model MODEL --test-category CATEGORY
bfcl evaluate --model MODEL --test-category CATEGORY
bfcl scores                  # display leaderboard
```

## 4. OpenCompass

Heavy dependency (torch, transformers, 30+ GB). Skip unless running on GPU machine with dedicated env. For Chinese benchmarks (C-Eval, CMMLU), use OpenCompass on a GPU server; use Arena-Hard + lm-eval on local for everything else.

## Model API Reference

| Model | API Base | Model ID | Thinking Mode |
|---|---|---|---|
| DeepSeek V4 Pro | `api.deepseek.com` | `deepseek-v4-pro` | Default ON, strips temperature/top_p silently |
| Qwen3.8 Max | `dashscope.aliyuncs.com/compatible-mode/v1` | `qwen3.8-max-preview` | `enable_thinking` + `thinking_budget` |
| MiniMax M3 | `api.minimax.io/v1` | `MiniMax-M3` | `thinking: {type: "adaptive"}` (Anthropic API style) |
| Kimi K3 | `api.moonshot.cn` | `kimi-k3` | Always ON, temperature locked to 1.0, top_p to 0.95 |

## Pitfalls

- lm-eval `local-chat-completions`: auth_token in model_args is ignored; only OPENAI_API_KEY env var works
- BFCL: the `berkeley-nest/BFCL` GitHub repo does NOT exist — clone `ShishirPatil/gorilla` and use sparse checkout
- Arena-Hard: answer generation caches by default; if model output changes, clear the cache directory
- DeepSeek thinking mode: setting temperature/top_p silently has no effect — no error thrown, just ignored
- Kimi K3: do NOT set temperature or top_p in API calls — they're locked and will cause errors
- Qwen3.8 Max: requires DashScope Token Plan subscription; if unavailable, fall back to qwen3.7-max
- All four: `loglikelihood` (multiple-choice scoring) is NOT available via chat-completions API — use generative task variants only