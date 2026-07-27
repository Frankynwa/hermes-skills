# Parallel Document Writing with delegate_task

When writing long documents (thesis, report, multi-chapter output), split into independent chunks and dispatch as parallel delegate_task subagents. Each subagent reads the relevant data files independently and writes its chapter(s).

## Proven Pattern: 3-Agent Parallel Thesis

A 15,000-word Chinese thesis (6 chapters) was completed in **~5 minutes wall-clock** using 3 parallel subagents, versus estimated 15+ minutes serial.

### Task Decomposition

| Subagent | Chapters | Dependencies | Toolsets |
|----------|----------|-------------|----------|
| 1 | Ch1-2 (Intro + Literature) | Literature review files, web search | terminal, file, web |
| 2 | Ch3-4 (Methodology + Experiment Design) | Model implementation code, experiment configs | terminal, file |
| 3 | Ch5-6 (Results + Conclusion) | All JSON result files, figure paths | terminal, file |

### Key Design Decisions

1. **No web search for Ch3-6**: Chapters 3-6 are purely based on existing project data. Only Ch1-2 (literature review) needs web access. This reduces token waste.

2. **Each subagent gets full file paths**: Pass all relevant file paths in the context. Subagents read files independently — no inter-agent data passing needed.

3. **Merge step in main agent**: After all subagents finish, the main agent runs a simple `cat` merge:
   ```bash
   cat chapter_header.md chapter_1_2.md chapter_3_4.md chapter_5_6.md > full_document.md
   ```

4. **No dependency between subagents**: Chapters reference each other by chapter number only (e.g. "详见第3章"), not by content. This makes parallel execution safe.

5. **Shared data files are read-only**: All subagents read from the same JSON/data directories but write to separate output files. No race conditions.

### Result Tracking

Each delegate_task result includes `tokens` (input/output) and `duration_seconds`. Sum these for the full report:

```python
total_input = sum(r["tokens"]["input"] for r in results)
total_output = sum(r["tokens"]["output"] for r in results)
total_time = max(r["duration_seconds"] for r in results)  # parallel, so max not sum
```

### When to Use This Pattern

- Document has 3+ clearly separable sections
- Each section can be written independently (no "see previous section for details")
- Data sources for each section are known upfront
- Target word count > 5,000 words (not worth the overhead for short docs)

### When NOT to Use

- Document requires narrative continuity (fiction, creative writing)
- Later sections depend on exact wording of earlier sections
- Data is generated dynamically (not pre-existing files)
- Document is < 3,000 words — serial is fast enough
