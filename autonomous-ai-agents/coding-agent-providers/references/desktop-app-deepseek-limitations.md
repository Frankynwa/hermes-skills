# Desktop App DeepSeek Limitations

Last updated: 2026-05-24. Covers Claude Desktop App and Codex Desktop App vs DeepSeek.

## Bottom Line

Neither desktop app supports DeepSeek or any custom provider. Use CLI versions for DeepSeek.

## Claude Desktop App

- Authentication: OAuth-based, connects to Anthropic's identity service
- Even in developer mode (`allowDevTools: true` in `~/Library/Application Support/Claude/developer_settings.json`), no custom API endpoint field is exposed in the UI or config files
- Config files inspected: `config.json`, `claude_desktop_config.json`, `developer_settings.json` — none contain API endpoint override fields
- The OAuth token is bound to Anthropic's servers; changing the base URL wouldn't work because DeepSeek can't validate Anthropic OAuth tokens
- Port 50845 was previously misidentified as a working proxy — it no longer listens and shouldn't be relied on

## Codex Desktop App

- Authentication: OpenAI-based, first-run setup requires `sk-...` OpenAI API key
- Config paths: `~/.codex/config.toml` (CLI), `~/.codex/app.toml` (Desktop), `~/.codex/settings.json` (Desktop alternate) — none enable custom providers for Desktop
- Even with valid provider config in `app.toml`, the GUI setup screen still demands an OpenAI key
- CLI version (`codex`) works with custom providers via `@codeproxy/cli` proxy on port 8787

## What DOES Work with DeepSeek

- CC: `claude` CLI, via `ANTHROPIC_BASE_URL=/anthropic` env var
- Codex CLI: `codex` command, via `@codeproxy/cli` proxy (port 8787)
- Both verified working on 2026-05-24

## Verification Checklist

When verifying coding agent connectivity, always:
1. Run an actual test command (not just check binary version)
2. Verify the proxy/gateway is truly listening (`lsof -i :PORT`)
3. Don't infer "working" from config files alone — config can be misconfigured or ignored
