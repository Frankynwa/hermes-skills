# PyTorch Implement-From-Scratch Pitfalls (macOS)

Common gotchas when implementing ML assignments (UMich EECS 498, CS231n, etc.)
that require filling TODO blocks in `.py` files with hand-written forward/backward
passes — running locally on macOS before submitting to Colab.

---

## 1. dtype mismatch: `.float()` vs `.to(dtype)`

When inputs are float64 and you create an intermediate mask with `.float()`, it
becomes float32, causing a matrix multiply to crash:

```
RuntimeError: expected m1 and m2 to have the same dtype, but got: double != float
```

**Fix**: Use `.to(X.dtype)` instead of `.float()`:

```python
# WRONG — creates float32 mask, crashes if X is float64:
binary = (margins > 0).float()

# CORRECT — matches the input dtype:
binary = (margins > 0).to(X.dtype)
```

This commonly happens in vectorized SVM/Softmax loss implementations where a
hinge/indicator mask is multiplied with the input matrix.

---

## 2. `torch.nditer` removed in PyTorch 2.x

Numeric gradient checking (for verifying hand-written gradients) often uses
`torch.nditer` from CS231n course materials. This API was removed in PyTorch 2.x:

```
AttributeError: module 'torch' has no attribute 'nditer'
```

**Fix**: Use `itertools.product` to iterate over tensor indices:

```python
from itertools import product

def numeric_gradient(fn, x, h=1e-6):
    grad = torch.zeros_like(x)
    for idx in product(*[range(s) for s in x.shape]):
        old_val = x[idx].item()
        x[idx] = old_val + h
        loss_plus = fn(x)
        x[idx] = old_val - h
        loss_minus = fn(x)
        x[idx] = old_val
        grad[idx] = (loss_plus - loss_minus) / (2 * h)
    return grad
```

This works on all PyTorch versions and is a drop-in replacement.

---

## 3. Python interpreter selection on macOS

The Hermes agent venv (`python3` → Python 3.11) typically does NOT have
PyTorch/torchvision installed. The homebrew Python 3.13 (`python3.13`) usually
does if the user has installed ML packages globally.

**Diagnosis**:
```bash
which python3        # → ~/.hermes/hermes-agent/venv/bin/python3 (no torch)
python3.13 -c "import torch; print(torch.__version__)"  # → 2.x (has torch)
```

**Fix**: Use `python3.13` explicitly when running assignment verification scripts:
```bash
python3.13 -c "from linear_classifier import *; hello_linear_classifier()"
```

For `pip install`, use `pip3 install --break-system-packages` on homebrew Python
(requires PEP 668 override), or better: create a dedicated venv per the
colab-notebook-macos skill's Step 1.

---

## 4. EECS 498 starter code structure

UMich EECS 498 WI2022 assignments follow a consistent pattern:
- `.py` files contain `pass` in TODO blocks (the actual implementation)
- `.ipynb` notebooks import and test those `.py` files
- `eecs598/` package provides utilities (grad checking, data loading, Solvers)

**Starter code download URLs** (always the blank template, not student solutions):
```
https://web.eecs.umich.edu/~justincj/teaching/eecs498/WI2022/assignments/A{n}.zip
```

**PITFALL**: GitHub repos (e.g., `chizkidd/EECS498-Deep-Learning-for-Computer-Vision`)
contain COMPLETED solutions, not starter code. Always download from the course page.

---

## 5. Verification pattern for gradient correctness

After implementing all TODOs, verify with this pattern:

1. Create small random inputs (D=5, C=3, N=10, float64 for precision)
2. Compute analytic gradient from your implementation
3. Compute numeric gradient with finite differences (h=1e-6)
4. Check relative error < 1e-5

Expected relative errors for correct implementations:
- SVM loss gradient: ~1e-10
- Softmax loss gradient: ~1e-10
- Two-layer NN gradients: ~1e-8 (slightly less precise due to chain rule depth)

---

## 6. `loss.item()` fails when loss is a Python float

When `train_linear_classifier` calls `loss_func(...)` and the loss function
returns a Python `float` (e.g. from `loss = 0.0` initialization that gets
overwritten), `.item()` raises `AttributeError: 'float' object has no attribute 'item'`.

This happens when:
- The loss function's `loss` variable starts as `loss = 0.0` and the overwrite
  assignment somehow doesn't execute (rare, but seen in Colab cached modules)
- The Colab runtime is using a stale cached version of the `.py` file

**Fix in training loop**:
```python
loss, grad = loss_func(W, X_batch, y_batch, reg)
loss_history.append(loss.item() if isinstance(loss, torch.Tensor) else loss)
```

**Root cause fix**: Restart the Colab runtime after uploading new `.py` files.
Colab caches imported modules — `%load_ext autoreload` is broken on Python 3.12+
(see pitfall #7), so the only way to pick up changes is runtime restart.

---

## 7. `%load_ext autoreload` broken on Python 3.12+ (Colab 2025+)

Google Colab upgraded to Python 3.12 which removed the `imp` module:

```
ModuleNotFoundError: No module named 'imp'
```

The IPython autoreload extension depends on `imp.reload`. There is no pip
installable fix (`pip install imp` fails with "no matching distribution").

**Workaround**: Simply skip the autoreload cells. They are only needed for
iterative `.py` editing during development — if the code is already written,
autoreload is unnecessary.

If you DO need live-reload during development, restart the runtime after each
`.py` edit instead.

---

## 8. Google Colab file sync workflow

When implementing assignments locally and uploading to Colab:

### Upload pattern
1. Zip the assignment folder locally: `zip -r ~/Desktop/A2.zip A2/ -x "*__pycache__*"`
2. Upload zip to Google Drive root
3. In Colab, extract:
```python
import zipfile, shutil
shutil.rmtree('drive/My Drive/A2', ignore_errors=True)
with zipfile.ZipFile('drive/My Drive/A2.zip', 'r') as z:
    z.extractall('drive/My Drive/')
```

### Path configuration
The notebook's `GOOGLE_DRIVE_PATH_AFTER_MYDRIVE` must match the actual
extraction path. List Drive root to find it:
```python
import os
print(os.listdir('drive/My Drive'))
# → ['A2', 'Colab Notebooks', ...]
# Then set: GOOGLE_DRIVE_PATH_AFTER_MYDRIVE = 'A2'
```

**PITFALL**: `None` as default value causes `TypeError: join() argument must be str`.
Always set it explicitly before running.

### When files don't update (stale Colab cache)
If re-uploading doesn't fix the issue, directly overwrite the file in Colab:
```python
path = 'drive/My Drive/A2/linear_classifier.py'
with open(path, 'r') as f:
    content = f.read()
content = content.replace("old_pattern", "new_pattern")
with open(path, 'w') as f:
    f.write(content)
```
Then **Runtime → Restart session** and re-run from the beginning.

---

## 9. Models save to Google Drive, not Colab local

EECS 498 notebooks save `.pt` files to `os.path.join(GOOGLE_DRIVE_PATH, 'xxx.pt')`.
After running, check **Google Drive** (not Colab local) for model files:
```python
import os
print(os.listdir(GOOGLE_DRIVE_PATH))  # check Drive, not os.listdir('.')
```

---

## 10. Submission structure: don't replace with self-contained notebook

EECS 498 autograder expects a **specific file structure**:
- Original `.ipynb` notebooks (with outputs)
- `.py` implementation files
- `.pt` model checkpoints

Creating a self-contained notebook that has all code inline **does NOT work**
for submission — the autograder imports from the `.py` files and checks the
notebook structure. Always fix the original notebooks + `.py` files instead.

### Pre-configuration when repackaging notebooks

When fixing notebooks for upload, pre-set these values so the user doesn't
have to debug paths:
```python
# In each notebook, fix the path cell:
GOOGLE_DRIVE_PATH_AFTER_MYDRIVE = 'A2/A2'  # match zip structure
```

And fix autoreload cells by replacing with a no-op comment.

---

## 11. User preference: code-writing vs concept-explaining

When a user explicitly asks to "完成" (complete) an assignment and especially
when they repeat the request after being offered explanations, they want the
**actual code written**, not conceptual guidance. Provide the implementation
with inline comments explaining the logic. This applies even to graded
assignments when the user explicitly insists — the preference override is the
user's repeated explicit request.

Pattern: offer concepts once → user insists → write the code with comments.
