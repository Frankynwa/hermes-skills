---
name: hermes-git-upgrade-with-patches
description: Upgrade Hermes Agent (git checkout) while preserving local patches across major versions. Handles stash conflicts, moved files, and dependency updates.
triggers:
  - "hermes update"
  - "upgrade hermes"
  - "update hermes-agent"
---

# Hermes Git Upgrade with Local Patches

## When to Use
Hermes is installed as a git checkout at `~/.hermes/hermes-agent/` with local patches. Need to upgrade to latest while preserving patches.

## Steps

### 1. Backup and Extract Patches
```bash
cd ~/.hermes/hermes-agent
mkdir -p /tmp/hermes-backup-$(git describe --tags --abbrev=0 2>/dev/null || echo "pre-upgrade")
git diff HEAD -- <patched files> > /tmp/hermes-backup-*/local-patches.diff
cp <patched files> /tmp/hermes-backup-*/
```

### 2. Stash, Pull, Install
```bash
git stash save "local-patches-pre-upgrade"
git pull origin main
source venv/bin/activate
pip install -e .
```

### 3. Attempt Stash Pop
```bash
git stash pop
```

### 4. If Conflicts (Expected on Major Version Jumps)
Conflicts are normal when code is refactored between versions. Do NOT try to resolve merge conflicts in large files — it's error-prone.

The stash pop may **partially succeed**: some files merge cleanly while others conflict. After `git stash pop`:
- Files that merged cleanly are already staged with your patches applied — leave them alone.
- Only the conflicted files need to be reset.

```bash
# After a partial-merge stash pop:
# 1. Check which files merged cleanly vs conflicted
git status --short

# 2. Reset ONLY the conflicted files (unmerged ones)
git reset HEAD <conflicted files>
git checkout -- <conflicted files>

# 3. Drop the stash (all changes are either applied or discarded)
git stash drop
```

Example: `usage_pricing.py` merged cleanly but `gateway/run.py` and `run_agent.py` conflicted → reset only the two conflicted files, keep `usage_pricing.py`.

### 5. Re-apply Patches Manually
**Critical pitfall**: Patch target files may have moved. In v0.11.0→v0.14.0:
- `run_agent.py` compression code → `agent/conversation_compression.py`
- Always `grep` for unique strings from your patch to find the new location

Use the `patch` tool (find-and-replace) rather than git apply, since the context lines may have shifted.

**Technique for finding moved code**: Extract 2-3 unique strings from your saved diff (function names, distinctive comments, rare variable names) and grep across the repo:
```bash
# From the saved diff, pick unique strings like:
grep -rn "old_session_id.*uuid\|Reset flush cursor\|_last_flushed_db_idx" agent/ run_agent.py --include="*.py"
```
This finds the same logical code even when it moved to a different file or got refactored.

### 6. Verify
```bash
python -c "import py_compile; py_compile.compile('<file1>', doraise=True); ..."
git diff --stat HEAD
hermes --version
```

### 7. Restart Gateway
The running gateway uses the old code from before the pull. Restart for changes to take effect:
```bash
hermes gateway restart
```
Verify with `hermes gateway status` and check `~/.hermes/logs/gateway.log` for reconnection.

## Pitfalls
- `git stash pop` on large files (800+ KB like gateway/run.py) almost always conflicts across major versions — skip to manual re-apply
- Stash pop often **partially succeeds**: small files merge cleanly while large refactored files conflict. Use `git status --short` to identify which are `UU` (unmerged) vs `M` (merged). Only reset the `UU` files.
- Compression/session-split code moved from `run_agent.py` to `agent/conversation_compression.py` in v0.14.0 — grep to find it
- `pip install -e .` may downgrade some deps (e.g., openai 2.32→2.24) — check for compatibility
- `hermes --version` may show stale "commits behind" — ignore this after a fresh pull
- After upgrading, the running gateway must be restarted (`hermes gateway restart`) for changes to take effect
- v0.14.0 debloating: heavy platform SDKs (Slack/Matrix/Feishu) are now lazy-installed on first use. If a platform stops working after upgrade, run `pip install hermes-agent[all]`
