# Diebold-Mariano 检验实现

## 用途

检验两个模型的预测准确性是否有统计显著差异。

- H0: E[d_t] = 0，其中 d_t = loss_1_t - loss_2_t
- 正DM统计量 => 模型2更好（损失更低）

## 实现

```python
def diebold_mariano_test(losses_1, losses_2, h=1):
    """
    Parameters
    ----------
    losses_1, losses_2 : array-like
        每个窗口的损失序列（如平方预测误差）
    h : int
        预测期数（用于HAC调整）

    Returns
    -------
    dm_stat : float
    p_value : float
    """
    d = np.array(losses_1) - np.array(losses_2)
    n = len(d)
    d_mean = np.mean(d)

    # HAC方差（Newey-West，h-1个滞后）
    gamma_0 = np.var(d, ddof=1)
    hac_var = gamma_0
    for k in range(1, h):
        weight = 1 - k / h  # Bartlett核
        gamma_k = np.sum((d[k:] - d_mean) * (d[:-k] - d_mean)) / n
        hac_var += 2 * weight * gamma_k

    if hac_var <= 0:
        return 0.0, 1.0

    dm_stat = d_mean / np.sqrt(hac_var / n)
    # 双侧p值（正态近似）
    from scipy.stats import norm
    p_value = 2 * (1 - norm.cdf(abs(dm_stat)))

    return float(dm_stat), float(p_value)
```

## 使用场景

1. **协方差预测准确性**：比较不同模型的Frobenius误差
2. **波动率预测准确性**：比较不同模型的波动率预测误差
3. **组合表现**：比较不同模型的Sharpe比率差异

## 解读

| p值 | 显著性 | 含义 |
|-----|--------|------|
| < 0.01 | *** | 高度显著差异 |
| < 0.05 | ** | 显著差异 |
| < 0.10 | * | 边际显著差异 |
| >= 0.10 | n.s. | 无显著差异 |

## 注意事项

1. **需要足够的窗口数**：至少10个窗口才有意义
2. **损失函数选择**：Frobenius误差是最常用的协方差预测损失
3. **多重比较**：多对模型比较时需要Bonferroni校正
4. **单侧vs双侧**：通常用双侧检验，除非有先验方向

## 扩展：Bootstrap置信区间

```python
def bootstrap_dm_ci(losses_1, losses_2, n_bootstrap=1000, alpha=0.05):
    """Bootstrap DM检验的置信区间。"""
    n = len(losses_1)
    dm_stats = []
    
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, size=n, replace=True)
        l1 = np.array(losses_1)[idx]
        l2 = np.array(losses_2)[idx]
        dm, _ = diebold_mariano_test(l1, l2)
        dm_stats.append(dm)
    
    ci_lower = np.percentile(dm_stats, 100 * alpha / 2)
    ci_upper = np.percentile(dm_stats, 100 * (1 - alpha / 2))
    
    return ci_lower, ci_upper
```
