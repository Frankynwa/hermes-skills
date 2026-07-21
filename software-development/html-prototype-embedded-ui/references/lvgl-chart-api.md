# LVGL v9 Chart API Quick Reference

## Function Signatures (v9.x)

### Line Charts
```c
lv_obj_t *chart = lv_chart_create(parent);
lv_chart_set_type(chart, LV_CHART_TYPE_LINE);
lv_chart_set_point_count(chart, N);           // max data points per series
lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_Y, ymin, ymax);
lv_chart_set_div_line_count(chart, h_lines, v_lines);

lv_chart_series_t *s = lv_chart_add_series(chart, color, LV_CHART_AXIS_PRIMARY_Y);
lv_chart_set_next_value(chart, s, (int32_t)value);   // auto-increment x
lv_chart_refresh(chart);
```

### DO NOT USE
```c
// WRONG — this is for LV_CHART_TYPE_SCATTER only
lv_chart_set_series_value_by_id2(chart, s, id, x, y); // CRASHES on LINE charts
lv_chart_set_next_value2(chart, s, x, y);              // 4 args = scatter only
```

### Correct for Line Charts
```c
lv_chart_set_next_value(chart, series, value);  // 3 args, auto x
```

## Chart Styling (Dark Theme)
```c
lv_obj_set_style_bg_color(chart, lv_color_hex(0x0A0A0A), 0);
lv_obj_set_style_border_color(chart, COLOR_SEP, 0);
lv_obj_set_style_line_color(chart, lv_color_hex(0x222222), LV_PART_MAIN);
lv_obj_set_style_text_color(chart, COLOR_GRAY, 0);
```

## Common Pitfalls
1. `lv_chart_set_series_value_by_id2` requires `LV_CHART_TYPE_SCATTER` — generates 30+ warnings per call on LINE charts, leading to memory exhaustion
2. `lv_chart_set_next_value2` takes 4 args (obj, series, x, y) — for scatter only
3. After populating series data, call `lv_chart_refresh(chart)` to force redraw
