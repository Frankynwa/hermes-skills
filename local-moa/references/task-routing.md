# 多模型调度决策树

## 快速判断（3 个问题）

**Q1: 任务能画出清晰的子任务边界和交付物吗？**

- 不能 → **MoA 委员会**（local-moa skill）
- 能 → Q2

**Q2: 子任务之间有强依赖吗？**

- 没有 → **20min 模式**（autonomous-task-paradigms skill，并行 delegate_task）
- 有 → Q3

**Q3: 整合阶段修补工作多吗？**

- 不多 → **20min 模式够了**（串行 delegate_task + 主 agent 整合）
- 多 → **Multi Agents 自动修正**（CrewAI/AutoGen，但需额外框架）

## 实际落地方案

| 场景 | 推荐方案 | 工具 |
|------|---------|------|
| 简单指令（发消息、查天气）| 单模型 | Hermes 默认 |
| 可拆分无依赖（搜论文×3、lint检查）| 20min 并行 | delegate_task 并行 |
| 可拆分有依赖（查API→写框架→审查）| 20min 串行 | delegate_task + 主 agent 整合 |
| 拆不开的深度推理（bug定位、策略争议）| MoA | local-moa 脚本 |
| 关键决策需多视角 | MoA | local-moa 脚本 |
| 单模型卡死、直觉不信 | MoA | local-moa 脚本 |

## MoA 成本指南

| 模式 | 提案者数 | API调用数 | 估算成本 |
|------|:---:|:---:|------|
| budget | 2 (DS + MiMo) | 3 | ¥0.03-0.08 |
| optimal | 3 (DS + MiniMax + Qwen) | 4 | ¥0.05-0.20 |
| full | 4 (全部) | 5 | ¥0.10-0.30 |

## 互补性测试

运行前先确认模型组合的互补性：
```bash
python3 ~/scripts/model_complementarity.py --prepare
python3 ~/scripts/model_complementarity.py --run
python3 ~/scripts/model_complementarity.py --judge
```

互补性 >20% 的组合才值得用 MoA，<5% 的组合纯粹浪费 token。
