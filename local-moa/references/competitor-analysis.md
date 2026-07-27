# Qoder 与 Trae 多模型/专家组能力分析

## Trae（字节跳动 AI IDE）

### 官网宣称功能
- "Multi Agents for Better Problem-Solving"
- "Built-in agents come with their own expertise right out of the box"
- "Customize your own agents that can handle specific tasks"
- "Your agents can plan, execute, and act as sub-agents"

### 实际机制
- **代理分工（Task Decomposition）**，非多模型投票
- 可以将任务拆成子任务分配给不同 Agent（前端/后端/审查）
- Agent 可配置不同模型（Claude、GPT、DeepSeek），但选择是静态的
- 子 Agent 机制：Agent 可 spawn 子 Agent 处理子任务

### 与 MoA 的区别
| | Trae Multi Agents | Hermes MoA | local-moa |
|---|---|---|---|
| 模型多样性 | Agent 间分工 | 跨模型聚合 | 跨模型聚合 |
| 同一问题多模型 | 否 | 是 | 是 |
| 迭代辩论 | 否 | 是 | 规划中 |
| 范式 | 横向分工 | 纵向聚合 | 纵向聚合 |

### 结论
Trae 的 Multi Agents 是**横向任务分解**（不同 Agent 做不同事），MoA 是**纵向多模型聚合**（多个模型回答同一问题后综合）。两者都是"多 Agent"但范式完全不同，不可相互替代。

## Qoder（AI 编程助手）

### 能力范围
- 标准 AI 编程助手
- Quest 功能：设计文档生成工具
- 系统提示词分析：无任何多模型或专家组功能

### 结论
Qoder 无专家组/多模型委员会功能。Quest 是设计文档工具，不是委员会。

## 社区实现（有类似功能的开源项目）

- **ensemble** (GitHub: raiyanyahya/ensemble, 9 star)：LLM 提案 → 同行评审 → 反驳 → 投票 → 综合，CLI + MCP
- **V-BReE** (GitHub: MiladEbrahimiAbyzandi/V-BReE-test-time-scaling)：多 agent 推理 + 方差阈值盲审优化
