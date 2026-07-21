---
name: ui-localization
description: Localize web UI (HTML/JS) to Chinese while preserving DOM ID integrity. Use for batch translations of JavaScript UI prototypes.
---

## When to Use
- User asks to localize a web UI prototype to Chinese
- Batch-find-and-replace translations across a JS/HTML file
- The UI has tab switching, filter buttons, or other interactivity driven by `data-*` attributes

## Core Principle: Split Display from Logic

**The most common and costly bug**: translating `data-*` attribute values to Chinese breaks DOM queries because element IDs (`ov-Record`, `s-Instrument`, `tr-Flicker`, `si-License`) remain in English.

### Pattern
```javascript
// BEFORE (English):
var tabs = ['Flicker','Unbalance','Current'];
tabs.map(function(t){ return '<button data-trtab="'+t+'">'+t+'</button>'; })
// AFTER (localized) — keep data-* English, translate display only:
var tabs = ['Flicker','Unbalance','Current'];
tabs.map(function(t){ return '<button data-trtab="'+t+'">'+
  ({'Flicker':'闪变','Unbalance':'不平衡','Current':'电流'})[t]+'</button>'; })
```

This applies to: Overview tabs (`data-tab`), Settings tabs (`data-stab`), Info subtabs (`data-sitab`), Trend tabs (`data-trtab`), Config panels (`data-cftab`).

### Also fix event listeners
If the event listener's `forEach` array was translated (e.g. `['仪器','通信','工具','信息','存储'].forEach(...)`), revert it to English so `document.getElementById('s-'+t)` resolves correctly.

### Exceptions — can translate data-* too
- SimpleMeas (`data-smtab`): DOM IDs are Chinese too (`sm-仪表`, `sm-相量`, `sm-波形`) — consistent.
- Config (`data-cftab`): DOM IDs match since they're generated from the same `panels` array.
- Events filter (`data-filter`): just fix the `f==='All'` comparison to match the translated value.

## Batch Translation Workflow

### ⚠️ CRITICAL PITFALL: `read_file` inside `execute_code`
`read_file()` in execute_code returns content **with line number prefixes** (e.g. `"  3|const PAGES=["`). Writing this back verbatim corrupts the file. This caused a full black screen.

**CORRECT approach**: write a standalone Python script, then run it via `terminal`:

```bash
# Step 1: write_file to /tmp/translate.py
# Step 2: terminal("python3 /tmp/translate.py")
```

The standalone script opens files directly with `open()`, avoiding the line prefix issue entirely.

### Translation script template
```python
with open('ui_prototype.js', 'r') as f:
    content = f.read()

# Longest/most-specific matches first to avoid partial replacements
tr = [
    ("old_string", "new_string"),
    # ... 100+ pairs ...
]

for old, new in tr:
    if old in content:
        content = content.replace(old, new)

with open('ui_prototype.js', 'w') as f:
    f.write(content)
```

### Post-translation verification
```bash
# Syntax check
node --check ui_prototype.js

# Scan for remaining English UI text
python3 -c "
import re
with open('ui_prototype.js') as f:
    text = f.read()
matches = re.findall(r'>([A-Z][a-z]+(?: [A-Z][a-z]+)*)<', text)
for m in sorted(set(matches)):
    print(m)
"
```

Expected remaining English: `English` (language option), `On`/`Off` (toggles), `Auto (DHCP)`.

### DOM consistency check
After translation, verify each `data-*` value matches its corresponding element ID:

| Tab group | data attr | DOM ID pattern | Values |
|-----------|----------|----------------|--------|
| Overview | data-tab | ov-{value} | Realtime, Record, Trend, Table, Verify |
| Settings | data-stab | s-{value} | Instrument, Communication, Tools, Info, Memory |
| Info subtabs | data-sitab | si-{value} | Overview, License, Comm, Sensor, OSS, RadioCert |
| Trends | data-trtab | tr-{value} | Flicker, Unbalance, Current |
| SimpleMeas | data-smtab | sm-{value} | 仪表, 相量, 波形 |
| Config | data-cftab | cf-{value} | 连接, 标称电压, ... |
| Events | data-filter | (comparison) | 全部, 骤降, 骤升, 瞬变, 谐波 |

## Sed as a fallback
For small targeted fixes after the main script, `sed -i ''` on macOS works well:
```bash
sed -i '' "s/old/new/g" file.js
```
Always verify with `grep` and `node --check` after sed edits.
