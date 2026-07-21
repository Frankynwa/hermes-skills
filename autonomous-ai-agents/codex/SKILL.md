---
name: codex
description: "Delegate coding to OpenAI Codex CLI (features, PRs)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## When to use

- Building features
- Refactoring
- PR reviews
- Batch issue fixing

Requires the codex CLI and a git repository.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI auth configured: either `OPENAI_API_KEY` or Codex OAuth credentials
  from the Codex CLI login flow
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

For Hermes itself, `model.provider: openai-codex` uses Hermes-managed Codex
OAuth from `~/.hermes/auth.json` after `hermes auth add openai-codex`. For the
standalone Codex CLI, a valid CLI OAuth session may live under
`~/.codex/auth.json`; do not treat a missing `OPENAI_API_KEY` alone as proof
that Codex auth is missing.

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## Codex Desktop App (`codex app`)

Codex ships a desktop GUI alongside the CLI. Launch it with `codex app [path]`:

```
codex app ~/projects/my-project
```

First launch downloads the installer (~453 MB) from OpenAI's CDN and installs `Codex Desktop.app` to `/Applications`. The download takes ~3 minutes at typical broadband speeds. Subsequent launches open the installed app directly without re-downloading.

Key points:
- The desktop app opens a graphical workspace browser and interactive coding session
- Requires a display/GUI environment — won't work over SSH-only connections
- Workspace path defaults to `.` (current directory)
- Use `codex app --help` to see all options (config overrides, feature toggles, etc.)
- If the QR-code auth flow appears, authenticate via the displayed URL or QR code

Pitfalls with Codex Desktop:

1. **Desktop auth requires OpenAI credentials.** The Desktop app (Electron) validates API keys against `api.openai.com` on the welcome screen BEFORE reading `~/.codex/config.toml`. A custom `model_providers` entry (e.g., pointing to a DeepSeek proxy) is ignored during auth. The CLI works fine with custom providers via config.toml, but the Desktop app's login flow is hardcoded to OpenAI. Setting `OPENAI_API_KEY` to a non-OpenAI key and launching from CLI does not bypass the welcome screen — the UI still requires ChatGPT login or a real OpenAI API key.

   The Desktop app reads multiple config sources: `~/.codex/app.toml` (primary, created by `codex app`), `~/.codex/config.toml` (shared with CLI), and `~/.codex/settings.json` (Electron app preferences). However, the welcome/auth screen checks credentials BEFORE loading any of these config files — so custom providers in `app.toml` or `settings.json` won't help you get past the login screen. If a user needs DeepSeek or another custom backend, the CLI is the only viable path for now.

2. **Desktop bundles its own CLI.** The app ships an embedded `codex` binary at `/Applications/Codex.app/Contents/Resources/codex` (v0.133.0-alpha.1) that runs as `app-server --listen stdio://`. This communicates with the Electron renderer via IPC. The npm-installed `codex` CLI at `/opt/homebrew/bin/codex` is a SEPARATE binary, used only by `codex exec` / `codex` CLI mode — the Desktop app never uses it.

3. On headless/remote machines, `codex app` will download the installer but cannot display the GUI. The app binary will be installed and ready for when a display is available.

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--full-auto` for building** — auto-approves changes within the sandbox
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work
