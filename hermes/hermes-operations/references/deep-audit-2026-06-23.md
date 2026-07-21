# Deep Audit Report — 2026-06-23

## Hermes Gateway Findings

### Critical
- `.env` permissions were `644` (world-readable) → fixed to `600`
- 1,298 ERRORs, 126 WARNINGs in gateway.log (cumulative)
- DeepSeek stream instability: `RemoteProtocolError` + streams hanging 15-114 minutes
- 30+ Feishu WebSocket disconnects in 48h (keepalive ping timeout, no close frame)
- 553 proxy errors (127.0.0.1:7897 not running)

### Config Changes Made
- `gateway_timeout`: 1800 → 600
- `gateway_timeout_warning`: 900 → 300
- `tirith_fail_open`: true → false
- `sessions.auto_prune`: false → true
- `sessions.retention_days`: 90 → 30

### State
- state.db: 225MB (VACUUM didn't shrink — data is real)
- Memory drift: 339→363MB over 2 days (slow leak)
- Gateway PID 1570, uptime ~60h

## Open WebUI Findings

### Critical
- JWT key 16 bytes (RFC requires 32+) → regenerated 64-char hex
- Bound to `0.0.0.0` (all interfaces) → added `WEBUI_HOST=127.0.0.1` to plist
- CORS `*` → added `CORS_ALLOW_ORIGIN=http://localhost:8080` to plist
- Ollama endpoint (localhost:11434) causing connection errors → removed from config
- Empty API key OpenAI endpoint → removed from config

### State
- Version: 0.9.5
- 1 user (admin), 14 chats, 0 knowledge entries
- vector_db: 2.1MB (single chroma.sqlite3)
- Embedding model: all-MiniLM-L6-v2 (384-dim)
- No ffmpeg → suggested `brew install ffmpeg`

## Feishu Integration Findings

### Issues
- Duplicate pairing stores: `pairing/` and `platforms/pairing/` (same user, different timestamps)
- Unbounded seen-message-ID cache (112 entries, no TTL)
- 289 DNS resolution failures for `open.feishu.cn`
- Empty `user_name` in approved user record

### State
- Connected since 2026-06-18, stable
- 1 approved user (ou_1e6a1b2ebfe154d5b0470b6f003ecd06)
- 5 registered channels (all DM, same chat)
- Connection mode: WebSocket (not webhook)

## Lessons Learned
1. `patch` tool on config.yaml silently fails — use `sed -i ''` then verify with `grep`
2. Open WebUI stores ALL config in SQLite `config.data` JSON, not env files
3. Open WebUI embedding model takes 30-60s to load on restart — health checks need `sleep 60`
4. `launchctl kickstart -k` restarts macOS LaunchAgent services
5. VACUUM on state.db only reclaims deleted pages — if data is real, size won't shrink
