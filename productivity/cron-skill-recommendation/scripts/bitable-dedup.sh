#!/bin/bash
# Bitable deduplication — remove duplicate records keeping the earliest
#
# Usage: bash bitable-dedup.sh <base-token> <table-id>
# Requires: lark-cli with bot auth
#
# Steps:
#   1. Read all records (markdown format)
#   2. Extract record_id + Skill名称 + 日期
#   3. Group by Skill名称, keep earliest date
#   4. Batch delete duplicates (20 per batch)
#
# Safe to re-run — idempotent.

set -euo pipefail

BASE_TOKEN="${1:?Usage: bitable-dedup.sh <base-token> <table-id>}"
TABLE_ID="${2:?Usage: bitable-dedup.sh <base-token> <table-id>}"

echo "=== Reading records ==="
ALL=$(lark-cli base +record-list --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --as bot --limit 200 2>&1)

TOTAL=$(echo "$ALL" | grep -c "^| rec" || true)
echo "Total records: $TOTAL"

# Extract and deduplicate using Python
DELETE_IDS=$(python3 -c "
import sys
from collections import defaultdict

records = []
for line in sys.stdin:
    line = line.strip()
    if not line.startswith('| rec'):
        continue
    parts = [p.strip() for p in line.split('|')]
    if len(parts) >= 4:
        records.append({'id': parts[1], 'name': parts[2], 'date': parts[3]})

groups = defaultdict(list)
for r in records:
    groups[r['name']].append(r)

to_delete = []
for name, recs in groups.items():
    recs.sort(key=lambda x: x['date'])
    for r in recs[1:]:
        to_delete.append(r['id'])

for rid in to_delete:
    print(rid)
" <<< "$ALL")

COUNT=$(echo "$DELETE_IDS" | grep -c "^rec" || true)
echo "Duplicates to delete: $COUNT"

if [ "$COUNT" -eq 0 ]; then
    echo "No duplicates found. Done."
    exit 0
fi

# Batch delete (20 per batch)
BATCH=0
echo "$DELETE_IDS" | while IFS= read -r rid; do
    [ -z "$rid" ] && continue
    ARGS="$ARGS --record-id $rid"
    BATCH=$((BATCH + 1))
    if [ "$BATCH" -ge 20 ]; then
        lark-cli base +record-delete --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --as bot --yes $ARGS 2>&1 | head -1
        ARGS=""
        BATCH=0
    fi
done

# Delete remaining
if [ -n "${ARGS:-}" ]; then
    lark-cli base +record-delete --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --as bot --yes $ARGS 2>&1 | head -1
fi

# Verify
REMAINING=$(lark-cli base +record-list --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --as bot --limit 1 2>&1 | grep "Meta:" | grep -oP 'count=\K[0-9]+')
echo "Done. Remaining records: $REMAINING"
