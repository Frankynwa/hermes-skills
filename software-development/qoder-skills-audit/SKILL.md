---
name: qoder-skills-audit
description: 审查 Qoder Skills 库并配置 Hermes 共享使用
---

# Qoder Skills 库审查 & 互通配置

## 用途

Qoder（Codex CLI）的 Skills 存放在 `~/.qoder/skills/`，与 Hermes Agent 的 Skill 格式（SKILL.md + scripts）完全兼容。这个 Skill 帮你：

1. 配置 Hermes 读取 Qoder 的 Skill 库
2. 审查 Qoder Skills 的结构兼容性和安全性
3. 让 Hermes 直接使用合格的 Qoder Skill

## 配置方法

```bash
# 设置 Hermes 读取 Qoder Skills 目录
hermes config set skills.external_dirs '["/Users/wangruifan/.qoder/skills"]'

# 重启 Gateway 使配置生效
hermes gateway restart
```

## 运行审查

```bash
python ~/.hermes/scripts/audit_qoder_skills.py
```

审查会输出：
- 哪些 Skill 可直接使用
- 哪些与 Hermes 内置重复
- 哪些有安全/兼容警告

## 结果解读

| 状态 | 含义 |
|------|------|
| ✅ ready | 结构兼容，无警告，可直接使用 |
| 🔄 duplicate | 已通过 `hermes skills install` 安装过 |
| 🔵 builtin | Hermes 已有同名内置版本 |
| ⚠️ needs_review | 有轻微警告，大概率仍可用 |

## 注意

- `external_dirs` 中的 Skill 是**只读**的（不可修改/删除）
- Hermes 按需加载这些 Skill，不会自动全部加载到列表中
- Qoder 的 Skill 来源是 anthropics/skills（trusted），安全性值得信任
- 审查脚本在 `~/.hermes/scripts/audit_qoder_skills.py`
- **绝对不要直接修改 Qoder 的 SKILL.md 文件**——Qoder 通过 `npx skills add` / `skills update` 从上游仓库管理技能，本地修改会被覆盖。如需附加 metadata（如 category），应在 Hermes 侧维护独立的映射文件。
- **审查脚本是持续的存量管理工具**，不是一次性验证工具——Qoder 和 Hermes 的 skill 库都会动态增减，在安装/调用 skill 前跑一次脚本可避免重复安装、发现新可用 skill。
