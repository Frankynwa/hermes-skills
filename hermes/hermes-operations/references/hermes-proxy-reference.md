# hermes-proxy.py — Reference Implementation & Troubleshooting

Full proxy code at `~/.open-webui/hermes-proxy.py`.
Launched via launchd plist `com.hermes.tool-proxy`.

## Architecture

```
Open WebUI (:8080) → proxy (:8643) → Hermes gateway API (:8642) → Model API (xiaomi/deepseek)
```

The proxy translates `hermes.tool.progress` SSE events into OpenAI-compatible content chunks that Open WebUI can display.

## Key Design Points

1. **Character-by-character SSE parsing** — iterates over upstream chunks one char at a time, building lines in a buffer. When `\n` is hit, processes the line. This avoids splitting issues with multi-byte UTF-8.
2. **Event context tracking** — `current_event` tracks the last `event:` line seen. Reset after every processed `data:` line.
3. **Heartbeat** — empty content chunk (`data: {"choices":[{"delta":{"content":""}}]}\n\n`) every 5 seconds. CRITICAL: must be real SSE data, not SSE comments (`: heartbeat\n\n`), because comments don't reset client `sock_read` timeout.
4. **Write lock** — `asyncio.Lock` syncs heartbeat and data writes to avoid interleaving.
5. **safe_write() helper** — wraps all `response.write()` calls with try/except for `ConnectionResetError`, `BrokenPipeError`, `OSError` to handle client disconnection gracefully.

## Port Layout

| Port | Service | Description |
|------|---------|-------------|
| 8642 | Hermes API Server (gateway) | Upstream — emits raw SSE with `hermes.tool.progress` events |
| 8643 | hermes-proxy | Downstream — translates SSE events to content chunks for Open WebUI |
| 8080 | Open WebUI | Web frontend — connects to proxy at `:8643/v1` |

## TOOL_EMOJI Mapping

```python
TOOL_EMOJI = {
    "search_files": "🔍",  "read_file": "📖",  "write_file": "✏️",
    "patch": "🩹",  "terminal": "💻",  "execute_code": "🐍",
    "browser_navigate": "🌐",  "browser_snapshot": "📸",
    "browser_click": "👆",  "browser_type": "⌨️",
    "vision_analyze": "👁️",  "memory": "🧠",
    "web_search": "🔎",  "session_search": "📜",
    "skill_view": "📚",  "skill_manage": "🛠️",
    "delegate_task": "🤖",  "process": "⚙️",  "todo": "📋",
}
```

## TransferEncodingError: Complete Diagnostic Workflow

**Symptom:** Open WebUI shows:
```
Response payload is not completed: <TransferEncodingError: 400, message='Not enough data to satisfy transfer length header.'>
```

### Root Cause Chain

1. **MiMo API rate limits** — `HTTP 429: quota exhausted` from `token-plan-cn.xiaomimimo.com`
2. Multiple concurrent sessions amplify the issue (3-6 sessions competing for quota)
3. Fallback to DeepSeek, which drops connections mid-stream: `peer closed connection without sending complete message body (incomplete chunked read)`
4. Hermes gateway's SSE response to proxy gets mid-stream truncation
5. **Chunked `Transfer-Encoding` breaks** because chunks don't terminate properly
6. Proxy forwards broken chunks → Open WebUI parses incomplete chunked encoding → `TransferEncodingError`

### Diagnostic Commands

```bash
# Step 1: Check proxy stderr for client disconnect errors
tail -30 ~/.open-webui/hermes-proxy.stderr.log
# Expected: ClientConnectionResetError: Cannot write to closing transport

# Step 2: Check gateway error log for upstream model API failures
grep -i "RateLimitError\|incomplete chunked\|peer closed\|TransferEncoding" ~/.hermes/logs/errors.log | tail -10

# Step 3: Trace specific API session through gateway log
grep "api-<session-id>" ~/.hermes/logs/gateway.log | tail -20

# Step 4: Verify proxy is running
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8643/v1/models
```

### Error Log Pattern Reference

| Pattern | Location | Meaning |
|---------|----------|---------|
| `HTTP 429: quota exhausted` on xiaomi | errors.log | MiMo rate limited |
| `peer closed connection without sending complete message body (incomplete chunked read)` | errors.log | DeepSeek dropped mid-stream |
| `ClientConnectionResetError: Cannot write to closing transport` | proxy stderr | OpenWebUI client already disconnected |
| `Stream stale for 180s` | errors.log | Gateway detects 3-min model silence |
| `Streaming failed after partial delivery, not retrying` | errors.log | Gateway gave up on broken stream |
| `ReadTimeout(The read operation timed out)` | errors.log | DeepSeek API read timeout |

## Fix Implementation (July 2026)

### Fix 1: Real Data Heartbeat (NOT SSE comments)

SSE comments (`: heartbeat\n\n`) are invisible to clients and don't reset `aiohttp`'s `sock_read` timeout. When no actual data arrives for the timeout duration, aiohttp closes the connection.

```python
# BEFORE (broken):
await response.write(b": heartbeat\\n\\n")

# AFTER (correct):
HEARTBEAT_CHUNK = json.dumps({
    "choices": [{"index": 0, "delta": {"content": ""}, "finish_reason": None}]
})
await response.write(f"data: {HEARTBEAT_CHUNK}\n\n".encode())
```

### Fix 2: Upstream Exception Handling

Wraps the `async for chunk in upstream.content.iter_any()` loop with exception handling for chunked encoding breaks:

```python
try:
    async for chunk in upstream.content.iter_any():
        # ... process SSE events ...
    
    if client_ok["alive"]:
        await safe_write(response, "data: [DONE]\n\n".encode(), client_ok)
        
except (aiohttp.ClientPayloadError, aiohttp.ClientConnectionError,
        ConnectionResetError, asyncio.TimeoutError) as e:
    # Upstream chunked encoding broke — send clean termination
    error_msg = json.dumps({
        "choices": [{
            "index": 0,
            "delta": {"content": f"\n\n⚠️ 连接中断：{str(e)[:200]}\n"},
            "finish_reason": "error",
        }]
    })
    await safe_write(response, f"data: {error_msg}\n\n".encode(), client_ok)
    await safe_write(response, "data: [DONE]\n\n".encode(), client_ok)
```

### Fix 3: sock_read Timeout

Prevents the proxy from hanging indefinitely when gateway stops sending data:

```python
timeout = aiohttp.ClientTimeout(sock_read=120)  # 120s without data = cleanup
async with aiohttp.ClientSession(timeout=timeout) as session:
    async with session.request("POST", target_url, headers=headers, data=body) as upstream:
```

### Fix 4: safe_write() Helper

All `response.write()` calls routed through this to handle client disconnection:

```python
async def safe_write(response, data: bytes, client_ok: dict) -> bool:
    try:
        await response.write(data)
        return True
    except (ConnectionResetError, BrokenPipeError, OSError):
        client_ok["alive"] = False
        return False
```

## OpenWebUI Timeout Configuration

`AIOHTTP_CLIENT_TIMEOUT` env var (default: 300s = 5 min) controls the total HTTP request timeout. For 20min autonomous mode, increase it:

```xml
<!-- In ~/Library/LaunchAgents/ai.openwebui.server.plist -->
<key>AIOHTTP_CLIENT_TIMEOUT</key>
<string>1800</string>
```

Verify it's loaded: `ps eww -p $(pgrep open-webui) | tr ' ' '\n' | grep AIOHTTP_CLIENT_TIMEOUT`

## Launchd Management

```bash
# Restart proxy
launchctl unload ~/Library/LaunchAgents/com.hermes.tool-proxy.plist
launchctl load ~/Library/LaunchAgents/com.hermes.tool-proxy.plist

# Verify
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8643/v1/models  # expect 200
```
