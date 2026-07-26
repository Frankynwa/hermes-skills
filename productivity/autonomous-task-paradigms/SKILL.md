---
name: autonomous-task-paradigms
description: |
  Four autonomous task paradigms with a decision tree for routing:
  1. Overnight 8h mode — structured bedtime questionnaire → one-shot cronjob with quality gates, checkpointing, and failure recovery
  2. Daytime 20min mode — no-questions trigger word, immediate delegate_task, 20min timebox
  3. Recurring cron templates — daily/weekly/hourly persistent jobs (arXiv digest, morning briefing, watchdog, etc.)
triggers:
  - overnight: 过夜模式, overnight, 睡前任务, 晚上跑, 通宵跑
  - 20min: 20min, 免问, auto, 直接跑, ⚡, 无询问, 快跑
---

# Autonomous Task Paradigms

Three reusable autonomous execution protocols, plus a task routing decision tree. The key insight: Hermes is synchronous per-turn — to run unattended, we use cronjob (overnight) or delegate_task (quick burst).

**Background:** See `references/ecosystem-survey.md` for the full survey of existing autonomous task patterns across Claude Code, Hermes, and skills.sh — and why this skill fills a genuine gap.
**Overnight implementation reference:** `references/odyssey-implementation.md` — full overnight dialogue + planning system with cron orchestration, Feishu integration, and psych-nlp data injection.

---

## Task Routing Decision Tree

Before choosing a paradigm, route the task through three questions. For a detailed comparison of MoA vs Multi Agents vs 20min, see `references/moa-vs-multi-agents.md`.

```
任务能拆成清晰的子任务边界和交付物吗？
├── 不能 → MoA 委员会（local-moa skill）
│            ⚠️ 前置条件：先跑互补性测试确认 MiMo+DeepSeek 互补性 > 20%
│            python3 ~/scripts/model_complementarity.py --report
│            互补性 < 5% 则 MoA 无价值，退回单模型
│            （需要全局视角、不可拆分的深度推理）
└── 能 → 子任务之间有强依赖吗？
    ├── 没有 → Paradigm 2: 20min 模式（并行派发 + 主 agent 整合）
    │            （独立任务并行跑，主 agent 只在最后汇总）
    └── 有 → 整合阶段修补工作多吗？
        ├── 不多 → Paradigm 2: 20min 模式够了
        │            （子代理质量稳定，主 agent 基本只是拼接）
        └── 多 → Paradigm 4: Multi-Agent Relay 模式
                    （代理间实时修正循环，不等到整合阶段才暴露问题）
```

**判断标准：** 能在 30 秒内画出清晰子任务边界 → 能拆。不能 → MoA。整合修补"多不多"取决于实际体验——如果主 agent 整合时经常需要大量修补而非简单拼接，就值得上 Multi Agents。

**典型分配：**
- LVGL 新页面开发 → 能拆 + 有依赖 + 修补通常不多 → 20min
- LVGL 运行时 bug 调试 → 不能拆 → MoA
- AlphaSeeker 新因子开发 → 能拆 + 无强依赖 → 20min
- AlphaSeeker 策略争议分析 → 不能拆 → MoA
- 论文解读批判 → 不能拆 → MoA
- 飞书消息/审批 → 单模型就够了

---

## Paradigm 1: Overnight Mode (8-hour autonomous)

### When triggered
User says any overnight trigger phrase. Run the structured questionnaire IMMEDIATELY — don't wait, don't ask if they're sure.

### Step 1: Structured Questionnaire

Ask these 5 questions in sequence (use clarify() with choices where applicable). Do NOT dump all at once — ask one at a time unless the user has already provided some answers in their trigger message.

#### Q1: Task List
"What tasks do you want me to work on overnight? List them, with any specifics."

User provides tasks. Paraphrase back for confirmation.

#### Q2: Priority & Ordering
"Do these have a priority order, or should I run them in parallel where possible?"

Options: "串行按顺序" / "能并行就并行" / "你决定"

#### Q3: Permission Tier
"What am I ALLOWED to do without asking?"

| Tier | Scope |
|------|-------|
| 🔒 Read-only | Only read files, search web, analyze — no writes, no git, no API calls that modify |
| ✏️ Local writes | Read + write local files, run scripts, git commit (no push) |
| 🚀 Full access | Anything including git push, deploy, API calls, package installs |
| ⚠️ Custom | User specifies boundaries (e.g. "可以 git push 但不能花钱") |

Present as options, user picks one.

#### Q4: Error Handling
"What should I do if a task fails?"

Options:
- "Skip and continue with next task" (default)
- "Stop everything and report"
- "Retry up to 3 times, then skip"

#### Q5: Morning Delivery
"How should I deliver results?"

Options:
- "Full summary in the morning" (default — cron delivers back to this chat)
- "Urgent items only, details in a file"
- "Save everything to local files, no push notification"

### Step 2: Craft the Cronjob Prompt

After all 5 questions are answered, craft a self-contained cronjob prompt. The prompt must include these sections:

1. **Header:** `## Overnight Autonomous Session`
2. **Task list:** Full task descriptions with file paths and context
3. **Permission boundaries:** Explicit rules from Q3
4. **Error handling:** Rules from Q4 + failure mode recovery rules (see Failure Modes table below)
5. **Execution strategy** (see Step 3)
6. **Memory checkpointing:** After EACH completed task, update `~/.hermes/overnight/task-queue.md` to mark `[x]`. This ensures partial progress survives cron crashes.
7. **Quality gates** (see Step 4)
8. **Delivery instructions:** From Q5

**CRITICAL:** The cronjob prompt is for a FRESH session with no memory of this conversation. Include ALL context — file paths, project directories, API keys reference, etc. The cron session knows NOTHING about what we discussed. Write in the SAME LANGUAGE the user is speaking.

### Step 3: Inject Loop Selection Flow

Add an execution strategy section to the cron prompt, based on task dependencies:

```
## Execution Strategy

Analyze task dependencies and choose:

- ALL INDEPENDENT → parallel (use delegate_task, up to 3 concurrent subagents)
- ALL SEQUENTIAL → serial execution in listed order
- MIXED → parallelize independent tasks, serialize dependent chains

State which strategy you chose and why.
```

### Step 4: Inject Quality Gates

Add a mandatory self-audit section at the end of the cron prompt, adapted from subagent-driven-development's two-stage review:

```
## Quality Gates (run after all tasks complete)

### Gate 1: Completion Audit
For each task, mark status:
- [ ] COMPLETED — all sub-steps done
- [ ] PARTIAL — some steps done, see notes
- [ ] FAILED — blocked or errored

### Gate 2: Sanity Check
For each completed task, verify:
- Results look reasonable? (no obvious nonsense)
- File outputs exist at expected paths?
- Numbers/calculations make sense?

### Gate 3: Delivery Decision
- If all tasks COMPLETED → deliver full summary
- If some PARTIAL → deliver summary with clear "INCOMPLETE" markers
- If critical tasks FAILED → deliver error report with diagnostic info
```

### Step 5: Persist Task Queue (survival guarantee)

Before creating the cronjob, write the task list to `~/.hermes/overnight/task-queue.md` so it survives cron failures:

```markdown
# Overnight Task Queue — 2026-07-20
**Created:** 23:05
**Permission:** ✏️ Local writes
**Error policy:** Skip and continue

## Tasks
- [ ] Task 1: Run AlphaSeeker full backtest → save to ~/course-project-ex2-team-6/results/
- [ ] Task 2: Fetch latest arXiv cs.AI papers → append to ~/Documents/arXiv/papers_record.xlsx
- [ ] Task 3: Check all monitored GitHub repos for new issues

## Status
- Cron job ID: <id>
- Fired at: <time>
```

This file serves as a **checkpoint**. If the morning delivery is empty or the cron silently failed, the user can say "继续昨晚的任务" and the agent reads this file to resume.

### Step 6: Create the Cronjob

```python
cronjob(
    action="create",
    name="Overnight autonomous session",
    schedule="<ISO timestamp 2 minutes from now>",
    prompt="<the crafted prompt>",
    deliver="origin",  # back to this Feishu chat
    skills=[],  # any skills the tasks need
    toolsets=["terminal", "file", "web", "delegation"]  # match permission tier
)
```

- Schedule: always 2 minutes from now (ISO 8601 format)
- deliver: "origin" so results come back to this chat
- Permission tier → toolsets: Read-only=["file","web"], Local=["terminal","file","web"], Full=["terminal","file","web","delegation"]
- After creating the cron, immediately update the task queue file with the cron job ID

### Step 7: Confirm & Summarize

After creating the cronjob, tell the user:
- "Cron job created, will fire at [time]"
- "Tasks: [summary]"
- "Permission: [tier]"
- "You'll see results here in the morning 🌅"

### Pitfalls
- Do NOT create the cronjob until ALL 5 questions are answered
- If the user provides partial answers in the trigger message (e.g. "过夜模式，跑 AlphaSeeker 回测，可以写文件"), pre-fill those answers and skip those questions
- The cronjob session has NO conversation context — the prompt must be fully self-contained
- Timezone: cron uses system time (macOS local time), not UTC
- NEVER set schedule more than 1 hour in the future — the user should be about to sleep
- Quality gates are mandatory — the cron agent MUST run the self-audit before delivering
- Parallel subagents must not touch the same files (race condition risk)
- **CRITICAL: "once at" cron jobs may silently fail to fire** — when schedule is set to the current time or a few minutes from now, the scheduler may never trigger the job. Symptom: `last_run_at: null, state: scheduled` long after the scheduled time. **After creating the cronjob, IMMEDIATELY verify with `cronjob(action='list')` that `last_status` is non-null.** If `last_run_at` is still null 5 minutes after the scheduled time, the job silently failed. **Recovery: prefer running the overnight tasks in the CURRENT session** (the agent stays active until the user returns), OR use `cronjob(action='run')` to force-trigger it, OR create with schedule 15+ minutes in the future to give the scheduler time to register. Never let the user go to sleep without confirming the job is actually running.

- **Cron ≠ interactive dialogue** — 用 cron 做追问/对话是错误设计。用户可能在秒级回复，但 cron 最快粒度为分钟级。交互式对话必须留在当前 session 中处理，cron 只负责"定时触发第一个问题"这一步。

- **Gate: BUILD only after user APPROVES design** — 不要在用户审阅方案前擅自进入构建阶段。先呈现设计方案 → 等用户审批/修改 → 再动手实现。跳过这个 gate 就是抢用户的决策权，触发用户"主角是我，为什么方案都没给我审批"的合理愤怒。

### Failure Modes & Recovery

The overnight cron agent faces these known failure modes. Encode recovery rules directly in the cron prompt:

| Failure Mode | Symptom | Recovery Rule (in cron prompt) |
|-------------|---------|-------------------------------|
| **Loop churn** | Same subtask retried >3x with no progress | Freeze that task, skip to next, report in morning |
| **Context exhaustion** | Token limit approaching, compression degrading | Stop new tasks, run quality gates on what's done, deliver partial |
| **API rate limit** | HTTP 429 from external APIs | Back off 60s, retry once. If still failing, skip and note |
| **Cost drift** | Single task consuming excessive turns | Hard cap: 15 turns per task. Exceeded → mark FAILED, move on |
| **Silent failure** | Cron didn't fire or errored before delivery | Task queue file survives — user can resume with "继续昨晚的任务" |
| **Race condition** | Two subagents modified same file | Prevention: cron prompt must list which files each task touches. Never assign overlapping files to parallel agents |

### Resuming After Failure

If the morning delivery is empty or incomplete:

1. Read `~/.hermes/overnight/task-queue.md`
2. Parse which tasks are `[ ]` (pending) vs `[x]` (done)
3. Ask user: "昨晚只完成了 X/Y 个任务。继续剩下的？"
4. If yes, create a new 20min-mode run for remaining tasks

---

## Paradigm 2: 20-Minute No-Questions Mode

### Why this mode exists

Traditional agent interaction is a ping-pong pattern: user sends → waits → reads response → sends next → waits… This fragments time into 2-5 minute chunks. The user can't do deep work — they're stuck monitoring the agent, filling gaps with short-form content or trivial tasks.

**20-minute mode inverts this:** the user defines the goal upfront, grants permission, then walks away for an uninterrupted block of focused work (study, coding, reading). The agent runs autonomously and delivers results when done. The user's attention stays intact.

The 20-minute budget is calibrated for a Pomodoro-like focus block — enough time for the agent to accomplish meaningful work, but short enough that the user can check results at the next natural break.

### When triggered
User includes any 20min trigger phrase in their message. The trigger can be anywhere in the message — beginning, end, or inline.

### Two-Phase Protocol

#### Phase 1: Alignment (explicit, thorough, before execution starts)

The quality of autonomous output depends entirely on the quality of upfront alignment. If the agent misunderstands the goal or misses context, 20 minutes of autonomous work goes in the wrong direction. This phase invests a few extra turns to ensure the autonomous phase produces the same quality as if the user were watching.

**Principle:** "What would I need to know to deliver the same result as if the user were guiding me turn-by-turn?"

Key dimensions to align on:

**Q1: Goal & Scope**
"What exactly should I accomplish? What does 'done' look like?"
- Ask for the concrete deliverable, not just the topic
- If the user says "检查回测", ask "检查什么维度？只看收益还是也看信号/风险/异常？"

**Q2: Context & Constraints**
"What context do I need that I might not have?"
- File paths, project directories, data sources
- Known pitfalls or edge cases the user is aware of
- "Anything you've learned from doing this manually that I should know?"

**Q3: Success Criteria**
"How will you judge whether the result is good enough?"
- What metrics matter? What thresholds?
- What would make you say "this was worth it" vs "I should have done it myself"?

**Q4: Permission**
"Permission for this run?"

| Shortcut | Meaning |
|----------|---------|
| 🔒 只读 | Read files, search, analyze only |
| ✏️ 写本地 | Read + write files, run scripts, git commit |
| 🚀 全权限 | Anything including push, deploy, spend |

If user doesn't specify, default to ✏️.

**Q5: Anti-goals (optional, ask only if task is complex)**
"What should I explicitly NOT do? What would be a waste of time?"
- Prevents the agent from going down rabbit holes
- Example: "不要改信号逻辑，只看数据" / "别碰前端代码"

**Flexibility rule:** If the user provides rich detail in the trigger message (goal + context + success criteria), skip the questions they already answered. Never ask a question the user already addressed. Maximum 2-3 turns for alignment — if it's taking longer, the task may be too vague for autonomous mode and should be decomposed into a smaller scope.

#### Phase 2: Autonomous Execution (budget: 20 minutes, ZERO interaction)

After Phase 1 confirmation, execute with these iron rules:

1. **Parse the task** — extract the confirmed goal
2. **Make assumptions** — do NOT call clarify(). If ambiguous, make the best reasonable assumption and note it
3. **Decompose immediately** — break into subtasks
4. **Execute via delegate_task** — parallelize where possible (up to 3 concurrent subagents)
5. **Self-audit** — run lightweight quality check before reporting (see below)
6. **Return structured report** — what was done, what assumptions were made, results

- **ABSOLUTELY NO clarify() calls during Phase 2** — this is the defining characteristic
- **No permission re-requests** — the Phase 1 answer is binding for the entire run
- **Timebox is a budget, not a quota** — aim to finish within 20 minutes, but stop early when quality is sufficient. The rule: if another 5 minutes of work won't produce a meaningful improvement the user would notice, deliver now. Do NOT pad time or over-polish just to hit the 20-minute mark.
- If truly impossible without clarification, do what you can and flag what's missing
- If a subtask runs long, return partial results with clear markers
- State assumptions explicitly in the summary: "I assumed X, Y, Z"
- Use delegate_task (not execute_code) so subagents can reason about errors

#### Self-Audit (run after execution, before reporting)

A lightweight version of the overnight quality gates. Takes <1 minute:

```
### Self-Audit (internal, not shown to user unless issues found)

1. COMPLETION CHECK: Did each subtask finish?
   - All done → ✅
   - Some partial → flag in report

2. SANITY CHECK: Do results pass the sniff test?
   - Numbers in reasonable ranges?
   - Files created at expected paths?
   - No obvious garbage output?

3. DIMINISHING RETURNS CHECK: Is further work worth it?
   - If the task is done and quality is good → deliver now, don't pad
   - If another 5 min would produce a visible improvement → continue
   - If already past the point of meaningful gains → stop, deliver

4. ASSUMPTIONS CHECK: Did any assumption turn out wrong?
   - If yes → flag in report, explain impact
```

If the self-audit finds issues, include them in the report under a `⚠️ Issues Found` section. Do NOT silently hide problems.

#### Report Format

After self-audit passes, deliver a structured report:

```
## ⚡ 20min 任务完成

**任务：** [original goal]
**耗时：** [actual time]
**权限：** [tier used]

### 做了什么
- [subtask 1 result]
- [subtask 2 result]

### 假设
- [assumption 1]
- [assumption 2]

### ⚠️ 注意事项（如有）
- [any issues found during self-audit]
```
### Complete Example

**Trigger:**
> User: "20min 检查 AlphaSeeker 最近一周回测有没有异常"

**Phase 1 (alignment):**
> Agent: "确认目标：检查回测异常。几个问题对齐一下——检查哪些维度？只看收益曲线还是也查信号分布、最大回撤、换手率？"
> User: "收益和信号分布就行，风险指标不用"
> Agent: "明白。数据源用 ~/course-project-ex2-team-6/ 的对吧？有什么我已经知道的坑吗？"
> User: "对，注意 7/16 那天是除权日，数据可能有跳变"
> Agent: "收到。权限 ✏️ 写本地可以？"
> User: "可以"
> Agent: "对齐完成。开始 20 分钟自主运行，不再询问。"

**Phase 2 (autonomous):**
1. Context applied: project path, skip risk metrics, 7/16 ex-right date noted
2. Delegate: 2 parallel subagents — one checks returns data (flagging 7/16), one checks signal logic
3. Self-audit: both returned valid, 7/16 handled correctly
4. Report:

```
## ⚡ 20min 任务完成

**任务：** 检查 AlphaSeeker 最近一周回测异常
**耗时：** ~8 分钟
**权限：** ✏️ 写本地

### 做了什么
- 拉取最近 5 个交易日回测数据：累计收益 +1.2%，跑赢基准 +0.8%
- 信号分布检查：5 级信号占比正常，无异常跳变
- 已将详细数据写入 results/weekly_check_2026-07-20.csv

### 假设
- 项目路径 ~/course-project-ex2-team-6/
- "最近一周" = 最近 5 个交易日（7/14-7/18）

### ⚠️ 注意事项
- 无异常。7/17 信号 4→3 降级属正常波动（置信度仍在阈值内）
```

### Pitfalls
- **Alignment is the quality guarantee** — if you skip context questions because they feel "slow," the autonomous output will be worse than interactive mode. The user chose this mode to free their attention, not to get lower quality. Invest the turns upfront.
- Phase 1 should be thorough but bounded — align on goal, context, success criteria, and permissions. Never more than 3 turns.
- If user provides rich context upfront (goal + known pitfalls + paths), skip the questions they already answered
- Once Phase 2 starts, there is NO going back to ask questions
- Do NOT overthink — the point is speed over perfection
- If tasks fail, report the failure honestly — don't silently skip
- Use delegate_task (not execute_code) so subagents can reason about errors

---

## Paradigm 3: Recurring Cron Templates

For tasks that repeat on a fixed schedule — daily standup, weekly review, monitoring. These are persistent cron jobs (not one-shot). The user triggers setup once, then it runs forever.

### When to suggest these
- User says "每天早上帮我查一下…" / "每小时监控…" / "每周一跑…"
- User has a recurring data-collection or monitoring need
- User wants a standing notification without remembering to ask

### Template Table

| Template | Schedule | Typical Prompt | Use Case |
|----------|----------|---------------|----------|
| 🌅 Morning briefing | `0 8 * * *` | "Check arXiv for new papers in cs.AI, review GitHub notifications, summarize" | 睡醒看到今日要点 |
| 📊 Daily data sync | `0 9 * * 1-5` | "Pull latest AlphaSeeker market data, run quick scan, report anomalies" | 交易日数据更新 |
| 🔍 Hourly watchdog | `0 * * * *` | "Check if [service] is responding, alert if down" | 服务健康监控 |
| 📝 Weekly review | `0 10 * * 1` | "Summarize last week's GitHub activity: PRs merged, issues opened, commits" | 周一回顾 |
| 🌙 Nightly build | `0 2 * * *` | "Run full test suite, security scan, generate coverage report" | 夜间全量检查 |
| 📡 arXiv digest | `0 7 * * 1,3,5` | "Fetch new cs.AI papers, rank by relevance, deliver top 5 with summaries" | 论文追踪 |

### Setup Protocol

When user requests a recurring task:

1. **Confirm:** "Should this run on a fixed schedule? I'll set up a recurring cron job."
2. **Pick template:** Show the table, let user choose or customize
3. **Permission:** Same tiered model as overnight mode (🔒/✏️/🚀)
4. **Create persistent cron:**

```python
cronjob(
    action="create",
    name="<descriptive name>",
    schedule="<cron expression>",
    repeat=0,  # 0 = run forever
    prompt="<self-contained task description>",
    deliver="origin",
    skills=["<relevant skills>"],
    toolsets=["terminal", "file", "web"]
)
```

5. **Confirm:** "Created. Next run: [time]. To stop: `hermes cron remove <id>`"

### Key differences from Overnight Mode
- **No questionnaire** — recurring tasks have a fixed scope
- **repeat=0** (forever) not one-shot
- **Minimal delivery** — recurring jobs should be concise. No one wants a 2000-word essay every hour
- **Include stop instructions** — always tell the user how to disable it

### Pitfalls
- Don't create recurring crons without explicit user request — they persist until removed
- Hourly crons with heavy computation will burn tokens fast — keep prompts minimal
- If a recurring cron starts failing silently, the user won't notice until they check. Add a health check pattern: "If you cannot complete this task, explicitly say FAILED: <reason>"

---

## Paradigm 4: Multi-Agent Relay Mode (CrewAI)

### Why this mode exists

20min mode uses delegate_task: the main agent dispatches subagents, collects results, integrates. Subagents cannot communicate with each other — the main agent is the relay. This works when subagent outputs are independent and integration is simple. But when subagent B depends on subagent A's output and A's quality is inconsistent, the main agent ends up doing heavy repair work in the integration phase. The user sees the final result, but the machine did more turns than necessary, and quality suffered from the Chinese whispers of "A → main agent → B" relay.

Multi-Agent Relay mode uses CrewAI to let agents communicate directly. A code reviewer agent can flag an issue to the original author agent, the author fixes it, the reviewer re-checks — all without the main agent stepping in. This is automatic correction loops, not manual re-dispatch.

### When to use

Only when the task satisfies ALL of:
1. Clear subtask boundaries (can decompose)
2. Strong dependencies between subtasks (B needs A's output)
3. Integration/repair work is consistently heavy in 20min mode

If integration in 20min mode is just light stitching, this mode is overkill — the framework overhead outweighs the benefit.

### Key difference from 20min mode

| | 20min mode | Multi-Agent Relay |
|---|---|---|
| Agent communication | Through main agent only | Direct agent-to-agent |
| Error correction | Main agent spots errors at integration → re-dispatches | Reviewer agent flags → author agent fixes in real-time |
| Human attention cost | Low (hands-off during execution) | Lower (fewer integration failures mean fewer re-runs) |
| Setup cost | Zero (uses delegate_task) | Pip install crewai + define agent roles |
| Token overhead | Baseline | Slightly higher (agent-to-agent messages), but offset by fewer re-runs |

### Setup

CrewAI is the recommended framework for Hermes integration. Both CrewAI and AutoGen support custom OpenAI-compatible APIs (MiMo + DeepSeek), but CrewAI's declarative API (Agent role + Task + kickoff) is a better fit for cronjob/script-based execution than AutoGen's manual conversation loop.

```python
from crewai import Agent, Task, Crew, LLM

mimo = LLM(
    model='openai/mimo-v2.5-pro',
    base_url='https://api.xiaomimimo.com/v1',
    api_key=os.environ['MIMO_API_KEY']
)
deepseek = LLM(
    model='openai/deepseek-chat',
    base_url='https://api.deepseek.com/v1',
    api_key=os.environ['DEEPSEEK_API_KEY']
)

# Define agents with roles
frontend_agent = Agent(
    role='LVGL UI Developer',
    goal='Write LVGL v9 UI code',
    backstory='Embedded GUI specialist',
    llm=mimo,
    verbose=True
)
reviewer_agent = Agent(
    role='Code Reviewer',
    goal='Review for memory leaks, NULL checks, API compatibility',
    backstory='Embedded C quality assurance',
    llm=deepseek,
    verbose=True
)

# Tasks with dependencies auto-resolved by CrewAI
task1 = Task(description='Write LVGL settings page with roller component', agent=frontend_agent)
task2 = Task(description='Review the code for issues', agent=reviewer_agent, context=[task1])

crew = Crew(agents=[frontend_agent, reviewer_agent], tasks=[task1, task2], process='sequential')
result = crew.kickoff()
```

**Agent role assignment rule of thumb:**
- MiMo → UI/frontend/creative tasks (training data bias toward IoT/consumer devices)
- DeepSeek → backend logic, code review, aggregation (stronger at structured reasoning)

### CC + Codex Pipeline (alternative to CrewAI)

Claude Code and Codex CLI can be pipelined for agent relay without external frameworks:

```
1. Codex (DeepSeek) writes code
2. Hermes (MiMo) reviews + suggests improvements
3. Codex corrects
4. Hermes confirms
```

**Critical pitfall:** CC and Codex both use DeepSeek API under the hood. If you route
both through DeepSeek, you lose cross-model diversity (same training data). For the
pipeline to add value beyond 20min mode, at least one agent must use MiMo for a
different knowledge perspective. Without cross-model diversity, a simple 20min
delegate_task run achieves the same quality with less complexity.

When to use CC + Codex pipeline vs CrewAI vs 20min mode:
- 20min mode: default, covers 80% of multi-step tasks
- CC + Codex: when you need CC's file-tree awareness + Codex's structured output,
  AND you route them through different model families
- CrewAI: when you need agent-to-agent correction loops AND the task has
  persistent quality issues in integration phase

### Pitfalls
- CrewAI installs heavy (chromadb, openai, lancedb). Use only if the integration repair savings justify it
- Pydantic version conflicts with Hermes (CrewAI 2.11 vs Hermes 2.13). Functional but may cause warnings
- CrewAI's LiteLLM layer adds one extra hop of latency per API call vs direct HTTP
- Do NOT use this for tasks with no subagent dependencies — 20min mode is faster and cheaper
- Never assign multiple agents to touch the same file simultaneously (race condition)
- CC + Codex pipeline loses cross-model diversity if both routed through DeepSeek — route at least one through MiMo
