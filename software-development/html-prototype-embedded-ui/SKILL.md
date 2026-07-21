---
name: html-prototype-embedded-ui
description: Use HTML/CSS/JS prototypes for embedded UI development when native simulators are unstable. Rapid visual iteration in browser, then translate to C/LVGL code.
version: 1.0.0
---

# HTML Prototype for Embedded UI

When developing UI for embedded systems (LVGL, TouchGFX, etc.) and the native simulator is unstable or slow, build a self-contained HTML prototype first. Iterate visually in the browser with zero crashes and instant reload, then translate the final design to C code.

## Trigger Conditions

Load this skill when:
- User is developing embedded UI (LVGL, embedded C GUI, etc.)
- Native simulator keeps crashing or is too slow for rapid iteration
- User wants to see UI changes immediately without compilation
- User needs to prototype complex nested navigation (tabs, sidebars, dialogs)

## Workflow

1. **Build HTML prototype** — single `.html` + separate `.js` file, dark theme matching the target device
2. **Use Chart.js CDN** for charts/graphs (line, bar, scatter)
3. **Iterate** — user refreshes browser to see changes instantly
4. **Translate to C** — once design is finalized, convert HTML structure to LVGL API calls

## Key Pitfalls

### DO NOT use Python write_file for complex HTML/JS
Python's `write_file` and string escaping corrupt backslashes in nested quotes. Three levels of quoting (Python → file → JavaScript string) always break.

**Use shell heredoc instead:**
```bash
cat > file.js << 'JSEOF'
// JavaScript code here — no escaping needed
// Single quotes, double quotes, backslashes all work natively
JSEOF
```

### Event delegation and text nodes
When using `e.target.dataset.*` for click delegation, clicking on special characters (like `›`) inside buttons makes `e.target` a text node, not the button. Use `e.target.closest('[data-*]')` or add `onclick` directly to buttons.

### Separate HTML and JS
Keep HTML structure and JavaScript logic in separate files (`ui_prototype.html` + `ui_prototype.js`). This avoids escaping hell entirely.

## LVGL Translation Guide

| HTML/CSS | LVGL C API |
|----------|-----------|
| `<div class="sidebar">` | `lv_obj_create()` + `lv_obj_set_flex_flow(LV_FLEX_FLOW_COLUMN)` |
| `<button>` | `lv_btn_create()` + `lv_obj_add_event_cb(btn, cb, LV_EVENT_CLICKED, ...)` |
| `<table>` | `lv_table_create()` + `lv_table_set_cell_value()` |
| Chart.js line chart | `lv_chart_create()` + `lv_chart_add_series()` + `lv_chart_set_next_value()` |
| `<input>` / `<select>` | `lv_textarea_create()` / `lv_dropdown_create()` |
| `position:fixed` overlay | `lv_obj_create()` on top layer + `lv_obj_center()` |
| `classList.toggle('show')` | `lv_obj_add_flag/clear_flag(obj, LV_OBJ_FLAG_HIDDEN)` |
| `display:flex` row | `lv_obj_set_flex_flow(cont, LV_FLEX_FLOW_ROW)` |

## macOS LVGL v9 Simulator Stability

If using the LVGL SDL2 simulator on macOS, disable these debug flags in `lv_conf_macos.h` to prevent OOM crashes:

```c
#define LV_USE_ASSERT_MEM_INTEGRITY 0  // memory canaries double usage
#define LV_USE_ASSERT_OBJ           0  // object sanity checks add overhead
#define LV_USE_MEM_MONITOR          0  // allocation tracking grows unbounded
```

These three flags with 500+ LVGL objects cause `lv_realloc: couldn't reallocate memory` crash within ~6 seconds.

## References

- `references/lvgl-chart-api.md` — LVGL v9 chart API notes (correct function signatures, common mistakes)
