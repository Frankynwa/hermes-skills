# Wiki Link → Base Token Resolution

When a user shares a wiki URL like `https://my.feishu.cn/wiki/YUU2wgJhFiWDT8ki91vcVna5nHc?table=tblJvuTAw57HMoVR&view=vewSpzDg9J`:

- The token in the URL path (`YUU2wgJhFiWDT8ki91vcVna5nHc`) is a **wiki node token**, NOT the bitable base token
- Using it directly as `--base-token` returns `"param baseToken is invalid"` (code `800004006`)
- The `?table=tbl...` parameter IS the correct `--table-id` (prefix `tbl` = table)

## Resolution Steps

```bash
# Step 1: Resolve wiki node → get the actual bitable obj_token
lark-cli wiki +node-get --token "https://my.feishu.cn/wiki/YUU2wgJhFiWDT8ki91vcVna5nHc"
# Returns: data.obj_type=bitable, data.obj_token="WCNZbCQkJa7OFjs32q7cvqxlnmb"

# Step 2: Use data.obj_token as --base-token
lark-cli base +record-list --base-token WCNZbCQkJa7OFjs32q7cvqxlnmb --table-id tblJvuTAw57HMoVR
```

If the user pastes just the wiki token without the URL, you need `--obj-type bitable`:
```bash
lark-cli wiki +node-get --token YUU2wgJhFiWDT8ki91vcVna5nHc --obj-type bitable
```

The `?view=...` parameter can be extracted as `--view-id` for view-specific queries.

## URL Parameter Prefix Guide

| Prefix | Object Type | Use as |
|--------|------------|--------|
| `tbl` | Table | `--table-id` |
| `blk` | Dashboard | `--dashboard-id` |
| `wkf` | Workflow | workflow ID |
| `ldx` | Embedded doc | NOT a table ID |
| `vew` | View | `--view-id` |
