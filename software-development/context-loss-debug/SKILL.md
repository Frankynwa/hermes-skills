---
name: context-loss-debug
description: 排查 Hermes Gateway 重启导致的会话上下文丢失问题，定位会话持久化、drain 超时、sessions.json 覆盖等根因，并审计记忆/上下文机制的健康度
---

# 上下文丢失排查 & 记忆机制审计指南

## 适用场景

- 用户报告"任务做到一半上下文丢了"、"之前聊的内容不记得了"
- 会话重启后开了全新会话，旧进度丢失
- 需要审计 Hermes 的记忆/上下文/持久化机制是否高效

## 排查步骤

### 1️⃣ 确定最后一次写盘时间

```bash
ls -la ~/.hermes/sessions/session_*.json | sort -k6,7
```

检查文件内容中的 `last_updated` 字段，对比日志中的最后活动时间。如果 `last_updated` 明显早于日志中的最后用户消息时间，说明会话文件**未被及时写盘**。

**深层检查：** 读取会话 JSON 直接查看最后一条消息：
```python
python3 -c "
import json
with open('SESSION_FILE_PATH') as f:
    data = json.load(f)
print('last_updated:', data.get('last_updated'))
msgs = data.get('messages', [])
print('total messages:', len(msgs))
# 找最后一条用户消息
for i, m in enumerate(reversed(msgs)):
    if m.get('role') == 'user':
        print(f'last user msg [{len(msgs)-1-i}]:', str(m.get('content',''))[:200])
        break
"
```

### 2️⃣ 从 agent.log 重建丢失的对话

```bash
# 找到用户发送的消息
grep "inbound message" ~/.hermes/logs/agent.log | grep "feishu\|telegram\|discord" | tail -30

# 找到对应的回复
grep "response ready" ~/.hermes/logs/agent.log | grep "feishu\|telegram\|discord" | tail -30
```

### 3️⃣ 检查 Gateway 重启原因

```bash
# 是否由外部信号触发
grep -A5 "Stopping gateway for restart" ~/.hermes/logs/agent.log | tail -30

# 是否 Telegram 网络错误触发了自动重启
grep "Telegram polling could not reconnect\|Fatal telegram" ~/.hermes/logs/agent.log | tail -5

# drain 是否超时
grep "drain timed out" ~/.hermes/logs/agent.log

# 是否有 clean_shutdown 标记被跳过
grep "clean_shutdown\|Skipping" ~/.hermes/logs/agent.log
```

### 4️⃣ 检查 sessions.json（核心线索）

```bash
python3 -c "
import json
with open('/Users/wangruifan/.hermes/sessions/sessions.json') as f:
    data = json.load(f)
for k, v in data.items():
    print(f'{k}:')
    print(f'  session_id:     {v[\"session_id\"]}')
    print(f'  created_at:     {v[\"created_at\"]}')
    print(f'  updated_at:     {v[\"updated_at\"]}')
    print(f'  suspended:      {v.get(\"suspended\")}')
    print(f'  resume_pending: {v.get(\"resume_pending\")}')
    print(f'  resume_reason:  {v.get(\"resume_reason\")}')
    print()
"
```

关键字段：
- `suspended: true` — 会话被挂起，不会自动恢复
- `resume_pending: true` — 本应恢复但可能被新消息覆盖了
- 旧 session_id 是否从 sessions.json 中**彻底消失**（说明被新会话覆盖）

### 5️⃣ 检查 config.yaml 是否损坏

```bash
python3 -c "import yaml; yaml.safe_load(open('/Users/wangruifan/.hermes/config.yaml'))"
```

Gateway 日志中 `Warning: Failed to load config` 说明 YAML 格式错误。

### 6️⃣ 检查记忆系统完整健康度

```bash
# 查看当前持久化的记忆内容
cat ~/.hermes/memories/MEMORY.md
cat ~/.hermes/memories/USER.md

# 查看会话 DB 中的 token 使用情况
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/wangruifan/.hermes/state.db')
# 当前会话
cursor = conn.execute(\"SELECT id, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, estimated_cost_usd, message_count, tool_call_count FROM sessions ORDER BY rowid DESC LIMIT 5\")
for row in cursor.fetchall():
    print(f'{row[0]:35} in={row[1]:>10,} out={row[2]:>8,} cache_read={row[3]:>12,} cache_write={row[4]:>6,} cost={row[5]} msgs={row[6]} tools={row[7]}')
conn.close()
"

# 查看会话总数
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/wangruifan/.hermes/state.db')
cursor = conn.execute('SELECT COUNT(*) FROM sessions')
print('Total sessions in DB:', cursor.fetchone()[0])
conn.close()
"
```

### 7️⃣ 检查文件系统上的会话文件

```bash
ls -la ~/.hermes/sessions/session_*.json | wc -l
# 对比 DB 里的 session 数，看是否有文件比 DB 多（残留）或比 DB 少（丢失）
```

## 排查陷阱（常见误判）

### 🚫 误判 1：立刻归咎于 GitHub API 限流

**表面现象：** 日志里大量 `GitHub API rate limit exhausted (unauthenticated: 60 req/hr)`
**实际真相：** 即使 `GITHUB_TOKEN` 已配置，skills_hub 工具可能走了不同认证路径。但限流**不会导致上下文丢失**——只会让 Skill 搜索变慢，而慢本身不是丢上下文的根因。

**教训：** 不要被日志中高频出现的 WARNING 分散注意力。先确认**会话文件的写盘时间**，这是最直接的证据。

### 🚫 误判 2：认为"重启是系统自动行为"

**表面现象：** Gateway 重启了，用户没手动执行 restart
**实际真相：** 查 `Stopping gateway for restart` 之前的日志。如果是 `Telegram polling could not reconnect... Restarting gateway` — 这是 Telegram 网络错误触发的自动重启。如果是 `Feishu button resolved` 之后紧接着重启 — 说明 Agent 执行了 `hermes gateway restart` 命令并由用户在飞书批准了。Agent 执行 restart 通常是因为**用户指示了"修改后重启"**或配置变更需要生效。

**教训：** 始终向前追溯重启的触发源，不要假设是系统自动行为。

### 🚫 误判 3：认为"sessions.json 覆盖是 bug"

**表面现象：** 旧会话从 sessions.json 中"消失"了，新会话取代了它
**实际真相：** 查阅源码 `gateway/session.py:769-780`，`resume_pending: true` 会被优先尊重，不会覆盖。真正导致旧会话消失的原因是：
1. drain 超时后 `.clean_shutdown` 被跳过
2. 重启后 `suspend_recently_active()` 运行，旧会话被标记 `suspended: true`
3. 用户新消息进来 → 发现 `suspended` → 走了重置路径（line 769-770）→ 创建新会话

**这是设计行为，不是 bug。** 被挂起的会话不应该自动恢复（防止死循环）。真正的问题是**文件里的消息没写完**。

### 🚫 误判 4：认为"压缩导致上下文丢失"

**表面现象：** 会话文件压缩后消息数从 412→7 条
**实际真相：** 压缩后 `_save_session_log()` 会写入新文件（新 session_id），原文件会通过 `atomic_json_write` 保留。压缩本身不丢数据。问题出在**压缩后的后续对话**没有写回任何文件。

**教训：** 区分"压缩前的消息"（在旧文件里）和"压缩后的消息"（可能在内存中丢失了）。

### 🚫 误判 5：认为"所有飞书/Telegram 用户消息都存到了会话文件"

**表面现象：** 日志里显示了完整的用户消息和 Agent 回复，但重启后新会话没有这些内容
**实际真相：** 日志文件（`agent.log`）会记录所有 `inbound message` 和 `response ready` 事件，即使会话文件没更新。**日志不是会话持久化机制，只是调试输出。** 检查会话文件 `last_updated` 字段——如果远比最后一条日志消息的时间早，说明消息只存在于内存中。

**验证方法：**
```bash
# 比较日志中的最后用户消息时间和会话文件的 last_updated
grep "inbound message.*feishu\|response ready.*feishu" ~/.hermes/logs/agent.log | tail -5
python3 -c "import json; d=json.load(open('PATH_TO_SESSION_JSON')); print('last_updated:', d.get('last_updated'))"
```

## 根本原因诊断

### 根因链分析（从日志逆行推导）

1. **直接原因** — Gateway 重启时 drain 超时，会话被强制中断
2. **触发原因** — 谁触发了重启？（Telegram 网络错误 → 自动重启 / 用户指示重启 / 配置变更）
3. **深层问题** — 会话文件最后一次写盘是什么时候？为什么后续消息没写盘？
4. **系统缺陷** — sessions.json 条目被新会话覆盖，resume_pending 失效

### 常见根因速查表

| 现象 | 根因 | 修复 |
|------|------|------|
| `drain timed out` + 会话被中断 | Agent 处理超时（>60s），内存消息未写盘 | 增大 `restart_drain_timeout` 到 120-180s |
| `sessions.json` 旧条目消失 | 新消息创建了新会话，覆盖了 resume_pending | 无自动修复，需手动从日志重建 |
| `Failed to load config` | config.yaml YAML 格式错误 | `hermes config validate` 修复或回退备份 |
| 会话文件 `last_updated` 早于最后活动时间 | 压缩后 session_id 变更，原文件不再更新 | 这是 Hermes 内部缓存机制问题 |
| `cost_status: unknown` + `cost: 0.0` | Cost tracking provider 未配置 | 不影响功能，但失去费用可见性 |
| Telegram 反复断开触发重启 | Telegram API 网络不通（墙/代理） | 关闭 Telegram 平台或配置 fallback IP |

## 记忆机制全链路审计

### 审计命令一键执行

```bash
# ========== 1. 会话层 ==========
echo "=== 会话文件最后写盘时间 ==="
ls -la ~/.hermes/sessions/session_*.json | sort -k6,7 | tail -10

echo ""
echo "=== sessions.json 活跃条目 ==="
python3 -c "
import json
with open('/Users/wangruifan/.hermes/sessions/sessions.json') as f:
    data = json.load(f)
for k, v in data.items():
    print(f'{k}:')
    print(f'  session_id={v[\"session_id\"]}  created={v[\"created_at\"][:19]}')
    print(f'  suspended={v.get(\"suspended\")}  resume_pending={v.get(\"resume_pending\")}')
    print(f'  last_prompt_tokens={v.get(\"last_prompt_tokens\",\"?\")}  memory_flushed={v.get(\"memory_flushed\")}')
"

echo ""
echo "=== SQLite 会话 DB 摘要 ==="
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/wangruifan/.hermes/state.db')

# Token/cost breakdown
cursor = conn.execute('''
    SELECT id, model, input_tokens, output_tokens,
           cache_read_tokens, cache_write_tokens,
           message_count, tool_call_count, estimated_cost_usd,
           started_at
    FROM sessions ORDER BY rowid DESC LIMIT 5
''')
for row in cursor.fetchall():
    print(f'{row[0][:35]:35} {str(row[1] or \"\")[:18]:18} in={row[2]:>8,} out={row[3]:>8,} cr={row[4]:>10,} cw={row[5]:>6,} msgs={row[6]:>4} tools={row[7]:>4} cost={row[8]}')

# Total
cursor.execute('SELECT COUNT(*) FROM sessions')
print(f'Total sessions in DB: {cursor.fetchone()[0]}')
conn.close()
"

echo ""
echo "=== 会话 JSON 文件数量 ==="
ls -la ~/.hermes/sessions/session_*.json 2>/dev/null | wc -l

# ========== 2. 记忆层 ==========
echo ""
echo "=== MEMORY.md ==="
cat ~/.hermes/memories/MEMORY.md 2>/dev/null || echo "(empty/no file)"
echo ""
echo "=== USER.md ==="
cat ~/.hermes/memories/USER.md 2>/dev/null || echo "(empty/no file)"

# ========== 3. 配置层 ==========
echo ""
echo "=== Config 关键参数 ==="
python3 -c "
import yaml
with open('/Users/wangruifan/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)
a = cfg.get('agent', {})
print(f'restart_drain_timeout: {a.get(\"restart_drain_timeout\", \"?\")}')
print(f'gateway_timeout: {a.get(\"gateway_timeout\", \"?\")}')
m = cfg.get('memory', {})
print(f'memory_char_limit: {m.get(\"memory_char_limit\", \"?\")}  user_char_limit: {m.get(\"user_char_limit\", \"?\")}')
c = cfg.get('compression', {})
print(f'compression threshold: {c.get(\"threshold\", \"?\")}  target_ratio: {c.get(\"target_ratio\", \"?\")}')
d = cfg.get('display', {})
print(f'show_cost: {d.get(\"show_cost\", False)}')
ck = cfg.get('checkpoints', {})
print(f'checkpoints: {ck.get(\"enabled\", False)}  max_snapshots: {ck.get(\"max_snapshots\", \"?\")}')
"
```

### 审计指标解读

| 指标 | 健康值 | 危险值 |
|------|--------|--------|
| `cache_write_tokens` | > 0（说明 prompt caching 生效） | = 0（缓存没被利用，浪费钱） |
| `cache_read_tokens` / `input_tokens` 比例 | > 50%（命中率高） | < 10%（几乎无缓存命中） |
| 会话文件 `last_updated` vs 日志最后活动时间 | 差异 < 30s | 差异 > 5min（内存消息未写盘） |
| `sessions.json` 条目数 | 1 个活跃会话 | 多个条目或 0 个 |
| 记忆文件占用 | < 2200 chars | 接近上限或溢出 |
| 压缩率（compressed msgs/total msgs） | < 10%（大部分对话未压缩） | > 30%（频繁压缩，质量退化） |

### 本次审计实际发现（用户 wangruifan 环境）

```python
# 当前会话 token 使用
# session_id        model             in       out     cache_read   cw    msgs tools cost
# 20260514_004539   deepseek-chat     183,314  29,216  16,185,728   0     229  104   0.0
```

**发现：** `cache_write_tokens: 0` — 说明系统 prompt 缓存未被有效利用。每次压缩创建新 session_id，缓存状态就丢失了。这是深层优化空间。

## 记忆机制健康度评分标准

检查以下维度并逐项评分：

| 维度 | 检查方法 | 健康标准 |
|------|---------|---------|
| MEMORY.md 内容 | `cat ~/.hermes/memories/MEMORY.md` | 有实际内容，不超过 2200 字符 |
| USER.md 内容 | `cat ~/.hermes/memories/USER.md` | 有实际用户偏好，不超过 1375 字符 |
| 记忆写盘及时性 | 检查记忆文件 `.lock` 是否常驻 | 锁文件不常驻，修改即写盘 |
| 会话持久化及时性 | 对比会话文件 `last_updated` 和最新对话时间 | 差距不超过 1 次对话轮次 |
| 上下文压缩频率 | 查看 agent.log 中 `Session hygiene: compressed` | 不过度频繁（每轮对话最多 1 次） |
| Token 效率 | 检查 DB 中 cache_write_tokens = 0？ | cache_write > 0 说明缓存生效 |
| Session DB vs 文件覆盖 | 对比 DB session 数量和 `.json` 文件数量 | 接近一致，没有大量孤儿文件 |
| Checkpoint 是否启用 | `checkpoints.enabled: true` 在 config.yaml | 已启用 |

## 经验方案

### 源码修复清单（已应用）

以下修复已本地修改生效，重启 Gateway 后可用：

| 文件 | 修改 | 作用 |
|------|------|------|
| `gateway/run.py` (line ~2660) | drain 超时后遍历 `_running_agents` 调用 `_save_session_log()` | **防止内存中的消息在强制中断时丢失** |
| `run_agent.py` (line ~7597) | 压缩后在旧 session 日志写入 `continued_as_session` 和 `compression_time` | **追溯链完整，知道旧会话继续到了哪里** |
| `gateway/run.py` (line ~10240) | 每次回复自动追加 `📊 tok% · 🗜 compressed ×N · 💰 $`  footer | **所有平台（飞书/Telegram等）都能看到上下文占用和费用** |

### 方案 A：增大 drain 超时（简单有效）

```yaml
# config.yaml 中修改
agent:
  restart_drain_timeout: 120    # 默认 60s，给复杂任务更多时间
```

### 方案 B：启用费用显示

```yaml
display:
  show_cost: true              # 显示每个请求的费用
```

### 方案 C：手动恢复丢失的会话

1. 从 agent.log 的 `inbound message` 提取用户消息
2. 从 `Sending response` 提取当时的回复内容
3. 从旧会话文件加载压缩前的信息
4. 通过 `session_search` 搜索相关关键词

### 方案 D：降低会话强制压缩硬阈值

当前 `_HARD_MSG_LIMIT = 400`（代码硬编码在 gateway/run.py）。如果 Agent 常因消息过多引发 disconnected，可尝试降低此值（需修改源码）。
