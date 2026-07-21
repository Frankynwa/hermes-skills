# Codex + DeepSeek via @codeproxy/cli

## Why this exists

Codex CLI uses OpenAI Responses API (`/v1/responses`), which DeepSeek doesn't support. The `@codeproxy/cli` package translates OpenAI Responses API calls into DeepSeek Chat Completions, allowing Codex to use DeepSeek models.

## Setup summary

### Proxy startup script: `~/.hermes/scripts/start-codex-proxy.sh`

```bash
npx @codeproxy/cli \
    --base-url https://api.deepseek.com/v1 \
    --model deepseek-v4-pro \
    --apikey "$DEEPSEEK_API_KEY"
```

Run in background (port 8787).

### Codex config: `~/.codex/config.toml`

```toml
[model_providers.deepseek]
name = "DeepSeek"
base_url = "http://127.0.0.1:8787/v1"
wire_api = "responses"

[profiles.deepseek-pro]
model = "deepseek-v4-pro"
model_provider = "deepseek"
```

### Claude Code + DeepSeek

CC connects directly via `ANTHROPIC_BASE_URL=/anthropic` environment variable pointing at a DeepSeek-compatible endpoint. No proxy needed.

## Proxy health verification

### The silent-failure trap

`lsof -i :8787` showing a LISTEN port is NOT sufficient proof the proxy is alive. A stale node process can hold the port while being completely non-responsive to requests. This is the most common failure mode.

**Always verify with a real HTTP probe:**

```bash
curl -s http://127.0.0.1:8787/v1/models
```

A healthy proxy returns a JSON error (e.g. `{"error":{"message":"Not found: GET /v1/models"}}`) — this is normal, the proxy doesn't implement `/v1/models`. An empty response or connection refused = proxy is dead.

### Symptoms of stale proxy

- Codex fails with `stream disconnected before completion: error sending request for url (http://127.0.0.1:8787/v1/responses)`
- `lsof` shows port listening but `curl` returns empty
- `ps aux | grep codeproxy` shows no matching process (the node process exists but isn't identifiable as codeproxy)

### Fix

```bash
# Find and kill the stale process
kill -9 $(lsof -ti :8787)
# Wait for port release
sleep 1
# Restart proxy (background=true in Hermes terminal)
```

### Startup script weakness

The current `start-codex-proxy.sh` uses `lsof -i :8787 >/dev/null` as its health check and exits 0 if the port is busy. This means a stale proxy blocks automatic restart. Future improvement: replace lsof check with a curl health probe.
