# Xiaomi MiMo API

## Current Endpoints (as of 2026-05)

| Item | Value |
|------|-------|
| Base URL | `https://api.xiaomimimo.com/v1` |
| Old Base URL (dead) | `https://token-plan-cn.xiaomimimo.com/v1` |
| Env var | `XIAOMI_API_KEY` |
| Config provider | `xiaomi` |
| Format | OpenAI-compatible |
| Vision model | `xiaomi/mimo-v2-omni` |

## Key Gotchas

1. **Base URL changed**: The old `token-plan-cn.xiaomimimo.com` returns 401 "Invalid API Key" even with a valid new key. Must use `api.xiaomimimo.com`.

2. **API key rotation**: Old keys stop working when rotated. If you get 401 on MiMo, verify the base URL first — the error message is the same for both wrong key and wrong endpoint.

3. **Profile .env**: MiMo profiles need the symlink: `ln -sf ~/.hermes/.env ~/.hermes/profiles/<name>/.env`

4. **Rate limits**: MiMo has quota limits. Running benchmarks while an active session is on MiMo can exhaust quota.

5. **Test endpoint verification**:
```bash
curl -s https://api.xiaomimimo.com/v1/chat/completions \
  -H "Authorization: Bearer sk-YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-v2.5-pro","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

## Hermes Config (profile config.yaml)

```yaml
model:
  provider: xiaomi
  default: mimo-v2.5-pro
  context_length: 1048576
```
