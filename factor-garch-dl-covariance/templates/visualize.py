#!/usr/bin/env python3
"""
协方差建模研究可视化
==================

生成图表：
1. 模型对比柱状图（Sharpe、波动率、回撤）
2. Pareto前沿（速度 vs 性能）
3. 条件数稳定性热力图
4. DM检验显著性矩阵

用法：
    cd ~/projects/factor-garch-dl-research
    /opt/anaconda3/bin/python3 visualize.py

输出：
    figures/model_comparison.png
    figures/pareto_frontier.png
    figures/condition_numbers.png
    figures/dm_heatmap.png
"""

import json
import numpy as np
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("matplotlib not available")

RESULTS_DIR = Path.home() / 'projects' / 'factor-garch-dl-research' / 'results'
FIGURES_DIR = Path.home() / 'projects' / 'factor-garch-dl-research' / 'figures'
FIGURES_DIR.mkdir(exist_ok=True)

# 中文字体支持
if HAS_MPL:
    rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
    rcParams['axes.unicode_minus'] = False

def load_results():
    with open(RESULTS_DIR / 'experiment_results.json') as f:
        return json.load(f)

def plot_model_comparison(results):
    """柱状图：模型对比。"""
    models = []
    sharpes = []
    vols = []
    dds = []

    for key, res in results.items():
        if key.startswith('_'):
            continue
        models.append(res.get('model_name_cn', key))
        sharpes.append(res.get('min_var', {}).get('overall_sharpe_ratio', 0))
        vols.append(res.get('min_var', {}).get('mean_annualized_volatility', 0) * 100)
        dds.append(abs(res.get('min_var', {}).get('mean_max_drawdown', 0)) * 100)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(models)))

    # 按Sharpe排序
    idx = np.argsort(sharpes)[::-1]
    sorted_models = [models[i] for i in idx]
    sorted_sharpes = [sharpes[i] for i in idx]
    sorted_vols = [vols[i] for i in idx]
    sorted_dds = [dds[i] for i in idx]

    # Sharpe
    bars = axes[0].barh(range(len(sorted_models)), sorted_sharpes, color=[colors[i] for i in idx])
    axes[0].set_yticks(range(len(sorted_models)))
    axes[0].set_yticklabels(sorted_models, fontsize=9)
    axes[0].set_xlabel('Sharpe Ratio')
    axes[0].set_title('Min-Var Portfolio Sharpe Ratio')
    axes[0].axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    for i, v in enumerate(sorted_sharpes):
        axes[0].text(v + 0.01, i, f'{v:.3f}', va='center', fontsize=8)

    # 波动率（升序=更好）
    vol_idx = np.argsort(sorted_vols)
    axes[1].barh(range(len(sorted_models)), [sorted_vols[i] for i in vol_idx],
                 color=[plt.cm.RdYlGn(0.8 - 0.6*i/len(vol_idx)) for i in range(len(vol_idx))])
    axes[1].set_yticks(range(len(sorted_models)))
    axes[1].set_yticklabels([sorted_models[i] for i in vol_idx], fontsize=9)
    axes[1].set_xlabel('Annualized Volatility (%)')
    axes[1].set_title('Min-Var Portfolio Volatility')

    # 回撤（升序=更好=更小）
    dd_idx = np.argsort(sorted_dds)
    axes[2].barh(range(len(sorted_models)), [sorted_dds[i] for i in dd_idx],
                 color=[plt.cm.RdYlGn(0.8 - 0.6*i/len(dd_idx)) for i in range(len(dd_idx))])
    axes[2].set_yticks(range(len(sorted_models)))
    axes[2].set_yticklabels([sorted_models[i] for i in dd_idx], fontsize=9)
    axes[2].set_xlabel('Mean Max Drawdown (%)')
    axes[2].set_title('Min-Var Portfolio Drawdown')

    plt.tight_layout()
    out = FIGURES_DIR / 'model_comparison.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 {out}")
    return out


def plot_pareto_frontier(results):
    """Pareto前沿：计算时间 vs Sharpe。"""
    models = []
    times = []
    sharpes = []
    vols = []

    for key, res in results.items():
        if key.startswith('_'):
            continue
        t = res.get('timing', {}).get('total_time', 0)
        s = res.get('min_var', {}).get('overall_sharpe_ratio', 0)
        v = res.get('min_var', {}).get('mean_annualized_volatility', 0) * 100
        if t > 0 and s != 0:
            models.append(res.get('model_name_cn', key))
            times.append(t)
            sharpes.append(s)
            vols.append(v)

    fig, ax = plt.subplots(figsize=(10, 7))

    # 气泡大小 = 1/波动率（越大=波动率越低=越好）
    sizes = [500 / max(v, 1) for v in vols]
    colors = plt.cm.RdYlGn([(s - min(sharpes)) / (max(sharpes) - min(sharpes) + 1e-6) for s in sharpes])

    scatter = ax.scatter(times, sharpes, s=sizes, c=sharpes, cmap='RdYlGn',
                        alpha=0.7, edgecolors='black', linewidth=0.5)

    for i, m in enumerate(models):
        ax.annotate(m, (times[i], sharpes[i]),
                   textcoords="offset points", xytext=(8, 5),
                   fontsize=8, alpha=0.8)

    ax.set_xlabel('Total Computation Time (seconds)', fontsize=11)
    ax.set_ylabel('Min-Var Sharpe Ratio', fontsize=11)
    ax.set_title('Pareto Frontier: Speed vs Performance\n(Bubble size ∝ 1/Volatility)', fontsize=12)
    ax.set_xscale('log')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
    ax.grid(True, alpha=0.3)

    plt.colorbar(scatter, label='Sharpe Ratio')
    plt.tight_layout()
    out = FIGURES_DIR / 'pareto_frontier.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 {out}")
    return out


def plot_condition_numbers(results):
    """条件数柱状图（对数刻度）。"""
    models = []
    conds = []

    for key, res in results.items():
        if key.startswith('_'):
            continue
        cn = res.get('cov_metrics', {}).get('mean_condition_number', 0)
        if cn > 0:
            models.append(res.get('model_name_cn', key))
            conds.append(cn)

    # 排序
    idx = np.argsort(conds)
    sorted_models = [models[i] for i in idx]
    sorted_conds = [conds[i] for i in idx]

    fig, ax = plt.subplots(figsize=(10, 5))

    colors = []
    for c in sorted_conds:
        if c < 50:
            colors.append('#2ecc71')  # 绿色
        elif c < 500:
            colors.append('#f39c12')  # 橙色
        else:
            colors.append('#e74c3c')  # 红色

    bars = ax.barh(range(len(sorted_models)), sorted_conds, color=colors)
    ax.set_yticks(range(len(sorted_models)))
    ax.set_yticklabels(sorted_models, fontsize=9)
    ax.set_xlabel('Mean Condition Number (log scale)')
    ax.set_title('Covariance Matrix Numerical Stability\n(Green < 50, Orange < 500, Red ≥ 500)')
    ax.set_xscale('log')
    ax.axvline(x=50, color='green', linestyle='--', alpha=0.5)
    ax.axvline(x=500, color='red', linestyle='--', alpha=0.5)

    for i, v in enumerate(sorted_conds):
        ax.text(v * 1.2, i, f'{v:.0f}', va='center', fontsize=8)

    plt.tight_layout()
    out = FIGURES_DIR / 'condition_numbers.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 {out}")
    return out


def plot_dm_heatmap(results):
    """DM检验p值热力图。"""
    dm = results.get('_diebold_mariano_tests', {})
    if not dm:
        print("No DM test results found")
        return None

    # 提取唯一模型名
    model_set = set()
    for pair_key in dm.keys():
        parts = pair_key.split(' vs ')
        model_set.update(parts)
    models = sorted(model_set)
    n = len(models)

    # 构建p值矩阵
    pval_matrix = np.ones((n, n))
    for pair_key, info in dm.items():
        parts = pair_key.split(' vs ')
        if len(parts) == 2:
            try:
                i = models.index(parts[0])
                j = models.index(parts[1])
                pval_matrix[i, j] = info['p_value']
                pval_matrix[j, i] = info['p_value']
            except ValueError:
                pass

    fig, ax = plt.subplots(figsize=(10, 8))
    # -log10(p) 越高=越显著
    log_p = -np.log10(np.clip(pval_matrix, 1e-10, 1))
    np.fill_diagonal(log_p, 0)

    im = ax.imshow(log_p, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(n))
    ax.set_xticklabels(models, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(n))
    ax.set_yticklabels(models, fontsize=8)
    ax.set_title('Diebold-Mariano Test: -log10(p-value)\n(Higher = more significant difference)')

    # 显著性标记
    for i in range(n):
        for j in range(n):
            if i != j and pval_matrix[i, j] < 0.05:
                ax.text(j, i, '*', ha='center', va='center', fontsize=12, fontweight='bold', color='white')

    plt.colorbar(im, label='-log10(p-value)')
    plt.tight_layout()
    out = FIGURES_DIR / 'dm_heatmap.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 {out}")
    return out


if __name__ == '__main__':
    if not HAS_MPL:
        print("Install matplotlib: pip install matplotlib")
        exit(1)

    results = load_results()

    print("Generating figures...")
    plot_model_comparison(results)
    plot_pareto_frontier(results)
    plot_condition_numbers(results)
    plot_dm_heatmap(results)
    print(f"\n✅ All figures saved to {FIGURES_DIR}")
