---
name: hermes-session-lifecycle-debugging
description: Debug Hermes Agent session context loss, lifecycle issues, and gateway restart problems by correlating session files, agent logs, gateway code, and the sessions registry.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [debugging, hermes, session, gateway, context-loss, troubleshooting]
    related_skills: [systematic-debugging]
---

# Hermes Session Lifecycle Debugging

## Overview

Hermes sessions can lose context or fail to resume after gateway restarts. This skill provides a systematic approach to diagnosing session lifecycle issues — tracing the chain of events from user message → agent processing → gateway restart → session suspension → context loss.

**The key insight:** session context loss is rarely a code bug — it's typically a **timing problem** caused by drain timeouts during gateway restart, triggered by slow agent turns (e.g., GitHub API rate limiting) that exceed the 60s drain window.

## Diagnostic Sources

Three data sources must be correlated:

| Source | Path | What it reveals |
|--------|------|-----------------|
| **Session JSON** | `~/.hermes/sessions/session_<timestamp>_<id>.json` | Full message history, conversation state per session |
| **Agent Log** | `~/.hermes/logs/agent.log` | Gateway lifecycle events: restarts, drains, suspensions, button approvals |
| **Gateway Source** | `~/.hermes/hermes-agent/gateway/run.py` | Code paths for restart triggers, drain timeout, session suspension |
| **Sessions Registry** | `~/.hermes/sessions/sessions.json` | Maps platform+chat → active session_id; resetting = context loss |
| **Feishu dedup** | `~/.hermes/feishu_seen_message_ids.json` | Track which Feishu messages were already processed across restarts |

## Investigation Phases

### Phase 1: Identify the Session Timeline

1. **List recent sessions**, sorted by time:
   ```bash
   ls -lt ~/.hermes/sessions/session_*.json | head -10
   ```

2. **Check sessions.json** to see which session is ACTIVE for the platform:
   ```python
   import json
   with open("~/.hermes/sessions/sessions.json") as f:
       data = json.load(f)
   # Look for agent:main:feishu:dm:<chat_id> → session_id
   ```

3. **Read the active session file** to check if context is present (or a fresh blank session).

4. **Read the previous session file** — it may contain the full conversation history even after context was "lost."

### Phase 2: Trace Gateway Events in Agent Log

Search `~/.hermes/logs/agent.log` for these key events around the time of context loss:

```bash
# Find gateway restart events
grep -n "Stopping gateway for restart\|restart" agent.log

# Find drain timeout (the smoking gun)
grep -n "drain timed out\|Skipping .clean_shutdown\|Suspended" agent.log

# Find session hygiene / compression events
grep -n "Session hygiene\|compressed" agent.log

# Find Feishu button approvals (often precede restarts)
grep -n "Feishu button resolved\|Stopping gateway for restart" agent.log

# Find what triggered the restart
grep -n "request_restart\|SIGUSR1\|Telegram polling could not reconnect\|Fatal telegram" agent.log
```

**Key patterns to recognize:**

| Log Pattern | Meaning |
|-------------|---------|
| `Stopping gateway for restart...` | Gateway is shutting down intentionally |
| `feishu:xxx` right before restart | The agent (or you) triggered a restart (e.g., `hermes gateway restart`) |
| `Telegram polling could not reconnect` | Telegram network failure triggered restart |
| `SIGUSR1 restart handler called` | Unix signal triggered restart |
| `drain timed out after 60.0s` | **THE smoking gun** — agent didn't finish within drain window |
| `Skipping .clean_shutdown marker` | Unscheduled shutdown → sessions will be suspended |
| `Suspended 1 in-flight session(s)` | Old session put on ice, not resumed |
| `Sending response (71 chars)` after restart | New blank session responding to user — context lost |

### Phase 3: Understand the Drain Timeout Mechanism

The 60s drain timeout in `gateway/run.py`:

```python
# Default restart_drain_timeout = 60 seconds
# When stop(restart=True) is called:
#   1. Sends shutdown notification to user
#   2. Waits up to drain_timeout for active agents to finish
#   3. If agents don't finish → interrupts them
#   4. Writes/doesn't write .clean_shutdown marker
#   5. On restart: checks .clean_shutdown → resume or suspend sessions
```

A `restart_drain_timeout` of 60s means: if any agent turn takes longer than 60s to respond (e.g., stuck in a GitHub API rate-limited loop), the restart will interrupt it mid-work and the session will be **suspended** rather than **resumed**.

### Phase 4: Check the Restart Trigger Chain

Trace backwards from the restart to find its origin:

1. **User triggered** — Look for `hermes gateway restart` in session messages, or user messages like "重启服务"
2. **Agent triggered** — Agent may run `systemctl --user restart hermes-gateway` to apply config changes
3. **Telegram failure** — Network errors auto-trigger restart
4. **SigUSR1** — Sent by `hermes update` or `hermes gateway restart --replace`
5. **Config change** — Agent modifies `~/.hermes/config.yaml`, then restarts to apply

### Phase 5: Assemble the Full Timeline

Piece together the evidence into a timeline:

```
Time | Event | Source
-----|-------|------
T-5m | User says "修改后重启服务" | session JSON
T-3m | Agent modifies config.yaml | session JSON
T-2m | Agent runs `hermes gateway restart` (approved by user) | session JSON + agent.log
T-1m | Agent starts new turn (slow GitHub API) | session JSON
T-0s | Gateway drain starts | agent.log (Stopping gateway)
T+60s | Drain TIMEOUT — interrupting agent | agent.log
T+61s | Skipping clean_shutdown → sessions suspended | agent.log
T+62s | Gateway restarts, user sends new message → new blank session | agent.log + sessions.json
```

## Critical Finding: Session File Not Written Between Turns

**The most insidious cause of context loss:** The session JSON file is NOT written to disk after every turn. It's only saved periodically (e.g., during compression events, or when the agent finishes a response). If the Gateway restarts **while the agent is still processing a turn**, the in-memory conversation state is **permanently lost**.

**Diagnostic pattern:**

```
Session file last_modified: May 14 00:09       ← last disk write
Agent log shows messages at: 00:17, 00:18, ... ← later messages in memory only
Gateway restart at:          00:43              ← all in-memory messages lost
```

To detect this:
```bash
# Compare session file modification time with last agent.log activity
ls -la ~/.hermes/sessions/session_<id>.json
tail ~/.hermes/logs/agent.log | grep "inbound message\|response ready"
# If file time is EARLIER than log activity → messages were lost
```

## Common Root Causes

| Cause | Indicator | Fix |
|-------|-----------|-----|
| **No GITHUB_TOKEN** | 60 req/hr limit → GitHub Skills Hub searches slow | `gh auth login` or set `GITHUB_TOKEN` |
| **restart_drain_timeout too low** | Repeated drain timeouts | Increase to 120-180s in config.yaml |
| **User asked for restart mid-work** | "重启服务" in conversation | Wait for agent to finish before restarting |
| **Telegram network flapping** | Repeated Telegram reconnects | Disable Telegram if not used, or fix DNS/network |
| **Mid-task restart for config change** | Agent modifies config.yaml, then runs `hermes gateway restart` | Avoid mid-conversation config changes; batch them or wait for task completion |
| **Compressed session ≠ resumed session** | `Session hygiene: compressed N → M msgs` exists in log, but restart still creates new blank session | The compression reduces old session size but doesn't help resume — the `sessions.json` pointer is what matters |
| **✅ Session file not saved between turns [NEW]** | File mtime older than last log activity; long delay between "response ready" and next "inbound message" | Session saving should happen after each turn completes, not only during compression |

## The "Parallel Universe" Sessions Pattern

A key diagnostic finding: when sessions keep getting lost, the system creates **multiple sessions with identical content** — each restart spawns a new session that starts from the same initial conversation (你好 → 你是什么模型 → 检查健康 → ...), while the real advanced progress lives in older suspended sessions:

```
Session A (88 msgs) — starts: "你好" → ends: "不对啊deepseekv4没有视觉"
Session B (129 msgs) — same start → ends: "那Hermes怎么知道..."
Session C (209 msgs) — same start → ends: "先不改，先帮我对比"
Session D (314 msgs) — same start → ends: "全程汇报模式"
Session E (378 msgs) — same start → ends: "skills.sh搜code formatter"
Session F (411 msgs) — same start → ends: "anthropics官方skill" ← interrupted by restart
```

To detect this: check if multiple session files share the same first few user messages.

## Missing Log Pattern: "New Blank Session After Restart"

After a drain-timeout restart, look for this pattern in `agent.log`:

```
Suspended 1 in-flight session(s) from previous run   ← old session suspended
...
[Feishu] Inbound dm message received: text='后续消息'   ← user sends new message
inbound message: platform=feishu chat=oc_... msg='后续消息'
Sending response (71 chars) to oc_...               ← VERY short response = blank session
```

The short response (under 100 chars with generic "what can I help" format) is a clear indicator the new session has NO context from previous work.

## Recovery: How to Resume a Suspended Session

If the session data still exists on disk:

```python
import json

# 1. Find the old session file (check timestamps)
import glob
old_sessions = sorted(glob.glob("~/.hermes/sessions/session_*.json"))
for f in old_sessions[-10:]:
    with open(f) as fh:
        data = json.load(fh)
    print(data["session_id"], data["platform"], len(data.get("messages",[])))

# 2. Read its last user message and assistant response to understand context
with open("path/to/old_session.json") as f:
    data = json.load(f)
messages = data["messages"]
for m in messages[-5:]:
    if m["role"] == "user":
        print(f"Last user: {m['content'][:200]}...")
    elif m["role"] == "assistant" and m.get("content"):
        print(f"Last response: {m['content'][:200]}...")

# 3. Check sessions.json — the pointer was reset to a new session_id
with open("~/.hermes/sessions/sessions.json") as f:
    registry = json.load(f)
# Compare: old session_id vs active session_id for this platform

# 4. The old file is intact — read it and continue from the interruption point
```

**Manual recovery steps for the agent:**
1. Identify the suspended session file
2. Read its last 20-30 messages to understand what was being worked on
3. Summarize the context to the user: "I found you were working on X, we were at step Y, and were interrupted at Z"
4. Write memory entries for any important findings from the old session
5. Continue the task in the active session

The old session file is **NOT deleted** — it's still on disk with full message history. Only the `sessions.json` pointer was reset. You can read it and manually pick up where it left off.

**CLI-based recovery** (if user has CLI access):
```bash
# List available suspended sessions
hermes --list-sessions

# Resume a specific session
hermes --resume 20260513_184022_0fcbc1b9
```

## Prevention

1. **Set GITHUB_TOKEN** — Raise GitHub API limit from 60 to 5,000 req/hr
2. **Increase `restart_drain_timeout`** in config.yaml (e.g., 180s):
   ```yaml
   agent:
     restart_drain_timeout: 180
   ```
3. **Avoid mid-conversation restarts** — If config changes need restart, finish the current task first
4. **Disable Telegram** if not used — its polling failures cascade into full gateway restarts

## Gateway Platform Message Formatting

### `final_response_markdown` is CLI-only

The `display.final_response_markdown` config (values: `strip`, `render`, `raw`) **only controls CLI output formatting**. Gateway platforms (Feishu, Telegram, Discord, etc.) each have their own independent rendering logic that ignores this config.

### Feishu Message Rendering

The Feishu adapter (`gateway/platforms/feishu.py`) decides between two modes:

**Post mode** (rich text) — triggered when `_MARKDOWN_HINT_RE` matches:
- Headings (`#`), lists (`-`, `*`, `1.`), code fences (` ``` `), inline code (`` ` ``), bold (`**`), italic (`*`), strikethrough (`~~`), underline (`<u>`), links (`[]()`), blockquotes (`>`)
- **Pitfall:** Feishu post does NOT render markdown tables — if a table is in the response, the entire message is silently degraded to text mode. Remove tables to get rich formatting.
- **Pitfall:** `_MARKDOWN_HINT_RE` does NOT match table rows (`|...|`). A message that only has a table and no other markdown elements falls through to text mode with raw `|` characters visible.

**Text mode** (plain text) — default fallback:
- Any content without markdown hints
- Messages containing tables (even if they have other markdown)
- Messages where post payload causes `content format of the post type is incorrect` error → auto-retried as text

**Diagnosing "ugly Feishu messages":**
1. **Check for tables** — most common cause of unexpected plain text
2. **Check for missing markdown hints** — ensure at least one heading, bold, or code fence exists
3. **Check if `final_response_markdown` was changed** — it won't help; look in `gateway/platforms/feishu.py` instead
4. **Check model output style** — some models produce less markdown-rich output; this isn't a rendering bug, it's a content style issue

See `references/feishu-rendering.md` for source-code-level detail.
