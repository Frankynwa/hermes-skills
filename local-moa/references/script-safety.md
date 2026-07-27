# API Script Safety Patterns

> 2026-07-23: `model_complementarity.py` 因缺少防护导致 268 次 kimi-k3 请求、22.77 元账单。以下是必须内置的保护模式。

## 必须的保护

### 1. 断路器（Circuit Breaker）

连续 N 次相同错误后永久跳过该模型，防止重试风暴。

```python
_circuit_breaker = {}  # model_key → consecutive_error_count

def call_api(model_key, question):
    if _circuit_breaker.get(model_key, 0) >= 3:
        return False, None, f"[断路器] 连续3次失败"

    try:
        result = client.chat.completions.create(...)
        _circuit_breaker[model_key] = 0  # 成功→重置
        return True, result, None
    except Exception as e:
        if is_retryable(e):  # 429, 5xx
            _circuit_breaker[model_key] = _circuit_breaker.get(model_key, 0) + 1
            if _circuit_breaker[model_key] >= 3:
                print(f"⚡ 断路器触发，跳过 {model_key}")
        raise
```

### 2. 去重（Dedup）

已成功的 (模型, 问题) 组合不重跑。

```python
# 从 results.json 加载已有结果
results = load_results()
for question in questions:
    for model in models:
        if (qid in results and model in results[qid]
                and results[qid][model].get("success")):
            print(f"⏭ 跳过 {model}（已成功）")
            continue
        # ... 调用模型
```

### 3. API Key 管理

**绝对禁止硬编码**。全部用环境变量。

```python
# ❌ 危险
"key": "sk-WiD...D4zk"

# ✅ 安全
"key_env": "MOONSHOT_API_KEY"
```

读取 key 时先查系统环境变量，再 fallback 到 `.env` 文件。

### 4. SDK 重试控制

OpenAI Python SDK 默认自动重试 429。如果脚本自己有重试逻辑，必须关闭 SDK 重试防止叠加。

```python
# 关闭 SDK 自动重试，由脚本自己的断路器控制
client = OpenAI(..., max_retries=0)
```

### 5. 速率控制（建议）

并行调用时控制并发数，避免同时轰炸 API。

```python
# 不要无限制全量并行
with ThreadPoolExecutor(max_workers=5) as executor:  # 不是 len(models)
    ...
```

## 检查清单

运行任何 API 批量脚本前确认：

- [ ] 所有 API key 通过环境变量（不是硬编码）
- [ ] 有断路器（连续 3 次失败→跳过）
- [ ] 有去重（已成功不重跑）
- [ ] SDK 自动重试已关闭（`max_retries=0`）
- [ ] 并发数有限（建议 ≤5）
- [ ] 每轮之间有间隔（`time.sleep(0.5)`）
