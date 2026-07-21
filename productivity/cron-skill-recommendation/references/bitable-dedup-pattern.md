# Bitable Deduplication Pattern

When automated cron jobs write to Feishu Bitable without checking existing records, duplicates accumulate. This reference documents the cleanup and prevention patterns.

## Cleanup Script (execute_code)

```python
from hermes_tools import terminal
from collections import defaultdict

BASE_TOKEN = "JfJJbW0EaaukYqsUYA1cnlzondh"
TABLE_ID = "tblyg5CbsoBoqgaX"

# Step 1: Read all records (markdown format is more reliable than JSON)
all_records = []
for offset in range(0, 1000, 100):
    result = terminal(
        f"lark-cli base +record-list --base-token {BASE_TOKEN} --table-id {TABLE_ID} --as bot --limit 100 --offset {offset} 2>&1",
        timeout=30
    )
    output = result["output"]
    batch_count = 0
    for line in output.split("\n"):
        line = line.strip()
        if not line.startswith("| rec"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            all_records.append({"id": parts[1], "name": parts[2], "date": parts[3]})
            batch_count += 1
    if batch_count < 100:
        break  # no more pages

# Step 2: Group by dedup key (Skill名称)
groups = defaultdict(list)
for r in all_records:
    groups[r["name"]].append(r)

# Step 3: Keep earliest, collect delete IDs
to_delete = []
for name, recs in groups.items():
    recs.sort(key=lambda x: x["date"])
    for r in recs[1:]:  # skip first (earliest)
        to_delete.append(r["id"])

# Step 4: Batch delete (20 per batch, --record-id is repeatable)
for i in range(0, len(to_delete), 20):
    batch = to_delete[i:i+20]
    args = " ".join(f"--record-id {rid}" for rid in batch)
    terminal(
        f"lark-cli base +record-delete --base-token {BASE_TOKEN} --table-id {TABLE_ID} --as bot --yes {args} 2>&1",
        timeout=30
    )
```

## Why Markdown Format Over JSON

`+record-list --format json` can contain illegal control characters (e.g. `\x00`) that break `json.loads()`. The default markdown table format is always parseable. Parse by splitting on `|` and extracting columns.

## Prevention: Pre-Write Dedup Check

Before writing N new records, read the table and build an exclusion set:

```python
existing = set()
for line in markdown_output.split("\n"):
    if line.strip().startswith("| rec"):
        parts = [p.strip() for p in line.split("|")]
        existing.add(parts[2].lower())  # Skill名称

new_candidates = [s for s in candidates if s["name"].lower() not in existing]
```

## Batch Delete Limits

- `--record-id` flag is repeatable (up to ~20 per call recommended)
- `--yes` is required for `+record-delete`
- For 50+ deletions, batch into groups of 20 to avoid timeouts
