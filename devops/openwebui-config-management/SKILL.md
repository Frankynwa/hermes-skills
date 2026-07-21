---
name: openwebui-config-management
description: "Manage Open WebUI configuration — SQLite-backed settings, model endpoints, and macOS launchd lifecycle."
tags: [openwebui, sqlite, macos, launchd, local-services]
triggers:
  - "Open WebUI settings, endpoints, model connections"
  - "add/remove Ollama or OpenAI endpoints in Open WebUI"
  - "Open WebUI not connecting to models"
  - "reset or modify Open WebUI config"
---

# Open WebUI Configuration Management

Open WebUI stores **all configuration in a SQLite database**, not in `.env` files or YAML configs. This is the critical fact most sessions miss.

## Architecture

| Component | Path |
|-----------|------|
| Data dir | `~/.open-webui/` |
| Database | `~/.open-webui/webui.db` |
| Config table | `config` (id=1, `data` JSON column) |
| Launchd plist | `~/Library/LaunchAgents/ai.openwebui.server.plist` |
| Server log | `~/.open-webui/server.log` |
| Error log | `~/.open-webui/server.error.log` |
| Embedding model | `all-MiniLM-L6-v2` (cached in `~/.cache/huggingface/hub/`) |
| Python venv | `~/openwebui-venv/` |
| Port | `127.0.0.1:8080` (localhost only, set via `WEBUI_HOST`) |

## Config Table Schema

```sql
CREATE TABLE config (
    id INTEGER PRIMARY KEY,
    data JSON NOT NULL,      -- all settings live here
    version INTEGER NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
);
```

The `data` JSON contains top-level keys: `version`, `ui`, `direct`, `models`, `openai`, `ollama`, etc.

## How to Modify Config

**Step 1: Read current config**
```bash
sqlite3 ~/.open-webui/webui.db "SELECT data FROM config WHERE id=1;"
```

**Step 2: Backup**
```bash
cp ~/.open-webui/webui.db ~/.open-webui/webui.db.bak.$(date +%Y%m%d_%H%M%S)
```

**Step 3: Modify JSON** (use Python for safe JSON manipulation)
```python
import sqlite3, json
conn = sqlite3.connect(db_path)
row = conn.execute("SELECT data FROM config WHERE id=1").fetchone()
data = json.loads(row[0])
# ... modify data ...
conn.execute("UPDATE config SET data=?, updated_at=CURRENT_TIMESTAMP WHERE id=1", (json.dumps(data),))
conn.commit()
```

**Step 4: Restart Open WebUI**
```bash
launchctl kickstart -k gui/$(id -u)/ai.openwebui.server
```

**Step 5: Verify** (embedding model takes ~60-90s to load)
```bash
sleep 15 && curl -s http://127.0.0.1:8080/health
```

## Endpoint Config Structure

The `openai` and `ollama` keys in `data` JSON control model endpoints:

```json
{
  "openai": {
    "enable": true,
    "api_base_urls": ["https://api.openai.com/v1", "http://127.0.0.1:8642/v1"],
    "api_keys": ["", "hermes-local-key-2026"],
    "api_configs": {
      "0": {"enable": true},
      "1": {"enable": true, "connection_type": "external", "auth_type": "bearer"}
    }
  },
  "ollama": {
    "enable": true,
    "base_urls": ["http://localhost:11434"],
    "api_configs": {"0": {"enable": true}}
  }
}
```

To remove a backend entirely: delete its top-level key from the JSON dict.

## Security Hardening

After initial setup, apply these security fixes:

### 1. JWT Secret Key (32+ bytes)
```bash
openssl rand -hex 32 > ~/.webui_secret_key
```
Default is 16 bytes → triggers `InsecureKeyLengthWarning` on every startup. Must be 32+ bytes for HMAC-SHA256 (RFC 7518 §3.2).

### 2. Bind to localhost
Add to launchd plist `EnvironmentVariables`:
```xml
<key>WEBUI_HOST</key>
<string>127.0.0.1</string>
```
Without this, defaults to `0.0.0.0` (all interfaces = LAN accessible).

### 3. Restrict CORS
Add to launchd plist `EnvironmentVariables`:
```xml
<key>CORS_ALLOW_ORIGIN</key>
<string>http://localhost:8080</string>
```
Default `*` allows any website to make cross-origin requests.

After all plist changes:
```bash
launchctl kickstart -k gui/$(id -u)/ai.openwebui.server
```

## Troubleshooting: Service Won't Start

1. **Check plist validity**: `plutil -lint ~/Library/LaunchAgents/ai.openwebui.server.plist`
2. **Check if already running**: `lsof -i :8080 | grep LISTEN` and `ps aux | grep open-webui | grep -v grep`
3. **Check launchd status**: `launchctl list | grep openwebui`
4. **Manual start fallback** (if launchd broken):
   ```bash
   DATA_DIR=~/.open-webui WEBUI_HOST=127.0.0.1 CORS_ALLOW_ORIGIN="http://localhost:8080;http://127.0.0.1:8080" ~/openwebui-venv/bin/open-webui serve --host 127.0.0.1
   ```
5. **After fixing plist**: `launchctl kickstart -k gui/$(id -u)/ai.openwebui.server`
6. **Wait for startup**: embedding model needs 60-120s. Check `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/`

## Service Audit Findings (2026-06-23)

Full audit of Open WebUI + Hermes Gateway + Feishu integration found 12 optimization items. Key findings relevant to Open WebUI:

1. **state.db size**: Hermes `state.db` can grow to 225MB+ without auto-prune. Enable `sessions.auto_prune: true` + `retention_days: 30` in Hermes config.
2. **DeepSeek stream instability**: RemoteProtocolErrors cause responses to hang for 15-21 minutes. Set `gateway_timeout: 600` (not 1800).
3. **Feishu WebSocket churn**: 1264 errors in 48 hours, mostly from proxy/DNS failures. If local proxy (e.g., 7897) is down, Feishu logs fill with proxy errors.
4. **Gateway error log**: 4MB+ cumulative. Contains 1298 errors and 126 warnings from old sessions. Check PID-specific entries to distinguish current vs old.
5. **Memory tool loops**: Agent retries memory updates 5-7 times when entries exceed char limit. Set `memory.char_limit` appropriately.
6. **vector_db orphaned collections**: Chroma dirs may persist after knowledge entries deleted. Check `~/.open-webui/vector_db/` size.

## Pitfalls

1. **No `.env` file exists** — don't look for one. All config is in SQLite.
2. **Plist XML validation** — the plist has been found with duplicate `<key>WEBUI_HOST</key>` and `<key>CORS_ALLOW_ORIGIN</key>` entries plus broken `</dict>` nesting. Symptom: `launchctl load` fails with cryptic `Load failed: 5: Input/output error`. Fix: validate plist XML structure before loading. Use `plutil -lint ~/Library/LaunchAgents/ai.openwebui.server.plist` to check. If it reports errors, fix the XML (remove duplicate keys, ensure proper nesting) then reload.
2. **Embedding model load is slow** — after restart, port 8080 takes 60-120 seconds to become available. The `all-MiniLM-L6-v2` model loads from HuggingFace cache. **Do NOT assume startup failed before 2 minutes.**
3. **`launchctl kickstart -k`** — the `-k` flag kills the old process first. Without it you get two instances competing for port 8080.
4. **Empty API key endpoints cause log spam** — if an endpoint has `api_keys: [""]`, every model-list call generates `Connection error` in the log. Disable or remove it.
5. **Old log entries persist** — after fixing security issues (JWT, CORS), old warnings remain in `server.error.log`. Check the latest `Started server process [PID]` block to see if new warnings appear.
6. **Restart writes to same log files** — old and new process output mixes in `server.log` / `server.error.log`. Check PID or timestamps to distinguish.
7. **Duplicate processes after failed restart** — `launchctl kickstart -k` may leave orphan processes. Always check `ps aux | grep open-webui | grep -v grep` and `lsof -i :8080 | grep LISTEN` after restarts. Kill orphans with `kill <PID>`.
8. **Safari Web App wrapper** — macOS may have `~/Applications/Open WebUI.app` which spawns a separate `Web App` process (PID visible in `ps aux`). This is a Safari-based PWA wrapper, NOT the server. Don't confuse it with the actual open-webui server process.
9. **SQLite CLI can timeout in execute_code** — use Python `sqlite3` module via `execute_code` for config reads/writes, not raw `sqlite3` shell commands which may block.
10. **vector_db orphaned collections** — Chroma directories may persist after knowledge entries are deleted. Check `~/.open-webui/vector_db/` size if storage is a concern.
11. **Launchd port conflict (exit code 1)** — if `com.hermes.tool-proxy` shows exit code 1 in `launchctl list`, check `hermes-proxy.stderr.log`. The most common cause is `[errno 48] address already in use` — meaning another process (often a manually-started proxy from a bash login shell) already owns port 8643. Fix: `kill $(lsof -ti :8643) && sleep 2` then `launchctl kickstart -k gui/$(id -u)/com.hermes.tool-proxy`. Launchd's `KeepAlive: true` will restart it automatically. Verify with `curl -s http://127.0.0.1:8643/v1/models`.

## Config Modification via Python (Recommended Pattern)

```python
import json
from hermes_tools import terminal

r = terminal("sqlite3 ~/.open-webui/webui.db \"SELECT data FROM config WHERE id=1;\"")
data = json.loads(r['output'])

# Modify...
data['openai']['api_configs']['0']['enable'] = False

new_json = json.dumps(data).replace("'", "''")
terminal(f"sqlite3 ~/.open-webui/webui.db \"UPDATE config SET data = json('{new_json}'), updated_at = CURRENT_TIMESTAMP WHERE id = 1;\"")
```

## Launchd Plist Details

A known-good plist template is at `templates/ai.openwebui.server.plist` — use it as reference if the live plist gets corrupted.

- Label: `ai.openwebui.server`
- `RunAtLoad: true` + `KeepAlive: true` — auto-starts on boot, auto-restarts on crash
- `DATA_DIR` env var points to `~/.open-webui/`
- Recommended env vars: `WEBUI_HOST=127.0.0.1`, `CORS_ALLOW_ORIGIN=http://localhost:8080`, `AIOHTTP_CLIENT_TIMEOUT=1800` (critical for long-running agents — default 300s is too short for 20min autonomous mode)

## Installation Paths (from openwebui-management)

| Component | Path |
|-----------|------|
| Binary | `~/openwebui-venv/bin/open-webui` |
| Data dir | `~/.open-webui/` |
| Database | `~/.open-webui/webui.db` |
| LaunchAgent | `~/Library/LaunchAgents/ai.openwebui.server.plist` |
| JWT secret | `~/.webui_secret_key` |
| Python venv | `~/openwebui-venv/` |

## FAQ Quick Reference

| Issue | Cause | Fix |
|-------|-------|-----|
| `InsecureKeyLengthWarning` | JWT key < 32 bytes | `openssl rand -hex 32 > ~/.webui_secret_key` |
| CORS warning | `CORS_ALLOW_ORIGIN=*` | Set to `http://localhost:8080` |
| Ollama connection fail | Ollama not running | Remove ollama from config or install Ollama |
| `Cannot connect to host localhost:11434` | Same | Same |
| Slow startup (2-3 min) | Embedding model loading | Normal — all-MiniLM-L6-v2 needs to load |
| `resource_tracker: leaked semaphore` | Python multiprocessing | Harmless warning, ignore |
| `launchctl load` fails `5: Input/output error` | Malformed plist XML (duplicate keys, bad nesting) | `plutil -lint` the plist, fix XML, then reload |
| ffmpeg warning | ffmpeg not installed | `brew install ffmpeg` |
| 卡顿无输出 (appears stuck, no response) | Hermes tool calls invisible to Open WebUI | Point Open WebUI at proxy `127.0.0.1:8643/v1`. Check proxy: `lsof -i :8643 -P \| grep LISTEN`. Start if needed: `launchctl kickstart -k gui/$(id -u)/com.hermes.tool-proxy` |
| 切后台后"重新连接中" (reconnects after switching apps) | macOS Safari/Chrome kills idle SSE connections for background tabs | SSE heartbeat fix is in `hermes-proxy.py` (sends empty content chunks every 5s). Verify via `launchctl list | grep tool-proxy` — exit code should be 0. If issue persists, restart proxy: `launchctl kickstart -k gui/$(id -u)/com.hermes.tool-proxy` |
| `TransferEncodingError: 400, Not enough data to satisfy transfer length header` during long agent tasks | OpenWebUI `AIOHTTP_CLIENT_TIMEOUT` defaults to 300s (5 min) — aiohttp client drops the connection before the agent finishes | Add `<key>AIOHTTP_CLIENT_TIMEOUT</key><string>1800</string>` to `ai.openwebui.server.plist` EnvironmentVariables. Restart Open WebUI. Verify: `ps eww -p <PID> | grep AIOHTTP_CLIENT_TIMEOUT` |
| Proxy log shows `ClientConnectionResetError: Cannot write to closing transport` | Client disconnected before proxy finished — no graceful handling | Ensure `hermes-proxy.py` has `safe_write()` pattern with `client_ok` shared state (should be included in current proxy) |

## Model Endpoint Config Details

Open WebUI models are connected via OpenAI-compatible API:
- `api_base_urls`: list of API endpoints
- `api_keys`: list, one per endpoint
- `api_configs`: dict keyed by endpoint index

Connecting Hermes via proxy (RECOMMENDED — shows tool calls + thinking in chat):
```json
{
  "openai": {
    "api_base_urls": ["http://127.0.0.1:8643/v1"],
    "api_keys": ["hermes-local-key-2026"],
    "api_configs": {"0": {"enable": true, "connection_type": "external", "auth_type": "bearer"}}
  }
}
```

Connecting Hermes API directly (no tool visibility — use only if proxy is down):
```json
{
  "openai": {
    "api_base_urls": ["http://127.0.0.1:8642/v1"],
    ...
  }
}
```

## Related: Hermes API as Open WebUI Backend

The Hermes API Server (`127.0.0.1:8642`) is configured as an OpenAI-compatible endpoint in Open WebUI, using key `hermes-local-key-2026`. This lets Open WebUI users chat through Hermes/MiMo.

## "卡顿无输出" Problem (Tool Progress Visibility)

When using Hermes API via Open WebUI, the UI appears stuck with no output during tool-heavy requests. Root cause: Hermes API emits custom SSE events (`hermes.tool.progress`) that Open WebUI v0.9.5 does not render. The agent is working — making tool calls — but the user sees nothing until all tool calls complete.

### What's missing

Hermes API emits these custom SSE events during streaming:

```
event: hermes.tool.progress
data: {"tool": "search_files", "emoji": "🔎", "label": "*.py", "toolCallId": "call_00_xxx", "status": "running"}

event: hermes.tool.progress
data: {"tool": "search_files", "toolCallId": "call_00_xxx", "status": "completed"}
```

Open WebUI v0.9.5 ignores these — they're not standard OpenAI SSE format. The user sees a blank screen while the agent works.

### Solution: Thinking Proxy

A proxy intercepts the stream between Hermes API (:8642) and Open WebUI, **translating** `hermes.tool.progress` events into visible content chunks:

```
💻 调用 terminal          ← running → rendered as text in chat
💻 terminal 完成          ← completed → rendered as text in chat
🔍 调用 search_files     ← each tool call visible
```

**Proxy script**: `scripts/hermes-thinking-proxy.py` — requires `aiohttp`. Listens on :8643, forwards to :8642.

**Dependency install**:
```bash
pip install aiohttp
```

**Launchd auto-start** (recommended — survives reboots):
Plist is at `~/Library/LaunchAgents/com.hermes.tool-proxy.plist`. The service label is `com.hermes.tool-proxy`.

```bash
# Install and start
cp ~/.open-webui/hermes-proxy.py ~/.hermes/skills/devops/openwebui-config-management/scripts/hermes-thinking-proxy.py
launchctl load ~/Library/LaunchAgents/com.hermes.tool-proxy.plist

# Restart after proxy code changes
launchctl kickstart -k gui/$(id -u)/com.hermes.tool-proxy

# Check status
lsof -i :8643 -P | grep LISTEN
```

**To use**:
Point Open WebUI at `http://127.0.0.1:8643/v1` instead of `:8642` (Admin Panel → Settings → Connections → OpenAI API URL). API key unchanged: `hermes-local-key-2026`.

### What the proxy does NOT show

- Interior agent reasoning (Hermes API may strip it before transmission — if `hermes.reasoning` events are present, the proxy will emit them as `💭 ...`)
- Tool call results or intermediate data (not exposed via SSE)

### Manual test (no proxy)

```bash
# Verify Hermes API streams tool events
curl -s -N -X POST http://127.0.0.1:8642/v1/chat/completions \
  -H "Authorization: Bearer hermes-local-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"列出文件"}],"stream":true,"max_tokens":100}' | head -30
```

### Manual test (through proxy)

```bash
# Verify proxy translates tool events
curl -s -N -X POST http://127.0.0.1:8643/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"列出文件"}],"stream":true,"max_tokens":100}' | head -30
```

### SSE Disconnection on Background Tab ("重新连接中")

When the user switches away from Open WebUI's browser tab (e.g., to Feishu or another app), macOS Safari/Chrome aggressively kills idle SSE connections to save power — typically within 30-90 seconds of being in the background. When the user returns, Open WebUI shows "重新连接中" (Reconnecting) because the SSE stream was severed.

This is NOT a port conflict between Feishu and Open WebUI — they use completely independent paths. It's purely a browser power-saving behavior.

**Fix: SSE Heartbeat + TransferEncodingError Prevention**

The proxy runs an independent `asyncio.create_task` heartbeat coroutine that sends real SSE data chunks (empty OpenAI content deltas) every 5 seconds during streaming.

**CRITICAL: use real SSE data, NOT SSE comments.** SSE comment lines (`: heartbeat\n\n`) are ignored by aiohttp's `sock_read` timeout — they do NOT reset the client read deadline. Only actual `data:` lines count as real frames. For `aiohttp.ClientTimeout(total=N)` (used by Open WebUI), SSE comments provide zero protection against the total timeout either. The heartbeat MUST send genuine content chunks like:
```python
HEARTBEAT_CHUNK = json.dumps({"choices": [{"index": 0, "delta": {"content": ""}, "finish_reason": None}]})
# sent as:  data: {HEARTBEAT_CHUNK}\n\n
```
This empty content delta is a valid OpenAI streaming chunk that resets both `sock_read` and counts as activity within the `total` timeout window.

Key implementation details:
- Use an independent `asyncio.create_task` coroutine for the heartbeat
- Use `asyncio.Lock` (write_lock) to protect all `response.write()` calls — both from the main stream loop and the heartbeat task — preventing interleaved writes that would corrupt the SSE stream
- Cancel the heartbeat task in a `finally` block after streaming ends
- The proxy at `~/.open-webui/hermes-proxy.py` already has this fix; the launchd-managed service (`com.hermes.tool-proxy`) auto-restarts with it

**Graceful client disconnection:** All `response.write()` calls must be wrapped via `safe_write()` that catches `ConnectionResetError` / `BrokenPipeError` / `OSError` and sets a shared `client_ok["alive"]` flag to `False`. Both the main loop and heartbeat check this flag before writing. The `write_eof()` call in the final cleanup must also be wrapped in try/except — the transport is already closed when the client disconnected mid-stream.
