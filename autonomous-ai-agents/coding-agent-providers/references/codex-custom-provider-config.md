# Codex CLI — Custom Provider Configuration

## Config File Location
`~/.codex/config.toml`

## Custom Provider Format (verified on Codex v0.133.0)

```toml
# Set the active model provider
model_provider = "my-provider"
model = "my-model-name"

[model_providers.my-provider]
name = "my-provider"          # REQUIRED — must match section key, must not be empty
base_url = "https://api.example.com/v1"  # API root URL
env_key = "MY_API_KEY"        # Environment variable name for auth
```

## Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `name` | YES | Provider display name. Must match section key. Error if empty. |
| `base_url` | YES | API root URL. Codex probes `GET /models` on this URL. |
| `env_key` | YES | Name of env var containing the API key. Codex checks if this var is set. |

## Verified Working Config: DeepSeek (connectivity only)

```toml
model_provider = "deepseek"
model = "deepseek-v4-pro"

[model_providers.deepseek]
name = "deepseek"
base_url = "https://api.deepseek.com/v1"
env_key = "DEEPSEEK_API_KEY"
```

**codex doctor output:**
- ✅ config loaded
- ✅ auth: DEEPSEEK_API_KEY present
- ✅ reachability: HTTP 401 (auth required, but endpoint reachable)
- ❌ Runtime fails: 404 on `/v1/responses` — DeepSeek doesn't support Responses API

## CLI Override

```bash
# Override model at runtime
codex exec -m "deepseek-v4-pro" "my task"

# Override any config value
codex -c 'model="deepseek-v4-pro"' exec "my task"
```

## Built-in Provider IDs (reserved, cannot be used as custom names)
Likely includes: `openai`, `aws`, `azure`, `gcp`, and other first-party providers.

## Pitfalls

- **`name` field is REQUIRED** — omitting it gives "provider name must not be empty"
- **Codex uses Responses API (`/v1/responses`)** — not Chat Completions. Most non-OpenAI providers don't support this wire format.
- **`base_url` is probed** — Codex does `GET /models` on startup. If your provider doesn't have this endpoint, connectivity check may fail.
- **`--oss` mode** is for local providers only (lmstudio, ollama) — not for remote custom APIs.
