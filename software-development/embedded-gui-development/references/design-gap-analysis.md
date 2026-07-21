# Design-to-Code Gap Analysis Methodology

Reusable workflow for comparing embedded UI design documents (PDFs) against
actual code implementation, producing quantifiable completion metrics.

## When to Use

- User has a design PDF/spec for an embedded GUI and wants to know what's
  implemented vs missing
- Porting a UI from one platform to another and need to track parity
- Code review of a UI project against its design spec

## Step-by-Step

### 1. Extract design pages as high-res images

Use PyMuPDF (fitz) — typically already available in Python environments:

```python
import fitz, os
doc = fitz.open('/path/to/design.pdf')
outdir = '/tmp/project_pages'
os.makedirs(outdir, exist_ok=True)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)  # 200 DPI for readable text
    pix.save(f'{outdir}/page_{i+1:02d}.png')
doc.close()
```

**Pitfall**: Don't inline the Python in `terminal()` — single quotes in
file paths cause shell escaping issues. Use `write_file` to save the script
to `/tmp/`, then `terminal("python3 /tmp/script.py")`.

### 2. Analyze each page with vision

Call `vision_analyze` for each page, asking structured questions:

- "Describe the layout structure (top bar, sidebar, content area)"
- "List all sub-pages/tabs and their names"
- "List every control (buttons, dropdowns, inputs, switches, checkboxes, charts, tables)"
- "Include exact label text for each control"

### 3. Read corresponding source code

For each UI page in the design, read the matching source file(s) with
`read_file`. Note the line count, widget count, and what's actually implemented.

### 4. Create a structured comparison

For each design page, produce a table:

| Sub-page | Design Controls | Code Status | Gap |
|---|---|---|---|

Mark each as: fully implemented / partially implemented / not implemented.

### 5. Quantify completion

At the end, produce a summary table:

| Category | Total Pages | Done | Partial | Missing |
|---|---|---|---|---|
| Settings | 14 | 6 | 3 | 5 |
| ... | ... | ... | ... | ... |

And a completion percentage to give a clear picture of overall progress.

## Bug Verification Pre-check

Before fixing any reported bugs, ALWAYS read the source code to verify
each one. Common false reports include:

- `lv_snapshot_take` return type: returns `lv_draw_buf_t *` not
  `lv_image_dsc_t *`, but both structs are binary-compatible by design
  (reserved fields ensure alignment). Only produces a compiler warning,
  not a crash.
- `printf` format mismatches: if code already has explicit casts like
  `(unsigned long)ms` with `%lu`, it's correct on both 32-bit and 64-bit ARM.
- systemd `ProtectSystem=strict`: only restricts `/usr`, `/boot`, `/etc`;
  `/mnt` is NOT restricted, so eMMC paths under `/mnt` don't need
  `ReadWritePaths` additions.

### Per-page Smoke Testing

When a simulator crashes on startup, isolate which page causes the crash
by testing each page individually via CLI args:

```bash
./simulator overview      # baseline — should work
./simulator config        # test each page one at a time
./simulator trends
./simulator simplemeas    # find the crashing page
```

If the simulator has per-page CLI support, this is the fastest way to
distinguish SDL2/driver bugs (rare) from page-specific UI bugs (common).

## Confirmed Common Pitfalls (verified in UT285E)

- **`lv_event_get_target` vs `lv_event_get_current_target`**: When a button
  has a label child, clicking the label returns the label as target, not
  the button. Tab switching by pointer comparison fails silently. Fix:
  use `lv_event_get_current_target(e)`.
- **Macro redefinition**: Page files redefining `CONTENT_W/H`, `COLOR_*`
  already in the project header. These copies drift apart silently.
  Double-wrapping (`lv_color_hex(COLOR_ACCENT)` when the macro already
  expands to `lv_color_hex(...)`) causes type errors.
