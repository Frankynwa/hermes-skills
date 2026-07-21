# Multi-Direction Project Planning — Worked Example

> Reference for the `plan` skill. Captures the 4-direction → 1-focus convergence from 2026-05-24 session.

## The Pattern

User proposes N ambitious directions. The anti-pattern is to plan each in equal depth. The correct pattern:

```
Direction A ─┐
Direction B ─┼─→ Deep Research (parallel) ─→ Feasibility Filter ─→ Find Overlaps
Direction C ─┤                                              │
Direction D ─┘                                              ▼
                                               Merge overlapping directions
                                               De-prioritize non-overlapping
                                               Output ONE integrated roadmap
```

## The Session: Four Directions → One

### Initial Scope
1. Game dev (Persona-style dialogue + strategy/football)
2. Stock quant screening tool
3. AI image/video generation → virtual human → social media
4. AI research paper

### Research Phase (Parallel)
- **Quant**: GitHub found 7 actionable repos (AlphaSuite, Algorithmic_Trading_Strategies, etc.)
- **Game dev**: Ren'Py (6.5k★) for visual novels, Godot for strategy
- **AI art**: ComfyUI + Draw Things (already installed), LivePortrait (18k★) for virtual human
- **Paper**: arXiv search + YOLO defect detection angle from user's Visionox internship

### Feasibility Filter (Honest Assessment)
- **"Can I build a consistently profitable quant model?"** → No, even professional funds struggle. But a well-designed backtest with rigorous methodology is achievable and meets thesis standards.
- **"Can I really write a paper?"** → Yes, quant strategy backtesting is a classic undergrad thesis template.
- **"Can I do all four?"** → No, a student can't. Need to focus.

### Convergence Discovery
User self-corrected: "论文应该写量化相关的东西，最好是毕业设计相关，也是量化方向" + "选导师工具得完善，找到学校最适合量化方向的老师"

This merged three directions:
- **Quant tool** → becomes the thesis experiment platform
- **AI paper** → becomes the quant finance thesis
- **Supervisor tool** → becomes the immediate blocker (find the right advisor)

### Final Allocation
```
60% → Quant thesis (merged quant tool + paper)
25% → Game dev (quick wins with Ren'Py, no deadline pressure)
15% → AI art (ongoing interest, low priority)
```

## Feasibility Assessment Rules

When a user asks "can I really do X?":

1. **Separate academic standard from industry standard** — "Stable profitability" is an industry standard for quant funds. "Rigorous backtest outperforming baseline" is an academic standard for a thesis. The user only needs the latter.
2. **Don't just say yes** — Identify the specific barriers and what the achievable version looks like.
3. **Reframe constraints as scope** — "You can't build a profitable trading system, but you CAN build a methodologically sound strategy backtest that would make an excellent thesis."

## Candidate Evaluation Pattern (OpenAlex + Keyword Matching)

This session also produced a reusable pattern for evaluating candidates (professors, job candidates, funding sources) against a domain interest:

```
Scraped data (names, emails, research areas)
  │
  ├─→ OpenAlex API (free, no key): real h-index, citation count, works
  │     Search by name + institution ROR ID
  │
  ├─→ Keyword matching (tiered weights):
  │     Tier 1 (direct): weight 10 — exact domain match
  │     Tier 2 (related): weight 5 — adjacent skills
  │     Tier 3 (adjacent): weight 2 — foundational overlap
  │
  └─→ Combined ranking: direction_match DESC, then h-index DESC

Fallback: when API misses (~50% for non-English names), use scraped data as lower bound.
```

The resulting script (`find_quant_supervisor.py` in the session workspace) is a template for any "find the best X for my Y interest" task.
