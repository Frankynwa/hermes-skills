# LVGL v9 API Migration Pitfalls

Collected from the UT285E RK3568 port. LVGL v9 changed several APIs from v8.x.

## 1. lv_point_t → lv_point_precise_t

**Symptom:** `-Wincompatible-pointer-types` when passing `lv_point_t[]` to `lv_line_set_points()`

**Fix:** Use `lv_point_precise_t` for all line point arrays.

```c
// v8 (broken in v9):
lv_point_t pts[] = {{0,0}, {100,100}};

// v9 (correct):
lv_point_precise_t pts[] = {{0,0}, {100,100}};
```

## 2. lv_obj_align() position order

In v9, `lv_obj_align(obj, LV_ALIGN_TOP_LEFT, x_offset, y_offset)` — the offset order is x then y, which is intuitive. But ensure you're not accidentally swapping them (easy to do with auto-generated code).

## 3. lv_chart_set_range() dual-axis

```c
lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_Y, 200, 250);   // Y range
lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_X, 0, 30);       // X range
lv_chart_set_range(chart, LV_CHART_AXIS_SECONDARY_Y, -20, 20);   // Secondary Y
```

## 4. lv_table_set_cell_value() — no return value check

`lv_table_set_cell_value()` returns void in v9 (was `void` in v8 too). The cell must already exist — use `lv_table_set_row_count()` and `lv_table_set_column_count()` first.

## 5. lv_conf_internal.h pragma-message warning

```
warning: Possible failure to include lv_conf.h [-W#pragma-messages]
```

**Harmless.** This is LVGL's internal sanity check. It fires on all platforms when `LV_CONF_INCLUDE_SIMPLE` is used. Can be safely ignored. Do NOT try to suppress it — it confirms the config IS being picked up.

## 6. lv_obj_set_style_bg_opa()

In v9, opacity is set via `lv_obj_set_style_bg_opa(obj, LV_OPA_20, 0)` — the third argument is the style selector (0 = main part). This is unchanged from v8 but worth noting because forgetting it causes no-op.

## 7. Fonts: Latin + Custom Chinese

```c
// lv_conf.h
#define LV_FONT_MONTSERRAT_14   1
#define LV_FONT_CUSTOM_DECLARE \
    LV_FONT_DECLARE(lv_font_cn_18)

// In code:
lv_obj_set_style_text_font(obj, &lv_font_cn_18, 0);       // Chinese text
lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, 0); // Latin text
```

Chinese fonts are generated offline via LVGL Font Converter and compiled as `.c` files. The `.c` file must be listed in CMakeLists.txt as a source.
