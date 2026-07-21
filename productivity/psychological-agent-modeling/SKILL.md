---
name: psychological-agent-modeling
description: "Model internal psychological systems (IFS Parts, Schema Therapy modes, attachment patterns) as multi-agent AI simulations. Covers theoretical foundations (IFS, Schema, ACT, Attachment, Rogers), NLP-based continuous assessment from Chinese text (PsychAnalyzer API, 12 psycholinguistic dictionaries), interactive self-assessment delivery (ECR-R, YSQ-S3), MiroFish simulator integration, and daily reflection workflows. Use when user wants to understand their internal psychological dynamics, build assessment tools, simulate life scenarios, or integrate psychology with AI tools."
platforms: [linux, macos, windows]
---

# Psychological Agent Modeling

## When to use

Use when the user wants to:
- Understand their internal psychological dynamics beyond MBTI/typology
- Simulate how different parts of their personality respond to scenarios
- Build a personal "life navigation system" using AI multi-agent simulation
- Integrate therapeutic frameworks (IFS, Schema Therapy) with AI tools
- Explore life decisions through internal system simulation rather than external prediction

## Critical Workflow Principle: Meaning Before Emotion

**When the user is in a meaning crisis (Odyssey period, breakup, identity confusion):**

1. **First**: Help them find a direction, project, or purpose — something to care about
2. **Then**: Do the emotional/psychological work within that context
3. **Never reverse**: Pushing body-awareness or emotion exercises on someone without purpose feels empty and will be abandoned

SDT (Deci & Ryan): autonomy + competence + relatedness → meaning emerges. A project the user CHOOSES, BUILDS, and SHARES satisfies all three. The psychology assessment project itself can be this vehicle.

## Theoretical Foundation

This skill integrates three psychological frameworks into a multi-agent simulation architecture:

### 1. Internal Family Systems (IFS) — Richard Schwartz

Every person's psyche contains multiple **Parts** with independent personalities, beliefs, fears, and behavioral strategies:

- **Exiles**: Vulnerable parts carrying childhood pain, shame, fear. They hold core beliefs like "I'm unlovable" or "I'm not enough."
- **Managers**: Proactive protectors that control, plan, criticize, and prevent exiles from being triggered. Examples: the perfectionist, the intellectualizer, the controller.
- **Firefighters**: Reactive protectors that use impulsive behaviors (dissociation, addiction, fantasy, busyness) to extinguish pain when exiles break through.
- **Self**: The core consciousness — calm, curious, compassionate, confident, clear, courageous, creative, connected (the "8 C's"). NOT a part. The natural leader of the internal system.

**Key source**: Schwartz, R.C. & Sweezy, M. (2020). *Internal Family Systems Therapy* (2nd ed.). Guilford Press.

### 2. Attachment Theory — Bowlby, Ainsworth, modern extensions

Adult attachment varies along two dimensions: **anxiety** (fear of abandonment) and **avoidance** (fear of intimacy). Four types emerge from their intersection: secure, anxious, dismissive-avoidant, fearful-avoidant.

- **ECR-R** (Fraley, Waller, & Brennan, 2000) is the gold-standard self-report measure
- Insecure attachment maps onto specific schema domains: anxious → abandonment/approval-seeking; avoidant → emotional deprivation/social isolation; fearful → defectiveness/subjugation (Pepping et al., 2013/2021)
- **Emotionally Focused Therapy (EFT)**, rooted in attachment theory, shows d≈0.7-1.0 in couple therapy RCTs (Hudson et al., 2023)

**Key sources**: Bowlby (1969/1982), Mikulincer & Shaver (2022, *Attachment in Adulthood* 3rd ed.)

### 3. Schema Therapy — Jeffrey Young

18 Early Maladaptive Schemas in 5 domains. Each schema is a deep cognitive-emotional pattern formed in childhood:

| Domain | Schemas |
|--------|---------|
| Disconnection & Rejection | Abandonment, Mistrust, Emotional Deprivation, Defectiveness, Social Isolation |
| Impaired Autonomy | Dependence, Vulnerability, Enmeshment, Failure |
| Impaired Limits | Entitlement, Insufficient Self-Control |
| Other-Directedness | Subjugation, Self-Sacrifice, Approval-Seeking |
| Overvigilance & Inhibition | Negativity, Emotional Inhibition, Unrelenting Standards, Punitiveness |

**Key source**: Young, J.E., Klosko, J.S., & Weishaar, M.E. (2003). *Schema Therapy: A Practitioner's Guide*. Guilford Press.

### 4. ACT (Acceptance and Commitment Therapy) — Steven Hayes

Third-wave behavioral therapy centered on **psychological flexibility** — the ability to contact the present moment and change or persist in behavior in service of chosen values.

- Six core processes: acceptance, cognitive defusion, present moment, self-as-context, values, committed action
- **Self-as-context** (the "observing self") is the key mechanism for identity distress — you are the observer of your thoughts/feelings, not the content (Halliburton & Cooper, 2021)
- Medium effect sizes (g≈0.57) for reducing experiential avoidance (Gloster et al., 2020); comparable to trauma-focused CBT for PTSD (Lang et al., 2023)
- Particularly relevant for emerging adults in identity exploration: values-based action predicts healthier identity resolution (Kashdan & McKnight, 2022)

**Key sources**: Hayes, S.C. et al. (2012). *ACT in Practice*; Harris, R. (2009). *ACT Made Simple*.

### 5. Carl Rogers — Person-Centered Therapy

- **Organismic Valuing Process**: An innate internal compass that knows what promotes growth
- **Conditions of Worth**: Internalized beliefs ("I'm only lovable if...") that override the compass
- **Self-Actualization**: The natural directional process toward growth and fulfillment

**Key source**: Rogers, C.R. (1961). *On Becoming a Person*. Houghton Mifflin.

## Agent Architecture Mapping

| Psychological Concept | Agent Model |
|---|---|
| IFS Parts (Managers, Firefighters, Exiles) | Specialized agents with roles, goals, fears, behavioral strategies |
| IFS Self | Orchestrator/meta-agent with 8C qualities |
| Attachment styles (anxious/avoidant/fearful) | Agent interaction protocols — how agents seek or reject connection |
| Schema Modes | Agent states activated by environmental triggers |
| Early Maladaptive Schemas | Deep agent belief weights (core memories, default assumptions) |
| ACT Self-as-Context | Observer agent — meta-awareness that transcends any single Part |
| ACT Values | System-level objective function — what the whole system optimizes toward |
| Narrative Externalization (White & Epston) | Named agents representing externalized problems |
| Self-Actualization tendency | System optimization objective |
| Unconditional Positive Regard | Agent interaction protocol — no agent is rejected |
| "Blending" (a Part takes over) | Agent override of the orchestrator |
| "Unblending" (Self regains control) | Orchestrator regaining observation capacity |

## Multi-Agent Simulation with MiroFish

**MiroFish** is a custom-built Python multi-agent simulator for internal psychological dynamics. It is NOT an existing open-source tool — it was built from scratch as a single-file Python script using the OpenAI API.

**GitHub**: `Frankynwa/mirofish` (private repo)

### Setup

The simulator lives at `~/projects/mirofish/mirofish.py`. It uses:
- OpenAI Python library (installed via pip)
- MiMo V2.5 Pro API (`https://token-plan-cn.xiaomimimo.com/v1`)
- API key from `~/.hermes/.env` (`XIAOMI_API_KEY=...`)

```bash
# Interactive mode (menu of scenarios + mode selection)
cd ~/projects/mirofish && python3 mirofish.py

# Single-round simulation
python3 mirofish.py -s "你刚经历了一段分手"

# Dialogue mode (agents respond to each other, 2+ rounds)
python3 mirofish.py -s "你遇到了一个不错的人" --dialogue

# Specify rounds
python3 mirofish.py -s "场景" --dialogue --rounds 3

# List preset scenarios
python3 mirofish.py --list
```

Reports auto-save to `~/projects/mirofish/reports/sim_YYYYMMDD_HHMMSS.md`.

### MiMo API Pitfalls

- **System prompts return empty**: MiMo V2.5 Pro may return empty content when using `role: "system"` messages. Fix: merge system prompt into user message as `f"{system_prompt}\n\n---\n\n{user_prompt}"` with `role: "user"`. Add a fallback that retries with separated system+user if the merged version also returns empty.
- **API key location**: Not in `config.yaml` (masked to "***"). Read from `~/.hermes/.env` file: parse `XIAOMI_API_KEY=...` line. Full key is 51 chars starting with `tp-`.
- **Temperature 0.8+** recommended for creative/expressive agent responses.
- **max_tokens=400** for agent responses (2-4 sentences); 300 was too short for some responses.
- **Dialogue mode is more revealing than single-round**: When agents can see each other's responses, they adapt — protectors double down, firefighters get more desperate, exiles get more specific. The multi-round dynamic reveals inter-part conflicts that single-round misses.
- **Some agents randomly return empty**: Even with the fix, MiMo occasionally returns empty for specific agents. This is a model-level issue, not a prompt issue. The fallback retry helps but doesn't eliminate it. Protect with `if content and content.strip()` checks.

3. Define Agent personas based on IFS assessment

### Agent Definition Template

For each IFS Part, create an Agent with:
- **Persona**: Name, role, core belief, personality traits
- **Memory stream**: Key experiences that shaped this Part
- **Goals**: What this Part is trying to achieve
- **Fears**: What this Part is trying to prevent
- **Behavioral strategies**: How this Part acts when triggered
- **Relationship to other Parts**: Allies, conflicts, dependencies

### Simulation Scenarios

Run scenarios like:
- "User encounters a career decision" → observe which Parts activate and how they interact
- "User enters a new relationship" → observe approach/avoidance dynamics between Parts
- "User faces failure" → observe which protective strategies deploy

### Interpreting Results

The simulation output shows:
- Which Part-agent dominates in which situations
- How Parts amplify or suppress each other
- Where the Self-agent gets overridden
- What triggers specific Part activations

This is NOT prediction of external events. It's **visualization of internal dynamics** to increase self-awareness and enable conscious choice.

## Evidence Levels by Framework

Before recommending a framework, know its scientific standing. The user will ask "is this actually scientific?" — have answers ready.

| Framework | Evidence Level | Key RCTs / Meta-analyses | Main Criticism |
|-----------|---------------|--------------------------|----------------|
| **Schema Therapy** | ⭐⭐⭐⭐⭐ Strong | Bamelis et al. (2014, *JAMA Psychiatry*, N=323, recovery 81% vs 37%); Firth et al. (2023) meta-analysis; d≈1.0-1.2 for PDs | Evidence strongest for PDs; expanding to depression/PTSD |
| **Attachment Theory** | ⭐⭐⭐⭐⭐ Very strong | Candel & Turliuc (2023, 148-study meta-analysis); EFT RCTs d≈0.7-1.0; Li & Chan (2021) cultural moderation | Mostly correlational; causal inference requires longitudinal designs |
| **ACT** | ⭐⭐⭐⭐ Strong | Lang et al. (2023, 15 RCTs for PTSD, g≈0.57); Gloster et al. (2020) | Identity-specific evidence still early |
| **IFS** | ⭐⭐⭐ Moderate | Hodgdon et al. (2021, systematic review, d=0.52-0.81); growing RCT base | "Parts" model lacks independent construct validation |
| **Polyvagal Theory** | ⭐⭐ Weak | Montgomery et al. (2022): core claims poorly supported; Beauchaine (2023): mechanisms oversimplified | Phylogenetic hierarchy rejected by comparative neuroanatomy; "neuroception" unfalsifiable |
| **MBTI** | ⭐ Insufficient | Not accepted by academic psychology | Poor reliability and validity |

**Rule**: Use Polyvagal only as clinical metaphor, not hard science. Use MBTI as self-awareness language, not diagnostic tool.

## Self-Assessment Framework

A structured assessment combining attachment style (ECR-R based) and Early Maladaptive Schemas (YSQ-S3 based) is available as a support file. See `references/assessment-framework.md`.

**完整外部文档**：`~/projects/psychology-assessment/心理模式自我评估框架.md`（含解读框架、干预策略地图、推荐阅读、学术引用，可独立使用）

**完整改变执行手册**：`~/projects/psychology-assessment/图式深度分析与改变执行手册.md`（含各图式形成机制、维持循环、日常表现、10个具体改变策略、每日/每周练习计划、进度追踪模板）。精简版已推至GitHub `03-intervention/schema-deep-analysis.md`。

**Project storage**: Psychology assessment projects go to `~/projects/psychology-assessment/` (kebab-case, private). GitHub repo: `Frankynwa/psychology-of-meaning-research` (private). Do NOT push to public GitHub repos — user's personal psychological data is private.

**Interactive delivery preference**: The user prefers being asked assessment questions **one at a time** rather than receiving the full questionnaire document. Ask each question, record the score, then move to the next. After all scores are collected, produce the cross-interpretation analysis (Attachment Type × Top Schema Domains → core conflict → intervention strategy map).

**Intervention strategies**: For concrete change strategies (body awareness, emotion naming, graduated exposure, cognitive defusion, corrective emotional experience, deliberate imperfection experiments, daily practice protocol, red flags for professional help), see `references/intervention-strategies.md`.

**Borderline scores**: When anxiety or avoidance mean = exactly 3.5, do NOT force a category. Use the tie-breaking rules in `references/assessment-framework.md`. Real example: anxiety=3.5 + avoidance=4.5 → classified as fear-avoidant with avoidance dominant.

## Academic Evidence Detail

For the full literature review (specific papers, effect sizes, criticisms per framework), see `references/academic-evidence-2020-2025.md`.

## Academic References

- Schwartz, R.C. & Sweezy, M. (2020). *Internal Family Systems Therapy* (2nd ed.). Guilford Press.
- Young, J.E. et al. (2003). *Schema Therapy: A Practitioner's Guide*. Guilford Press.
- Rogers, C.R. (1961). *On Becoming a Person*. Houghton Mifflin.
- Frankl, V.E. (1946). *Man's Search for Meaning*. (Logotherapy — meaning as primary motivational force)
- Park, J.S. et al. (2023). "Generative Agents: Interactive Simulacra of Human Behavior." UIST 2023.
- White, M. & Epston, D. (1990). *Narrative Means to Therapeutic Ends*. W.W. Norton.
- Steger, M.F. et al. (2006). "The Meaning in Life Questionnaire." *J. Counseling Psychology*, 53(1), 80-83.
- Arnett, J.J. (2000). "Emerging Adulthood." *American Psychologist*, 55(5), 469-480.
- Bamelis, L.L.M. et al. (2014). Multicenter RCT of Schema Therapy for Personality Disorders. *JAMA Psychiatry*.
- Candel, O.S. & Turliuc, M.N. (2023). Insecure attachment and relationship satisfaction: A meta-analysis. *PAID*, 202.
- Lang, A.J. et al. (2023). ACT for PTSD: A systematic review and meta-analysis. *J. Traumatic Stress*.
- Hodgdon, H.B. et al. (2021). IFS for PTSD, Depression, and Anxiety: A Systematic Review. *J. Clinical Psychology*, 77(6).
- Montgomery, T. et al. (2022). Is polyvagal theory empirically testable? *Frontiers in Psychology*.
- Beauchaine, T.P. (2023). Polyvagal Theory: Time for a second look? *Psychophysiology*.
- Fraley, R.C., Waller, N.G., & Brennan, K.A. (2000). ECR-R. *J. Personality and Social Psychology*.
- Mikulincer, M. & Shaver, P.R. (2022). *Attachment in Adulthood* (3rd ed.). Guilford.
- Hudson, N.W. et al. (2023). Attachment-based interventions in couple therapy: A meta-analysis. *J. Marital and Family Therapy*.
- Li, T. & Chan, D.K.S. (2021). Anxious and avoidant attachment and romantic relationship quality: A meta-analysis. *EJSP*, 51(3).
- Gloster, A.T. et al. (2020). ACT increasing valued behaviors: A meta-analysis. *J. Consulting and Clinical Psychology*.
- Halliburton, A.E. & Cooper, L.D. (2021). ACT in identity exploration: A systematic review. *J. Contextual Behavioral Science*.
- Kashdan, T.B. & McKnight, P.E. (2022). Psychological flexibility and identity exploration in emerging adults.

## Post-Assessment Workflow: Deep Analysis + Intervention Plan

After collecting all scores and producing the cross-interpretation, the user will typically ask "现在怎么办？" (what now?). At this point, deliver a **deep analysis document** for each high-scoring schema containing:

1. **Formation mechanism** — how this schema was installed (childhood environment patterns)
2. **Maintenance cycle** — the self-reinforcing loop (trigger → body signal → schema alarm → defense strategy → short-term relief → long-term cost)
3. **Daily manifestations** — specific behavioral patterns in relationships, work, self-perception
4. **Interconnections** — how schemas interact (e.g., emotional inhibition × emotional deprivation = self-fulfilling prophecy of loneliness)
5. **Change strategies** — concrete, numbered exercises with specific steps (not vague advice)
6. **Weekly practice plan** — daily/weekly schedule with time estimates
7. **Progress tracking** — monthly self-check template
8. **Red flags for professional help** — specific criteria that indicate self-help is insufficient

**Key insight (2026-06)**: When the user asks for the full picture, they want ALL of the above — not a summary. Deliver as a complete document (local + push to private GitHub if user has a project repo). The user's phrase "推进完成这个项目" means they want the full deliverable, not incremental discussion.

**Meaning-first principle**: If the user is in a meaning crisis (Odyssey period, recent breakup, identity confusion), do NOT push emotional exercises before they have a sense of direction. The order is:
1. Help them find a "why" (meaning/purpose project)
2. THEN do the emotional/psychological work
3. Not the reverse

Pushing "feel your body" or "do an emotion diary" on someone who has no purpose will feel empty and be abandoned. The user needs something to care about FIRST. SDT (Deci & Ryan): autonomy + competence + relatedness → meaning emerges. A project that the user chooses, builds, and shares with others satisfies all three needs simultaneously.

## Project-Based Self-Work

The user may want to use a GitHub repository as the vehicle for their psychological self-exploration. This gives them:
- **Autonomy**: they chose the project
- **Competence**: building something tangible
- **Relatedness**: the project can be shared/reviewed

**Standard project structure** (when user asks to "build this into a project"):

```
psychology-of-meaning-research/  (or user-chosen name, kebab-case)
├── README.md                          # Project overview with theory table
├── 01-literature-review/              # Academic literature reviews
├── 02-assessment/                     # Self-assessment tools
├── 03-intervention/                   # Change strategies & practice protocols
├── 04-tracking/                       # Progress tracking templates
└── references/                        # Academic citations
```

**Storage rules**:
- Private repos only — personal psychological data must not be public
- Local detailed versions in `~/projects/<project-name>/`
- GitHub condensed versions pushed via MCP tools (they handle auth automatically)
- GitHub MCP tools have built-in auth via `GITHUB_PERSONAL_ACCESS_TOKEN` in MCP server config — no need to find the token; just call `mcp_github_create_or_update_file` directly

**Large file push pattern**: When pushing large documents (>10KB) to GitHub via MCP tools, condense to key sections. The full version stays local. The MCP tool handles files up to ~15KB reliably as content parameter.

## NLP-Based Continuous Assessment (from psych-nlp-pipeline)

A Python package (`psych-nlp`) at `~/projects/psych-nlp/` provides continuous psychological assessment from Chinese natural language text. It extracts features using 12 custom Chinese psycholinguistic dictionaries and maps them to attachment dimensions, schema activation, and IFS part activity.

**How it integrates with MiroFish**: The NLP assessment can auto-update MiroFish agent parameters based on real-time language analysis. Instead of static agent prompts, the system dynamically adjusts agent behavior weights based on detected emotional state, schema activation, and attachment patterns.

### PsychAnalyzer API (Critical)

**`PsychAnalyzer.analyze(text)` returns a `PsychProfile` dataclass, NOT a dict.**

```python
from psych_nlp import PsychAnalyzer
analyzer = PsychAnalyzer()
profile = analyzer.analyze("今天有点累")

# ✅ 正确 — 属性访问
profile.attachment.anxiety_score    # float
profile.attachment.avoidance_score  # float
profile.attachment.anxiety_level    # str: '低'/'中低'/'中'/'高'
profile.schema.top_schema           # str: e.g. '情感抑制'
profile.schema.top_score            # float
profile.schema.contributions        # dict: {'情感抑制': 1.79, '苛刻标准': 0.0, ...}
profile.ifs.dominant_part           # str: '保护者'/'被流放者'/'Self'
profile.ifs.protector               # float
profile.ifs.firefighter             # float
profile.ifs.exile                   # float
profile.ifs.self_presence           # float
profile.ifs.conflict_level          # float
profile.summary                     # str
profile.text_length                 # int
profile.word_count                  # int

# ❌ 错误 — 不是 dict
profile.get("attachment")           # AttributeError
profile["schema"]                   # TypeError
```

### LongitudinalTracker API

```python
from psych_nlp.tracking import LongitudinalTracker, AssessmentRecord

tracker = LongitudinalTracker()
record = AssessmentRecord(
    timestamp="2026-06-26 23:00:00",
    text_preview="今天有点累...",
    text_length=500,
    anxiety=0.65, avoidance=1.96,
    schema_top1_name="情感抑制", schema_top1_score=3.21,
    ifs_dominant="保护者",
    summary="...",
)
tracker.add_record(record)
tracker._save_history()
```

### 12 Dictionary Categories

1. Positive emotion / 2. Negative emotion / 3. Cognitive processing words
4. Absolutist words / 5. Pronouns (1sg/1pl/2/3) / 6. Somatic expressions (Chinese-specific)
7. Internet slang emotion / 8. Emotional inhibition markers / 9. Harsh standards markers
10. Emotional deprivation markers / 11. Topic shift markers / 12. Hedging/uncertainty words

See `references/dictionary-spec.md` for full word lists.

### Chinese-Specific NLP Considerations

1. **Somaticization**: 心里堵得慌, 胸闷, 喘不过气 — psychological pain expressed as physical symptoms
2. **Indirectness**: "还行吧" may mean "not okay at all"
3. **Modal particles**: 吧/呢/啊/了 carry emotional information
4. **Internet slang**: emo了/破防了/裂开/绷不住了 — high frequency in young users
5. **Double negation**: "不是不好" = good
6. **No open-source Chinese LIWC clone exists** — must build custom dictionaries

### Daily Reflection System (2026-06)

Automated daily psychological reflection via Feishu cron:
- `scripts/daily_questions.py` — 42 questions across 6 dimensions, deduplicates recent 7 days
- `scripts/analyze_daily_reflection.py` — fetches Feishu replies via `lark-cli im +chat-messages-list --chat-id --as bot`, runs PsychAnalyzer, saves to tracking
- Cron 21:30 sends questions → user replies naturally → Cron 23:00 analyzes and archives

### NLP Pitfalls

- **Fearful-avoidant masking**: Avoidant users systematically underreport distress in language. Cross-validate with MiroFish simulation results.
- **Minimum text length**: Need ≥50 chars for emotion analysis, ≥500 chars for schema assessment, ≥2000 chars/week for reliable tracking.
- **Don't diagnose**: System provides trend tracking, not clinical diagnosis. Always attach confidence levels.
- **Calibration cycle**: Questionnaires every 3 months to recalibrate NLP-based scores against ground truth.
- **jieba accuracy**: Domain-specific psychological terms may not be in default dictionary. Add custom entries.

## Interactive Self-Assessment Delivery (from psych-self-assessment)

When delivering psychological self-assessment tools:

### Delivery Rules
- **ONE question at a time** — never dump the full survey
- Track running scores for each dimension
- Give brief dimension-level results when a section completes
- Full interpretation only after ALL data collected
- **Borderline scores (exactly 3.5)**: When anxiety or avoidance mean = exactly 3.5, do NOT force a binary classification. Report as "临界值" and note direction based on other dimension.

### Assessment Instruments
- **Attachment**: ECR-R (Fraley et al., 2000) — 2 dimensions × 8 items
- **Schema**: YSQ-S3 (Young, 2005) — 5 domains, 3 items per schema
- **Cross-reference**: attachment type × schema domains for personalized interpretation

### Evidence Hierarchy

| Theory | Evidence Level | Best For |
|--------|---------------|----------|
| Schema Therapy | ⭐⭐⭐⭐⭐ (RCTs, d≈1.0-1.2) | Repeated relationship patterns, deep beliefs |
| Attachment Theory | ⭐⭐⭐⭐⭐ (60yrs, meta-analyses) | Relationship behavior, intimacy patterns |
| ACT | ⭐⭐⭐⭐ (15+ RCTs for trauma) | Identity confusion, psychological flexibility |
| IFS | ⭐⭐⭐ (growing, g≈0.78) | Internal conflict, trauma parts |
| Polyvagal Theory | ⭐⭐ (criticized neurobiology) | Clinical metaphor only, not hard science |
| MBTI | ⭐ (not scientifically valid) | Casual self-reflection language only |

### Self-Assessment Pitfalls

- **Meaning before emotion**: When user is in meaning crisis, do NOT push emotional exercises before they have direction. Order: (1) find "why" → (2) emotional work within that context.
- **The analysis trap**: User's schemas may cause SELF-ANALYSIS as defense against CHANGE. Signs: keeps asking "tell me more about my patterns" without doing exercises. Name it ONCE, redirect to ONE concrete action.
- **Self-narrative distortion**: Users with strong unrelenting standards describe themselves MORE negatively than reality. When you notice gap between stated inaction and actual behavior, point it out ONCE.
- **"怎么办" = ACTION, not more theory**: Give ONE specific action they can do RIGHT NOW, not another framework.
- **Don't "challenge" defense patterns directly**: Listen to what they say they need (meaning, direction, project) and provide THAT.

## Academic References

## Agent Prompt Design (from llm-agent-psych-simulation)

Each agent prompt has 4 parts:
1. **Identity**: "你是'保护者'，一个内在心理部分"
2. **Core belief**: "你的核心信念：只有控制才安全"
3. **Behavioral traits**: 3-5 specific behavioral patterns with examples
4. **Output directive**: "用第一人称表达你的想法和感受。2-4句话。"

Keep prompts under 300 tokens. MiMo and similar models respond better to concise, structured prompts.

### Simulation Modes

**Single Round**: Each agent reacts independently to a scenario. Observer integrates.
- Use for: quick self-check, seeing which part dominates

**Dialogue Mode**: Agents react, then see each other's responses and react again (2-3 rounds).
- Use for: deeper exploration, seeing how parts influence each other
- Key insight: dialogue reveals inter-part dynamics (e.g., protector doubling down when exile surfaces)

### Scenario Design

Effective scenarios are:
- **Specific**: "对方说你像一堵墙" not "你遇到了人际关系问题"
- **Emotional**: include the felt experience, not just the situation
- **Real**: based on actual user situations, not hypotheticals
- **Multi-layered**: combine relationship + identity + daily behavior

### Observer Agent Design

The Observer/Self agent is NOT just another agent. It:
- Receives all other agents' responses as context
- Names what each part is doing ("保护者在用沉默守护秩序")
- Does NOT judge or suppress any part
- Offers integration, not resolution

## Pitfalls

- **Watch for the "analysis trap"**: The user's schemas may cause them to use SELF-ANALYSIS as a defense against ACTUAL CHANGE. Signs: they keep asking "tell me more about my patterns" without doing any exercises, they say "that's accurate" to every insight but nothing changes in their behavior. When you detect this, name it ONCE ("this is your emotional inhibition using analysis as a defense"), then immediately redirect to a concrete small action. Don't name it repeatedly — that becomes another form of analysis.
- **"怎么办" = user wants ACTION, not more theory**: When the user asks "那怎么办？" (so what should I do?), they want a concrete next step they can do RIGHT NOW, not another framework or explanation. Give ONE specific action, not a menu of options.
- **Don't use for diagnosis**: This is a self-exploration tool, not a clinical instrument
- **Simulation ≠ prediction**: The goal is internal awareness, not fortune-telling
- **Parts are not enemies**: Every Part is trying to help — the system should treat all agents with UPR
- **Self cannot be simulated**: The Self-agent is a placeholder for the user's own observer consciousness
- **Requires honest self-assessment**: Garbage in, garbage out — the Agent definitions must reflect genuine internal experience, not idealized self-image
- **INTJ trap**: Ni-doms may use this as another intellectual exercise — the goal is behavioral change, not more analysis
- **"信仰" pattern (faith/belief cycle)**: User may describe needing a "grand belief" to anchor them. History: believed in love → disillusioned; believed in Marxism → disillusioned; now empty. The pattern is: believe deeply → reality disappoints → pain becomes a "thorn" → rationalize/numb → empty → search for next belief. The fix is NOT finding a better belief. It's learning to act WITHOUT perfect belief ("带着空心动"). Reference: Frankl's logotherapy (meaning discovered in action, not before action), SDT (meaning is a RESULT of need-satisfaction, not a prerequisite). Marx's alienation theory may resonate strongly — the user's emptiness may be less about "lost faith" and more about "alienated labor" (doing work that isn't theirs). If the user shares Marxist content, connect it to their personal alienation pattern.
- **Self-description harsher than reality**: User will describe themselves as "lying in bed avoiding everything" while actually having taken concrete social actions (reached out to friends, made plans). Gently point out the disconnect — their protector narrative is harsher than their actual behavior. This is a corrective observation, not cheerleading.
- **"继续" means DO, not discuss more**: When the user says "继续" (continue), they want the next concrete deliverable or action, not another round of analysis or explanation. Build, push, run — don't discuss.
- **Project = meaning vehicle**: The psychology project itself (GitHub repo, assessment tools, MiroFish simulator) IS the meaning-seeking activity. Don't treat it as preparation for "real" meaning — it IS the thing that satisfies SDT's three needs (autonomy: user chose it; competence: building something tangible; relatedness: shareable output).
- **Don't dump the full questionnaire**: User explicitly prefers one-at-a-time interactive delivery. Presenting the full document overwhelms and loses engagement.
- **Core framework set is four, not two**: The full assessment integrates Attachment Theory + Schema Therapy + ACT + IFS. Don't reduce to just IFS + Schema Therapy. Attachment provides the relational dimension, ACT provides the identity-flexibility dimension (self-as-context). All four have ≥⭐⭐⭐ evidence.
- **Evidence first, application second**: When introducing any framework, lead with its scientific standing and limitations before applying it. The user demands academic rigor and will reject surface-level claims. Don't just say "this works" — cite the RCTs, give effect sizes, and state limitations honestly.
- **Cross-interpretation is the real value**: Attachment type alone or schema scores alone are insufficient. The insight comes from the intersection — e.g., anxious attachment + abandonment schema = specific relational pattern. Always produce the cross-analysis after collecting scores.
- **Academic database search limitation**: The available tools cannot query PubMed/PsycINFO directly. When delegating to subagents for literature search, explicitly instruct them to use `web_search` or `web_fetch` targeting Google Scholar URLs (`scholar.google.com/scholar?q=...`) — NOT GitHub search. Subagents default to GitHub if not directed. Always be transparent that results come from web scraping + training knowledge, not a direct database API. Verify key papers by fetching their actual URLs. If the user needs citations for academic use, offer to verify specific papers individually.
