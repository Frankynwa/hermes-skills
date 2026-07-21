# Notebook Conversion Script Pattern

When adapting a Colab `.ipynb` to macOS, a Python script using `json.load`/`json.dump` is the most reliable way to modify notebook cells programmatically (the source is split across JSON string arrays — text-based `patch` will miss matches).

## Template Outline

```python
import json

SRC = "original.ipynb"
DST = "original_macos.ipynb"

with open(SRC) as f:
    nb = json.load(f)

new_cells = []

for cell in nb["cells"]:
    src = "".join(cell["source"])

    # 1. Skip Colab-specific cells
    if "from google.colab" in src:
        continue
    if "!unzip" in src or "apt-get install" in src:
        continue
    if "Restart the runtime" in src.strip():
        continue

    # 2. Replace LD_PRELOAD cells
    if "LD_PRELOAD" in src:
        cell["source"] = [
            "# Verify installation — expect output: (11,)\n",
            "import gymnasium as gym\n",
            'env = gym.make("Reacher-v4")\n',
            "print(env.reset()[0].shape)\n",
            "env.close()\n"
        ]

    # 3. Fix device: CUDA → MPS
    if 'device = torch.device("cuda:0"' in src:
        src = src.replace(
            'device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")',
            'device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")'
        )
        cell["source"] = [line + "\n" for line in src.split("\n")]

    # 4. Add sys.path for local module imports
    if "from utils import" in src:
        # Insert after matplotlib import or similar
        lines = cell["source"]
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if "import matplotlib.pyplot as plt" in line and not inserted:
                new_lines.append("import sys; sys.path.insert(0, 'lab1')\n")
                inserted = True
        if inserted:
            cell["source"] = new_lines

    # 5. Fix data paths
    for pattern in ["'data/", '"data/']:
        if pattern in src:
            src2 = src
            src2 = src2.replace("'data/", "'lab1/data/")
            src2 = src2.replace('"data/', '"lab1/data/')
            cell["source"] = [line + "\n" for line in src2.split("\n")]
            break

    # 6. Expert policy: keep on CPU
    if "map_location=torch.device(device)" in src:
        src2 = "".join(cell["source"])
        src2 = src2.replace(
            "map_location=torch.device(device)",
            "map_location='cpu'"
        )
        # Remove .to(device) call on expert
        if "expert_policy.to(device)" in src2:
            src2 = src2.replace(
                "                expert_policy.to(device)\n", ""
            )
        cell["source"] = [line + "\n" for line in src2.split("\n")]

    new_cells.append(cell)

nb["cells"] = new_cells

with open(DST, "w") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
```

## Common Cell Patterns to Watch For

| Colab Pattern | macOS Replacement |
|---|---|
| `from google.colab import files` + `files.upload()` | Delete cell |
| `!unzip lab1.zip` + `!cp -r lab1/* .` | Delete cell (files already extracted) |
| `!apt-get install -y libgl1-mesa-dev …` | Delete cell (deps in venv) |
| `os.environ['LD_PRELOAD'] = …` | Remove the line |
| `os.kill(os.getpid(), 9)` | Delete (no runtime restart needed) |
| `'data/reacher_expert_data.pkl'` | `'lab1/data/reacher_expert_data.pkl'` |
