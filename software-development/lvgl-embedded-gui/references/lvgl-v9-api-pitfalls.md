# LVGL v9 API Pitfalls — Quick Reference for Agents

## Banned APIs (will not compile)

| ❌ DO NOT USE | ✅ USE INSTEAD |
|---|---|
| `lv_table_set_col_count(tbl, n)` | `lv_table_set_column_count(tbl, n)` |
| `lv_canvas_draw_line(canvas, pts, n, dsc)` | `lv_line` widget + `lv_line_set_points()` |
| `lv_canvas_draw_arc(canvas, x, y, r, start, end, dsc)` | `lv_line` or draw layer API |
| `lv_indev_get_data(indev)` | `lv_indev_get_key(indev)` |
| `lv_scr_act()` | `lv_screen_active()` |
| `lv_obj_set_style_size(obj, val, part)` | `lv_obj_set_style_width()` + `lv_obj_set_style_height()` |

## Fonts Only Available If Explicitly Enabled

By default, only these are compiled:
- `lv_font_montserrat_14`, `16`, `20`, `24`, `28`, `32`, `36`, `40`

These do NOT exist unless added to lv_conf:
- ❌ `lv_font_montserrat_10`
- ❌ `lv_font_montserrat_12`

**Always use font size ≥ 14** unless you explicitly enable smaller fonts.

## Canvas Drawing in v9

v8 used: `lv_canvas_draw_line(canvas, pts, 2, &dsc)`
v9 requires: init_layer → draw_line → finish_layer (complex)

**For simple diagrams (phasors, axes, vectors):**
Use `lv_line` widgets directly — they are trivial and v9-native:
```c
lv_obj_t *line = lv_line_create(parent);
static lv_point_t pts[] = {{0, 0}, {100, 100}};  // remove 'static' if values are runtime
lv_line_set_points(line, pts, 2);
lv_obj_set_style_line_color(line, lv_color_hex(0xFF0000), 0);
lv_obj_set_style_line_width(line, 3, 0);
```

## Static With Runtime Values

❌ `static lv_point_t pts[2] = {{cx, cy}, {ex, ey}};` // cx/cy are runtime → compile error
✅ `lv_point_t pts[2] = {{cx, cy}, {ex, ey}};` // non-static, compiles fine

## Event Target vs Current Target

`lv_event_get_target(e)` returns the **deepest child** that was clicked (e.g., a label inside a button).
`lv_event_get_current_target(e)` returns the **widget the event handler was registered on**.

When comparing against stored widget pointers (tab button arrays, sidebar items), always use `lv_event_get_current_target`:

```c
// ❌ BROKEN — clicking label child fails pointer comparison
lv_obj_t *btn = lv_event_get_target(e);
for (int i = 0; i < 3; i++) {
    if (ctx->tab_btns[i] == btn) { idx = i; break; }  // label ≠ button
}

// ✅ CORRECT
lv_obj_t *btn = lv_event_get_current_target(e);
for (int i = 0; i < 3; i++) {
    if (ctx->tab_btns[i] == btn) { idx = i; break; }  // always matches
}
```

**Real-world impact**: In `ui_page_dip_swell.c`, clicking on tab label text caused `tab_click_cb` to get the label as target instead of the button. The pointer comparison loop found no match, so `idx` fell back to 0 — tab switching broke entirely for label clicks.

## Macro Redefinition in Page Files

**Never redefine shared constants in individual `.c` files when the project header already defines them.**

### The problem
```c
// ut285e.h — project header
#define CONTENT_W    (SCREEN_W - CONTENT_X - 4)
#define COLOR_ACCENT lv_color_hex(0xFF8C00)

// ui_page_harmonics.c — PAGE FILE (WRONG)
#define CONTENT_W    682          // shadows header — drifts on layout changes
#define COLOR_ACCENT lv_color_hex(0xFF8C00)  // duplicate, maintenance hazard

// Code elsewhere then double-wraps:
lv_color_hex(COLOR_ACCENT)  // → lv_color_hex(lv_color_hex(0xFF8C00)) → TYPE ERROR
```

### The fix
1. Delete all duplicate `#define` blocks from page `.c` files
2. The `#include "ut285e.h"` already provides them
3. Remove any `lv_color_hex(COLOR_*)` wrappers in code — the macro IS already `lv_color_t`

```c
// ✅ CORRECT
#include "ut285e.h"
// CONTENT_W, COLOR_ACCENT, etc. are already defined

lv_obj_set_style_bg_color(obj, COLOR_ACCENT, 0);  // no extra lv_color_hex()
```

**Real-world impact**: `ui_page_harmonics.c` had 15 duplicate macros (lines 12-24). `ui_page_transient.c` had 15 duplicates PLUS 45 instances of double-wrapped `lv_color_hex(COLOR_XXX)` that broke after the duplicates were removed and the header's `lv_color_hex()`-wrapped values kicked in.

## Delegation Checklist

When delegating LVGL code to subagents, prepend to context:
```
USE LVGL v9 API ONLY. Do not use:
- lv_canvas_draw_line / lv_canvas_draw_arc (deprecated, use lv_line instead)
- lv_table_set_col_count (use lv_table_set_column_count)
- lv_font_montserrat_12 or _10 (not compiled by default, use font ≥ 14)
- lv_indev_get_data (does not exist, use lv_indev_get_key)
- static arrays with runtime initializer values
- lv_event_get_target for comparing against stored widget pointers (use lv_event_get_current_target)
Use COLOR_* constants from ut285e.h directly — do not redefine or double-wrap with lv_color_hex().
```
