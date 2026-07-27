---
name: local-moa
description: 本地多模型委员会（MoA）——支持多 provider preset 切换 + 成本估算 + token 追踪。最优组合（deepseek + MiniMax-M3 + qwen3.8-max）已通过 15 题互补性实证验证。基于 ModelSwitch (2025)、MoA (Together AI 2024)。
category: software-development
---

## 触发条件

用户需要对复杂推理问题进行多模型交叉验证。或用户说"用 MoA 分析""多模型对比""委员会模式"。

## 用法

```bash
export $(grep -v '^#' ~/.hermes/.env | xargs)
python3 ~/scripts/moa.py --verbose "你的问题"
```

### Provider Preset

| Preset | 提案者 | 成本 | 适用场景 |
|--------|--------|------|---------|
| `--provider optimal` (默认) | deepseek + MiniMax-M3 + qwen3.8-max | ¥0.05-0.20/次 | 日常关键推理 |
| `--provider budget` | deepseek + MiMo | 较低 | 快速验证 |
| `--provider full` | 全部 4 模型 | 最高 | 最高质量要求 |
| `--provider deepseek` | 无（单模型） | 最低 | 对比基线 |

### 参数

| 参数 | 说明 |
|------|------|
| `--provider PRESET` / `-p` | 选择模型组合（默认 optimal） |
| `--provider list` | 列出所有预设方案 |
| `--verbose` / `-v` | 显示 token 用量、耗时、成本估算 |
| `--file PATH` / `-f` | 从文件读取问题 |
| 管道输入 | `echo "问题" \| python3 ~/scripts/moa.py` |

## 模型定价

| 模型 | 输入 ¥/百万tokens | 输出 ¥/百万tokens | 计费方式 |
|------|:---:|:---:|------|
| deepseek-v4-pro | ¥3.12 | ¥6.24 | 按量，无限额 |
| MiniMax-M3 | ¥2.10 | ¥8.40 | 按量，永久五折 |
| qwen3.8-max-preview | ~¥0.70 | ~¥4.17 | Token Plan 月费，预览期 1 折，有 5h/7d 限额 |
| mimo-v2.5-pro | 按量 | 按量 | 按量 API |

## 互补性测试实证

15 题完整测试（LVGL 调试 / 策略回测 / 论文分析各 5 题），已通过 3 位裁判交叉验证（DeepSeek + Qwen + MiMo）。MiniMax 裁判因 API 延迟过高（30s+/题）不适合做裁判。

### 三裁判完整对比

#### 各模型净胜率

| 模型 | DS 裁判 | Qwen 裁判 | MiMo 裁判 | 均值 |
|------|:-------:|:--------:|:--------:|:----:|
| mimo-v2.5-pro | -1 | +5 | +1 | +1.7 |
| qwen3.8-max | +1 | +4 | -1 | +1.3 |
| MiniMax-M3 | +1 | 0 | -2 | -0.3 |
| deepseek-v4-pro | -1 | -4 | -5 | -3.3 |

#### 两两互补率（三裁判平均）

| 组合 | DS 评 | Qwen 评 | MiMo 评 | 平均 | 趋势 |
|------|:-----:|:-----:|:-----:|:----:|------|
| MiniMax + DS | 40.0% | 13.3% | 33.3% | 28.9% | Qwen 不认 |
| DS + MiMo | 20.0% | 6.7% | 40.0% | 22.2% | MiMo 自评高 |
| Qwen + MiniMax | 33.3% | 40.0% | 6.7% | 26.7% | MiMo 不认 |
| Qwen + MiMo | 6.7% | 40.0% | 6.7% | 17.8% | 唯 Qwen 认 |
| Qwen + DS | 26.7% | 53.3% | 13.3% | 31.1% | Qwen 极偏 |
| **MiniMax + MiMo** | **20.0%** | **20.0%** | **20.0%** | **20.0%** | **唯一三方一致！**|

#### 三模型组合覆盖率（/15 题）

| 组合 | DS 判 | MiMo 判 | 均值 |
|------|:-----:|:-----:|:----:|
| **DS + MiniMax + Qwen** | 7 | 7 | **7.0** |
| DS + MiniMax + MiMo | 5 | 7 | 6.0 |
| DS + Qwen + MiMo | 6 | 5 | 5.5 |
| Qwen + MiniMax + MiMo | 3 | 4 | 3.5 |

结论：**DS + MiniMax + Qwen 在 DS 和 MiMo 两位裁判下都获得最高覆盖率（7/15），双裁判共识。** 最优三模型组合确认。

### 裁判自偏好效应

| 裁判模型 | 自评净胜 | 倾向 |
|---------|:------:|------|
| DeepSeek | -1 | 自我批评 |
| Qwen | +4 | 明显自我偏袒 |
| MiMo | +1 | 轻微偏好 |

教训：不能用单一模型做裁判——必须交叉验证 2+ 裁判。Qwen 做裁判时有明显自偏好，但三裁判均值能消除单裁判偏差。

### 官方 Benchmark 参考：测量体系不可比

搜索了四个模型的官方 benchmark 数据，发现关键问题：**不同模型使用完全不同的评测体系，官方数据无法横向对比。**

| 模型 | 评测体系 | 可比的推理基准 |
|------|---------|:---:|
| MiMo v2.5 Pro | Agent 导向（SWE-bench、τ3-bench、Terminal-bench） | 无 AIME/GPQA |
| DeepSeek V4 Pro | 推理导向（AIME、GPQA、LiveCodeBench） | 有 |
| MiniMax-M3 | 推理导向（AIME、GPQA、LiveCodeBench、SWE） | 有 |
| Qwen3.7-Max | 官方未公开 benchmark | 无 |
| Qwen3.8-max-preview | 官方未公开 benchmark | 无 |

MiMo 测的是「能不能完成多步工程任务」，DeepSeek 测的是「数学题能做对多少」。就像跳高和游泳——数字放在一起没意义。**实测的 3 裁判互补性测试是唯一能把它们放在同一坐标系下比较的方法。** 完整原始数据见 `references/official-benchmarks.md`。

完整方法论见 `references/complementarity-methodology.md`。三裁判交叉验证方法见 `references/three-judge-methodology.md`。集成学习理论依据见 `references/ensemble-theory.md`。

## 环境变量

| 变量 | 对应模型 |
|------|---------|
| DEEPSEEK_API_KEY | deepseek-v4-pro |
| MINIMAX_API_KEY | MiniMax-M3 |
| QWEN_API_KEY | qwen3.8-max-preview |
| MIMO_API_KEY | mimo-v2.5-pro |

## 何时用 MoA vs 单模型

MoA 不适用于所有场景。按任务类型决策：

**高收益**（委员会显著优于单模型）：
- 答案存在多个独立维度，单模型容易漏维度
- 错误有累积放大效应（调试代码、策略争议分析）
- 关键决策需要多视角验证

**低收益/负收益**：
- 简单指令（飞书消息、查天气）——多模型纯噪音
- 主观解释（八字命理）——聚合器可能搅浑
- 创意任务（写诗）——共识点通常是平庸点

**触发条件**：
1. 单模型卡死——同一段代码问了几轮还是找不到 bug
2. 关键决策——策略回测结果决定真金白银
3. 验证——单模型答案太自信但你直觉觉得不对劲

## 为什么 MiMo 不参与 MoA

经过四模型互补性测试（15 题 × 3 裁判交叉验证），结论是 **MiMo v2.5 Pro 不适合做 MoA 提案者——不是因为它弱，是因为它太全面。**

| MiMo 组合 | DS 评 | Qwen 评 | 平均 |
|-----------|:-----:|:-----:|:----:|
| MiMo + DS | 20.0% | 6.7% | 13.4% |
| MiMo + Qwen | 6.7% | 40.0% | 23.4% |
| MiMo + MiniMax | 20.0% | 20.0% | 20.0% |

所有 MiMo 组合互补率 < 25%。这是因为 MiMo 的错误模式和其他模型高度重叠——MiMo 答对的题，其他模型基本也对；MiMo 答错的题，其他模型基本也错。加入 MoA 只是重复花钱，不覆盖新的知识盲区。

**理论支撑：** 这是集成学习中经典的「精度-多样性悖论」（Kuncheva & Whitaker 2003）。Breiman (2001) 定理：集成误差 ≤ ρ × 个体误差，ρ = 模型间错误相关性。MiMo 作为覆盖面最广的模型，和其他模型的 ρ 接近 1，集成增益趋近于零。

**务实策略：** MiMo 做日常主力单模型。当 MiMo 也卡住时（同一问题 3 轮无进展），切到 DS + MiniMax + Qwen 三模型 MoA。

## 论文依据

- MoA (Together AI 2024): 多层聚合架构，6 开源模型 + 3 层聚合
- ModelSwitch (2025): 多模型 + 重复采样互补，跨模型多样性 > 单模型推理路径多样性
- Beyond Consensus (2026): 推理路径多样性关键，但封闭式基准（MMLU/MATH）结论不直接适用于开放式任务
- RouteMoA (ACL 2026): 稀疏路由，成本降低 89.8%
- MCA (2026): 互补性选择框架——选互补性最强的组合，而非最强的模型
- Breiman (2001): 随机森林定理——集成误差 ≤ ρ × 个体误差，ρ = 错误相关性
- Krogh & Vedelsby (1995): 模糊度分解——集成增益 = 模型间分歧度，个体越强增益越小
- Kuncheva & Whitaker (2003): 多样性-精度悖论——个体精度和多样性本质反比

## 模型 API 配置

所有模型已验证可用的端点和模型名（2026-07-20）：

| mkey | 模型名 | base_url | 特点 |
|------|--------|----------|------|
| qwen | qwen3.8-max-preview | token-plan.cn-beijing.maas.aliyuncs.com | Token Plan 月费，5h/7d 限额 |
| kimi | kimi-k3 | api.moonshot.cn | 高峰期频繁 429 overloaded。429 不收费，但脚本需断路器防重试风暴 |
| minimax | MiniMax-M3 | api.minimax.chat | 输出含 `<think>` 标签，需 strip |
| mimo | mimo-v2.5-pro | api.xiaomimimo.com | 按量付费 |
| deepseek | deepseek-v4-pro | api.deepseek.com | 最稳定 |

## API 调用关键陷阱

三条铁律，每次调用推理模型时必须遵守：

1. **max_tokens 必须 >= 4000**：MiMo/Qwen/MiniMax 的 reasoning_tokens 会吃掉输出预算。MiMo 实测 500 max_tokens → 499 reasoning + 1 content = 空输出。4000 max_tokens 可产出 1500-3000 字内容。

2. **timeout 必须在 OpenAI() 构造时设置**：`OpenAI(..., timeout=120)`。不能在 `create()` 里传 `timeout=`——openai>=2.0 的 `create()` 不接受该参数，静默忽略后无超时保护。

3. **MiniMax 输出含 `<think>...</think>`**：必须用 `re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL)` 剥离后才能用于聚合。

4. **Kimi K3 429 过载 — 不计费但会拖垮脚本**：Kimi 官方确认：**429 `engine_overloaded_error` 请求不收费**（无 session_id、无响应内容、未处理）。但脚本若无重试控制，会在过载期间疯狂重试，等服务恢复后批量成功才产生计费。2026-07-21 实测：`model_complementarity.py` 无断路器 + openai SDK 自动重试叠加，导致 268 次 kimi-k3 请求（132 次 429 免费 + 135 次 200 成功扣费 22.77 元）。**429 本身不花钱，但无节制的重试会在恢复后产生大量成功请求。** 跑 benchmark 前确认脚本有断路器（连续 3 次 429 跳过）和去重（已成功不重跑）。详见 `references/script-safety.md`。

详见 `references/api-quirks.md`。完整模型配置和端点见 `references/api-quirks.md`。脚本安全防护模式见 `references/script-safety.md`。

## 已知限制

- 仅文本，不支持多模态
- 当前无迭代（1 轮提案 + 1 次聚合）
- DeepSeek 同时做提案者和聚合器时有自我偏好风险
- qwen3.8-max 有 Token Plan 5h/7d 硬限额
- kimi-k3 高峰期频繁 429 overloaded，不建议作为日常提案者。429 请求不计费，但需脚本断路器防重试风暴
