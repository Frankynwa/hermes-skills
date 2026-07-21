# macOS ML Dependency Compatibility

## Known-Working Combination (macOS Apple Silicon, Python 3.11)

Tested 2026-05 on macOS 26.3.1 (arm64), MPS backend.

```bash
python3 -m venv venv && source venv/bin/activate
pip install torch torchvision torchaudio
pip install mujoco
pip install "gymnasium-robotics>=1.2.0,<1.3.0" --no-deps
pip install "gymnasium==0.29.1" "numpy>=1.24,<2.0" matplotlib tqdm Jinja2 imageio PettingZoo
```

### Version Resolution

| Package | Version | Note |
|---|---|---|
| torch | 2.12.0 | MPS backend included by default |
| mujoco | 3.8.1 | Latest at time of test |
| gymnasium-robotics | 1.2.4 | Installed `--no-deps` to avoid mujoco<3.0 pin |
| gymnasium | 0.29.1 | Pinned for gymnasium-robotics 1.2.x compat |
| numpy | 1.26.4 | `<2.0` constraint from gymnasium-robotics |

### Why --no-deps for gymnasium-robotics

`gymnasium-robotics 1.2.x` declares `mujoco<3.0,>=2.3.3` as a dependency, but mujoco<3.0 lacks prebuilt wheels for Python 3.11+. The latest mujoco (3.8.x) works fine at runtime for the environments used in CS461/MuJoCo-based RL courses (Reacher-v4, PointMaze). The version constraint is overly strict — installing `--no-deps` skips the downgrade while the runtime still works.

### MuJoCo Rendering on macOS

For headless training (no rendering), no extra deps needed. For rendering with `render_mode='human'`, MuJoCo uses native macOS OpenGL — no `apt-get` packages required unlike Linux.

## Environment Verification

```python
# Reacher
import gymnasium as gym
env = gym.make("Reacher-v4")
assert env.reset()[0].shape == (11,)

# PointMaze
from reach_goal.envs.pointmaze_env import PointMazeEnv
env = PointMazeEnv()
assert env.reset()[0].shape == (4,)
```

## AdroitHand Warning (Safe to Ignore)

```
AdroitHandRelocateDense-v1, AdroitHandHammerDense-v1, AdroitHandDoorDense-v1 
environment's reward functions were updated in v1.2.1...
```

This warning fires every `import gymnasium` with gymnasium-robotics 1.2.4. It's about AdroitHand environments only — Reacher and PointMaze are unaffected. Suppress with `import warnings; warnings.filterwarnings('ignore')` if desired.
