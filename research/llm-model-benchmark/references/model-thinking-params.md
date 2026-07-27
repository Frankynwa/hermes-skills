# Model-Specific Thinking Parameter Reference (2026-07)

Each of the 4 Chinese LLMs implements thinking/reasoning differently.
Getting this wrong means thinking is silently disabled or causes API errors.

## DeepSeek V4 Pro
- **Parameter**: `reasoning_effort` (string)
- **Where**: `extra_body` in the API request
- **Values**: `low`, `medium`, `high`, `max`
- **t/p behavior**: When reasoning_effort is set, `temperature` and `top_p` are silently IGNORED by the API. Setting them does nothing — no error, just ignored.
- **Default**: reasoning_effort is default-on; model always reasons unless you explicitly disable
- **Endpoint**: `https://api.deepseek.com/chat/completions` (no /v1 suffix)
- **Model ID**: `deepseek-v4-pro`
- **Deprecation**: `deepseek-chat` and `deepseek-reasoner` deprecated 2026/7/24

```python
extra_body = {"reasoning_effort": "high"}
# DO NOT set temperature or top_p — they'll be ignored
payload = {
    "model": "deepseek-v4-pro",
    "messages": [...],
    "extra_body": extra_body,
    # no temperature, no top_p
}
```

## Qwen3.8 Max (Token Plan Exclusive)
- **Parameter**: `enable_thinking` (bool) + `thinking_budget` (int)
- **Where**: `extra_body`
- **Budget range**: 1024-8192 tokens
- **t/p behavior**: Normal — temperature/top_p work as expected
- **Default**: thinking is OFF by default; must explicitly enable
- **Access**: Requires Token Plan subscription. Standard DashScope keys get HTTP 403.
- **Model ID**: `qwen3.8-max-preview` (may change to `qwen3.8-max` on GA)
- **Pitfall**: JSON mode (`response_format: json_object`) may not produce strict JSON when thinking is enabled

```python
extra_body = {
    "enable_thinking": True,
    "thinking_budget": 4096,
}
payload = {
    "model": "qwen3.8-max-preview",
    "messages": [...],
    "temperature": 0.6,
    "extra_body": extra_body,
}
```

## MiniMax M3 (428B MoE, 22B active)
- **Parameter**: `thinking` (object, not string!)
- **Where**: `extra_body`
- **Format**: `{"thinking": {"type": "adaptive"}}` — nested object, not a simple value
- **Values**: `{"type": "adaptive"}` (the only documented option)
- **t/p behavior**: Normal
- **Default**: thinking is OFF — must explicitly enable. Model runs standard mode without it.
- **Context window**: 1,000,000 (some docs incorrectly state 512K)
- **Max output**: 131,072 (can go up to 524,288)
- **Dual API**: Supports both OpenAI and Anthropic API formats

```python
extra_body = {"thinking": {"type": "adaptive"}}  # note: nested object
payload = {
    "model": "MiniMax-M3",
    "messages": [...],
    "temperature": 0.3,
    "extra_body": extra_body,
}
```

## Kimi K3 (Moonshot)
- **Parameter**: `reasoning_effort` (string)
- **Where**: TOP-LEVEL request parameter — NOT in extra_body! **This is unique to Kimi.**
- **Values**: `low`, `medium`, `high`
- **t/p behavior**: `temperature` is LOCKED at 1.0, `top_p` is LOCKED at 0.95. Setting them causes API errors. **Never set them.**
- **Default**: reasoning is always on — Kimi always thinks
- **Endpoint**: `https://api.moonshot.cn/v1` (NOT `api.moonshot.ai`)
- **Model ID**: `kimi-k3`
- **Capabilities**: Vision (image + video), 1M context, Chinese-first

```python
payload = {
    "model": "kimi-k3",
    "messages": [...],
    "reasoning_effort": "high",  # TOP-LEVEL, not extra_body!
    # DO NOT set temperature or top_p — they're locked by API
}
```

## Comparison Matrix

| | DeepSeek V4 Pro | Qwen3.8 Max | MiniMax M3 | Kimi K3 |
|---|---|---|---|---|
| Param name | reasoning_effort | enable_thinking | thinking | reasoning_effort |
| Location | extra_body | extra_body | extra_body | TOP-LEVEL |
| Value type | string | bool + int | nested object | string |
| Default | ON | OFF | OFF | ON |
| t/p when thinking | IGNORED | normal | normal | LOCKED (error) |

## Testing Checklist

Before running a full benchmark:
1. Call each model with thinking enabled and verify the response includes reasoning tokens or thinking trace
2. For Kimi: confirm reasoning_effort is at request root level and no t/p is set
3. For MiniMax: confirm thinking is explicitly activated (otherwise it runs standard mode and you're benchmarking the wrong capability)
4. For DeepSeek: remove t/p from payload when thinking is on
5. For Qwen3.8: test API access first — if 403, fall back to qwen3.7-max
