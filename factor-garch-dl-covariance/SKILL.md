---
name: factor-garch-dl-covariance
description: 高维波动率与协方差建模——Factor-GARCH + 深度学习 + 组合优化。16 篇核心论文 + 9 个 Python 模型 + A股/美股跨市场实验。毕业设计项目。A股数据：~/course-project-ex2-team-6/backend/database_dump/stock_prices_YYYY.csv.gz（2021-2026, 5506只股票, 635万条记录）。
---

# Factor-GARCH + Deep Learning 协方差建模

## 核心论文 Top 5（被引排序）

| 论文 | 期刊 | 被引 | DOI |
|------|------|------|-----|
| Engle (2002) DCC | JBES | 5,893 | 10.1198/073500102288618487 |
| Andersen Bollerslev Diebold (2003) RV | Econometrica | 3,014 | 10.1111/1468-0262.00418 |
| Engle Kroner (1995) BEKK | Econ Theory | 3,009 | 10.1017/s0266466600009063 |
| Bollerslev (1990) CCC | REStat | 2,453 | 10.2307/2109358 |
| Ledoit Wolf (2004) Shrinkage | JMA | 2,395 | 10.1016/s0047-259x(03)00096-4 |

## 深度文献精读

详见 `~/projects/factor-garch-dl-research/literature_deep_review.md`（472行），涵盖：
- DCC两步QMLE估计、Aielli不一致性问题
- BEKK正定性保证、参数爆炸（O(N²)）
- LW Oracle收缩系数 δ*=π/ρ、Frobenius最优
- HAR-RV三成分级联、R²≈0.55、长记忆近似
- GAS Score驱动更新、统一GARCH/ACD、自然梯度连接

## 模型实现（~/projects/factor-garch-dl-research/models/）

10 个模型，v2修复了GKX-NN和LSTM-GARCH：
1. `dcc_garch.py` — DCC-GARCH(1,1)
2. `bekk_garch.py` — BEKK(1,1,K)
3. `factor_garch.py` — Factor-GARCH + PCA
4. `gas_model.py` — GAS(1,1)
5. `har_rv.py` — HAR-RV 三成分
6. `shrinkage_cov.py` — Ledoit-Wolf 收缩估计
7. `lstm_garch.py` — LSTM-GARCH 混合（PyTorch）— v3: **Factor Model架构**（单LSTM输入全股票→输出K因子载荷→协方差重构，NLL loss + Woodbury identity，速度提升5.6x）
8. `gu_kelly_xiu.py` — Gu-Kelly-Xiu 神经网络 — v2: Cholesky target, 100 epochs, batch norm
9. `drl_portfolio.py` — DRL 组合优化
10. `utils.py` — 工具函数

## S&P500 实验结论（2018-2025, 30只股票, 75窗口）

### 最小方差组合排名

| 排名 | 模型 | Sharpe | 波动率 | 平均回撤 |
|------|------|--------|--------|---------|
| 1 | HAR-RV | +0.509 | 8.96% | -2.06% |
| 2 | Ledoit-Wolf | +0.507 | 8.44% | -1.99% |
| 3 | GAS | +0.502 | 8.65% | -2.03% |
| 4 | 样本协方差 | +0.494 | 8.60% | -2.03% |
| 5 | GKX-NN | +0.388 | 9.04% | -2.23% |
| 6 | Factor-GARCH | +0.353 | 8.62% | -2.10% |
| 7 | DCC | +0.263 | 11.77% | -3.04% |
| 8 | BEKK | +0.132 | 11.61% | -3.02% |
| 9 | LSTM-GARCH | +0.071 | 11.86% | -3.30% |

### Diebold-Mariano 检验

- DCC-GARCH 显著差于所有其他模型 (p<0.001)
- BEKK-GARCH 显著差于 LW/HAR-RV/GAS/GKX-NN (p<0.001)
- LW、HAR-RV、GAS 之间无统计显著差异

### 鲁棒性（分时段）

| 模型 | Pre-COVID | COVID | Post-COVID |
|------|-----------|-------|------------|
| HAR-RV | **+0.392** | **+0.528** | **+0.779** |
| LW | +0.204 | +0.017 | +0.719 |
| GKX-NN | -0.156 | +0.282 | +0.653 |
| BEKK | -0.034 | -1.218 | +0.274 |
| LSTM | -0.141 | -1.237 | +0.270 |

**关键发现**: HAR-RV 在所有三个时段都是最优，鲁棒性最强。

## A股实验结论（2021-2026, 30只样本, 46窗口, 真实数据）

### 最小方差组合排名

| 排名 | 模型 | Sharpe | 波动率 | 平均回撤 |
|------|------|--------|--------|---------|
| 1 | GAS | **+0.244** | 16.0% | -4.00% |
| 2 | HAR-RV | +0.206 | 17.5% | -4.21% |
| 3 | 样本协方差 | +0.198 | 16.3% | -4.12% |
| 4 | LW | +0.184 | **15.8%** | -4.06% |
| 5 | LSTM-GARCH | +0.165 | 19.0% | -5.73% |
| 6 | BEKK | +0.070 | 20.7% | -4.73% |
| 7 | GKX-NN | +0.055 | 19.6% | -4.65% |
| 8 | DCC | +0.041 | 20.4% | -5.02% |
| 9 | Factor-GARCH | +0.037 | 16.8% | -4.14% |

### A股DM检验
- DCC-GARCH显著差于所有其他模型
- LSTM-GARCH显著差于所有其他模型
- GAS与LW/HAR-RV/GKX-NN无显著差异

## 跨市场对比（A股 vs 美股）

| 模型 | A股 Sharpe | 美股 Sharpe | A股波动率 | 美股波动率 |
|------|-----------|-----------|----------|----------|
| GAS | **+0.244** | +0.502 | 16.0% | 8.6% |
| HAR-RV | +0.206 | **+0.509** | 17.5% | 9.0% |
| LW | +0.184 | +0.507 | 15.8% | 8.4% |
| LSTM-GARCH | +0.165 | +0.431 | 19.0% | 10.2% |
| BEKK | +0.070 | +0.132 | 20.7% | 11.6% |
| DCC | +0.041 | +0.263 | 20.4% | 11.8% |

**跨市场规律**：
- A股整体Sharpe低于美股，波动率约为美股2倍
- GAS在A股最优 vs HAR-RV在美股最优
- Ledoit-Wolf在两个市场都表现稳定（最安全选择）
- DCC/BEKK在两个市场都表现差

## ⚠️ 关键Pitfalls

1. **优先使用本地真实数据**：用户有A股真实数据（`~/course-project-ex2-team-6/backend/database_dump/`），不要默认用yfinance下载或合成数据。先检查本地数据再决定数据源。

2. **LSTM-GARCH不要用独立LSTM**：v1用了30个独立LSTM分别预测每只股票方差，这是根本性错误——丢失了cross-asset dynamics。必须用单LSTM + Factor Model架构。

3. **GKX-NN不要用外积当target**：`np.outer(ret, ret)`是秩1噪声矩阵，不是条件协方差。用滚动窗口协方差的Cholesky分解当target。

4. **过夜任务结束要清理cron**：监控cron job在任务完成后必须删除，否则会持续推送。

5. **实验深度不够时主动拆细**：48分钟跑完6轮的"过夜研究"是表面功夫。每个Round要有实际计算等待，不是纯LLM生成。

## 最优实践

```
协方差 = Factor-GARCH（基础层）
       + Ledoit-Wolf 收缩（正则化）
       + HAR-RV（波动率预测）
```

## 参考文档

- `references/model-fix-patterns.md` — GKX-NN和LSTM-GARCH的修复方案（Cholesky target、NLL loss、EWMA相关）
- `references/lstm-factor-model-architecture.md` — LSTM v3 Factor Model架构详解（单LSTM→因子载荷→协方差重构，Woodbury identity）
- `references/a-share-data-preparation.md` — A股数据位置、字段说明、准备脚本使用方法
- `references/cross-market-comparison.md` — A股 vs 美股跨市场对比分析结果
- `references/diebold-mariano-test.md` — DM检验实现、使用场景、解读方法、Bootstrap扩展

## 模板脚本

- `templates/robustness_analysis.py` — 分时段鲁棒性分析脚本
- `templates/visualize.py` — 可视化脚本（柱状图、Pareto前沿、条件数、DM热力图）

## 可视化

`~/projects/factor-garch-dl-research/figures/`:
- `model_comparison.png` — 三指标对比柱状图
- `pareto_frontier.png` — 速度-性能Pareto前沿
- `condition_numbers.png` — 数值稳定性热力图
- `dm_heatmap.png` — DM检验显著性矩阵

## 报告

- `~/projects/factor-garch-dl-research/高维波动率建模_研究报告.pdf`（v1, 16页）
- `~/projects/factor-garch-dl-research/results/summary_table.md`（v2）
- `~/projects/factor-garch-dl-research/results/robustness_table.md`
- `~/projects/factor-garch-dl-research/results/dm_test_results.json`
