# Odyssey: Overnight Dialogue + Planning System

## What it is

A nightly dialogue system with multi-scale planning (daily/weekly/monthly/yearly). Combines academic research, dialogue framework design, and automation. Delivers a structured 22:30 question each night + morning planning card.

## Architecture

```
~/.hermes/overnight/                    # Design & state
├── odyssey-research.md                 # Academic foundations
├── dialogue-framework.md               # 5 themes × 5 days × 29 questions
├── planning-templates.md               # Daily/weekly/monthly/yearly templates
├── implementation-plan.md              # Week 1-4 rollout roadmap
├── state.json                          # Current theme week, question progress
└── conversations/                      # Archived dialogue JSONs

~/scripts/odyssey.py                    # Automation engine (5 subcommands)

Cron jobs (recurring):
├── e88c630bd2c5  奥德赛晚间对话  22:30 daily  → python3 odyssey.py evening
└── 7576aac2d3d1  奥德赛晨间卡片   7:00 daily  → python3 odyssey.py morning
```

## Key design decisions

1. **Cron pushes the FIRST question only.** Follow-up dialogue happens in the live Feishu session, not via cron. Cron cannot do interactive dialogue — the user might reply in seconds while cron's best granularity is minutes.

2. **Delivery: Hermes cron `deliver: origin`, NOT lark-cli.** lark-cli's `im +messages-send` returns OK but the user may not see the messages if lark-cli's bot app differs from the Hermes Feishu integration app. Instead, the cron agent outputs the message as its final response, and Hermes delivers it to the current conversation via `deliver: origin`.

3. **lark-cli for READ only** (reply detection, history). The read path (`+chat-messages-list`) works reliably and is used by psych-nlp. Only the send path is unreliable.

4. **Question parsing**: Script parses `dialogue-framework.md` to extract questions by theme and day — single source of truth.

5. **Psych-nlp integration**: Morning card calls `LongitudinalTracker.get_trend(days=7)` for anxiety/avoidance snapshot.

6. **State tracking**: `state.json` tracks current week, questions asked per week/day, progress through 5-theme rotation.

## Pitfalls from implementation

1. **Silent cron failure**: The original overnight cron job (once at 23:05) never fired — `last_run_at` stayed null. Documented as a pitfall in the parent skill. ALWAYS verify with `cronjob(action='list')`.

2. **lark-cli send messages invisible**: Messages sent via `lark-cli im +messages-send --text` returned `"ok": true` with valid message_id but the user never saw them — the lark-cli bot app differs from the Hermes Feishu integration app. Use Hermes cron delivery instead.

3. **Cron for follow-up is wrong**: Initial design had a 22:50 follow-up cron. User correctly identified this is absurd — they might reply at 22:31. Follow-up dialogue MUST happen in the live session.

4. **Tirith scanning**: Chinese text in `--markdown` triggers confusable_text scanning. Use `--text -` with pipe input for lark-cli reads only.

5. **Build-gate violation**: Agent built cron jobs and deployed without user approval. User feedback: "主角是我，方案都没给我审批就做了什么完善了什么". Now codified as a gate in the parent skill.

## Integration points

- psych-nlp `analyze_daily_reflection.py` — already reads Feishu replies in 21:00-23:00 window; Odyssey replies in same window are picked up
- psych-nlp `LongitudinalTracker` — provides trend data for morning card psych snapshot
- Existing psych-nlp cron jobs `1753a8066171` (21:30) and `3081e9708879` (23:00) — run adjacent to Odyssey, no conflict
