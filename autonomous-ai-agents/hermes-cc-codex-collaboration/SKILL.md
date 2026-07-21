---
name: hermes-cc-codex-collaboration
description: "Hermes + Claude Code + Codex 三方协作方案：分工策略、调用方式、最佳实践"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Claude-Code, Codex, DeepSeek, Collaboration, Orchestration]
    related_skills: [claude-code, codex, hermes-agent]
---

# Hermes + Claude Code + Codex 三方协作指南

## 架构概述

```
用户 → Hermes（规划 + 编排 + 验证）
        ├── Claude Code（复杂实现 + 代码审查）
        ├── Codex（独立模块 + 沙箱执行）
        └── MiMo/DeepSeek（简单任务、对话、分析）
```

## 当前配置状态

### Claude Code（直连 DeepSeek）
- 配置文件：`~/.claude/settings.json`
- API 端点：`https://api.deepseek.com/anthropic`
- 模型映射：
  - Sonnet → `deepseek-v4-pro`
  - Opus → `deepseek-v4-pro`
  - Haiku → `deepseek-v4-flash`

### Codex（通过代理）
- 配置文件：`~/.codex/config.toml`
- 代理：`@codeproxy/cli` 运行在 `http://127.0.0.1:8787`
- 启动脚本：`~/.hermes/scripts/start-codex-proxy.sh`
- Profile：`--profile deepseek-pro`

## 分工策略

### 任务类型 → 工具选择

| 任务类型 | 推荐工具 | 原因 |
|----------|----------|------|
| **复杂多文件重构** | Claude Code | 最强的代码理解和修改能力 |
| **独立模块实现** | Codex | 沙箱隔离，安全执行 |
| **代码审查** | Claude Code | `--from-pr` 原生支持 |
| **测试编写** | Codex/Claude Code | 都可以，看复杂度 |
| **简单修改** | Hermes 自身 | 不浪费外部工具额度 |
| **中文文档/报告** | Hermes (MiMo) | 中文能力最强 |
| **调试和排查** | Hermes + CC | Hermes 定位问题，CC 修复 |
| **并行任务** | Kanban + 多 worker | 利用 Hermes 的 Kanban 系统 |

### 成本优化策略

1. **简单任务用 Hermes**：单文件修改、配置调整、文档编写
2. **中等任务用 Codex**：独立功能实现、测试编写（通过代理，成本低）
3. **复杂任务用 CC**：多文件重构、架构调整、复杂 bug 修复
4. **并行任务用 Kanban**：多个独立任务同时执行

## 调用方式

### Claude Code 调用

```bash
# 非交互模式（推荐）
claude -p "实现 FocusPaw 的宠物状态机" --max-turns 15 --bare

# 交互模式（复杂任务）
tmux new-session -d -s cc-work
tmux send-keys -t cc-work 'claude' Enter
```

### Codex 调用

```bash
# 确保代理运行
~/.hermes/scripts/start-codex-proxy.sh

# 非交互模式
codex exec --profile deepseek-pro "添加错误处理到 API 调用"

# 交互模式
codex --profile deepseek-pro
```

### Hermes 编排

```python
# 复杂任务委派给 CC
terminal(command="claude -p '重构认证模块' --max-turns 15 --bare", 
         workdir="~/project", timeout=180)

# 独立任务委派给 Codex
terminal(command="codex exec --profile deepseek-pro '编写单元测试'", 
         workdir="~/project", timeout=120)

# 简单任务自己处理
patch(path="~/project/src/auth.py", 
      old_string="...", new_string="...")
```

## 最佳实践

### 1. 任务分解
- **大型任务**：先用 Hermes 分解，再分配给 CC/Codex
- **中型任务**：直接委派给合适的工具
- **小型任务**：Hermes 自己处理

### 2. 上下文管理
- **CC**：使用 `--append-system-prompt` 提供项目上下文
- **Codex**：使用 `--add-dir` 添加相关目录
- **Hermes**：利用 memory 和 skills 系统

### 3. 错误处理
- **CC 失败**：检查 `--max-turns` 是否足够，增加后重试
- **Codex 失败**：检查代理是否运行，重启代理
- **Hermes 失败**：检查 LSP 诊断，修复语法错误

### 4. 并行执行
```python
# 使用 delegate_task 并行执行
delegate_task(tasks=[
    {"goal": "实现前端组件", "toolsets": ["file", "terminal"]},
    {"goal": "编写后端 API", "toolsets": ["file", "terminal"]},
    {"goal": "编写测试用例", "toolsets": ["file", "terminal"]}
])
```

## 故障排除

### Claude Code 问题
- **模型错误**：检查 `~/.claude/settings.json` 中的模型名
- **认证失败**：检查 `ANTHROPIC_API_KEY` 是否正确
- **超时**：增加 `--max-turns` 或使用交互模式

### Codex 问题
- **代理未运行**：执行 `~/.hermes/scripts/start-codex-proxy.sh`
- **配置错误**：检查 `~/.codex/config.toml` 格式
- **模型不存在**：确认代理配置的模型名正确

### Hermes 问题
- **LSP 错误**：检查代码语法，修复后重试
- **Kanban 问题**：检查 worker 状态，重启 if needed
- **Memory 问题**：清理旧 memory，释放空间

## 监控和日志

### Claude Code 日志
```bash
# 查看 CC 会话
ls ~/.claude/sessions/
```

### Codex 日志
```bash
# 查看 Codex 会话
ls ~/.codex/sessions/
```

### Hermes 日志
```bash
# 查看 Hermes 日志
hermes logs --follow
```

## 更新和维护

### 更新工具
```bash
# 更新 Claude Code
npm update -g @anthropic-ai/claude-code

# 更新 Codex
npm update -g @openai/codex

# 更新代理
npm update -g @codeproxy/cli
```

### 配置备份
```bash
# 备份配置
cp ~/.claude/settings.json ~/.claude/settings.json.bak
cp ~/.codex/config.toml ~/.codex/config.toml.bak
```
