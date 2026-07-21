---
name: post-task-reflection
description: >
  Post-task reflection and self-improvement protocol. Use after completing any
  complex task (5+ tool calls, multi-step analysis, debugging, or when errors
  occurred). Systematically captures what went wrong, what worked, and saves
  durable lessons to memory and skills.
triggers:
  - After any task that involved 5+ tool calls
  - After encountering errors, timeouts, or dead ends
  - After debugging or troubleshooting sessions
  - When the user asks "what did you learn" or "reflect on this"
  - At the end of any significant work session
---

# Post-Task Reflection Protocol

## When to Reflect

After completing a task, ask yourself:
1. Did I waste tool calls on approaches that failed?
2. Did I hit errors that could have been avoided with prior knowledge?
3. Did I discover something about the environment, tools, or user's setup?
4. Did the user correct me or redirect my approach?

If **any** answer is yes → run this reflection.

## Reflection Checklist (5 minutes max)

### Step 1: Error Inventory
List every error/timeout/dead-end encountered:
- What command/approach failed?
- Why did it fail?
- What was the correct approach?

### Step 2: Tool Call Efficiency
- How many tool calls did I make?
- How many were wasted (timeouts, wrong approach, redundant)?
- Could I have done this in fewer calls?
- Pattern: parallel independent calls first, sequential dependencies second

### Step 3: Knowledge Gaps Filled
- What did I learn about the user's environment?
- What new tool/command/approach did I discover?
- What assumptions were wrong?

### Step 4: Save Durable Knowledge
Use `memory` tool to save:
- Environment facts (OS, installed tools, file locations)
- Tool quirks (pandas not in sandbox, WeChat dirs too large for find)
- User preferences discovered during the task
- Workarounds for known problems

Use `skill_manage` to:
- Patch existing skills if I hit issues not covered by them
- Create new skills if I discovered a non-trivial workflow

### Step 5: Offer Summary to User
Briefly tell the user:
- What went well
- What could have been better
- What was saved for next time

## Memory Entry Format

```
[Topic] experience: 1) [lesson]; 2) [lesson]; 3) [lesson]
```

Keep entries compact. Group related lessons under one entry.

## Anti-Patterns to Avoid
- Don't save trivial facts (e.g., "Python uses print()")
- Don't save task progress or temporary state
- Don't save raw data dumps
- Don't create skills for one-off tasks
- Don't duplicate existing memory entries
- **NEVER** say "要不要我帮你记下来？" or "remind me to save this" — just save it. The user expects you to be proactive, not to offload judgment onto them.

## Command Approval UX

When a terminal command may trigger a security approval (modifying dotfiles, piping to interpreters, etc.), add a Chinese comment in the command explaining its purpose. Example:
```bash
# 把 API key 写入 shell 配置（永久生效）
echo "export KEY=value" >> ~/.zprofile
```
This reduces user friction — they can approve confidently when they understand the intent.

## Proactive Memory Saving (Mid-Conversation)

Memory saving is NOT only a post-task activity. Save durably **during** the conversation when you encounter:
- User preferences, habits, communication style corrections
- Project facts, architecture decisions, environment details
- Corrections to your behavior ("don't do X", "always do Y")
- New tool/API/workflow discoveries

**Critical rule: NEVER tell the user "remind me to save" or "let me know if you want me to remember this."** The user expects proactive intelligence — if something is worth remembering, save it immediately. Telling the user to prompt you to save is a failure of agency.

**Memory vs Skill decision:**
- `memory` tool → stable facts: who the user is, environment state, project configs, preferences
- `skill_manage` → reusable procedures: how to do a class of task, debugging patterns, workflows

If memory is near capacity (95%+), prioritize: user preferences > environment facts > project details > tool quirks. Evict stale entries to make room.

## Quick Self-Check Before Saving
- "Will this still be useful in 3 months?"
- "Would I need to re-discover this if I forgot?"
- "Is this specific enough to act on?"
