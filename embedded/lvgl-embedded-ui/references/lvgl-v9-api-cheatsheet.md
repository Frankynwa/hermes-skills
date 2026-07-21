# LVGL v9 API Cheatsheet (v8 → v9 Breaking Changes)

## Widget APIs

### Tabview
```c
// v8: lv_tabview_create(parent, LV_DIR_TOP, TABBAR_H)
// v9: 
lv_obj_t *tv = lv_tabview_create(parent);
lv_tabview_set_tab_bar_position(tv, LV_DIR_TOP);  // optional
lv_tabview_set_tab_bar_size(tv, 28);                // optional
```

### Table
```c
// v8: lv_table_set_col_count(table, 5)
// v9: REMOVED — columns auto-created when you set cell values
lv_table_set_cell_value(table, 0, 0, "Header");  // creates col 0
lv_table_set_cell_value(table, 0, 1, "L1");       // creates col 1
// Use lv_table_set_col_width(table, col, width) to set widths
```

### Chart
```c
// v8: lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_Y, 0, 100)
// v9:
lv_chart_set_axis_range(chart, LV_CHART_AXIS_PRIMARY_Y, 0, 100);

// v8: lv_chart_set_axis_tick(chart, axis, major, minor, ...)
// v9: REMOVED — use lv_chart_set_div_line_count() instead

// Series colors:
lv_chart_series_t *ser = lv_chart_add_series(chart, lv_color_hex(0xFF8C00), LV_CHART_AXIS_PRIMARY_Y);
// lv_chart_set_series_color(chart, ser, color) — works in both v8/v9

// Chart types:
lv_chart_set_type(chart, LV_CHART_TYPE_LINE);  // or LV_CHART_TYPE_BAR
```

### Fonts
```c
// NOT all sizes are enabled by default in lv_conf.h
// Available depends on LV_FONT_MONTSERRAT_XX defines
// Usually: 14, 16, 18, 20, 22, 24, 28, 32, 36, 40, 48
// 10, 12 are NOT enabled by default — check lv_conf.h

// Always use:
lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, 0);
```

### Parts
```c
// v8: LV_PART_TICKS
// v9: LV_PART_INDICATOR (for chart axis labels, tick marks)

// Common parts in v9:
LV_PART_MAIN        // Main background/border
LV_PART_ITEMS       // Table cells, chart bars
LV_PART_INDICATOR   // Chart axis labels, progress bar fill
LV_PART_KNOB        // Slider knob
LV_PART_SCROLLBAR   // Scrollbar
```

### Display
```c
// v8: lv_disp_set_draw_buf(disp, &buf)
// v9: 
lv_display_set_buffers(disp, buf1, buf2, buf_size, LV_DISPLAY_RENDER_MODE_PARTIAL);
// OR for direct mode:
lv_display_set_draw_buffers(disp, &draw_buf1, &draw_buf2);

// v8: lv_scr_load(scr)
// v9: lv_screen_load(scr);  // but lv_scr_load() still works as alias

// v8: lv_disp_get_scr_act(disp)
// v9: lv_screen_active();
```

### Color Handling
```c
// Macros like COLOR_BG = lv_color_hex(0x000000) return lv_color_t
// Do NOT wrap with lv_color_hex() again:
lv_obj_set_style_bg_color(obj, COLOR_BG, 0);        // ✓ correct
lv_obj_set_style_bg_color(obj, lv_color_hex(COLOR_BG), 0);  // ✗ type mismatch

// In static initializers, lv_color_hex() is a function call (not constant):
// ✗ static lv_color_t c = lv_color_hex(0xFF0000);  // NOT compile-time constant
// ✓ Use uint32_t in static structs, convert at usage:
typedef struct { uint32_t color; } entry_t;
static const entry_t entries[] = {{.color = 0xFF0000}};
lv_obj_set_style_bg_color(obj, lv_color_hex(entries[0].color), 0);
```

### Object Flags
```c
// v8: lv_obj_set_hidden(obj, true)
// v9: 
lv_obj_add_flag(obj, LV_OBJ_FLAG_HIDDEN);     // hide
lv_obj_clear_flag(obj, LV_OBJ_FLAG_HIDDEN);   // show

// Scrollable:
lv_obj_clear_flag(obj, LV_OBJ_FLAG_SCROLLABLE);  // disable scrolling
```

### Flex Layout
```c
lv_obj_set_flex_flow(container, LV_FLEX_FLOW_ROW);
lv_obj_set_flex_align(container, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
lv_obj_set_style_pad_column(container, 4, 0);
lv_obj_set_style_pad_row(container, 2, 0);
```
