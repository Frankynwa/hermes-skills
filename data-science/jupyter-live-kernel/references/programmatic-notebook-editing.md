# Programmatic .ipynb JSON Manipulation

When you need to programmatically modify a Jupyter notebook outside of a running
kernel — e.g., filling in template cells, replacing stubs with completed code,
or preparing a clean submission — manipulate the `.ipynb` JSON directly.

## Finding and Targeting Cells

Every cell in a notebook has an `id` field. Use it to target cells precisely:

```python
import json

with open("notebook.ipynb") as f:
    nb = json.load(f)

# Build index by cell id
cells_by_id = {c["id"]: i for i, c in enumerate(nb["cells"])}

# Modify a specific cell
for cell in nb["cells"]:
    if cell.get("id") == "target-cell-id":
        cell["source"] = ["new source code here\n"]
```

## Writing Cell Sources

Notebook sources are stored as **lists of strings** (one string per line). When
replacing source, split your content by newlines and append `\n` to each line
except the last:

```python
lines = content.split('\n')
cell["source"] = [l + '\n' for l in lines]
```

For `%%writefile` cells in Colab (which use a magic command prefix), include
the magic line as part of the source:

```python
cell["source"] = ["%%writefile path/to/file.py\n" + content]
```

## Clearing Outputs for Clean Submission

Most assignment notebooks should be submitted without stale outputs:

```python
for cell in nb["cells"]:
    if "outputs" in cell:
        cell["outputs"] = []
    if "execution_count" in cell:
        cell["execution_count"] = None

with open("notebook.ipynb", 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
```

## Unicode Pitfall with execute_code

When embedding Python source code containing **Unicode characters** (Chinese
text, emoji, accented characters) inside `execute_code`'s triple-quoted Python
strings, the characters can get mangled during transport. This manifests as
test assertions silently breaking because the expected strings lost their
Unicode characters.

**Workaround**: Use `write_file` to write the source files to disk first, then
use `execute_code` (or the notebook-update script) to read from those files.
The `write_file` tool preserves Unicode correctly.

```python
# ❌ BAD — emoji and CJK characters may be lost
execute_code("""
src = '''assert sanitize_username("用户 name") == "name"'''
""")

# ✅ GOOD — write to file first, then read
write_file("/tmp/tests.py", '''assert sanitize_username("用户 name") == "name"''')
```

## Local Test Verification

Before pushing, reconstruct the project structure and run pytest locally to
verify all tests pass:

```bash
mkdir -p /tmp/test_project/package_name/src /tmp/test_project/package_name/tests
touch /tmp/test_project/package_name/__init__.py
touch /tmp/test_project/package_name/src/__init__.py
touch /tmp/test_project/package_name/tests/__init__.py
# Copy source and test files into place
cd /tmp/test_project
python3 -m pytest package_name/tests/ -v
```

This catches issues like logic bugs in implementations and incorrect test
assertions that wouldn't be caught by syntax checks alone.
