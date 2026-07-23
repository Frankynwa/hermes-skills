# Open WebUI on Windows — Service Lifecycle

## Process Discovery

Find which Python process is OWUI (vs Hermes gateway or other services):

```bash
# Git-bash:
MSYS_NO_PATHCONV=1 wmic process where "name='python.exe' or name='pythonw.exe'" get processid,commandline

# Look for the line containing "open_webui" in CommandLine:
# python.exe  ... -c "from open_webui import app; app(['serve', '--host', '127.0.0.1', '--port', '3000'])"
# pythonw.exe ... -c "from open_webui import app; app(['serve', '--host', '127.0.0.1', '--port', '3000'])"
```

## Stopping OWUI

```bash
# MSYS_NO_PATHCONV=1 is REQUIRED — otherwise /PID gets path-translated
MSYS_NO_PATHCONV=1 taskkill /F /PID <pid>
```

**Pitfall**: Without `/F` (force), `taskkill` will fail with "只能强制终止此进程" (can only force-terminate). OWUI's Python process requires force-kill.

## Starting OWUI

### Correct Launch Syntax

Open WebUI uses **typer** CLI. There is NO `__main__.py`, so `python -m open_webui` fails with:
```
No module named open_webui.__main__; 'open_webui' is a package and cannot be directly executed
```

The `serve` subcommand is registered on the typer app object. Use `-c` form:

```bash
MSYS_NO_PATHCONV=1 PYTHONPATH="" DATA_DIR="C:\Users\<user>\open-webui\data" \
  "C:\Users\<user>\AppData\Local\Programs\Python\Python312\pythonw.exe" \
  -c "from open_webui import app; app(['serve', '--host', '127.0.0.1', '--port', '3000'])"
```

### Critical: PYTHONPATH Must Be Cleared

Hermes sets `PYTHONPATH` to its own venv (`hermes-agent/venv/Lib/site-packages`). Without `PYTHONPATH=""`, Python 3.12 will load Hermes' `pydantic_core` and fail with:
```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
```

### DATA_DIR Configuration

`DATA_DIR` is read from environment in `open_webui/env.py` (line 216):
```python
DATA_DIR = Path(os.getenv('DATA_DIR', BACKEND_DIR / 'data')).resolve()
```

If unset, defaults to `<open_webui_package>/data/`.

## Data Directory Migration

When moving OWUI data to a new location:

1. **Find and stop OWUI** (see above)
2. **Copy data directory**:
   ```bash
   mkdir -p "C:\Users\<user>\open-webui"
   cp -r "C:\Users\<user>\AppData\Local\Programs\Python\Python312\Lib\site-packages\open_webui\data" \
         "C:\Users\<user>\open-webui\data"
   ```
3. **Verify**: `du -sh` and `find -type f | wc -l` on both source and dest
4. **Restart with new DATA_DIR** (see above)
5. **Verify service**: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000` → expect `200`

## Health Check

```bash
# Quick check:
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000
# 200 = running, 000/code 7 = not running or still starting

# Process check:
tasklist | grep -i pythonw
# Look for pythonw.exe with ~600-800 MB memory (OWUI is heavy)
```

## Common Pitfalls Summary

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| PYTHONPATH pollution | `ModuleNotFoundError: pydantic_core._pydantic_core` | `PYTHONPATH=""` |
| No `__main__.py` | `No module named open_webui.__main__` | Use `-c "from open_webui import app; app([...])"` |
| MSYS path translation | `无效参数/选项 - 'C:/Program Files/Git/PID'` | `MSYS_NO_PATHCONV=1` |
| Missing `/F` on taskkill | `只能强制终止此进程` | Add `/F` flag |