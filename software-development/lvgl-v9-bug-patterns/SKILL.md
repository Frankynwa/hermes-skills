---
name: lvgl-v9-bug-patterns
description: Systematic LVGL v9 bug patterns — event target mismatch, layout overflow, macro redefinition. Run this before code review on any LVGL v9 project.
---

# LVGL v9 Bug Patterns

Trigger conditions: reviewing, debugging, or writing LVGL v9 C code — especially embedded UI pages with nested children (buttons with labels), page containers with fixed sizes, or shared header files.

## Pattern 1: `lv_event_get_target` vs `lv_event_get_current_target`

### The bug

When a button has a label child, clicking on the label text makes `lv_event_get_target(e)` return the **label** — not the button. Any callback that compares the target against stored button pointers will fail.

### Detection

```bash
grep -n 'lv_event_get_target(e)' src/*.c
```

Then check each hit: if the result is compared against stored `lv_obj_t *` pointers or used for state changes on the stored object, it's a bug.

### Safe patterns (not bugs)

- `lv_dropdown_get_selected(lv_event_get_target(e))` — dropdown VALUE_CHANGED always fires on the dropdown itself
- Printf-only callbacks that just log the target
- Callbacks that use `lv_event_get_user_data(e)` for identification (not target comparison)

### Fix

```c
// BEFORE (bug)
lv_obj_t *btn = lv_event_get_target(e);
for (int i = 0; i < N; i++) {
    if (ctx->btns[i] == btn) { ... }
}

// AFTER (fixed)
lv_obj_t *btn = lv_event_get_current_target(e);
```

`get_current_target` returns the object the event handler was **registered on** — always the button, never its label child.

### Radio button variant

Even without stored-pointer comparison, radio highlight callbacks are affected:

```c
// BEFORE: stores label as selected_btn → highlight on wrong object
static void radio_cb(lv_event_t *e) {
    lv_obj_t *btn = lv_event_get_target(e);
    selected_btn = btn;  // ← label, not button!
    lv_obj_set_style_border_color(btn, COLOR_ACCENT, 0);
}

// AFTER: use get_current_target
```

## Pattern 2: Page-level layout overflow

### The bug

Pages are created inside `page_container` (sized to `CONTENT_W × CONTENT_H`), but their root objects use `SCREEN_W × SCREEN_H` dimensions. The page_container clips the overflow, but when the page is given correct dimensions (CONENT_W × CONTENT_H), internal elements calculated from SCREEN_W/SCREEN_H may still be wrong.

### Detection

```bash
grep -n 'SCREEN_W\|SCREEN_H' src/*.c
```

Flag any use of `SCREEN_W` or `SCREEN_H` inside page builder functions (not statusbar/sidebar which are screen-level).

### Fix points

- Root page object: `SCREEN_W,SCREEN_H` → `CONTENT_W,CONTENT_H`
- Sidebar height: `SCREEN_H` → `CONTENT_H`
- Content area size: `SCREEN_H` → `CONTENT_H`
- Panel heights: `SCREEN_H - CONTENT_Y - 4` → `CONTENT_H - 4`
- Content width macros: `(SCREEN_W - sidebar - gap)` → `(CONTENT_W - sidebar - gap)`

### Verification

After fixing, check that `CFG_CONTENT_W + CFG_SIDEBAR_W + gaps ≤ CONTENT_W`.

## Pattern 3: Macro redefinition

### The bug

Page `.c` files redefine `CONTENT_W`, `COLOR_*`, `TABBAR_H` etc. that are already defined in `ut285e.h`. Local definitions shadow the header, so changing header values won't take effect.

### Detection

```bash
grep -rn '^#define (CONTENT_W|CONTENT_H|TABBAR_H|COLOR_)' src/*.c
```

Any hits mean redefinition. Delete the local copies.

### Watch out

If local copies use different formats (e.g., bare `0xFF8C00` vs header's `lv_color_hex(0xFF8C00)`), the page code may double-wrap (`lv_color_hex(COLOR_XXX)`). After removing local defines, strip the `lv_color_hex()` wrapper from usages:

```bash
sed -i '' 's/lv_color_hex(COLOR_\([A-Z0-9]*\))/COLOR_\1/g' src/file.c
```

## Pattern 4: Beachball freeze on page creation

### Symptoms

Clicking a sidebar menu item causes the SDL window to freeze (macOS beachball). The page is created on-demand via `ui_pages_switch → create_page → page_builder()`.

### Debugging approach

1. Add `printf("...\n"); fflush(stdout);` at each step in the page creation function
2. Comment out panels one by one (down to just one) to isolate
3. Rebuild and test
4. If even single-panel freezes, the issue is in the root page or sidebar layout
5. If single panel works, add panels back one at a time to find the culprit

### Common cause

Complex flex layouts with many children inside a fixed-size container. LVGL may trigger layout recalculation when showing a page for the first time.

## Pattern 7: LVGL debug flags cause OOM crash on macOS

### The bug

Three LVGL debug flags enabled in `lv_conf_macos.h` cause the SDL2 simulator to crash with OOM after ~6 seconds:

- `LV_USE_ASSERT_MEM_INTEGRITY 1` — adds memory canaries around every allocation (doubles usage)
- `LV_USE_ASSERT_OBJ 1` — sanity checks on every object operation (extra allocations per op)
- `LV_USE_MEM_MONITOR 1` — tracks all allocations in a growing data structure

With 500+ LVGL objects in a full UI, these three combined exhaust the memory pool. The crash is:
```
[Error] lv_realloc: couldn't reallocate memory
[Error] get_local_style: Asserted at expression: obj->styles != NULL (Out of memory)
```

### Detection

The crash always happens at exactly the same uptime (~6 seconds), suggesting a periodic LVGL timer triggers allocation. If the first screenshot shows the Overview page correctly but the process dies shortly after, this is likely the cause.

```bash
grep -E 'ASSERT_MEM_INTEGRITY|ASSERT_OBJ|MEM_MONITOR' lv_conf_macos.h | grep -v '//.*0'
```

Any of these returning `1` on macOS is a crash risk.

### Fix

Disable all three for macOS development builds:

```c
// In lv_conf_macos.h:
#define LV_USE_ASSERT_MEM_INTEGRITY 0
#define LV_USE_ASSERT_OBJ           0
#define LV_USE_MEM_MONITOR          0
```

Keep `ASSERT_NULL`, `ASSERT_MALLOC`, and `ASSERT_STYLE` enabled for safety — those don't cause OOM.

### Fallback: HTML prototyping

When the SDL2 simulator is still unstable even after fixes, create an HTML/CSS prototype with Chart.js for embedded UI development. Build all pages, navigation, and charts in a single `.html` file. Verify visual design in browser (zero compile, zero crash), then translate to C code only when the design is finalized. 

### Verification

Rebuild and run. The simulator should stay alive indefinitely (30+ seconds without crash). Log should show zero errors.

### The bug

`lv_chart_set_series_value_by_id2` is a scatter-chart-only API (`LV_CHART_TYPE_SCATTER`). Using it on a `LV_CHART_TYPE_LINE` chart:

- Produces `[Warn] lv_chart_set_series_value_by_id2: Type must be LV_CHART_TYPE_SCATTER` on **every single call**
- Each warning allocates internal buffers in LVGL's statically-sized memory pool
- After ~90+ warnings (31 data points × 3 series), the pool is exhausted
- Crashing with: `lv_realloc: couldn't reallocate memory` → `get_local_style: Out of memory`
- The simulator dies silently after ~6 seconds

### Detection

```bash
grep -rn 'set_series_value_by_id2' src/*.c
```

Then check the chart type: if it's `LV_CHART_TYPE_LINE`, this is a crash bug.

### Fix

```c
// BEFORE (crashes after 90+ calls)
lv_chart_set_series_value_by_id2(chart, s1, t, (int32_t)t, (lv_value_precise_t)val);

// AFTER (safe for LINE charts, auto-increments x)
lv_chart_set_next_value(chart, s1, (int32_t)val);
```

### Verification after fix

Rebuild and run. The warning count should be zero (or only unrelated warnings). The simulator should stay alive indefinitely (not crash after 6 seconds).

When panels are conditionally created or being debugged, `sidebar_set_active` must handle NULL:

```c
static void sidebar_set_active(int idx) {
    for (int i = 0; i < N; i++) {
        if (!sidebar_btns[i]) continue;       // guard against NULL btn
        // ... style changes ...
        if (cfg_ctx.panels[i]) {              // guard against NULL panel
            // ... show/hide ...
        }
    }
}
```
