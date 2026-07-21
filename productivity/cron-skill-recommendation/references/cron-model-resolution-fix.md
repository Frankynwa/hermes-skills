---
name: cron-model-resolution-fix
category: devops
description: Fix for cron jobs failing with 402/400 errors when config.yaml model is a dict with 'model' key instead of 'default'
---

# Cron Model Resolution Bug Fix

## Problem
Cron jobs fail with `HTTP 400: Param Incorrect` (xiaomi) then `HTTP 402: Insufficient Balance` (deepseek fallback). Root cause: `cron/scheduler.py` only checks for `default` key in model config dict.

## Config Structure
```yaml
model:
  model: mimo-v2.5-pro
  provider: xiaomi
```

## Bug Location
`cron/scheduler.py` line ~1432:
```python
# BEFORE (broken):
model = _model_cfg.get("default", model)

# AFTER (fixed):
model = _model_cfg.get("default") or _model_cfg.get("model") or model
```

## Diagnosis Steps
1. Check `~/.hermes/logs/gateway.error.log` for `model= summary=HTTP 400`
2. If model is empty in the error, the config dict lookup is failing
3. Verify: `python3 -c "import yaml; cfg=yaml.safe_load(open('config.yaml')); print(type(cfg.get('model')), cfg.get('model'))"`
4. If model is a dict with `model` key (not `default`), this is the bug

## Fix
```bash
cd ~/.hermes/hermes-agent
# Edit cron/scheduler.py, find the line with _model_cfg.get("default", model)
# Replace with: _model_cfg.get("default") or _model_cfg.get("model") or model
hermes gateway restart
```

## Verification
```bash
# Trigger a cron job manually
hermes cron run <job_id>
# Check output file for absence of "FAILED" marker
ls -lt ~/.hermes/cron/output/<job_id>/*.md | head -1
```

## Pitfall
This patch is in the hermes-agent source code. It will be **overwritten by `git pull`**. The fix needs to be submitted as a PR upstream or re-applied after updates.
