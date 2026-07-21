---
name: lvgl-v9-development
description: LVGL v9 embedded UI development — page creation patterns, chart API quirks, font configuration pitfalls, and project architecture conventions. Use when adding pages, charts, or troubleshooting LVGL v9 compilation.
---

# LVGL v9 Embedded UI Development

## When to use
- Adding a new page to an LVGL v9 project
- Creating charts (line, scatter) with `lv_chart`
- Compilation errors from font, color, or chart API mismatches
- Cross-platform LVGL projects (macOS simulator + embedded target)

## Page creation checklist (5 files to touch)

For any page `page_foo_create`, modify these files in order:

| # | File | Change |
|---|------|--------|
| 1 | `ut285e.h` | Add `PAGE_FOO` to `page_id_t` enum *before* `PAGE_COUNT`; add `lv_obj_t *page_foo_create(lv_obj_t *parent);` declaration |
| 2 | `ui_pages.c` | Add `extern lv_obj_t *page_foo_create(lv_obj_t *parent);` at top; add to `page_builders[]` array; add to `page_names[]` array |
| 3 | `ui_sidebar.c` | Bump `MAX_MENU_ITEMS`; add label to `menu_labels[]` |
| 4 | `CMakeLists.txt` | Add `src/ui_page_foo.c` to source list |
| 5 | Create `src/ui_page_foo.c` | Implement the page builder function |

**Pitfall**: `PAGE_COUNT` drives the sidebar's loop condition (`for i < PAGE_COUNT`). If your new enum value is after `PAGE_COUNT`, the sidebar button won't appear.

## LVGL v9 Chart API

### Correct API for line charts
```c
// ✅ CORRECT: 3 args, value auto-increments x
lv_chart_set_next_value(chart, series, (int32_t)value);

// ✅ CORRECT: 4 args, explicit x + y (SCATTER type only)
lv_chart_set_next_value2(chart, series, x_val, y_val);

// ✅ CORRECT: explicit point by ID
lv_chart_set_series_value_by_id2(chart, series, x_id, (int32_t)x, (lv_value_precise_t)y);
```

### Wrong API that causes compilation errors OR OOM crashes
```c
// ❌ WRONG: set_next_value2 needs 4 args, not 3
lv_chart_set_next_value2(chart, series, (lv_value_precise_t)value);

// ❌ WRONG: set_next_value2 requires LV_CHART_TYPE_SCATTER, not LINE

// ❌ CRITICAL: set_series_value_by_id2 on LINE chart causes silent OOM
lv_chart_set_series_value_by_id2(chart, s, t, (int32_t)t, (lv_value_precise_t)val);
```

**Pitfall — OOM CRASH**: `lv_chart_set_series_value_by_id2` requires `LV_CHART_TYPE_SCATTER`. Using it on a LINE chart produces a warning on EVERY call (e.g., 31 warnings for 31 data points × 3 series = 93 warnings). Each warning allocates internal buffers; after ~90+ warnings, LVGL exhausts its statically-sized memory pool and crashes with `lv_realloc: couldn't reallocate memory` followed by `get_local_style: Out of memory`. **This is not harmless — it kills the simulator after a few seconds.** Fix: use `lv_chart_set_next_value(chart, series, (int32_t)val)` for LINE charts.

### Chart setup boilerplate
```c
lv_obj_t *chart = lv_chart_create(parent);
lv_chart_set_type(chart, LV_CHART_TYPE_LINE);
lv_chart_set_point_count(chart, 50);
lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_Y, y_min, y_max);
lv_chart_set_div_line_count(chart, 4, 10);
// Dark theme styling:
lv_obj_set_style_bg_color(chart, lv_color_hex(0x0A0A0A), 0);
lv_obj_set_style_line_color(chart, lv_color_hex(0x222222), LV_PART_MAIN);

lv_chart_series_t *ser = lv_chart_add_series(chart, COLOR_L1, LV_CHART_AXIS_PRIMARY_Y);
for (int i = 0; i < N; i++) {
    lv_chart_set_next_value(chart, ser, (int32_t)(value));
}
lv_chart_refresh(chart);  // REQUIRED after bulk data fill — without this, chart shows empty
```

## Common compilation errors

### `srand` / `rand` implicit declaration
```c
// ❌ MISSING: stdlib.h not included
srand(42);
rand() % 100;

// ✅ FIX: add at top of file
#include <stdlib.h>
```
macOS clang in C99 mode rejects implicit function declarations. This applies to any file using `srand()`, `rand()`, or `malloc()`.

### Font not enabled in lv_conf

### Check which fonts are actually enabled
```bash
grep 'LV_FONT_MONTSERRAT.*1' lv_conf_macos.h
```

**Pitfall**: Many font sizes are disabled by default in LVGL config. Common enabled sizes: 14, 16, 20, 24, 28, 32, 36, 40. Sizes like 10, 12 are often NOT enabled — using `&lv_font_montserrat_10` causes `use of undeclared identifier` error. Always check `lv_conf_*.h` before using a font size.

## Color macro pitfalls

```c
// ❌ WRONG: lv_color_hex() is NOT a compile-time constant in C
static lv_color_t cols[] = {COLOR_L1, COLOR_L2};  // ERROR

// ✅ CORRECT: use non-static (local scope) arrays
lv_color_t cols[] = {COLOR_L1, COLOR_L2};  // OK
```

**Pitfall**: `lv_color_hex()` is a function call, not a constant expression. C compilers reject it in `static` array initializers. Remove `static` or use raw hex values.

## Architecture-first preference

When the user asks to consolidate multiple analyses, gap reports, or to cross-reference design documents with code — **always produce the structured architecture document first, before writing any code**. The user explicitly prefers this order:

1. Consolidate all analysis sources into one document
2. Cross-reference every claim against actual code
3. Correct misclassifications (e.g., items in different files marked "missing")
4. Present corrected status with completion statistics
5. Only then start implementation

Skipping this step and jumping to code wastes context, produces incomplete results, and the user will ask you to stop and go back. Save the architecture document to a `.md` file in the project root for future reference.

## Deferred page creation pitfall

The `ui_pages_process_deferred` / `g_pending_create` pattern creates LVGL objects **between** `lv_timer_handler()` calls. This was intended to avoid beachball freeze, but on macOS SDL2 it causes state corruption and crashes when clicking sidebar items.

### Symptoms
- Sidebar clicking causes crash even on already-created pages
- Non-deterministic crashes on page switch
- Memory errors after page creation

### Fix: remove deferred mechanism entirely

1. In `ui_pages.c`: make `ui_pages_switch()` call `create_or_get_page()` **synchronously** (not defer)
2. In `main.c`: remove `if (g_pending_create >= 0) ui_pages_process_deferred()` from main loop
3. In `ut285e.h`: remove `extern volatile int g_pending_create` and `extern void ui_pages_process_deferred()`

The simplified synchronous version:
```c
void ui_pages_switch(page_id_t page) {
    if (pages[visible_page]) lv_obj_add_flag(pages[visible_page], LV_OBJ_FLAG_HIDDEN);
    lv_obj_t *new_page = create_or_get_page(page);
    if (new_page) lv_obj_clear_flag(new_page, LV_OBJ_FLAG_HIDDEN);
    visible_page = page;
}
```

On modern macOS, page creation takes milliseconds — there is no beachball.

## HTML prototyping workflow

When the macOS SDL2 simulator repeatedly crashes (OOM, rendering bugs, LVGL internal errors) and debugging consumes more time than development, **pivot to an HTML/CSS prototype**:

1. Create a single-file HTML prototype that mirrors the LVGL simulator visually
2. Use Chart.js CDN for trend/bar/line charts with dark theme styling
3. Implement ALL pages + ALL navigation (sidebar, tabs, inner sidebars, dialogs)
4. Use event delegation (`data-*` attributes + click bubbling) instead of inline `onclick` — this avoids Python string escaping hell
5. Verify visual design in browser (instant feedback, zero compile, zero crash)
6. Only translate to C code when the design is finalized

### Critical: shell heredoc for writing HTML/JS

Python's `write_file` tool applies backslash escaping, which corrupts HTML/JS files with 3-level nested quoting (Python string → file → JavaScript string). **Always use shell heredoc** to write HTML/JS:

```bash
cat > file.html << 'HTMLEOF'
...raw HTML/JS content with no escape processing...
HTMLEOF
```

The `'HTMLEOF'` (quoted) prevents shell variable expansion and backslash interpretation. This is the ONLY reliable way to write complex frontend files through the terminal tool.
