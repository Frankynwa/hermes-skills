# LVGL Bug Patterns and Debugging

## 1. The `lv_event_get_target` Trap (HIGH-FREQUENCY BUG)

**Pattern:** Using `lv_event_get_target(e)` in button click callbacks that compare against stored button pointers.

**Why it fails:** When a button has a label child, clicking the label text makes `lv_event_get_target` return the label, not the button. If the callback then compares this against a stored `lv_obj_t *` array of button pointers, the match fails silently.

**Correct usage:**

```c
// WRONG — breaks when clicking label text
lv_obj_t *btn = lv_event_get_target(e);
for (int i = 0; i < COUNT; i++) {
    if (stored_btns[i] == btn) { ... }  // label never matches
}

// RIGHT — always returns the event-bound object
lv_obj_t *btn = lv_event_get_current_target(e);
```

**When `lv_event_get_target` IS safe:**
- `lv_dropdown_get_selected(lv_event_get_target(e))` — dropdown VALUE_CHANGED events always fire on the dropdown itself
- Callbacks that only modify the target's own styles (no pointer comparison)

**Scan command to find all instances:**
```bash
grep -rn 'lv_event_get_target(e)' src/*.c
```

**Expected count per callback class:**
- Radio button callbacks comparing against stored buttons → **BUG**
- Tab button callbacks matching against stored tab objects → **BUG**
- Dropdown callbacks → **OK**
- Printf-only callbacks with no comparison → **low impact**

## 2. LVGL Reentrancy Deadlock (beachball/freeze)

**Pattern:** Creating complex widget trees (many children, flex layouts, charts) inside an LVGL event handler callback.

**Root cause:** The SDL main loop calls `lv_timer_handler()` which processes events AND timers in one call. Creating heavy widgets during event processing can exhaust memory or trigger internal LVGL assertions, freezing the main thread.

**Diagnostics:** Add `printf(...); fflush(stdout);` at key points in page creation functions. Run from terminal to see which step hangs. LVGL assertion errors print to stderr.

**Known-safe approaches:**
1. Create lightweight pages (< 20 objects) in event handlers — fine
2. Create ALL pages at startup before `lv_timer_handler()` loop starts — safe but slow startup
3. Use `lv_timer_create(cb, 1, NULL)` to defer creation — UNRELIABLE in LVGL v9 (timer may fire in same handler call)

**Pitfall:** The LVGL main loop in SDL:
```c
while (1) {
    lv_timer_handler();  // processes events + timers in ONE call
    SDL_Delay(...);
}
```
Timers created during event processing fire in the same `lv_timer_handler()` call, NOT deferred to next frame. This defeats `lv_timer_create`-based deferral.

**Working solution — main-loop flag pattern:**

1. In `ut285e.h`, declare: `extern volatile int g_pending_create;` and `void ui_pages_process_deferred(void);`
2. In `ui_pages.c`, define `volatile int g_pending_create = -1;`. When a heavy page needs creation, set `g_pending_create = page_id;` and return immediately.
3. Implement `ui_pages_process_deferred(void)` that checks the flag, creates the page, and toggles visibility.
4. In `main.c`'s main loop, check the flag AFTER `lv_timer_handler()` returns:
```c
while (1) {
    uint32_t ms = lv_timer_handler();
    if (g_pending_create >= 0) {
        ui_pages_process_deferred();
    }
    SDL_Delay(ms);
}
```

This ensures creation happens OUTSIDE any LVGL event context, between event-handler calls. The key insight: `lv_timer_create` callbacks fire in the same `lv_timer_handler()` call, but a flag checked between calls is truly deferred.

## 3. Memory Allocation Failure → NULL Assertion

**Pattern:** `lv_chart_create()` or similar constructor returns NULL during startup page creation.

**Diagnosis:** Enable LVGL assertions (`LV_USE_ASSERT_OBJ`) to see which `lv_obj_set_size` or `lv_obj_create` gets NULL.

**Root cause:** With LVGL debug features enabled (`LV_USE_ASSERT_MEM_INTEGRITY`, `LV_USE_ASSERT_OBJ`, style checks), object allocation overhead increases significantly. Creating many complex objects (charts with series, tables) at once can exhaust memory even when only a few pages exist.

## 4. Macro Redefinition Bugs

**Pattern:** Page files (`ui_page_xxx.c`) redefining `CONTENT_W`, `CONTENT_H`, `TABBAR_H`, `COLOR_*` that are already in `ut285e.h`.

**Why it's bad:** Local definitions shadow the header. If someone updates values in the header, the local copies stay stale, causing inconsistent dimensions/colors.

**Scan command:**
```bash
grep -n '^#define \(CONTENT_W\|CONTENT_H\|TABBAR_H\|COLOR_\)' src/ui_page_*.c
```

Should return ZERO results — all these macros should come from `ut285e.h` only.

## 5. Layout Overflow from SCREEN vs CONTENT dimensions

**Pattern:** Page-level code using `SCREEN_W`/`SCREEN_H` when placed inside a `page_container` sized to `CONTENT_W`×`CONTENT_H`.

**Key dimensions:**
- `SCREEN_W` = 800, `SCREEN_H` = 480 (full display)
- `CONTENT_W` = 682, `CONTENT_H` = 442 (area inside page container, after sidebar + statusbar)
- Overflow: 800 > 682, 480 > 442 → elements clipped

**Scan command:**
```bash
grep -n 'SCREEN_W\|SCREEN_H' src/ui_page_*.c
```

Should return empty (or only in files that render at screen level, like statusbar).
