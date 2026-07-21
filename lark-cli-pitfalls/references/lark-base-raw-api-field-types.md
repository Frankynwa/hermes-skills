# Bitable Raw API Field Type Codes

Quick reference for when `+field-create` / `+field-update` shortcuts fail and you need to fall back to `lark-cli api`.

## Numeric Type Codes

| Code | Type | Code | Type |
|------|------|------|------|
| 1 | text | 15 | attachment |
| 2 | number | 17 | formula |
| 3 | select | 18 | location |
| 4 | multi_select | 20 | group_chat |
| 5 | datetime | 21 | created_time (system) |
| 7 | checkbox | 22 | modified_time (system) |
| 11 | user | 23 | created_user (system) |
| 13 | phone | 1001 | barcode |

## Extended Types (1000+)

| Code | Type | Notes |
|------|------|-------|
| 1002 | progress | Use this for progress bars |
| 1003 | created_by | **NOT progress** — this is a system field |
| 1004 | currency | |
| 1005 | rating | |

## Common API Patterns

```bash
# Create field
lark-cli api POST "/open-apis/bitable/v1/apps/{base}/tables/{table}/fields" \
  --as bot --data '{"field_name":"X","type":3,"property":{"options":[{"name":"A"},{"name":"B"}]}}'

# Update field (full PUT)
lark-cli api PUT "/open-apis/bitable/v1/apps/{base}/tables/{table}/fields/{field_id}" \
  --as bot --data '{"field_name":"X","type":3,"property":{"options":[{"name":"A"}]}}'

# Batch create records
lark-cli api POST "/open-apis/bitable/v1/apps/{base}/tables/{table}/records/batch_create" \
  --as bot --data '{"records":[{"fields":{"col":"val"}}]}'
```

## Success Response Format

Raw API returns `"code": 0` (not `"ok": true` which is the lark-cli shortcut wrapper format). Both indicate success.
