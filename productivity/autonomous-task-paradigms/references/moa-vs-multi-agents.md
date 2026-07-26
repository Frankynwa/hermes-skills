# MoA vs Multi Agents: When to Use What

## Core Insight

三种模式解决三个不同层面的问题，不是互相替代：

| 模式 | 解决的问题 | 适用场景 |
|------|-----------|---------|
| MoA 委员会 | 单模型知识盲区 → 多模型交叉覆盖 | 拆不开的深度推理（bug 调试、策略争议） |
| Multi Agents 接力 | 代理间不能通信 → 自动修正循环 | 可拆 + 依赖强 + 修补工作多的任务 |
| 20min 模式 | 人不在循环里 → 主 agent 自动编排 | 可拆的常规任务（80% 场景） |

## Why 20min Mode Covers 80%

Multi Agents 的唯一增量是「代理间实时修正循环」。如果：
- 子代理质量稳定，主 agent 整合时基本只是拼接 → 20min 够了
- 审查/整合阶段经常需要大量修补 → Multi Agents 值得

大多数开发任务落在前者。

## Efficiency Comparison of Pipeline vs 20min

CC + Codex 管道的真实提升：
- 取消了「主 agent 读结果 → 判断 → 再派」这一步（省 10-15 秒）
- 子代理直接拿到审查意见，不需要主 agent 转述（信息保真度提升）
- 机器总耗时差不多（API 调用次数一样）
- 主要价值：减少主 agent 误判导致的反复，不是省绝对时间

## Key Limitation

CC 和 Codex 可能走同一个 DeepSeek API —— 失去跨模型多样性。丢失了「不同知识盲区互相覆盖」的优势。最优方案是用 MiMo（Hermes）作为审查者，以保持跨模型多样性。

## 判断标准（30 秒决策规则）

能在 30 秒内画出清晰子任务边界 → 能拆 → 20min 或 Multi Agents
不能 → MoA

整合修补「多不多」= 主 agent 整合时经常需要大量修补而非简单拼接
