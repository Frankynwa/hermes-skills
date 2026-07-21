# Architecture-First: Pre-Planning Analysis

## When to apply

Use BEFORE `writing-plans` when the task involves:
- 5+ source files across multiple directories
- A design document (PDF/Figma/spec) that needs mapping to code
- Multiple gap analyses or audit reports that need cross-referencing
- User says "context is exploding" / "先拆解任务" / "先分析架构"

## Workflow

### Phase 1: Inventory

1. Map ALL source files with line counts and responsibilities
2. Identify the navigation/component hierarchy (what contains what)
3. List every sub-page/panel/widget per file

### Phase 2: Cross-reference

1. If multiple analyses exist, merge them into one matrix
2. Verify EACH claim against actual code — do not trust prior analyses
3. Flag contradictions explicitly

### Phase 3: Architecture document

Output a single markdown file containing:
- Navigation hierarchy diagram (ASCII tree)
- Design-to-code file mapping table
- Per-file responsibility matrix (lines, nav mode, sub-pages, completion %)
- Corrected implementation status (✅/⚠️/❌ with details)
- Statistics summary
- Prioritized roadmap

Save to project root as `UI_ARCHITECTURE.md` or similar.

## Rules

- **Never trust gap analyses generated from vision/PDF inspection alone** — they will miss code in unexpected files. Config pages often live in separate files from the UI mockup that showed them.
- **Cross-reference by reading actual source**, not by assuming file names map to features.
- **One document, one truth** — user should not need to hold state from earlier messages.
- **Completion percentage claims must be verified** — 14% vs 73% difference matters.
