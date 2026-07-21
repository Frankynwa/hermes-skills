# UT285E Project Reference

## Architecture

```
src/
├── main.c                  # SDL2 simulator entry
├── main_rk3568.c           # RK3568 embedded entry
├── ut285e.h                # Shared types, colors, page_id_t enum
├── ui_sidebar.c            # Left nav sidebar (10→11 pages)
├── ui_pages.c              # Page container, lazy creation, switching
├── ui_statusbar.c          # Top status bar
├── ui_data_emmc.c          # eMMC data access
│
├── ui_page_overview.c      # 424 lines — Realtime/Record/Trend/Table/Verify
├── ui_page_va_hz.c         # 164 lines — V/A/Hz with waveform chart
├── ui_page_power.c         # 67 lines  — Power table + trend chart
├── ui_page_dip_swell.c     # 341 lines — Dip/Swell event analysis
├── ui_page_harmonics.c     # 361 lines — Harmonic analysis
├── ui_page_transient.c     # 334 lines — Transient event display
├── ui_page_events.c        # 200 lines — Event log with filtering
├── ui_page_settings.c      # 765 lines — 5-tab settings (仪器/通信/工具/信息/内存)
├── ui_page_simple_measure.c # 653 lines — Verification (仪表/相量/波形) + placeholder settings
├── ui_page_config.c        # 1212 lines — 12-panel instrument config (接线/电压/K因数/闪变/Wye limits...)
└── ui_page_trends.c        # ~310 lines — Flicker/Unbalance/Current trend charts
```

## Page creation diff pattern

When adding `PAGE_TRENDS` to a project with 10 existing pages, these are the exact modifications:

### 1. ut285e.h — enum + declaration
```diff
     PAGE_CONFIG,
+    PAGE_TRENDS,
     PAGE_COUNT
...
 lv_obj_t *page_config_create(lv_obj_t *parent);
+lv_obj_t *page_trends_create(lv_obj_t *parent);
```

### 2. ui_pages.c — extern + builder + name
```diff
 extern lv_obj_t *page_config_create(lv_obj_t *parent);
+extern lv_obj_t *page_trends_create(lv_obj_t *parent);
...
     page_config_create,
+    page_trends_create,
 };
...
-    "SimpleMeas", "Config"
+    "SimpleMeas", "Config", "Trends"
 };
```

### 3. ui_sidebar.c — bump MAX + add label
```diff
-#define MAX_MENU_ITEMS  10
+#define MAX_MENU_ITEMS  11
...
-    "Config"
+    "Config",
+    "Trends"
 };
```

### 4. CMakeLists.txt — add source
```diff
     ${CMAKE_SOURCE_DIR}/src/ui_page_config.c
+    src/ui_page_trends.c
 )
```

## LVGL Chart API (v9.5)

| Function | Args | Chart type | Notes |
|---|---|---|---|
| `lv_chart_set_next_value(obj, ser, val)` | 3 | LINE | Auto-increments x |
| `lv_chart_set_next_value2(obj, ser, x, y)` | 4 | SCATTER | Explicit x |
| `lv_chart_set_series_value_by_id2(obj, ser, id, x, y)` | 5 | SCATTER | Set by ID |

## Font availability (lv_conf_macos.h)

Enabled: 14, 16, 20, 24, 28, 32, 36, 40
NOT enabled: 10, 12 — causes `use of undeclared identifier` error

## Color definitions (ut285e.h)

```c
COLOR_BG       lv_color_hex(0x000000)
COLOR_BG2      lv_color_hex(0x1A1A1A)
COLOR_TEXT     lv_color_hex(0xE0E0E0)
COLOR_DIM      lv_color_hex(0x888888)
COLOR_GRAY     lv_color_hex(0xAAAAAA)
COLOR_ACCENT   lv_color_hex(0xFF8C00)
COLOR_RED      lv_color_hex(0xFF3333)
COLOR_L1       lv_color_hex(0xFFD700)  // yellow
COLOR_L2       lv_color_hex(0x00CC00)  // green
COLOR_L3       lv_color_hex(0xFF3333)  // red
COLOR_N        lv_color_hex(0x4488FF)  // blue
COLOR_SEP      lv_color_hex(0x333333)
COLOR_BTN_BG   lv_color_hex(0x2A2A2A)
COLOR_BTN_SEL  lv_color_hex(0x3A3A00)
```

## Gap analysis corrections (2026-07-16)

Original PDF-based gap analysis (14% completion) was corrected after cross-referencing with actual code to ~60% completion. Key correction: `config.c` implements 12 panels previously labeled as "完全缺失" in simple_measure's event trigger settings:

| Config panel | Error in original analysis |
|---|---|
| `create_panel_flicker` (488) | Mislabeled as "missing" in simple_measure |
| `create_panel_kfactor` (552) | Mislabeled as "missing" |
| `create_panel_dip` (647) | Mislabeled as "missing" |
| `create_panel_rise` (744) | Mislabeled as "missing" |
| `create_panel_interruption` (833) | Mislabeled as "missing" |
| `create_panel_waveform` (916) | Mislabeled as "missing" |
| `create_panel_transient` (1019) | Mislabeled as "missing" |
