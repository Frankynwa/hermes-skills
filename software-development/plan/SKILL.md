---
name: plan
description: "Plan mode: write markdown plan to .hermes/plans/, no exec."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, plan-mode, implementation, workflow]
    related_skills: [writing-plans, subagent-driven-development]
---

# Plan Mode

Use this skill when the user wants a plan instead of execution.

## Core behavior

For this turn, you are planning only.

- Do not implement code.
- Do not edit project files except the plan markdown file.
- Do not run mutating terminal commands, commit, push, or perform external actions.
- You may inspect the repo or other context with read-only commands/tools when needed.
- Your deliverable is a markdown plan saved inside the active workspace under `.hermes/plans/`.

## Output requirements

Write a markdown plan that is concrete and actionable.

Include, when relevant:
- Goal
- Current context / assumptions
- Proposed approach
- Step-by-step plan
- Files likely to change
- Tests / validation
- Risks, tradeoffs, and open questions

If the task is code-related, include exact file paths, likely test targets, and verification steps.

## Save location

Save the plan with `write_file` under:
- `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

Treat that as relative to the active working directory / backend workspace. Hermes file tools are backend-aware, so using this relative path keeps the plan with the workspace on local, docker, ssh, modal, and daytona backends.

If the runtime provides a specific target path, use that exact path.
If not, create a sensible timestamped filename yourself under `.hermes/plans/`.

## Multi-Direction Planning (Convergence Pattern)

When a user proposes multiple ambitious directions at once (game dev + quant + AI art + paper), do NOT plan each in equal depth in isolation. The goal is convergence:

1. **Honest feasibility assessment first** — Before any plan, tell the user what's realistically achievable with their constraints (budget, time, skill level). Don't cheerlead; surface real limits. E.g. "stable profitability in quant trading is not realistic for an undergrad, but a well-designed backtest with rigorous methodology is."
2. **Deep research in parallel** — Search GitHub, arXiv, web for each direction simultaneously. Surface concrete repos, papers, tools — not vague suggestions.
3. **Find the convergence** — Look for themes that merge directions. In this session: quant tool + paper + thesis merged into ONE path (quant finance graduation thesis). Game dev and AI art became de-prioritized sub-directions.
4. **Output one integrated roadmap**, not four separate plans. Include: merged timeline, priority allocation (e.g. 60/25/15%), and immediate next actions.
5. **Leave de-prioritized directions as short sections** with "return when" triggers, so the user doesn't feel they were ignored.

See `references/multi-direction-convergence.md` for the worked example.

## Interaction style

- If the request is clear enough, write the plan directly.
- If no explicit instruction accompanies `/plan`, infer the task from the current conversation context.
- If it is genuinely underspecified, ask a brief clarifying question instead of guessing.
- After saving the plan, reply briefly with what you planned and the saved path.
- When the user questions feasibility of a direction, engage honestly — don't just plan around it. Adjust the scope to what's achievable.
