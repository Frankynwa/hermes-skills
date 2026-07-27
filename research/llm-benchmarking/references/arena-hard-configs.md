# Arena-Hard-Auto Config Templates

## API Config (config/api_config_4models.yaml)

```yaml
# DeepSeek V4 Pro
deepseek-v4-pro:
  model: deepseek-v4-pro
  endpoints:
    - api_base: https://api.deepseek.com
      api_key: ${DEEPSEEK_API_KEY}
  api_type: openai
  parallel: 32
  max_tokens: 4096
  temperature: 0.0

# Qwen3.8 Max
qwen3.8-max:
  model: qwen3.8-max-preview
  endpoints:
    - api_base: https://dashscope.aliyuncs.com/compatible-mode/v1
      api_key: ${DASHSCOPE_API_KEY}
  api_type: openai
  parallel: 32
  max_tokens: 4096
  temperature: 0.0

# MiniMax M3
minimax-m3:
  model: MiniMax-M3
  endpoints:
    - api_base: https://api.minimax.io/v1
      api_key: ${MINIMAX_API_KEY}
  api_type: openai
  parallel: 32
  max_tokens: 4096
  temperature: 0.0

# Kimi K3
kimi-k3:
  model: kimi-k3
  endpoints:
    - api_base: https://api.moonshot.cn/v1
      api_key: ${MOONSHOT_API_KEY}
  api_type: openai
  parallel: 32
  max_tokens: 4096
  temperature: 0.0  # Kimi locks this to 1.0; set here but API ignores it

# Judge model (GPT-4.1 via OpenAI)
gpt-4.1:
  model: gpt-4.1
  endpoints:
    - api_base: https://api.openai.com/v1
      api_key: ${OPENAI_API_KEY}
  api_type: openai
  parallel: 32
  max_tokens: 4096
  temperature: 0.0
```

## Answer Generation Config (config/gen_answer_4models.yaml)

```yaml
benchmark_name: arena-hard-v2.0
model_name:
  - deepseek-v4-pro
  - qwen3.8-max
  - minimax-m3
  - kimi-k3
```

## Judge Config (config/judge_4models.yaml)

```yaml
benchmark_name: arena-hard-v2.0
judge_model: gpt-4.1
baseline_model: o3-mini-2025-01-31
mode: pairwise
```

## Setup Script (setup_configs.sh)

```bash
#!/bin/bash
# Resolve env var placeholders in API config
set -euo pipefail

REQUIRED_VARS=(DEEPSEEK_API_KEY DASHSCOPE_API_KEY MINIMAX_API_KEY MOONSHOT_API_KEY OPENAI_API_KEY)
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done

envsubst < config/api_config_4models.yaml > config/api_config_4models_resolved.yaml
echo "Config resolved to config/api_config_4models_resolved.yaml"
```
