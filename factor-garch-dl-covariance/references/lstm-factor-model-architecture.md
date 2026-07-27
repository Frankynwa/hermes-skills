# LSTM-GARCH v3: Factor Model Architecture

## Problem with v1/v2 (Independent LSTMs)

v1 trained 30 independent LSTMs, each predicting one stock's variance from squared returns, then combining via EWMA correlation matrix.

**Why this is wrong:**
- Loses all cross-asset dynamics
- LSTM's strength is sequence modeling, not univariate variance prediction
- 30 independent models = 30x training time with no benefit
- EWMA correlation defeats the purpose of LSTM

## v3 Architecture (Single LSTM + Factor Model)

```
Input: (batch, seq_len=21, N=30) — all stocks' returns
  ↓
LSTM (hidden=64, 2 layers) — captures joint dynamics
  ↓
Three output heads:
  fc_loadings → B (N×K=30×5) — factor loadings
  fc_factor_var → σ²_f (K=5) — factor variances (softplus for positivity)
  fc_idio_var → σ²_ε (N=30) — idiosyncratic variances (softplus)
  ↓
Covariance: Σ = B @ diag(σ²_f) @ B' + diag(σ²_ε)
```

## Loss Function (NLL with Woodbury Identity)

Direct NLL requires N×N matrix inversion — expensive for N=30.

**Woodbury identity trick:**
```
Σ = B @ D_f @ B' + D_ε
Σ⁻¹ = D_ε⁻¹ - D_ε⁻¹ B (D_f⁻¹ + B' D_ε⁻¹ B)⁻¹ B' D_ε⁻¹
log|Σ| = log|D_ε| + log|D_f| + log|D_f⁻¹ + B' D_ε⁻¹ B|
```

This reduces to K×K Cholesky (K=5) instead of N×N (N=30).

## Training
- Adam lr=0.001
- ReduceLROnPlateau (factor=0.5, patience=5)
- Early stopping (patience=10)
- Gradient clipping (max_norm=1.0)
- 50 epochs

## Performance
- Speed: 3.4s/window (vs 19s for v1) — 5.6x faster
- US stock Sharpe: +0.346 (vs v1: +0.071)
- A-share Sharpe: +0.165 (vs v1: -0.432)

## Key Code Location
`~/projects/factor-garch-dl-research/round4_experiment.py`, function `model_lstm_garch()` (lines ~433-628)
