# Efficient Batch Skill Search

When evaluating multiple search queries (e.g., checking several topics for
available skills), use `execute_code` with `from hermes_tools import terminal`
to batch all `npx skills find` calls and parse results in one shot. This is
significantly faster than running sequential shell commands.

## Pattern

```python
from hermes_tools import terminal

searches = {
    "code review": "code review",
    "python performance": "python performance optimization",
    "mattpocock": "mattpocock",
}

for label, query in searches.items():
    out = terminal(f"npx skills find '{query}' 2>&1", timeout=60)
    lines = out['output'].split('\n')
    skills = []
    for line in lines:
        # Filter lines with install counts and skill references
        if 'installs' in line and '@' in line and '\u2514' not in line:
            parts = line.strip().split()
            if len(parts) >= 2:
                skill_full = parts[0]
                installs = parts[-2] if len(parts) > 2 else '?'
                skills.append(f"{skill_full} ({installs} installs)")
    print(f"\n=== {label} ===")
    for s in skills[:10]:
        print(f"  {s}")
```

## Pitfalls

- `npx skills info <skill>` does NOT exist. Use `npx skills find` with a
  specific query to get details about a skill.
- The `npx skills` CLI outputs ASCII art banner on stderr; grep-based
  parsing should target stdout lines containing `installs` and `@`.
- `npx skills list --source` shows skills across ALL agents (Hermes + Qoder
  + others), not just Hermes. Use filesystem inspection
  (`search_files` in `~/.hermes/skills/`) to confirm what Hermes actually has.
