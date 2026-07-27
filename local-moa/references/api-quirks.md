# 多模型 API 调用怪癖

2026-07-20 实测发现的关键问题。

## reasoning_tokens 吃掉输出预算

MiMo、Qwen、MiniMax 等推理模型在生成输出前先内部推理（thinking），这部分 token 从 max_tokens 扣除。

**实测数据：**

| 模型 | max_tokens=500 | max_tokens=4000 |
|------|:---:|:---:|
| MiMo | 499 reasoning + 1 content = 空 | 408 reasoning + 1558 content |
| Qwen | 27 reasoning + 32 content | 正常 |
| MiniMax-M3 | thinking 标签占位 | strip 后正常 |

**结论：所有推理模型的 max_tokens 不得低于 4000。** 2000 字输出 + 500 reasoning overhead = 2500 实际消耗。

## OpenAI client timeout

**错误用法（静默忽略）：**
```python
client = OpenAI(base_url=url, api_key=key)
resp = client.chat.completions.create(..., timeout=45)  # 不生效！
```

**正确用法：**
```python
client = OpenAI(base_url=url, api_key=key, timeout=120)
resp = client.chat.completions.create(...)  # 走 client 级 timeout
```

openai>=2.0 的 `create()` 不接受 `timeout` 参数。静默忽略后默认无超时，导致 hang 死。

## MiniMax-M3 `<think>` 标签

MiniMax-M3 输出格式：
```
<think>
用户要求...我应该...（内部推理）
</think>

实际回答内容...
```

剥离方法：
```python
import re
content = re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL).strip()
```

## Kimi-k3 频繁 429

`api.moonshot.cn` 的 kimi-k3 几乎每次调用都会返回：
```json
{"error":{"message":"The engine is currently overloaded, please try again later","type":"engine_overloaded_error"}}
```

建议跳过 kimi，用 qwen/minimax/mimo/deepseek 的组合。

## Qwen Token Plan 限制与 max_tokens 策略

Qwen3.8-max-preview 使用 Token Plan Credits，有 5 小时滚动配额。**max_tokens=2000 会在 ~10-15 次调用后耗尽配额**（配额按每小时重置，具体时间见 429 错误中的 reset time）。解决方案：

- 批量测试（complementarity testing）：`max_tokens=800`，足够产生有效回答
- 单次重要查询：`max_tokens=2000-4000`
- 密集会话（MoA 多次调用）：不要用 Qwen，换 DeepSeek（无限额按量付费）

实测数据：`max_tokens=800` 时 Qwen 单次耗时 ~27s（LVGL 技术问题）。`max_tokens=2000` 时 Qwen 单次耗时 >90s 后超时。

## 长时间运行脚本的 stdout 缓冲陷阱

在 terminal(background=true) 中运行 Python 脚本时，即使设置了 `PYTHONUNBUFFERED=1`，stdout 输出仍可能被完全缓冲直到进程退出。这导致在 5+ 分钟的 API 密集型脚本中无法追踪进度。

**解决方案：先写文件，后读文件。** 不要在长脚本中依赖 stdout 输出。每个阶段结束后立即 `json.dump()` 到文件，主进程通过检查文件存在性来判断是否完成。

相关：`/tmp/mm3_final.py` 因这个问题跑了 55+ 分钟无输出后被 kill。
