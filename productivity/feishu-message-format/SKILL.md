---
name: feishu-message-format
description: >
  Feishu message formatting and interaction rules for the Hermes gateway adapter.
  Covers markdown table rendering via interactive cards, suggested follow-up questions,
  card button callbacks, and adapter extension patterns.
  Apply when the current platform is Feishu (Lark).
version: 3.0.0
author: Hermes Agent
license: MIT
---

# Feishu Message Format Rules

Apply these rules when the active platform is Feishu/Lark.

## Tables: Now Supported via Interactive Cards

**As of 2026-05-27**, Hermes converts markdown tables to **Feishu interactive cards** with native `{"tag": "table", ...}` elements. This was implemented by studying how OpenClaw handles the same problem.

The conversion pipeline in `gateway/platforms/feishu.py`:

1. `_build_outbound_payload()` detects markdown tables via `_MARKDOWN_TABLE_RE`
2. If tables found → `_build_card_with_table()` builds an interactive card:
   - Text segments → `{"tag": "markdown", "content": "..."}`
   - Table segments → `{"tag": "table", "columns": [...], "rows": [...]}`
3. Sent as `msg_type="interactive"`

**Fallback chain** (if card is rejected by API):
- Interactive card → post format with list-converted tables → plain text

**Result**: You CAN use markdown tables freely in Feishu replies. They render as proper bordered tables with headers.

## When NOT to use tables

- Very wide tables (6+ columns) may overflow on mobile
- For 2-3 simple key-value pairs, lists are still cleaner
- Tables inside code blocks are not converted (they stay as code)
- **⚠️ Messages with 5+ tables may cause rendering failures** — the user reported tables disappearing entirely when a message contained 8+ tables plus code blocks. Keep tables per message to **3-4 max**. Split long multi-table comparisons into separate messages.
- When a message is very long (3000+ chars) with many tables, the card conversion may fail silently — the user sees text but no tables. **Split into shorter messages.**
- If tables disappear, re-send just the tables in a separate message with less surrounding text.

## Other Format Guidelines

- **Section headings** (## or ###) for grouping
- **Bold labels** for key-value pairs in list format
- **Code blocks** (```) for code snippets
- **Blockquotes** (>) for notes and summaries
- Avoid mixing multiple tables and code blocks in one message — keep it scannable

## Suggested Follow-up Questions (Coze-style)

**As of 2026-05-28**, the feishu adapter can append interactive question buttons after each agent reply, similar to Coze/Dify's "recommended questions" feature.

**Enable**: `feishu.suggested_replies: true` in config.yaml, or `FEISHU_SUGGESTED_REPLIES=true` env var.

**How it works**:
1. After the last chunk of a reply, `_generate_suggested_questions()` extracts topics (code blocks, inline code, headings, technical terms) and generates 2-3 Chinese question templates
2. For interactive cards (table messages): buttons are injected inline into the card
3. For text/post messages: a standalone follow-up card with buttons is sent via `asyncio.create_task()`
4. When a user clicks a question button, `_handle_card_action_event()` detects `hermes_suggested_question` in the action value and routes it as `MessageType.TEXT` (not COMMAND), so the agent treats it as a normal user question

**Action routing hierarchy** in `_on_card_action_trigger()`:
- `hermes_action` in value → approval handler
- `hermes_update_prompt_action` in value → update prompt handler
- `hermes_suggested_question` in value → TEXT message to agent (new)
- Everything else → generic COMMAND handler

## Technical Reference

Key functions in `feishu.py`:
- `_parse_md_table(lines)` → parses markdown table into `{columns, rows}`
- `_build_card_with_table(content)` → builds interactive card JSON
- `_convert_tables_to_lists(content)` → legacy fallback (still used as error recovery)
- `_generate_suggested_questions(content)` → rule-based topic extraction → question templates
- `_build_suggested_question_buttons(questions)` → button elements with `hermes_suggested_question` value
- `_inject_suggested_questions_into_card(card_json, questions)` → append buttons to existing card
- `_send_suggested_questions_followup(chat_id, content, reply_to)` → standalone card for text/post

See `references/feishu-adapter-architecture.md` for the full adapter extension patterns (settings, card actions, interactive buttons).
