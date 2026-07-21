# LVGL v9 API Quick Reference

## Display Setup
```c
lv_display_t *disp = lv_display_create(w, h);
lv_display_set_flush_cb(disp, flush_cb);
lv_display_set_buffers(disp, buf1, buf2, buf_size, LV_DISPLAY_RENDER_MODE_PARTIAL);
lv_display_set_color_format(disp, LV_COLOR_FORMAT_ARGB8888);
lv_display_set_render_mode(disp, LV_DISPLAY_RENDER_MODE_DIRECT);  // or PARTIAL/FULL
```

## Screen & Objects
```c
lv_obj_t *scr = lv_screen_active();           // was lv_scr_act() in v8
lv_obj_t *obj = lv_obj_create(parent);
lv_obj_set_size(obj, w, h);
lv_obj_set_pos(obj, x, y);
lv_obj_align(obj, LV_ALIGN_CENTER, x_ofs, y_ofs);
lv_obj_center(obj);
lv_obj_add_flag(obj, LV_OBJ_FLAG_HIDDEN);
lv_obj_clear_flag(obj, LV_OBJ_FLAG_HIDDEN);
lv_obj_clear_flag(obj, LV_OBJ_FLAG_SCROLLABLE);
```

## Styles
```c
lv_obj_set_style_bg_color(obj, lv_color_hex(0xRRGGBB), 0);
lv_obj_set_style_bg_opa(obj, LV_OPA_COVER, 0);
lv_obj_set_style_border_width(obj, 0, 0);
lv_obj_set_style_pad_all(obj, 0, 0);
lv_obj_set_style_text_color(obj, lv_color_hex(0xFFFFFF), 0);
lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, 0);
```

## Labels
```c
lv_obj_t *lbl = lv_label_create(parent);
lv_label_set_text(lbl, "Hello");
lv_label_set_text_fmt(lbl, "Value: %d", 42);
lv_label_set_long_mode(lbl, LV_LABEL_LONG_DOT);  // or WRAP, SCROLL, etc.
lv_obj_set_style_text_align(lbl, LV_TEXT_ALIGN_CENTER, 0);
```

## Tables
```c
lv_obj_t *table = lv_table_create(parent);
lv_table_set_col_cnt(table, 4);
lv_table_set_row_cnt(table, 8);
lv_table_set_cell_value(table, row, col, "text");
lv_table_set_col_width(table, col_idx, width);
// Style cells:
lv_obj_set_style_bg_color(table, lv_color_hex(0x333333), LV_PART_ITEMS);
```

## Charts (Line/Bar)
```c
lv_obj_t *chart = lv_chart_create(parent);
lv_chart_set_type(chart, LV_CHART_TYPE_LINE);  // or BAR
lv_chart_set_point_count(chart, 100);
lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_Y, min, max);
lv_chart_series_t *ser = lv_chart_add_series(chart, lv_color_hex(0xFF0000), LV_CHART_AXIS_PRIMARY_Y);
lv_chart_set_next_value(chart, ser, value);
lv_chart_refresh(chart);
```

## Tabs (v9: Tab View)
```c
lv_obj_t *tv = lv_tabview_create(parent);
lv_tabview_set_tab_bar_size(tv, 40);
lv_obj_t *tab1 = lv_tabview_add_tab(tv, "Tab 1");
lv_obj_t *tab2 = lv_tabview_add_tab(tv, "Tab 2");
```

## Dropdown
```c
lv_obj_t *dd = lv_dropdown_create(parent);
lv_dropdown_set_options(dd, "Option 1\nOption 2\nOption 3");
lv_dropdown_set_selected(dd, 0);
```

## Input Devices
```c
lv_indev_t *indev = lv_indev_create();
lv_indev_set_type(indev, LV_INDEV_TYPE_POINTER);
lv_indev_set_read_cb(indev, my_read_cb);
```

## Timer
```c
lv_timer_t *timer = lv_timer_create(callback, period_ms, user_data);
lv_timer_set_repeat_count(timer, count);  // -1 for infinite
```

## Color Constants (UT285E Theme)
```c
#define COLOR_BG       lv_color_hex(0x000000)  // Black
#define COLOR_TEXT     lv_color_hex(0xFFFFFF)  // White
#define COLOR_ACCENT   lv_color_hex(0xFF8C00)  // Orange
#define COLOR_RED      lv_color_hex(0xFF0000)  // Warning
#define COLOR_GREEN    lv_color_hex(0x00FF00)  // Good
#define COLOR_DIM      lv_color_hex(0x888888)  // Gray

// Three-phase colors
#define COLOR_L1       lv_color_hex(0xFFFF00)  // Yellow
#define COLOR_L2       lv_color_hex(0x00FF00)  // Green
#define COLOR_L3       lv_color_hex(0xFF0000)  // Red
#define COLOR_N        lv_color_hex(0x0088FF)  // Blue
```

## Render Modes
- `LV_DISPLAY_RENDER_MODE_PARTIAL` — render in strips (small buffer, most common)
- `LV_DISPLAY_RENDER_MODE_DIRECT` — render full framebuffer (needs large buffer)
- `LV_DISPLAY_RENDER_MODE_FULL` — render everything on every refresh

## Color Formats
- `LV_COLOR_FORMAT_ARGB8888` — 32-bit, most compatible with SDL2
- `LV_COLOR_FORMAT_RGB565` — 16-bit, common for embedded
- `LV_COLOR_FORMAT_I1` — 1-bit monochrome
