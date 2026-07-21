---
name: codebase-inspection
description: "Inspect codebases w/ pygount: LOC, languages, ratios."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LOC, Code Analysis, pygount, Codebase, Metrics, Repository]
    related_skills: [github-repo-management]
prerequisites:
  commands: [pygount]
---

# Codebase Inspection with pygount

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.

## When to Use

- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition
- User wants code-vs-comment ratios
- General "how big is this repo" questions
- User asks to "check", "review", "inspect", or "analyze" a project

## Pre-Flight: Repo Discovery (Before Any Inspection)

**Always find the correct repo before analyzing.** The user may be working from a local clone, a fork, or a team member's shared repo — NOT necessarily their own GitHub account.

### Step 1: Search Local First

```bash
# Search common project directories for a local clone
find ~/projects ~/Desktop ~/Documents -maxdepth 3 -iname "*<project-name>*" -type d 2>/dev/null
```

Check git remote for the actual source:

```bash
cd /path/to/local/clone
git remote -v
```

### Step 2: Only Fall Back to GitHub Search If No Local Copy

Use `mcp_github_search_repositories` with `user:<username> <project-name>` — but be aware: the local clone may point to a **different repo** (team org, shared repo, fork) than what appears under the user's own GitHub account.

### Step 3: If Repo Identity Is Ambiguous — Ask Early

If the local `.git/config` is broken/unreadable, or git remote returns nothing, **ask the user for the correct repo URL immediately**. Do not spend 4+ tool calls debugging a broken git config — pivot to asking.

> **Anti-pattern:** Searching GitHub, finding a repo under the user's name, and assuming it's the right one. The user may have forked someone else's repo, or the project may live in a team organization. When the user says "shared repo" or "团队仓库", they mean a different owner.

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. Basic Summary (Most Common)

Get a full language breakdown with file counts, code lines, and comment lines:

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will crawl them and take a very long time or hang.

## 2. Common Folder Exclusions

Adjust based on the project type:

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Interpreting Results

The summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## Pitfalls

### Repo Discovery Pitfalls

1. **Don't assume the repo is under the user's GitHub account.** It could be a fork, a team org repo, or a shared repo from a classmate/colleague. When the user says "检查XX项目", first check `find ~/Desktop ~/projects ~/Documents -maxdepth 3 -iname "*XX*"`, then check `git remote -v` for the actual origin.
2. **Don't over-debug broken git state.** If `.git/config` is unreadable or `git log` fails, ask the user for the repo URL after 1-2 attempts. Don't spend 4+ tool calls hammering at a broken git config.
3. **The user's local copy IS the source of truth** when they say "本地拉取过的" (cloned locally). GitHub search may return the user's own fork, not the shared team repo they actually mean.

### pygount Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific languages rather than scanning everything.
