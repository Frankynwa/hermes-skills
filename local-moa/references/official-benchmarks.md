# Official Benchmark Data (2026-07-20)

## MiMo v2.5 Pro (Agent 导向评测)

来源：`https://mimo.mi.com/models/zh-CN/mimo-v2.5-pro`

MiMo v2.5 Pro 的官方评测聚焦 Agent 能力——长程代码开发、工具调用、多步任务。没有公开传统推理基准（AIME、GPQA、MATH-500）。

### Coding Agent

| 基准 | MiMo v2.5 Pro | MiMo v2.5 | Claude Opus 4.6 | Gemini 3.1 Pro | GPT-5.4 |
|------|:-----------:|:---------:|:---------------:|:--------------:|:-------:|
| SWE-Bench Pro | 57.2 | 56.1 | 57.3 | 54.2 | **57.7** |
| MiMo Coding Bench | 73.7 | 71.8 | **77.1** | 67.8 | 77.1 |
| Terminal-Bench 2.0 | 68.4 | 65.8 | 65.4 | 68.5 | **75.1** |
| FrontierSWE (排名) | #3.4 | #5.0 | #3.9 | **#1.9** | **#1.9** |

### General Agent

| 基准 | MiMo v2.5 Pro | MiMo v2.5 | Claude Opus 4.6 | Gemini 3.1 Pro | GPT-5.4 |
|------|:-----------:|:---------:|:---------------:|:--------------:|:-------:|
| GDPVal-AA | 1581 | 1426 | 1317 | **1674** | **1674** |
| τ3-bench | **72.9** | 69.5 | 72.4 | 67.1 | **72.9** |
| Claw-Eval (pass³) | 63.8 | 62.3 | **70.4** | 57.8 | 60.3 |

### Reasoning

| 基准 | MiMo v2.5 Pro (no tools) | MiMo v2.5 Pro (with tools) | GPT-5.4 |
|------|:---------------------:|:------------------------:|:-------:|
| Humanity's Last Exam | 48.0 | 40.0 | **58.7** |

## DeepSeek V4 Pro

来源：`https://api.deepseek.com/models`（官方 API 文档）

| 基准 | 得分 |
|------|:----:|
| AIME 2025 | **91.4** |
| GPQA Diamond | **84.9** |
| Humanity's Last Exam | 28.4 |
| LiveCodeBench v6 | **80.9** |
| SWE-bench Verified | **76.8** |

## MiniMax-M3

来源：MiniMax 官方发布公告（2026.06.26）

| 基准 | 得分 |
|------|:----:|
| AIME 2025 | 67.6 |
| GPQA Diamond | 78.8 |
| LiveCodeBench v6 | 80.0 |
| SimpleQA | 73.3 |
| SWE-bench Verified | 74.2 |

## Qwen3.7-Max / Qwen3.8-max-preview

来源：无公开 benchmark 数据。阿里云帮助中心页面 404，Qwen 官方博客（CSR 渲染）无法抓取。

## 关键限制

不同模型使用不同的评测体系——MiMo 测 Agent 能力，DeepSeek/MiniMax 测推理能力。官方数据无法横向对比。实测的 3 裁判互补性测试是唯一能把它们放在同一坐标系下比较的方法。
