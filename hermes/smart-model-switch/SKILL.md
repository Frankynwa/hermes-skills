---
name: smart-model-switch
description: Smart model switching between MiMo (daily), Qwen (complex agent tasks), and DeepSeek (coding/budget) based on task complexity. Uses the agent's own judgment to suggest switching models via /model command.
version: 1.0.0
author: Hermes Agent
tags: [model, switching, fallback, cost-optimization, qwen, mimo, deepseek, benchmarking]
---

# Smart Model Switch

## 背景

用户 wangruifan 的 Hermes 配置（2026-05-25 两轮 benchmark 后）：
- **主模型：** MiMo 2.5 Pro (`xiaomi/mimo-v2.5-pro`) — 当前 config.yaml 设置
- **代用模型：** Qwen3.7 Max (`qwen/qwen3.7-max`) — 能力 10/10 全通过，最稳，中文最强，但贵 3-7x
- **预算模型：** DeepSeek V4 Pro (`deepseek-v4-pro`) — 代码/推理最强，缓存后实际成本极低，但慢且 20% 超时
- **视觉模型：** MiMo Omni (`xiaomi/mimo-v2-omni`) 或 Qwen3-VL-Plus

### Benchmark 结论

两轮 benchmark：Round 1（工具调用稳定性，6 tasks）、Round 2（核心能力，5 维度 10 tasks）。
详见 `references/benchmark-capability-2026-05-25.md`。

**Round 2 能力测试（5 维度 × 2 任务）：**

| 模型 | 通过率 | 均速 | 代码能力 | 推理 | 中文 | 文本 | 上下文 |
|------|--------|------|---------|------|------|------|--------|
| Qwen3.7 Max | 10/10 | 29.7s | 功能正确 | 谜题答错 | 最强 | 最强 | ✓ |
| DeepSeek V4 Pro | 8/10 | ~78s | **最强**（320行LRU）| **最强**（正确解谜）| 中文任务卡死 | 部分超时 | ✓ |
| MiMo 2.5 Pro | 0/10 | N/A | 余额耗尽，未实测能力 | — | — | — | — |

**关键教训**：工具调用稳定性（Round 1）≠ Hermes 框架下的真实能力。必须测试代码、推理、中文、文本质量。

### 缓存命中率实测（`hermes chat -v` 获取 token 数据）

| 模型 | 首次调用缓存 | 后续调用缓存 | 机制 |
|------|-------------|-------------|------|
| DeepSeek V4 Pro | **99%**（14336/14411）| **99%** | 持久化 prefix cache，跨 session 复用 |
| Qwen3.7 Max | 0% | **99%**（14430/14562）| Ephemeral 缓存，5min TTL，session 内有效 |

**缓存对成本的影响**：DeepSeek 的 system prompt + 工具定义在所有 session 中相同，prefix cache 跨 session 命中，实际有效输入成本 ≈ 0.05 元/M（而非标价 3 元/M），降低 ~120 倍。Qwen DashScope 首次调用无缓存，全价 2.5 元/M，但同 session 后续调用 99% 命中。

### 价格对比（来自 DeepSeek 官方页面，2.5折优惠中）

| 模型 | 缓存命中输入 | 未命中输入 | 输出 |
|------|-------------|-----------|------|
| V4 Pro | 0.025 元/M | 3 元/M | 6 元/M（原价24）|

Hermes 实际场景下，DeepSeek 的 99% 缓存命中率使有效价接近缓存命中价。

### ⚠️ 坑点备忘
- **DashScope 欠费会全拒** — 所有模型（包括 Qwen3.6-Plus 视觉能力）返回 "Access denied, Arrearage"。充值后恢复。
- **MiMo 余额耗尽也会静默失败** — `hermes chat -q` 返回 returncode=0，但 stdout 含 `HTTP 402: Insufficient account balance`。必须检查 stdout 内容判断真实成功/失败。
- **模型名不要加 `-latest` 后缀** — `qwen3-vl-plus-latest` 报 404 model_not_found，用 `qwen3-vl-plus` 列表里实际存在的名称。
- **Qwen3.6-Plus 本身也标注支持视觉理解**，但建议用专门的视觉模型 `qwen3-vl-plus` 效果更好。
- **目前只有 DASHSCOPE_API_KEY 和 DEEPSEEK_API_KEY 和 XIAOMI_API_KEY 可用**。
- **MiMo API base URL**：`https://token-plan-cn.xiaomimimo.com/v1`（2026-05-25 换回此地址）。
- **Hermes profile 不会继承 ~/.hermes/.env**：必须为每个 profile 创建 `.env` symlink。
- **`hermes chat -v` 输出完整 token + cache 数据**：用 `grep cache=` 提取缓存命中率，是 benchmark 的关键诊断工具。

### Hermes Fallback 机制说明（从源码确认）
当前 fallback 的触发条件（`run_agent.py`）：
- API 限流 (rate limit / 429)
- API 超时或连接错误
- 返回空/格式错误的响应
- 重试耗尽（默认 3 次）

**它不会在以下情况触发**：
- ❌ 模型跑得烂但输出合法（幻觉、死循环、质量差）
- ❌ 任务复杂但 Flash 能"硬撑"

这需要我（模型自身）基于自知之明来判断。**遇到复杂任务时我会主动建议切 Pro**。


## 触发条件

当用户提出任务时，评估以下维度。**满足 2 条及以上**，应主动建议切换到 Pro：

### 🟡 中等复杂度（建议切换）
- [ ] 任务涉及 3 个以上文件/模块的修改
- [ ] 任务包含复杂的数据分析或算法设计
- [ ] 任务需要深度推理（系统设计、架构决策）
- [ ] 任务涉及多个步骤的连锁依赖
- [ ] 用户明确要求高质量/严谨的回答
- [ ] 长文本生成（> 500 行代码或 > 2000 字分析）

### 🔴 高复杂度（主动要求切换）
- [ ] 需要理解整个项目架构后再工作
- [ ] 涉及安全/权限/敏感逻辑
- [ ] 用户描述中带有「复杂」「架构」「设计」「优化」「重构」等关键词
- [ ] 涉及调试难以复现的 bug
- [ ] 需要生成生产级完整代码

## 执行流程

### 方案 A：遇到复杂任务时主动询问（推荐，默认）

```
Agent: "这个任务涉及 [原因]，比较复杂。建议切换到 Qwen3.7 Max 来处理，要切吗？"
用户: "好" / "切吧"
→ Agent 执行 /model qwen3.7-max 或切换 profile
→ 完成任务后，询问是否需要切回 MiMo
```

### 方案 B：自动切换（如果用户授权）

在 session 开始或任务开始时，Agent 自行判断并执行：
```
/model qwen3.7-max    # 复杂任务切 Qwen
/model mimo-v2.5-pro  # 切回 MiMo
```
完成后自动切回。

### 模型选择指南（基于两轮 benchmark）

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 日常对话/简单任务 | MiMo 2.5 Pro | 速度最快（基准），成本适中 |
| 中文写作/职场沟通 | **Qwen3.7 Max** | 成语准确、共情自然、去AI味效果好 |
| 代码编写/调试/重构 | DeepSeek V4 Pro | 产质量最详备（320行LRU、12项重构），推理最深 |
| 复杂推理/逻辑题 | DeepSeek V4 Pro | 正确解出Qwen答错的谜题，会用Python暴力验证 |
| 多技能串联/复杂工作流 | Qwen3.7 Max | 10/10通过，DeepSeek 在此类任务20%超时 |
| 预算敏感批量任务 | DeepSeek V4 Pro | 99%缓存命中，实际成本接近缓存价（0.025元/M） |
| 文本摘要/创意写作 | Qwen3.7 Max | 五感描写、结构完整、控字数精准 |

**组合策略**：MiMo（主力，日常）→ Qwen（中文/文本/复杂链）→ DeepSeek（编码/推理/省钱）。按任务类型切换，非一刀切。

## /model 命令用法

在会话中切换模型：
```
/model qwen3.7-max      # 切到 Qwen（复杂任务）
/model mimo-v2.5-pro    # 切回 MiMo（日常）
/model deepseek-v4-pro  # 切到 DeepSeek（编码/省钱）
```

## 记忆

记住用户的偏好和当前状态：
- "User's main model: MiMo 2.5 Pro (xiaomi/mimo-v2.5-pro) as of 2026-05"
- "Capability benchmark: Qwen 10/10 (best Chinese/text), DeepSeek 8/10 (best code/reasoning, 20% timeout), MiMo untested (balance exhausted)"
- "Cache: DeepSeek 99% persistent (first call!), Qwen 99% ephemeral (second+ call only)"
- "Smart switch: MiMo (daily) → Qwen (Chinese/text/complex) → DeepSeek (coding/reasoning/budget)"
- "Diagnostic tool: hermes chat -v shows full token + cache data; grep cache= for hit rate"
