# A3 Implementation Patterns (UMich EECS 498 WI2022)

## Linear Layer (modular)

```python
# Forward
out = x.reshape(x.shape[0], -1) @ w + b

# Backward
x_flat = x.reshape(N, -1)
dx = (dout @ w.t()).reshape(x.shape)
dw = x_flat.t() @ dout
db = dout.sum(dim=0)
```

## ReLU (non-in-place)

```python
# Forward
out = torch.clamp(x, min=0)  # NOT torch.relu in A2

# Backward
dx = dout.clone()
dx[x <= 0] = 0
```

## Dropout (inverted)

```python
# Train: mask at probability p, scale by 1/(1-p)
mask = (torch.rand_like(x) >= p).to(x.dtype) / (1 - p)
out = x * mask

# Test: pass through
out = x

# Backward (train only)
dx = dout * mask
```

## Adam Optimizer

```python
config['t'] += 1  # increment FIRST
t = config['t']
config['m'] = beta1 * config['m'] + (1 - beta1) * dw
config['v'] = beta2 * config['v'] + (1 - beta2) * dw * dw
m_hat = config['m'] / (1 - beta1**t)
v_hat = config['v'] / (1 - beta2**t)
next_w = w - lr * m_hat / (v_hat.sqrt() + eps)
```

## BatchNorm Forward (train)

```python
mu = x.mean(dim=0)
var = x.var(dim=0, unbiased=False)
x_norm = (x - mu) / torch.sqrt(var + eps)
out = gamma * x_norm + beta
running_mean = momentum * running_mean + (1 - momentum) * mu.detach()
running_var = momentum * running_var + (1 - momentum) * var.detach()
```

## BatchNorm Backward (simplified)

```python
dgamma = (dout * x_norm).sum(dim=0)
dbeta = dout.sum(dim=0)
dx = gamma / (N * torch.sqrt(var + eps)) * (
    N * dout - dout.sum(dim=0) - x_norm * (dout * x_norm).sum(dim=0)
)
```

## SpatialBatchNorm

```python
# Forward: reshape (N,C,H,W) → (N*H*W, C), call BatchNorm, reshape back
x_2d = x.permute(0,2,3,1).reshape(-1, C)
out_2d, cache = BatchNorm.forward(x_2d, gamma, beta, bn_param)
out = out_2d.reshape(N, H, W, C).permute(0,3,1,2)
```

## Kaiming Initialization

```python
# Linear: weight = randn(Din, Dout) * sqrt(gain / Din)
# Conv: weight = randn(Dout, Din, K, K) * sqrt(gain / (Din*K*K))
gain = 2.0 if relu else 1.0
```

## Conv Forward (naive, 4 loops)

```python
x_padded = F.pad(x, [pad, pad, pad, pad])
for n in range(N):
    for f in range(F):
        for i in range(H_out):
            for j in range(W_out):
                h0, w0 = i*stride, j*stride
                window = x_padded[n, :, h0:h0+HH, w0:w0+WW]
                out[n,f,i,j] = (window * w[f]).sum() + b[f]
```

## Conv Backward (naive, 4 loops)

For each (n, f, i, j) where dout[n,f,i,j] contributes:
- `dw[f] += dout * window` (accumulates over all N and spatial positions)
- `dx_padded[n, :, h0:h0+HH, w0:w0+WW] += dout * w[f]`
- `db[f] += dout[n, f].sum()`

## DeepConvNet Architecture

```
{Conv3x3 → [BatchNorm] → ReLU → [MaxPool 2x2]} × (L-1) → Linear
```
- Conv: stride=1, pad=1 (preserves spatial size)
- MaxPool: only at specified layer indices
- Final: flatten → FC → scores

## A2 SVM/Softmax Vectorized Patterns

### SVM Loss (vectorized)
```python
scores = X @ W                           # (N, C)
correct_scores = scores[range(N), y].unsqueeze(1)  # (N, 1)
margins = scores - correct_scores + 1    # (N, C)
margins[range(N), y] = 0
margins = torch.clamp(margins, min=0)
loss = margins.sum() / N + reg * torch.sum(W * W)

binary = (margins > 0).to(X.dtype)       # must match X dtype!
dW = X.T @ binary / N
row_count = binary.sum(dim=1)
dW.index_add_(1, y, -(X * row_count.unsqueeze(1) / N).T)
dW += 2 * reg * W
```

### Softmax Loss (vectorized)
```python
scores = X @ W
scores -= scores.max(dim=1, keepdim=True).values  # numeric stability
exp_scores = torch.exp(scores)
probs = exp_scores / exp_scores.sum(dim=1, keepdim=True)
loss = -torch.log(probs[range(N), y]).sum() / N + reg * torch.sum(W * W)

dscores = probs.clone()
dscores[range(N), y] -= 1
dW = X.T @ dscores / N + 2 * reg * W
```

## FastConv / FastMaxPool (autograd-based)

These wrap `torch.nn.Conv2d` / `torch.nn.MaxPool2d` for efficient backward:
```python
class FastConv:
    @staticmethod
    def forward(x, w, b, conv_param):
        layer = torch.nn.Conv2d(C, F, (HH, WW), stride=stride, padding=pad)
        layer.weight = torch.nn.Parameter(w)
        layer.bias = torch.nn.Parameter(b)
        tx = x.detach(); tx.requires_grad = True
        out = layer(tx)
        cache = (x, w, b, conv_param, tx, out, layer)
        return out, cache
```

Sandwich layers compose these: `Conv_ReLU`, `Conv_ReLU_Pool`, `Conv_BatchNorm_ReLU`, `Conv_BatchNorm_ReLU_Pool`.
These MUST be included when rewriting the file — they are NOT student-implementable TODOs.
