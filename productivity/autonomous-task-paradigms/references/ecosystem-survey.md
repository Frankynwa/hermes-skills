# Autonomous Task Paradigms — Ecosystem Survey

Survey conducted 2026-07-20. Searched skills.sh, GitHub, and Hermes internals for existing autonomous task execution patterns.

## Key Finding

**No existing skill packages the "bedtime questionnaire → cronjob" or "trigger-word no-questions" pattern for Hermes.** The building blocks exist (cronjob, delegate_task, /background) but no one has assembled them into a reusable interaction protocol with permission tiers and quality gates.

---

## External Ecosystem (skills.sh)

### continuous-agent-loop
- **Source:** affaan-m/everything-claude-code
- **Installs:** 5.1K | **Security:** PASS/PASS/PASS
- **What it does:** Loop patterns for running Claude Code autonomously — pipelines, DAG orchestration, parallel agents, quality gates, context persistence
- **Relevance:** The loop selection flow and quality gate concepts are adaptable. Claude Code-specific (`claude -p` pipes), not portable directly.
- **URL:** https://skills.sh/affaan-m/everything-claude-code/continuous-agent-loop

### autonomous-agent-harness
- **Source:** affaan-m/everything-claude-code
- **Installs:** 4.0K | **Security:** PASS/WARN/WARN
- **What it does:** Turn Claude Code into a persistent, self-directing agent system. Consent boundaries, scheduled/continuous operation, context across sessions.
- **Relevance:** Consent/safety boundary patterns align with our permission tiers. Explicitly mentions "replicate Hermes functionality" as a use case.
- **URL:** https://skills.sh/affaan-m/everything-claude-code/autonomous-agent-harness

### hermes-agent-mission-control
- **Source:** aradotso/hermes-skills
- **Installs:** 178 | **Security:** PASS/PASS/WARN
- **What it does:** Hermes-specific mission control. 178 installs, not mature enough to rely on.
- **Verdict:** Too small to adopt.

### overnight-repo-auditor
- **Source:** onewave-ai/claude-skills
- **Installs:** 151
- **What it does:** Overnight repo auditing for Claude Code. Similar concept but Claude-specific and tiny.
- **Verdict:** Not relevant.

---

## Hermes Built-in Building Blocks

| Mechanism | What It Provides | Used By |
|-----------|-----------------|---------|
| `cronjob` tool | One-shot/recurring scheduled tasks with delivery to messaging platforms | Overnight mode core engine |
| `delegate_task` tool | Subagent spawning, parallel execution (up to 3 concurrent), context isolation | 20min mode core engine |
| `/background` slash command | Run prompt in background process | Alternative execution path |
| `subagent-driven-development` skill | Plan → implement → two-stage review (spec + quality) | Quality gates pattern source |
| `writing-plans` skill | Structured implementation plan creation | Could pre-plan overnight tasks |
| `webhook-subscriptions` skill | Event-driven agent triggering | Future extension: trigger on conditions |

---

## Patterns Adopted from External Work

### From continuous-agent-loop: Loop Selection Flow
Instead of always running serial or always parallel, analyze task dependencies and choose:
- **All independent** → parallel via delegate_task (max 3 concurrent)
- **All sequential** → serial in listed order
- **Mixed** → parallelize independent tasks, serialize dependent chains

### From subagent-driven-development: Quality Gates
After task completion, run a mandatory self-audit before delivering results:
1. **Completion Audit:** Mark each task as COMPLETED / PARTIAL / FAILED
2. **Sanity Check:** Verify outputs exist and results are reasonable
3. **Delivery Decision:** Based on audit outcome, decide what to report

### From autonomous-agent-harness: Consent Boundaries
Our permission tier system (🔒 Read-only / ✏️ Local writes / 🚀 Full access / ⚠️ Custom) already aligns with the consent boundary concept. The harness explicitly scopes what the agent is allowed to do — we encode this in the cron prompt as explicit rules.

---

## What Makes Our Approach Novel

1. **Hermes-native** — Uses cronjob + delegate_task, not Claude Code pipes
2. **Interactive protocol** — 5-question structured questionnaire before execution, not a static config
3. **Permission tiers** — Granular scoping that the cron agent must respect
4. **Quality gates** — Mandatory self-audit before delivery
5. **Dual-mode** — Overnight (cronjob) + rapid (delegate_task) in one skill
6. **Trigger-word activation** — Natural language triggers for 20min no-questions mode
