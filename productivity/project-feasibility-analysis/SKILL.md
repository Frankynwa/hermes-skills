---
name: project-feasibility-analysis
description: "Evaluate a project idea with structured commercial feasibility + software engineering analysis. Use when the user shares a project concept, business idea, or product plan and wants rational, objective assessment — not cheerleading. Covers market sizing, competitor research, risk matrix, Porter five forces, architecture design, WBS, and Go/No-Go decision. Triggers on: 'analyze this project', 'is this idea viable', 'feasibility study', '商业可行性', '这个项目如何'."
tags: [analysis, business, software-engineering, market-research, project-evaluation]
---

# Project Feasibility Analysis

Evaluate a project idea with **two lenses**: commercial viability and software engineering rigor. The goal is to give the user an honest, research-backed assessment — identify real risks, not theoretical ones. Be direct about weaknesses.

## User Preferences

- **Be critical, not cheerful.** When the user shares a project plan or AI-generated analysis, evaluate it objectively. Point out what's missing, what's over-optimistic, and where the real risks lie. The user explicitly values "理性客观" (rational and objective).
- **Research before writing.** Always gather real data (competitor scans, market data, open-source landscape) before forming conclusions. Don't analyze in a vacuum.
- **Combined analysis.** The user expects BOTH commercial feasibility AND software engineering analysis in one report, not just one dimension.
- **Identify the real bottleneck.** For any project, find the ONE thing that determines success or failure (e.g., "math formula handwriting is the real technical moat") and make it the focus.

## Workflow

### Phase 1: Research (delegate in parallel)

Use `delegate_task` with batch mode to run 2-3 research tasks concurrently:

1. **Competitor/market scan**: Search GitHub, web for existing solutions. Identify gaps.
2. **Domain research**: Understand the target market's current state (e.g., university submission requirements, platform landscape).
3. **Technical research**: Find open-source projects, academic papers, and techniques relevant to the core technical challenge.

### Phase 2: Commercial Feasibility Analysis

Structure the report with these sections:

#### 1. Demand Validation
- Is the pain point real? Who has it? How often?
- What are the limiting factors (seasonality, geography, niche)?
- **Don't assume demand — validate it with evidence.**

#### 2. Competitive Landscape
- Table of competitors: type, tech stack, features, user base, weaknesses
- Identify the **market gap** — what nobody does well
- Assess **barrier strength** for each differentiator (low/medium/high)

#### 3. Market Sizing (TAM/SAM/SOM)
- TAM: total addressable market
- SAM: serviceable market (who would actually use it)
- SOM: obtainable market (first year, realistic)
- Revenue model with pricing scenarios (optimistic/realistic/pessimistic)
- Cost structure (servers, marketing, **opportunity cost of dev time**)
- Break-even analysis

#### 4. Risk Matrix
- Table: risk × probability × impact × mitigation
- Distinguish **real risks** from **theoretical risks**
- Highlight the top 2-3 risks that could kill the project

#### 5. Porter Five Forces (simplified)
- New entrants, substitutes, buyer power, supplier power, rivalry
- One-sentence conclusion about market attractiveness

#### 6. Commercial Viability Summary
- Star ratings (1-5) for: demand, market size, barriers, profit potential, risk controllability
- One-line verdict

### Phase 3: Software Engineering Analysis

#### 1. Requirements
- Functional requirements table (ID, description, priority P0/P1/P2, complexity)
- Non-functional requirements (performance, usability, security, cost)

#### 2. Architecture
- Compare 3-4 architecture options with pros/cons
- Recommend one with justification
- ASCII architecture diagram
- Technology selection table (module → tech → rationale)

#### 3. Development Methodology
- Recommend method (incremental, agile, etc.) with justification
- WBS (Work Breakdown Structure) per phase
- Time estimates per task, total hours

#### 4. Risk Management
- Technical risks (with probability and mitigation)
- Project risks (scope creep, time conflicts, etc.)

#### 5. Quality Assurance
- Test strategy (unit, integration, visual regression, user acceptance)
- Acceptance criteria with measurable thresholds

#### 6. Maintenance & Evolution
- Expected technical debt
- Version roadmap (v0.1 → v2.0)

### Phase 4: Go/No-Go Decision

- Decision matrix: factors × weights × scores → weighted total
- **Final recommendation** with clear conditions (e.g., "Do it, but with staged validation")
- Staged approach: what to do first, what to defer, when to cut losses

## Output Format

Save the full report as a Markdown file in `~/projects/<project-name>-analysis.md`. Summarize key findings in the chat response. Use tables extensively — they communicate trade-offs better than paragraphs.

## Pitfalls

- **Don't be a yes-man.** If the idea has fundamental problems, say so clearly. The user values honesty over encouragement.
- **Don't over-engineer the analysis.** A 50-page business plan for a weekend project is wasteful. Scale depth to project ambition.
- **Opportunity cost is a real cost.** Always factor in the developer's time, especially for students with exam pressure.
- **"Nobody else does this" can mean "nobody wants this."** An empty market isn't always an opportunity — it might be a sign of insufficient demand.
- **Research competitors before concluding there are none.** GitHub search, web search, app store search — be thorough.
