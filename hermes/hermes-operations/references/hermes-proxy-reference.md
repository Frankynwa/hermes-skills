# hermes-proxy.py — Reference Implementation

Full proxy code as of July 2026. Sits at `~/.open-webui/hermes-proxy.py`.
Launched via launchd plist `com.hermes.tool-proxy`.

## Key Design Points

1. **Character-by-character SSE parsing** — iterates over upstream chunks one char at a time, building lines in a buffer. When `\n` is hit, processes the line. This avoids splitting issues with multi-byte UTF-8.
2. **Event context tracking** — `current_event` tracks the last `event:` line seen. Reset after every processed `data:` line.
3. **SSE heartbeat** — `: heartbeat\n\n` every 5 seconds prevents macOS background tab throttling.
4. **Write lock** — `asyncio.Lock` syncs heartbeat and data writes to avoid interleaving.
5. **Content chunk format** — uses `make_content_chunk()` to produce OpenAI-compatible `{"choices":[{"delta":{"content":"..."}}]}` for tool progress translations.

## Provider Upgrade Notes

- **Original proxy** (`~/.open-webui/hermes-proxy.py`): Uses `aiohttp`. Actively maintained. Supports tool.progress + reasoning + heartbeat.
- **Legacy proxy2** (`~/projects/hermes-thinking-proxy/proxy2.py`): Uses stdlib only (`asyncio`, `urllib`). Simpler but no heartbeat support. Reference only.

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

## Port Layout

| Port | Service | Description |
|------|---------|-------------|
| 8642 | Hermes API Server (gateway) | Upstream — emits raw SSE with `hermes.tool.progress` events |
| 8643 | hermes-proxy | Downstream — translates SSE events to content chunks for Open WebUI |
| 8080 | Open WebUI | Web frontend — connects to proxy at `:8643/v1` |
| 3000 | Hermes Dashboard | Admin UI |
