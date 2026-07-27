#!/usr/bin/env python3
"""
鲁棒性分析：分时段子样本实验
==========================

运行完整模型套件在三个子时段上的比较：
1. Pre-COVID:  2018-01 to 2020-02
2. COVID crash: 2020-02 to 2021-06
3. Post-COVID: 2021-06 to 2025-01

用法：
    cd ~/projects/factor-garch-dl-research
    /opt/anaconda3/bin/python3 robustness_analysis.py

输出：
    results/robustness_results.json — 完整结果
    results/robustness_table.md — 对比表格
"""

import sys
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path

# 导入实验函数
sys.path.insert(0, str(Path(__file__).parent))
from round4_experiment import (
    download_data, run_experiment, MODEL_REGISTRY,
    TRAIN_WINDOW, TEST_WINDOW, STEP_SIZE, RESULTS_DIR
)

PERIODS = {
    'pre_covid': ('2018-01-01', '2020-02-01'),
    'covid':     ('2020-02-01', '2021-06-01'),
    'post_covid': ('2021-06-01', '2025-01-01'),
}

def main():
    print("=" * 70)
    print("鲁棒性分析：分时段子样本实验")
    print("=" * 70)

    # 下载完整数据集
    returns = download_data()
    print(f"\n完整数据: {returns.shape[0]} 天 x {returns.shape[1]} 资产")
    print(f"日期范围: {returns.index[0].date()} → {returns.index[-1].date()}")

    all_period_results = {}

    for period_name, (start, end) in PERIODS.items():
        print(f"\n{'='*70}")
        print(f"时段: {period_name} ({start} → {end})")
        print(f"{'='*70}")

        mask = (returns.index >= start) & (returns.index < end)
        period_returns = returns.loc[mask]
        print(f"数据量: {period_returns.shape[0]} 天")

        if period_returns.shape[0] < TRAIN_WINDOW + TEST_WINDOW + 10:
            print(f"⚠️ 数据不足，跳过")
            continue

        # 临时修改超时时间
        import round4_experiment
        original_timeout = round4_experiment.TOTAL_MODEL_TIMEOUT
        round4_experiment.TOTAL_MODEL_TIMEOUT = 600  # 每个时段10分钟

        t0 = time.time()
        results, window_errors = run_experiment(period_returns)
        elapsed = time.time() - t0

        round4_experiment.TOTAL_MODEL_TIMEOUT = original_timeout

        # 运行DM检验
        from round4_experiment import run_dm_tests
        dm = run_dm_tests(window_errors)
        results['_dm_tests'] = dm

        all_period_results[period_name] = {
            'date_range': f"{start} → {end}",
            'n_days': period_returns.shape[0],
            'elapsed_seconds': round(elapsed, 1),
            'results': results,
        }

        # 打印快速摘要
        print(f"\n{period_name} 结果 ({elapsed:.0f}s):")
        for key, res in results.items():
            if key.startswith('_'):
                continue
            mv = res.get('min_var', {})
            print(f"  {res.get('model_name_cn', key):25s} | "
                  f"Sharpe={mv.get('overall_sharpe_ratio', 0):+.3f} | "
                  f"Vol={mv.get('mean_annualized_volatility', 0)*100:.1f}% | "
                  f"DD={mv.get('mean_max_drawdown', 0)*100:.2f}%")

    # 保存结果
    out_path = RESULTS_DIR / 'robustness_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_period_results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n📄 鲁棒性结果: {out_path}")

    # 生成对比表
    generate_robustness_table(all_period_results)

    print("\n✅ 鲁棒性分析完成！")


def generate_robustness_table(all_period_results):
    """生成跨时段对比表格。"""
    lines = []
    lines.append("# 鲁棒性分析：分时段子样本对比\n")
    lines.append("| 模型 | 指标 | Pre-COVID | COVID | Post-COVID | 全样本 |")
    lines.append("|------|------|-----------|-------|------------|--------|")

    # 获取模型列表
    first_period = list(all_period_results.values())[0]['results']
    model_keys = [k for k in first_period.keys() if not k.startswith('_')]

    for key in model_keys:
        for metric_name, metric_path in [
            ('Sharpe', lambda r: r.get('min_var', {}).get('overall_sharpe_ratio', 0)),
            ('波动率', lambda r: r.get('min_var', {}).get('mean_annualized_volatility', 0) * 100),
            ('回撤', lambda r: r.get('min_var', {}).get('mean_max_drawdown', 0) * 100),
        ]:
            vals = []
            for pname in ['pre_covid', 'covid', 'post_covid']:
                if pname in all_period_results:
                    pr = all_period_results[pname]['results'].get(key, {})
                    v = metric_path(pr)
                    if metric_name == 'Sharpe':
                        vals.append(f"{v:+.3f}")
                    elif metric_name == '波动率':
                        vals.append(f"{v:.1f}%")
                    else:
                        vals.append(f"{v:.2f}%")
                else:
                    vals.append("—")

            # 全样本结果
            try:
                full = json.load(open(RESULTS_DIR / 'experiment_results.json'))
                fv = metric_path(full.get(key, {}))
                if metric_name == 'Sharpe':
                    vals.append(f"{fv:+.3f}")
                elif metric_name == '波动率':
                    vals.append(f"{fv:.1f}%")
                else:
                    vals.append(f"{fv:.2f}%")
            except:
                vals.append("—")

            cn_name = first_period[key].get('model_name_cn', key)
            lines.append(f"| {cn_name} | {metric_name} | {' | '.join(vals)} |")

    table = "\n".join(lines)
    out_path = RESULTS_DIR / 'robustness_table.md'
    with open(out_path, 'w') as f:
        f.write(table)
    print(f"\n📄 鲁棒性对比表: {out_path}")


if __name__ == '__main__':
    main()
