# Open WebUI Diagnostic Playbook

## Quick Health Check

```bash
# Process running?
ps aux | grep -i openwebui | grep -v grep

# Port listening?
lsof -i :8080

# HTTP response time?
curl -s -o /dev/null -w "HTTP: %{http_code}, time: %{time_total}s\n" http://127.0.0.1:8080/

# Backend API reachable?
curl -s -o /dev/null -w "HTTP: %{http_code}, time: %{time_total}s\n" http://127.0.0.1:8642/v1/models
```

## Database Inspection

Open WebUI stores config in SQLite: `~/.open-webui/webui.db`

```bash
# List all tables
sqlite3 ~/.open-webui/webui.db ".tables"

# Config is JSON blob (not key-value!)
sqlite3 ~/.open-webui/webui.db "SELECT substr(data, 1, 2000) FROM config LIMIT 1;"

# Check registered models
sqlite3 ~/.open-webui/webui.db "SELECT id, name, base_model_id, is_active FROM model;"

# Check API keys
sqlite3 ~/.open-webui/webui.db "SELECT * FROM api_key;"
```

## Common Issues

### "卡顿无输出" (Lag with no output)

**Root cause: Streaming SSE failure.** Open WebUI defaults to `stream: true`. If the backend API's SSE stream has any issue (timeout, format error, connection drop), the UI freezes with no output.

**Diagnostic:**
```bash
# Test non-streaming (should work)
curl -s http://127.0.0.1:8642/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <key>" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"hi"}],"stream":false}'

# Test streaming (may hang if SSE broken)
curl -s -N http://127.0.0.1:8642/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <key>" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"hi"}],"stream":true}'
```

**Fix:** Turn off streaming in Open WebUI chat settings, or fix the backend SSE implementation.

### No models visible in UI

**Root cause:** `model` table is empty in webui.db.

**Fix:** Go to Admin Panel → Settings → Connections → verify API endpoint URL and key → click Save → models should auto-populate.

### Config table schema

The `config` table has columns: `id`, `data` (JSON), `version`, `created_at`, `updated_at`.
The `data` JSON contains sections: `ui`, `direct`, `models`, `openai` (with `api_base_urls`, `api_keys`, `api_configs`).

### Model table schema

`id`, `user_id`, `base_model_id`, `name`, `meta` (JSON), `params` (JSON), `created_at`, `updated_at`, `is_active`.

## Process Management

```bash
# Start (background)
DATA_DIR=~/.open-webui WEBUI_HOST=127.0.0.1 \
  CORS_ALLOW_ORIGIN="http://localhost:8080;http://127.0.0.1:8080" \
  ~/.openwebui-venv/bin/open-webui serve --host 127.0.0.1 &

# Kill
kill $(pgrep -f "open-webui serve")
```
