# HTML Prototyping for Embedded UI Development

## When to use

The SDL2/LVGL simulator is crashing, unstable, or too slow for rapid design iteration. Create a browser-based HTML prototype to:

1. Verify visual design and layout before writing C code
2. Test all navigation paths and interactions instantly
3. Iterate on colors, sizing, and spacing with F5 refresh
4. Avoid compile/recompile cycles

## Technique

Create a single self-contained `.html` file with:
- Inline CSS matching the LVGL theme (dark background, monospace fonts, color palette)
- Chart.js CDN for charts (bar, line, scatter — matches LVGL chart capabilities)
- Vanilla JS for page switching (no framework needed)
- DIV-based layout mimicking the LVGL object hierarchy

### Color mapping

| LVGL Constant | CSS Color | Usage |
|---|---|---|
| `COLOR_BG` | `#000000` | Page background |
| `COLOR_BG2` | `#1a1a1a` | Sidebar, tab bar |
| `COLOR_BTN_BG` | `#252525` | Button background |
| `COLOR_SEP` | `#333333` | Borders, separators |
| `COLOR_TEXT` | `#e0e0e0` | Primary text |
| `COLOR_DIM` | `#666666` | Secondary text |
| `COLOR_GRAY` | `#999999` | Labels |
| `COLOR_ACCENT` | `#ff8c00` | Active/highlight |
| `COLOR_L1` | `#ffd700` | Phase A (yellow) |
| `COLOR_L2` | `#00cc00` | Phase B (green) |
| `COLOR_L3` | `#ff3333` | Phase C (red) |
| `COLOR_N` | `#4488ff` | Neutral (blue) |

### Navigation replication

The three-tier LVGL navigation is replicated as:

```
L1: Sidebar buttons → show/hide page DIVs
L2: Tab buttons / inner sidebar buttons → show/hide sub-panel DIVs  
L3: Dialog overlays (absolute positioned DIVs)
```

### Chart replication

LVGL `lv_chart` maps to Chart.js `type: 'line'` with `pointRadius: 0` and `tension: 0.3`.
LVGL `lv_chart` bar type maps to Chart.js `type: 'bar'`.

### File location convention

Place in the project root as `ui_prototype.html`. Open with `open ui_prototype.html` or double-click in Finder.

## Limitations (CRITICAL)

**HTML does NOT translate to LVGL C code.** LVGL uses its own layout model (flex, row, column, grid) that is fundamentally different from CSS box model. The HTML prototype is a **visual reference only** — you will need to manually rewrite every page in LVGL C. Do not expect to copy-paste or mechanically convert HTML structure to LVGL object hierarchy.

**What it IS good for:**
- Rapid visual iteration (F5 refresh vs C compile)
- Stakeholder review and design approval
- Verifying color palette, spacing, and layout proportions

**What it is NOT:**
- A code generator for LVGL C
- A layout system that maps to LVGL widgets 1:1

## When to translate back to C

Only after:
1. Design is visually approved in browser
2. All interactions verified
3. Color/sizing/spacing finalized

Then translate each page section to LVGL C code — the HTML structure directly maps to the LVGL object hierarchy (DIV → lv_obj, table → lv_table, canvas → lv_chart).
