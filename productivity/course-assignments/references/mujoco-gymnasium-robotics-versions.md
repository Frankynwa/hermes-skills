# MuJoCo + gymnasium-robotics on macOS arm64

## Versions used (working)
- macOS 26.3.1 (arm64)
- Python 3.11.15
- torch 2.12.0 (MPS backend)
- mujoco 3.8.1
- gymnasium-robotics 1.2.4
- gymnasium 0.29.1
- numpy 1.26.4

## Dependency conflict
gymnasium-robotics 1.2.4 requires `mujoco<3.0,>=2.3.3`, but the latest mujoco
is 3.8.1. Installing gymnasium-robotics normally downgrades mujoco, which on
macOS can break or fail to find prebuilt wheels.

**Workaround:** Install mujoco first (latest), then gymnasium-robotics with
`--no-deps`, then manually install remaining deps.

## MPS float64 error

Full traceback:
```
TypeError: Cannot convert a MPS Tensor to float64 dtype as the MPS framework
doesn't support float64. Please use float32 instead.
```

Root cause: `torch.from_numpy(obs[None]).to(device).float()` moves float64
to MPS before converting. The `.to(device)` calls `.to(device, dtype=d)` where
`d` is the source dtype (float64), which MPS rejects.

Fix: swap order to `.float().to(device)`.

## Expert policy device mismatch

Symptom:
```
RuntimeError: Tensor for argument input is on cpu but expected on mps
```

When `torch.load(..., map_location='mps')` moves all parameters to MPS, but
`get_action()` internally creates tensors from numpy arrays → CPU tensors.
The forward pass then fails on MPS params vs CPU inputs.

Fix: load with `map_location='cpu'` and never call `.to(device)` on the
expert policy.

## Colab environment (Ubuntu 22.04 + T4 GPU)

On Colab, the same mujoco conflict appears (`mujoco 3.8.1` vs
`gymnasium-robotics<3.0`). It works identically to macOS — ignore the warning.

Additional Colab-specific harmless warnings (from pre-installed packages):
```
rasterio 1.5.0 requires numpy>=2
opencv-python 4.13.0.92 requires numpy>=2
jaxlib 0.7.2 requires numpy>=2.0
cupy-cuda12x 14.0.1 requires numpy>=2.0
```
These are irrelevant to the assignment. The `numpy<2.0` constraint is
intentional for gymnasium-robotics 1.2.x compatibility.

## Result comparison: MPS vs CUDA

| Experiment | MPS (macOS) | CUDA (Colab T4) |
|---|---|---|
| Reacher BC | 98% | 37% |
| Reacher DAgger | 98% | 98% |
| PointMaze BC | 0% | 2% |
| PointMaze DAgger | 83% | 83% |

BC Reacher shows variance across runs (seed/hardware dependent). DAgger
results are consistent. For submission, use the Colab results.
