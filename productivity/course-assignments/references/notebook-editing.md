# Programmatic Jupyter Notebook Editing

When a Colab notebook has many code cells with TODO stubs, editing them
one-by-one with `patch` calls is inefficient. Instead, use this pattern:

## Pattern: JSON-based batch editing

### Step 1: Build a cell ID index

Use `execute_code` to load the notebook JSON and map cell IDs to indices:

```python
import json

with open("notebook.ipynb") as f:
    nb = json.load(f)

cells_by_id = {}
for i, c in enumerate(nb["cells"]):
    cells_by_id[c.get("id", "")] = i
```

### Step 2: Write source files to /tmp

Use `write_file` to write each code block as a separate .py file under
`/tmp/assignment_src/`. This avoids triple-quote escaping issues in
`execute_code` and preserves Unicode characters correctly.

**Critical: Do NOT use raw triple-quoted strings inside `execute_code`**
for Python source that itself contains `"""` docstrings. The inner
triple quotes break the outer string. Instead, use `write_file` directly
or write files individually.

### Step 3: Read and inject

```python
UPDATES = {
    "cell_id_1": ("prefix\n", "source_file_1.py"),
    "cell_id_2": ("%%writefile path/to/file.py\n", "source_file_2.py"),
}

for cell in nb["cells"]:
    cid = cell.get("id", "")
    if cid in UPDATES:
        prefix, src_file = UPDATES[cid]
        with open(f"/tmp/assignment_src/{src_file}") as f:
            content = f.read()
        cell["source"] = [prefix + content]
```

For cells that use `%%writefile`, the prefix is the magic command line.
For non-writefile cells, the source list should mirror the original format.

### Step 4: Clear outputs and save

```python
# Clear all stale outputs for clean submission
for cell in nb["cells"]:
    if "outputs" in cell:
        cell["outputs"] = []
    if "execution_count" in cell:
        cell["execution_count"] = None

with open("notebook.ipynb", 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
```

## Verification

After modifying the notebook:
1. Check for remaining TODOs: `grep -c "TODO"` in the JSON
2. Verify key features exist: search for function names, imports, fixtures
3. Run syntax check: write source files to a temp directory and compile them
4. Set up the project structure and run `pytest` locally if possible

## Pitfalls

- **Triple-quote escaping in execute_code**: When embedding Python source
  that contains `"""..."""` docstrings inside an `execute_code` block's
  own string, the quotes collide. Solution: write files with `write_file`
  tool instead.
- **Unicode in execute_code**: Chinese characters, emojis, and other
  non-ASCII chars may be mangled when passed through `execute_code`. Use
  `write_file` for files containing Unicode.
- **Cell source format**: Notebook cells store source as `list[str]`, not
  a single string. When replacing, either use a single-element list
  `["code"]` or split on newlines with trailing `\n`.
- **Notebook JSON compactness**: Use `indent=1` for readability (not too
  verbose, not minified). Use `ensure_ascii=False` for Unicode.
