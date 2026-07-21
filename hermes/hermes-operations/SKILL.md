---
name: hermes-operations
description: "Operate, configure, and maintain Hermes Agent — model benchmarking, web UI integration, skill library management (sync, audit, cleanup), and memory optimization. Use when choosing models, connecting web frontends, syncing skills across devices, auditing/cleaning skills, or pruning memory."
tags: [hermes, operations, benchmarking, web-ui, skills, maintenance]
related_skills: [hermes-agent, smart-model-switch, hermes-git-upgrade-with-patches]
---

# Hermes Operations

Day-to-day operations for Hermes Agent — model selection, web frontend integration, and skill library health.

## Part 1: Model Benchmarking

Compare LLM models on their actual Hermes Agent performance — tool calling accuracy, chain execution, error recovery, coding, and complex multi-skill workflows.

### Profile Isolation

Each model needs its own Hermes profile:
```bash
hermes profile create bench-<model-name>
```

**CRITICAL**: Profiles do NOT auto-read `~/.hermes/.env`. Symlink:
```bash
ln -sf ~/.hermes/.env ~/.hermes/profiles/<name>/.env
```
Without this, all tasks fail with 401. This is the #1 setup failure.

### Test Phases

**Phase 1: Agent Reliability** (6 tasks)
| Dimension | Weight | Tests |
|-----------|--------|-------|
| Simple tool calling | 20% | read, write, search, terminal, patch |
| Chained tool calling | 25% | Multi-step workflows |
| Error recovery | 10% | Retry, adapt, report on failure |
| Coding tasks | 20% | Write code, find bugs, refactor |
| Instruction following | 10% | Multi-constraint prompts |
| Skill usage / complex workflow | 15% | Load/chain skills |

**Phase 2: Model Core Capability** (10 tasks)
| Dimension | Weight | Tests |
|-----------|--------|-------|
| 中文能力 | 15% | AI text rewriting, cultural metaphor |
| 代码能力 | 25% | Algorithm implementation, refactoring |
| 文本能力 | 20% | Structured summarization, creative writing |
| 复杂推理 | 25% | Multi-step logic, requirement decomposition |
| 上下文能力 | 15% | Long document retrieval, cross-step memory |

### API Failure Detection

Hermes CLI returns exit code 0 even on API failures. Always scan stdout/stderr for:
```
Insufficient account balance / API call failed after / 401 / 403 / 429 / 500
```

### Cache Hit Rate Analysis

- **DeepSeek V4 Pro**: Persistent prefix cache, 99% hit on first call, 120x discount
- **Qwen3.7 Max (DashScope)**: Ephemeral 5-min TTL, 0% cross-session

### Known Model Characteristics

| Model | Strengths | Weaknesses |
|-------|-----------|------------|
| Qwen3.7 Max | Fastest, most reliable, good coding | Most expensive (7x DeepSeek) |
| DeepSeek V4 Pro | Cheapest, best coding detail | Slowest (2x), may hang on complex chains |
| MiMo 2.5 Pro | Balanced speed, good tool calling | Fewer community reports |

## Part 2: Web UI Integration

Hermes connects to external web frontends via the **API Server** platform adapter, which exposes an OpenAI-compatible HTTP API.

### Supported Frontends

| Frontend | Compatibility | Notes |
|----------|--------------|-------|
| **Open WebUI** | Good (75%) | File upload needs workarounds |
| **LobeChat** | Good | Multimodal content array handled |
| **LibreChat** | Good | Session continuity via headers |
| **AnythingLLM** | Good | Text-only; RAG layers on top |
| **NextChat / ChatBox** | Basic | Pure chat, limited tool visibility |

### Setup

```bash
# In ~/.hermes/.env:
API_SERVER_ENABLED=true
API_SERVER_KEY=your-secret-key

# Start gateway
hermes gateway run  # or: hermes gateway install && hermes gateway start
```

Frontend config:
```
URL: http://localhost:8642/v1
API Key: (your API_SERVER_KEY)
Model: hermes-agent
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/chat/completions` | POST | Main chat (OpenAI-compatible) |
| `/v1/responses` | POST | Stateful responses API |
| `/v1/models` | GET | List models |
| `/v1/capabilities` | GET | Feature discovery |
| `/v1/runs` | POST | Async run (returns 202 + run_id) |
| `/v1/runs/{id}/events` | GET | SSE event stream |
| `/health` | GET | Health check |

### Session Continuity

`X-Hermes-Session-Id` header reuses sessions. `X-Hermes-Session-Key` for long-term memory scoping.

### Known Limitations

1. **File upload NOT supported** — only text and image_url parts accepted
2. **Tool progress not visible by default** — custom `hermes.tool.progress` SSE events not recognized by frontends. **Use the proxy (below) to translate them.**
3. **Dual context conflict** — frontends send full history, Hermes maintains internal state
4. **No slash commands** — `/new`, `/model`, `/skill` require CLI
5. **Simple auth** — Bearer token only, all requests share same instance

### Tool Progress Proxy (`hermes-proxy.py`)

A Python proxy (at `~/.open-webui/hermes-proxy.py`) sits between Open WebUI and Hermes, translating `hermes.tool.progress` SSE events into visible content chunks that Open WebUI can display:

**What you see:** emoji + tool name + status, e.g., `🔍 调用 search_files` → `🔍 search_files 完成`

**What is translated:**
| Upstream Event | Proxy Output |
|---|---|
| `event: hermes.tool.progress` with `status: running` | Content chunk: `🔧 [tool_name] label` |
| `event: hermes.tool.progress` with `status: completed` | Content chunk: `🔧 tool_name 完成` |
| `event: hermes.reasoning` | Content chunk: `💭 {thinking text}` |

**Architecture:**
```
Open WebUI → proxy(:8643) → Hermes API(:8642)
```

The proxy uses `aiohttp`. Tool emojis are defined in `TOOL_EMOJI` dict. It handles SSE character-by-character, matches `event:` lines to set context, then translates matching `data:` payloads.

**SSE Heartbeat (browser keepalive):** macOS Safari/Chrome aggressively throttle background tabs, causing SSE connections to drop and Open WebUI to show "重新连接中". The proxy sends `: heartbeat\n\n` (SSE comment, invisible to clients) every 5 seconds to keep TCP alive. Uses `asyncio.Lock` to prevent heartbeat vs data write races.

**Launchd plist:** `~/Library/LaunchAgents/com.hermes.tool-proxy.plist`
```xml
ProgramArguments: /opt/anaconda3/bin/python3, ~/.open-webui/hermes-proxy.py
WorkingDirectory: ~/.open-webui
KeepAlive: true
RunAtLoad: true
```
StandardOutPath/StandardErrorPath point to `~/.open-webui/hermes-proxy.{stdout,stderr}.log`.

**Common launchd failure:** exit code 1 = port 8643 already in use. Kill the old manual process first, then `launchctl kickstart`.

**Verification:**
```bash
# Check proxy is running
curl http://127.0.0.1:8643/health  # {"status": "ok", "platform": "hermes-agent"}

# Test tool progress translation
curl -s -N --max-time 30 http://127.0.0.1:8643/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hermes...2026" \
  -d '{"model":"mimo-v2.5-pro","messages":[{"role":"user","content":"列出 /tmp"}],"stream":true}'
# Look for: "🔍 调用 search_files" and "🔍 search_files 完成" in output
```

**Debugging tool progress NOT appearing in Open WebUI:**
1. Verify proxy is running and reachable (health check above)
2. Verify tool translation works (curl test above)
3. Check Open WebUI model URL: must be `http://127.0.0.1:8643/v1`, NOT `http://127.0.0.1:8642/v1`. If pointing to 8642 directly, tool progress events are raw SSE events that Open WebUI ignores.
4. Check Open WebUI SQLite config: `sqlite3 ~/.open-webui/webui.db "SELECT json_extract(data, '$.openai.url') FROM config LIMIT 1;"`

**Thinking/reasoning visibility:** Hermes emits `hermes.reasoning` SSE events for models that support thinking mode. The proxy translates them to `💭`-prefixed content chunks. For MiMo, thinking may not flow through this path; check if the model emits reasoning as SSE events vs inline in content.

**Restart after code changes:**
```bash
launchctl kickstart -k gui/$(id -u)/com.hermes.tool-proxy
curl -s http://127.0.0.1:8643/health  # verify
```

## Part 3: Open WebUI Operations

Open WebUI runs as a launchd service alongside Hermes. It stores ALL config in SQLite, not .env files.

### Config Location
```
Data dir: ~/.open-webui/
Database: ~/.open-webui/webui.db (config table, JSON in `data` column)
JWT key:  ~/.webui_secret_key
Launchd:  ~/Library/LaunchAgents/ai.openwebui.server.plist
Logs:     ~/.open-webui/server.log, server.error.log
```

### Reading Config
```bash
sqlite3 ~/.open-webui/webui.db "SELECT data FROM config WHERE id=1;" | python3 -m json.tool
```

### Modifying Config (programmatic)
```python
import json
from hermes_tools import terminal
r = terminal("sqlite3 ~/.open-webui/webui.db \"SELECT data FROM config WHERE id=1;\"")
data = json.loads(r['output'])
# modify data['openai'], data['ollama'], etc.
new_json = json.dumps(data).replace("'", "''")
terminal(f"sqlite3 ~/.open-webui/webui.db \"UPDATE config SET data = json('{new_json}'), updated_at = CURRENT_TIMESTAMP WHERE id = 1;\"")
```

### Security Hardening Checklist

| Issue | Fix | Command |
|-------|-----|---------|
| JWT key too short (< 32 bytes) | Regenerate 64-char hex | `openssl rand -hex 32 > ~/.webui_secret_key` |
| Binding to `0.0.0.0` | Add `WEBUI_HOST=127.0.0.1` to plist | Edit `~/Library/LaunchAgents/ai.openwebui.server.plist` |
| CORS `*` | Add `CORS_ALLOW_ORIGIN=http://localhost:8080` to plist | Edit plist EnvironmentVariables |
| Empty API key endpoint | Disable or remove from config | SQLite update on config table |
| Ollama endpoint (if no Ollama) | Remove from config | SQLite update: `data.pop('ollama', None)` |

### Restarting
```bash
# Restart and verify
launchctl kickstart -k gui/$(id -u)/ai.openwebui.server
sleep 60  # embedding model (all-MiniLM-L6-v2) takes 30-60s to load
curl -s http://127.0.0.1:8080/health
```

### Common Startup Warnings (all benign after fixing)
- `InsecureKeyLengthWarning` → JWT key too short
- `CORS_ALLOW_ORIGIN IS SET TO '*'` → needs plist env var
- `embeddings.position_ids UNEXPECTED` → MiniLM architecture warning, ignore
- `Couldn't find ffmpeg` → `brew install ffmpeg`
- `resource_tracker: leaked semaphore` → Python multiprocessing cleanup, ignore

### Deep Audit Procedure
When user asks to audit all services, run 3 parallel subagents:
1. **Hermes**: gateway.log errors/warnings, .env permissions, config.yaml settings, state.db size, memory drift
2. **Open WebUI**: webui.db config, server logs, JWT key length, CORS, binding, vector_db orphans
3. **Feishu**: pairing config duplicates, WebSocket churn in gateway.log, seen-message-ID cache size, channel_directory.json

Output format: priority-ranked table with 🔴🟡🟢 severity.

## Part 4: Skill Library Management

### Installation Verification (MANDATORY)

**NEVER trust "installed successfully". ALWAYS verify:**
```bash
ls -la ~/.hermes/skills/<category>/<skill-name>/
wc -c ~/.hermes/skills/<category>/<skill-name>/SKILL.md
head -5 ~/.hermes/skills/<category>/<skill-name>/SKILL.md
```

### Usefulness Evaluation

| Category | Definition | Action |
|----------|------------|--------|
| High frequency | Used weekly+ | Always keep |
| Occasional | Monthly, specific scenarios | Keep |
| No use case | Doesn't match user domains | Recommend delete |
| Uncertain | Might be useful | Ask user |

### Security Audit for Community Skills

| Risk | Signals | Action |
|------|---------|--------|
| Safe | Pure prompt engineering, known author | Install |
| Low | Local-only scripts, no network | Install with note |
| Medium | Localhost calls, unknown author | Review scripts first |
| High | External URL calls, sudo, eval | Manual review required |

```bash
# Scan for dangerous patterns
grep -rn "curl\|wget\|exec\|eval\|subprocess\|os.system\|rm -rf\|sudo" \
  ~/.hermes/skills/<category>/<skill-name>/SKILL.md
```

### Bulk Cleanup

```bash
find ~/.hermes/skills/ -name "SKILL.md" | wc -l          # total
find ~/.hermes/skills/ -type d -empty                      # empty dirs
find ~/.hermes/skills/ -name "SKILL.md" -size 0            # 0-byte
grep -rl "404: Not Found\\|TODO" ~/.hermes/skills/*/SKILL.md 2>/dev/null
```

### Skills Sync via Git (Cross-Device)

Hermes skills are plain files in `~/.hermes/skills/` — version them with git and push to GitHub for seamless sync between devices.

**CRITICAL: Only sync locally-created skills, NOT bundled or hub-installed ones.** Pushing 200+ bundled skills to a personal repo is clutter. The user expects only skills Hermes created from their local experience.

#### Distinguishing Skill Sources

Skills come from three sources. Know which is which before syncing:

| Source | Location | How to identify |
|--------|----------|-----------------|
| **Bundled** | Shipped with Hermes | `cut -d: -f1 ~/.hermes/skills/.bundled_manifest` |
| **Hub-installed** | `hermes skills install` | `grep 'INSTALL' ~/.hermes/skills/.hub/audit.log \| awk '{print $3}'` |
| **Locally-created** | `skill_manage` tool or `~/.agents/skills/` | Everything NOT in the two lists above |

```bash
# One-liner to list locally-created skills
comm -23 \
  <(find ~/.hermes/skills -name 'SKILL.md' -not -path '*/.archive/*' -not -path '*/.hub/*' -exec sed -n '/^---$/,/^---$/p' {} \; | grep '^name:' | sed 's/^name: *//' | sort -u) \
  <((cut -d: -f1 ~/.hermes/skills/.bundled_manifest; grep 'INSTALL' ~/.hermes/skills/.hub/audit.log | awk '{print $3}') | sort -u)
```

#### Initial Setup (Device A)

```bash
cd ~/.hermes/skills

# 1. Create .gitignore — see references/skills-gitignore.txt
# 2. Init + commit
git init
git branch -m main
git add -A
git commit -m "init: hermes skills collection"

# 3. Create GitHub repo (private), push
git remote add origin git@github.com:<user>/hermes-skills.git
git push -u origin main
```

#### Clone on Device B

```bash
# Backup existing skills
mv ~/.hermes/skills ~/.hermes/skills.bak

# Clone
git clone git@github.com:<user>/hermes-skills.git ~/.hermes/skills
```

#### Daily Sync

```bash
# Pull latest from other device
cd ~/.hermes/skills && git pull

# After making changes
cd ~/.hermes/skills && git add -A && git commit -m "..." && git push
```

#### .gitignore Essentials

Must exclude internal state files, hub caches, archives, and build artifacts:

```gitignore
# Hermes internal files
.usage.json
.usage.json.lock
.curator_state
.curator_backups/
.bundled_manifest
.hub/

# Archived (old versions, not needed for sync)
.archive/

# macOS
.DS_Store
**/.DS_Store

# Python
__pycache__/
**/__pycache__/
*.pyc
```

**Pitfall (pycache)**: `__pycache__/` directories in `pptx/`, `docx/`, `xlsx/` `scripts/office/validators/` contain `.pyc` files. If they were already staged before `.gitignore` was added, they remain tracked — use `git rm --cached $(git ls-files '**/__pycache__/*')` to clean them out after adding the gitignore, then amend.

**Pitfall (symlinks to `~/.agents/skills/`)**: Hermes often creates locally-authored skills in `~/.agents/skills/` and symlinks them into `~/.hermes/skills/`. Git tracks symlinks (mode 120000) but ONLY stores the link path — NOT the target content. When another device clones the repo, these become dangling symlinks and the skill is effectively lost. **Before committing, replace ALL symlinks with real directory copies**:

```bash
cd ~/.hermes/skills

# 1. Find all symlinks at the skills root
find . -maxdepth 1 -type l

# 2. Replace each with a real copy
for link in $(find . -maxdepth 1 -type l -exec basename {} \;); do
  git rm --cached "$link" 2>/dev/null   # unstage the symlink
  rm "$link"                              # remove symlink
  cp -a ~/.agents/skills/"$link" "$link" # copy real content
done

# 3. Commit the replacement
git add -A
git commit -m "fix: replace symlinks with real directories for cross-device sync"
```

Verify post-replacement: `find . -maxdepth 1 -type l | wc -l` should return 0.

#### China GFW Workaround

GitHub is blocked on mainland networks. The repo can be created and the commit staged locally, but `git push` requires a proxy/VPN. Options:

1. **SSH proxy**: add to `~/.ssh/config`:
   ```
   Host github.com
       ProxyCommand nc -X connect -x 127.0.0.1:7890 %h %p
   ```
2. **HTTPS proxy**: `git config http.proxy socks5://127.0.0.1:7890`
3. **Push when VPN is active** — the local repo stays ready

See `chinese-git-workflow` skill for Gitee mirror alternatives.

## Part 5: Cron Job Failure Diagnosis

When cron jobs fail, the diagnosis path is non-obvious. Follow this sequence:

### Symptom: All Cron Jobs Failing Simultaneously
If 3+ jobs all show `last_status: "error"` at the same time, the root cause is almost always **provider-level** (API balance/auth), not individual job logic.

### Step 1: Check cron output for the error
```bash
# Latest output for each job
for dir in ~/.hermes/cron/output/*/; do
  job_id=$(basename "$dir")
  latest=$(ls -t "$dir"*.md 2>/dev/null | head -1)
  [ -n "$latest" ] && echo "[$job_id] $(grep 'Error' "$latest" | tail -1)"
done
```

### Step 2: Check gateway.error.log for the FULL chain
The cron output only shows the final error. The gateway error log shows the **entire fallback chain**:
```bash
tail -100 ~/.hermes/logs/gateway.error.log | grep -i "cron\|402\|balance\|fallback\|retry"
```

**Critical pattern**: If you see the primary provider fail (402), then fallback provider ALSO fail (402), BOTH providers are out of balance. The user may know about one but not the other — always report both.

### Step 3: Verify provider balance
```bash
# Check which providers are configured
grep -A3 'provider:' ~/.hermes/config.yaml | head -20
grep 'fallback' ~/.hermes/config.yaml -A3
```

### Known Failure Patterns
| Pattern | Meaning |
|---------|---------|
| `HTTP 402: Insufficient Balance` on primary + fallback | Both providers need topping up — BUT first verify with `curl` manually; if APIs return 200, the issue is likely empty model name (see below) |
| `HTTP 401` on one provider | API key expired/invalid for that provider |
| `HTTP 429` | Rate limited, not a balance issue — wait or reduce concurrency |
| Job runs but produces no output | Script error, not API error — check the script separately |
| `last_status: "error"` but no Error in output file | Gateway killed the job (timeout) before it wrote output |

### Cron Output File Locations
- Job outputs: `~/.hermes/cron/output/<job-id>/<timestamp>.md`
- Job config: `~/.hermes/cron/jobs.json`
- Gateway logs: `~/.hermes/logs/gateway.log` and `gateway.error.log`

### Gateway Restart Race Condition (Delivery Failures)
When cron jobs succeed (`last_status: "ok"`) but `last_delivery_error` shows `"cannot schedule new futures after interpreter shutdown"`, this means the job completed during a gateway restart. The delivery system tried to send the message after the Python interpreter was already shutting down.

This is **transient** — the next scheduled run will deliver normally. To manually re-deliver, trigger the job with `cronjob(action='run')` after the gateway is fully up.

### Hidden Bug: Empty Model Name (402 misdiagnosis)
When ALL cron jobs fail with 402 but `curl` tests return 200, the real cause is often an **empty model name** in the API call. The scheduler resolves model from config.yaml:

```python
# scheduler.py line ~1432
model = _model_cfg.get("default") or _model_cfg.get("model") or model
```

If config.yaml uses `model: {model: "xxx", provider: "yyy"}` (no `default` key), the old code (`_model_cfg.get("default", model)`) returned empty string. This sent an empty model to the provider → HTTP 400 "Param Incorrect" → fallback to deepseek → 402. **Looks like a balance issue but isn't.**

**Diagnosis**: Check `gateway.error.log` for `model=` (empty) in the xiaomi/primary error line:
```bash
grep "model=$\|model= " ~/.hermes/logs/gateway.error.log | tail -5
```

**Fix**: Patch `cron/scheduler.py` line to also check `model` key (not just `default`):
```python
model = _model_cfg.get("default") or _model_cfg.get("model") or model
```

After patching, restart the gateway for the fix to take effect:
```bash
hermes gateway restart
```
Then manually trigger a job to verify: `cronjob(action='run', job_id='<id>')`.

## Part 6: Memory Management

Hermes memory is injected into every turn. When usage exceeds 90%, older entries get truncated, risking loss of critical preferences. Proactive pruning prevents this.

### Checking Usage

Memory tool reports usage % and char count on every operation. Also check current state:
```bash
grep -o '"usage": "[^"]*"' ~/.hermes/state.db 2>/dev/null || echo "check via memory tool"
```

### Systematic Prune Workflow

When memory approaches 90%+ (or user requests cleanup):

1. **List all entries** — call `memory` tool without action to see current state
2. **Sort by verbosity** — identify the longest entries (these give biggest returns per edit)
3. **Shorten, don't delete** — compress verbose entries without losing core facts:
   - Collapse multi-rule lists into comma-separated form
   - Remove redundant qualifiers ("在", "含", "等")
   - Drop secondary details that can be re-discovered (file counts, version numbers of frontend frameworks, etc.)
   - Keep: paths, API endpoints, IDs, credentials, personal info, active project state
4. **Batch edits** — 4-8 entries per session, check usage % after each batch
5. **Target**: below 85% is healthy, below 80% is ideal for headroom
6. **Verify**: re-read memory with `memory` tool after each batch to confirm changes stuck

### What NOT to prune

- Personal info (name, birth date, student ID)
- API keys and endpoint URLs
- Chat platform IDs (open_id, user-id)
- Active project paths and current state
- User communication preferences

### What to prune aggressively

- Secondary framework details (e.g., "Vue3+Vite非Bootstrap")
- Redundant qualifiers ("含", "在", "等")
- Verbose workflow descriptions that belong in skills, not memory
- Historical data that's re-derivable from project files

## Part 7: Security & Maintenance Hardening

### .env File Permissions
Always `chmod 600` — default may be `644` (world-readable). Contains API keys for all providers.
```bash
chmod 600 ~/.hermes/.env
ls -la ~/.hermes/.env  # verify: -rw-------
```

### GitHub Token Exposure
MCP server config in `config.yaml` may contain plaintext tokens (`ghp_...`). Prefer:
- Move token to `.env` as `GITHUB_TOKEN`
- Reference via `key_env` in MCP config (if supported)
- Or use `gh auth login` for CLI-based auth

### state.db Maintenance
Grows unbounded with session history. Key settings:
```yaml
sessions:
  auto_prune: true        # enable automatic cleanup
  retention_days: 30      # keep 30 days (was 90)
  vacuum_after_prune: true
  min_interval_hours: 24
```
Manual VACUUM (doesn't shrink if data is still there, but reclaims deleted pages):
```bash
sqlite3 ~/.hermes/state.db "VACUUM;"
```

### Gateway Timeout Tuning
Default 1800s (30 min) is too high — DeepSeek stream issues can cause responses to hang for 114+ minutes. Recommended:
```yaml
agent:
  gateway_timeout: 600          # 10 min hard limit
  gateway_timeout_warning: 300  # 5 min warning
```

### Tirith Security Engine
```yaml
security:
  tirith_fail_open: false  # deny on failure, not allow
```
Default `true` means if the policy engine crashes, all actions are permitted.

### DeepSeek Stream Instability
Common error pattern in gateway.log:
```
RemoteProtocolError: peer closed connection without sending complete message body
```
Streams hang for 900-1272s before being killed. Mitigation:
- Lower `gateway_timeout` (above)
- DeepSeek has persistent prefix cache (99% hit rate, 120x discount) — worth the instability for cost
- MiMo/Xiaomi as primary avoids this issue

### Feishu WebSocket Churn
Common disconnect causes:
1. **Local proxy down** (e.g., `127.0.0.1:7897`) — 500+ errors when proxy is expected but not running
2. **DNS resolution failures** — bursts of `NameResolutionError` for `open.feishu.cn`
3. **Keepalive ping timeout** — Feishu server stops responding to pings

The system auto-reconnects within 15-60s. Proxy errors dominate — if not using a proxy, ensure no proxy env vars are set.

## Pitfalls

1. **Profile .env not symlinked** → 401 on all tasks
2. **`hermes chat -q` takes prompt string, NOT `-m <file>`**
3. **Long prompts hit shell ARG_MAX** → use `subprocess.run` list form
4. **Task timeout too short** → use 600s for chained/capability tasks
5. **Base URL changes for providers** → verify endpoint with curl before benchmarking
6. **Confusing "usable" with "useful"** — evaluate against user's actual workflows
7. **Trusting batch install output** — verify files on disk
8. **Deleting skills without user confirmation** — present findings, let user decide
9. **`patch` tool on YAML may silently fail** — the tool reports success but changes don't persist. Use `sed -i ''` for config.yaml edits, then verify with `grep`.
10. **HTTP 402 on cron ≠ always balance** — test with `curl` first. If 200 from curl but 402 in cron, it's an empty model name from config structure mismatch (see Part 5 "Hidden Bug").
10. **Memory tool loop on char limit** — if a memory entry exceeds 2200 chars, agent retries 5-7 times before giving up. Truncate entries proactively.
11. **Open WebUI restart needs 60s wait** — the all-MiniLM-L6-v2 embedding model takes 30-60 seconds to load. Health checks immediately after restart will fail with connection refused.
12. **Open WebUI config is in SQLite, not .env** — the `config` table has a JSON `data` column. Don't look for `.env` files; query `webui.db` directly.
13. **macOS "Resource deadlock avoided" on files with `@` xattr**
14. **GFW blocks git operations** — `hermes update` (which runs `git fetch` + `git checkout`) fails on mainland China networks because GitHub is blocked. Before spending time on proxy workarounds, check: (a) current version (`hermes --version`), (b) latest tag on GitHub (`git ls-remote --tags` via proxy if available), (c) version gap. If the gap is small (< 10 commits), skip the upgrade — Hermes doesn't have critical patches that often. If the upgrade is needed, use the `hermes-git-upgrade-with-patches` skill which has proxy-aware workflows. — `cat`, `dd`, `xxd`, and even Python `open()` all fail with `OSError: Resource deadlock avoided` on files that have extended attributes (shown by `ls -la` as `@` suffix). This hits Desktop/Documents files on macOS. **Workaround**: `perl -pe '' /path/to/file` bypasses the restriction and reads the content normally. Use this when any file read tool fails with this specific error.

## Reference Files

- `references/benchmark-2026-05-24.md` — Round 1 benchmark results
- `references/capability-tasks-reference.md` — Round 2 task design and scoring rubric
- `references/xiaomi-mimo-api.md` — MiMo provider endpoints and gotchas
- `references/caching-models.md` — Cache hit rate analysis
- `references/api-server-source-analysis.md` — API Server code-level findings
- `references/deep-audit-2026-06-23.md` — Full audit: Hermes + Open WebUI + Feishu findings and fixes
- `scripts/run_bench.py` — Automated benchmark runner
