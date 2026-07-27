# 模型修复记录：GKX-NN & LSTM-GARCH

## GKX-NN 修复（v1→v2）

### v1 问题
- Target = `np.outer(next_ret, next_ret)` — 单次收益实现的秩1矩阵，不是条件协方差
- 25 epochs, lr=0.001, 无scheduler — 训练不足
- 网络太小（64→32→N²）— 严重欠拟合

### v2 修复方案
```python
# 1. Target改为滚动窗口协方差的Cholesky分解
cov_window = 60  # 3个月滚动窗口
target_cov = np.cov(X[t-cov_window:t].T)
chol = np.linalg.cholesky(target_cov + np.eye(n_assets) * 1e-8)
targets.append(chol[np.tril_indices(n_assets)])

# 2. 网络结构：256→128→64 + BatchNorm + Dropout
class CovNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, output_dim)
        )

# 3. 训练：100 epochs, CosineAnnealing, early stopping (patience=15)
# 4. 从Cholesky因子重建协方差矩阵（保证PSD）
L = np.zeros((n_assets, n_assets))
L[np.tril_indices(n_assets)] = pred_chol
pred_cov = L @ L.T
```

### 效果
- 条件数：3.7亿 → 43
- Frobenius误差：发散 → 0.0026
- Sharpe：+0.15 → +0.39

---

## LSTM-GARCH 修复（v1→v2）

### v1 问题
- 15 epochs, lr=0.01 — 训练不足+学习率太高
- MSE loss on squared returns — 不是正确的波动率损失
- 样本相关矩阵做非对角 — LSTM只影响对角线

### v2 修复方案
```python
# 1. NLL loss（负高斯对数似然）
pred_var = torch.nn.functional.softplus(pred) + 1e-8
loss = torch.mean(torch.log(pred_var) + y_train[idx] / pred_var)

# 2. 训练参数：50 epochs, lr=0.001, ReduceLROnPlateau
# 3. Train/val split (80/20) + early stopping (patience=10)
# 4. EWMA相关矩阵替代样本相关
lambda_ewma = 0.94
Q = np.eye(n_assets)
for t in range(T):
    Q = lambda_ewma * Q + (1 - lambda_ewma) * z[t:t+1].T @ z[t:t+1]
D_inv = np.diag(1.0 / np.sqrt(np.diag(Q) + 1e-10))
ewma_corr = D_inv @ Q @ D_inv

# 5. 最终协方差 = D @ ewma_corr @ D
```

### 效果
- 条件数：547万 → 3272（中位数145）
- 仍有问题：训练30个独立LSTM太慢（19s/window），极端市场下崩溃

### 待改进
- 改成单LSTM + Factor Model架构（LSTM输出factor loadings）
- 或用Transformer替代LSTM

---

## 关键教训

1. **Cholesky分解是保证PSD的最佳实践** — 直接预测协方差矩阵无法保证正半定
2. **NLL loss > MSE loss** — 波动率预测必须用统计上正确的损失函数
3. **EWMA相关 > 样本相关** — 捕捉时变相关性
4. **独立LSTM不适合多资产** — 忽略cross-asset dynamics
