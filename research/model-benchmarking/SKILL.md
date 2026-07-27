---
name: model-benchmarking
description: Run systematic model evaluations using community benchmarks — lm-eval-harness, OpenCompass, Arena-Hard-Auto, BFCL — plus local custom tasks. Use when benchmarking, comparing, or evaluating LLM API endpoints.
---

# Model Benchmarking

Integrate four industry-standard benchmark frameworks with API-based models (DeepSeek, Qwen, MiniMax, Kimi) and local custom tasks in a single project.

## Project Structure

The canonical project is at `~/projects/hermes-model-bench/`. Do NOT recreate — clone/extend it.

```
hermes-model-bench/
├── unified_runner.py         # Primary runner: --all, --framework, --model, --dry-run, --list
├── scripts/run_benchmarks.py # Alt runner with --status and --dry-run
├── run.py                    # Simpler runner
├── config/
│   ├── frameworks.py         # Model defs + API keys from ~/.hermes/.env
│   └── models.yaml           # Older config
├── frameworks/
│   ├── opencompass-configs/  # One .py per model, uses os.environ.get()
│   ├── arena-hard-auto/      # Arena-Hard configs + scripts
│   └── bfcl/                 # BFCL eval engine
└── results/                  # Output directory
```

## Four Frameworks — What Each Covers

| Framework | What It Tests | Key Limitation |
|---|---|---|
| lm-eval-harness | Academic: GSM8K, MMLU, HellaSwag, ARC, TruthfulQA | Objective questions only; no Chinese benchmarks |
| OpenCompass | Chinese: C-Eval, CMMLU, GAOKAO-Bench | Heavy deps (torch, transformers) |
| Arena-Hard-Auto | Conversation quality (500 hard prompts, GPT-4.1 judge) | Needs OPENAI_API_KEY for judge; English only |
| BFCL | Function calling (AST-based verification) | Requires manual handler registration |

## Your Local Project's Unique Contributions (Not Covered by Frameworks)

- Chinese creative writing (brand stories, copywriting, zhihu answers)
- Chinese cultural understanding (poetry, idioms, humor)
- Long-document comprehension (10k+ token context)
- Multi-turn memory (info given in turn 1, queried in turn 3)
- Instruction following (6+ constraints in one prompt)
- Thinking mode A/B comparison (same task, thinking on/off)

## Usage

```bash
# List available
python unified_runner.py --list

# Dry-run (see commands without executing)
python unified_runner.py --all --dry-run
python scripts/run_benchmarks.py --dry-run

# Run single framework + single model
python unified_runner.py --framework lm_eval --model deepseek-v4-pro

# Run single task
python unified_runner.py --framework lm_eval --model deepseek-v4-pro --task gsm8k
```

## OpenCompass Config Pitfall

OpenCompass config files in `frameworks/opencompass-configs/` MUST use `os.environ.get("API_KEY_ENV_VAR", "")`, NOT hardcoded keys (even masked ones). Hardcoded keys silently fail at runtime.

## Python 3.13 Compatibility

`opencompass` may fail with `ModuleNotFoundError: pkg_resources`. Fix:
```bash
pip install setuptools  # pkg_resources was removed from Python 3.13 stdlib
```

## Environment Variables Required

Set in `~/.hermes/.env`:
- `DEEPSEEK_API_KEY`
- `DASHSCOPE_API_KEY` (covers all Qwen models)
- `MINIMAX_API_KEY` (optional)
- `MOONSHOT_API_KEY` (optional, for Kimi K3)
- `OPENAI_API_KEY` (required ONLY for Arena-Hard GPT-4.1 judge)

## Model API IDs

| Model Key | API Model ID | Base URL |
|---|---|---|
| deepseek-v4-pro | deepseek-v4-pro | https://api.deepseek.com |
| qwen3.8-max | qwen3.8-max-preview | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| qwen3.7-max | qwen3.7-max | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| minimax-m3 | MiniMax-M3 | https://api.minimax.io/v1 |
| kimi-k3 | kimi-k3 | https://api.moonshot.cn/v1 |
