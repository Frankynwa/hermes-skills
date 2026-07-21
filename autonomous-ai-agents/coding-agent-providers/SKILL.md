---
name: coding-agent-providers
description: "Configure and connect coding agents (Claude Code, Codex, Aider, OpenCode, Cline, Continue) to various LLM providers. Covers provider compatibility matrices, config formats, API wire protocols, and known incompatibilities. Use when user asks to connect a coding tool to a specific model or provider."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Provider, DeepSeek, OpenAI, Anthropic, Configuration]
    related_skills: [claude-code, codex, opencode]
---

# Coding Agent — Provider Configuration Guide

When a user asks to connect a coding agent to a model/provider, load this skill FIRST to check compatibility before attempting configuration.

## Provider Compatibility Matrix

| Agent | OpenAI models | Anthropic models | DeepSeek | Arbitrary OpenAI-compat |
|-------|:---:|:---:|:---:|:---:|
| **Claude Code** | ❌ | ✅ native | ❌ | ❌ (only Bedrock/Vertex/Foundry) |
| **Codex CLI** | ✅ native | ❌ | ⚠️ via @codeproxy/cli | ⚠️ only if provider supports Responses API |
| **Codex Desktop** | ✅ native | ❌ | ❌ auth requires OpenAI | ❌ auth screen validates against api.openai.com |
| **Aider** | ✅ | ✅ | ✅ | ✅ (any OpenAI-compat) |
| **Continue** | ✅ | ✅ | ✅ | ✅ |
| **Cline** | ✅ | ✅ | ✅ | ✅ |
| **OpenCode** | ✅ | ✅ | ⚠️ via OpenRouter | ⚠️ LOCAL_ENDPOINT unreliable for remote APIs |

## Critical API Wire Protocol Knowledge

### Codex uses Responses API, NOT Chat Completions
- Codex calls `/v1/responses` (OpenAI Responses API)
- Most non-OpenAI providers (DeepSeek, Qwen, etc.) only support `/v1/chat/completions`
- HTTP 404 on `/v1/responses` = provider doesn't support this wire format
- **No workaround** — this is a protocol-level incompatibility, not a config issue

### Claude Code is Anthropic-only
- Hardcoded to `https://api.anthropic.com`
- Third-party: AWS Bedrock, GCP Vertex AI, MS Azure Foundry (all host Claude models)
- Cannot point at arbitrary endpoints — no `base_url` config for non-Anthropic providers

### DeepSeek API compatibility
- Supports: `/v1/chat/completions` (OpenAI Chat Completions compatible)
- Does NOT support: `/v1/responses` (OpenAI Responses API)
- Works with: Aider, Continue, Cline, OpenCode (via OpenRouter), Codex CLI (via @codeproxy/cli proxy)
- Does NOT work with: Claude Code, Codex Desktop (auth screen validates against api.openai.com before reading config)

## When user asks "can I use X with Y?"

1. Check the compatibility matrix above
2. If incompatible, explain the SPECIFIC technical reason (wire protocol, API format, etc.)
3. Don't just say "it doesn't work" — suggest the compatible alternative
4. If user insists it should work (e.g., "I saw people doing it"), verify before dismissing. They may be using a different tool than you think.

## Pitfalls

- **Don't assume incompatibility without checking** — Codex CLI can use DeepSeek via `@codeproxy/cli` (Chat Completions → Responses API bridge). See `references/codeproxy-deepseek-setup.md`. However, Codex DESKTOP cannot — its Electron welcome screen validates credentials against api.openai.com before config.toml is even read.
- **OpenRouter is the universal adapter** — $5 OpenRouter key unlocks most models for most tools. Suggest this before telling user they need multiple API keys.
- **"I saw people doing it"** — User likely saw Aider/Continue/Cline usage, not Codex/CC. Clarify which tool they mean.
- **lsof ≠ healthy proxy** — When Codex uses a local proxy (e.g. `@codeproxy/cli` on port 8787), `lsof -i :8787` showing LISTEN does NOT prove the proxy is alive. A stale node process can hold the port while returning empty responses. Always verify with `curl -s http://127.0.0.1:8787/v1/models` — a healthy proxy returns a JSON error body, not empty. See `references/codeproxy-deepseek-setup.md` for the full troubleshooting recipe.
- Codex Desktop vs CLI are separate binaries. Desktop bundles its own codex at /Applications/Codex.app/Contents/Resources/codex (v0.133.0-alpha.1) running as app-server. The npm-installed CLI at /opt/homebrew/bin/codex is only used for codex exec / terminal mode. Desktop never touches the npm binary.
- Config file mentioning a port does NOT mean a proxy is running. In Claude Desktop App config.json, a cached apiBase URL like http://127.0.0.1:50845 may be a historical artifact. Always verify with lsof -i :PORT before claiming connectivity. Claude Desktop App uses OAuth (not API key), so even a running proxy cannot bridge the auth gap to DeepSeek.
- Desktop apps lock you into vendor auth. Claude Desktop App = OAuth to Anthropic. Codex Desktop = OpenAI sk- key. Neither exposes custom endpoint fields in UI or config, even in developer mode. CLI versions are the only path for custom providers. See references/desktop-app-deepseek-limitations.md.

## See Also
- references/codex-custom-provider-config.md — Codex config.toml format for custom providers
- references/codeproxy-deepseek-setup.md — Codex + DeepSeek via @codeproxy/cli proxy: setup, health checks, stale-proxy fix
- references/cc-vs-codex-comparison.md — Claude Code vs Codex: capability, cost, UI, and provider compatibility comparison
- references/desktop-app-deepseek-limitations.md — Why Claude Desktop and Codex Desktop cannot use DeepSeek (OAuth, OpenAI-key auth, developer mode findings)
