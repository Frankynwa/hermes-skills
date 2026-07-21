---
name: opencode-mimo
description: "Configure and use OpenCode CLI with Xiaomi MiMo model. Use for delegating coding tasks to MiMo-powered OpenCode agent."
tags: [opencode, mimo, xiaomi, coding, cli-agent]
---

# OpenCode + MiMo 配置指南

## 何时使用
Hermes 需要将编程任务委托给 OpenCode + MiMo 执行时。

## 前提条件
- OpenCode v1.15.5 已安装（`npm i -g opencode-ai@latest`）
- MiMo API Key 已配置到环境变量 `XIAOMI_API_KEY`

## 配置
OpenCode 使用内置的 `xiaomi-token-plan-cn` provider，配置文件在 `~/.config/opencode/opencode.json`。无需额外配置 provider，API Key 自动从环境变量读取。

## 使用方式

### 通过 Hermes 调用（推荐）
Hermes 的 `terminal()` 不会自动继承 `~/.hermes/.env` 中的环境变量，必须显式 source：
```python
terminal(
  command='source ~/.hermes/.env && export XIAOMI_API_KEY && opencode run "实现功能描述" --model xiaomi-token-plan-cn/mimo-v2.5-pro',
  workdir="/path/to/project",
  timeout=300
)
```

### 命令行直接调用
## 使用方式

### 环境变量（关键）
MiMo 模型的发现依赖 `XIAOMI_API_KEY` 环境变量。必须在调用前 export：
```bash
source ~/.hermes/.env && export XIAOMI_API_KEY
# 验证：opencode models 应列出 xiaomi-token-plan-cn/mimo-v2.5-pro
```
如果 env var 未设置，`opencode models` 只显示免费模型（big-pickle 等），MiMo 模型不可用。

### 命令行调用（推荐）
```bash
# 一次性任务（必须 export XIAOMI_API_KEY）
source ~/.hermes/.env && export XIAOMI_API_KEY
opencode run "写一个Python函数" --model xiaomi-token-plan-cn/mimo-v2.5-pro

# 交互式 TUI（需要 pty）
opencode --model xiaomi-token-plan-cn/mimo-v2.5-pro
```

### 常见错误
- `Model not found: xiaomi-token-plan-cn/mimo-v2.5-pro` → 检查 XIAOMI_API_KEY 是否已 export
- `Model not found: mimo-v2.5-pro/.` → model 名必须带 provider 前缀 `xiaomi-token-plan-cn/`
- `Invalid API Key` → 检查 ~/.hermes/.env 中的 key 是否正确，用 `source ~/.hermes/.env && echo $XIAOMI_API_KEY` 验证

### 验证模型可用
```bash
source ~/.hermes/.env && export XIAOMI_API_KEY && opencode models | grep xiaomi
```
应看到 `xiaomi-token-plan-cn/mimo-v2.5-pro` 等模型列表。如果只显示 `opencode/*` 免费模型，说明 API Key 未生效。

## 可用模型
- `xiaomi-token-plan-cn/mimo-v2.5-pro` — 主力编程模型

## 认证配置（踩坑记录）
- `~/.local/share/opencode/auth.json` 中 provider key 必须是 `"xiaomi"`（不是 `"xiaomi-token-plan-cn"`）
- `auth.json` 配置**不够**——OpenCode 的 `opencode auth list` 可能仍显示 0 credentials
- **必须设置 `XIAOMI_API_KEY` 环境变量**，否则 `opencode models` 只显示免费模型，`opencode run` 会报 "Invalid API Key"
- 模型名格式：`xiaomi-token-plan-cn/mimo-v2.5-pro`（带 provider 前缀），不要用 `mimo/mimo-v2.5-pro`
- 如果 `opencode models` 输出中没有 `xiaomi-token-plan-cn/*`，说明 Key 没加载成功
- TUI 模式下 OpenCode 可能不响应 submit，优先用 `opencode run` 模式

## 注意事项
- OpenCode 的 provider 是 `xiaomi-token-plan-cn`（内置），不是 `xiaomi`
- base_url: `https://token-plan-cn.xiaomimimo.com/v1`
- 需要 `--model` 参数指定模型，否则可能用默认模型
- TUI 模式需要 pty 支持，`tool_pty: true` in config.yaml
- OpenCode 项目已于 2025/09 归档，继任项目是 Crush（Charm 团队）

## 与 Hermes 的分工
- **Hermes**: 指挥官 — 任务分解、上下文管理、多平台通信、定时任务、记忆
- **OpenCode**: 执行者 — 深度代码理解、文件编辑、git 操作、测试
- 轻量任务（改配置、修 typo）Hermes 自己干
- 重度编程（完整功能模块、跨文件重构）交给 OpenCode

## 编程 Agent 工具对比（接入 MiMo 可行性）
| 工具 | 自定义模型 | MiMo 兼容 |
|------|-----------|-----------|
| OpenCode | ✅ LOCAL_ENDPOINT | ✅ 天然支持 |
| Aider | ✅ OPENAI_API_BASE | ✅ 可接入 |
| Codex | ❌ 仅 Responses API | ❌ 需代理 |
| Claude Code | ❌ 仅 Anthropic Messages | ❌ 需代理 |
