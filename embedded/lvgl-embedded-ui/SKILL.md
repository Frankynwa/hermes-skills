---
name: lvgl-embedded-ui
description: Build embedded UIs with LVGL (v9.x) — display drivers, SDL2 simulator, widget patterns, rendering pipeline debugging. Use when creating instrument dashboards, multi-page navigation, chart displays, or any GUI for embedded targets.
triggers:
  - LVGL
  - embedded UI
  - instrument display
  - SDL2 simulator
  - lv_display
  - lv_chart
  - power quality analyzer UI
---

# LVGL Embedded UI Development

## Quick Reference (LVGL v9.5+)

### Display Initialization (PARTIAL mode — recommended)
```c
#define BUF_LINES 40
static uint8_t g_buf[HOR_RES * BUF_LINES * 4] __attribute__((aligned(64)));
static uint8_t g_fb[HOR_RES * VER_RES * 4] __attribute__((aligned(64)));

lv_display_t *disp = lv_display_create(HOR_RES, VER_RES);
lv_display_set_flush_cb(disp, flush_cb);
lv_display_set_buffers(disp, g_buf, NULL, sizeof(g_buf), LV_DISPLAY_RENDER_MODE_PARTIAL);
lv_display_set_color_format(disp, LV_COLOR_FORMAT_ARGB8888);
lv_tick_set_cb(SDL_GetTicks);
```

### Flush Callback Pattern (copy strip → full framebuffer → SDL)
```c
static void flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map) {
    int32_t w = area->x2 - area->x1 + 1;
    int32_t h = area->y2 - area->y1 + 1;
    uint8_t *dst = g_fb + (area->y1 * HOR_RES + area->x1) * 4;
    for (int32_t y = 0; y < h; y++) {
        memcpy(dst, px_map, w * 4);
        dst += HOR_RES * 4;
        px_map += w * 4;
    }
    if (lv_display_flush_is_last(disp)) {
        SDL_UpdateTexture(g_texture, NULL, g_fb, HOR_RES * 4);
        SDL_RenderClear(g_renderer);
        SDL_RenderCopy(g_renderer, g_texture, NULL, NULL);
        SDL_RenderPresent(g_renderer);
    }
    lv_display_flush_ready(disp);
}
```

### Multi-Page Navigation (Lazy Loading Pattern)
```c
// DON'T create all pages at startup — causes lv_timer_handler() hang with 8+ pages
// DO: create pages on demand when switching
static bool page_created[PAGE_COUNT] = {false};

static void create_page(int i) {
    if (page_created[i]) return;
    pages[i] = page_builders[i](page_container);
    page_created[i] = true;
}

void ui_pages_switch(page_id_t page) {
    if (pages[visible_page])
        lv_obj_add_flag(pages[visible_page], LV_OBJ_FLAG_HIDDEN);
    create_page(page);  // lazy create
    if (pages[page])
        lv_obj_clear_flag(pages[page], LV_OBJ_FLAG_HIDDEN);
    visible_page = page;
}
```

## Pitfalls (CRITICAL — read before debugging)

### P1: `lv_sdl_window_create()` crashes on first `lv_timer_handler()`
- **Symptom**: SEGV at address 0x0 in `lv_draw_sw_fill` (NULL draw buffer)
- **Cause**: LVGL v9.5 SDL driver doesn't properly initialize draw buffer on macOS
- **Fix**: Bypass `lv_sdl_window_create()`. Create SDL2 window + renderer + texture manually, then register LVGL display with PARTIAL mode + custom flush callback. See Quick Reference above.

### P2: Creating many pages inside a container hangs `lv_timer_handler()`
- **Symptom**: First `lv_timer_handler()` call blocks indefinitely (100% CPU, no crash)
- **Cause**: LVGL v9 rendering all hidden pages in a container simultaneously
- **Fix**: Use lazy loading — only create the visible page, create others on demand during `ui_pages_switch()`

### P3: SDL2 window invisible on macOS (Apple Silicon)
- **Symptom**: Process runs, rendering works (verified via BMP save), but screencapture shows all black
- **Cause**: macOS + SDL2 software renderer compatibility — window exists but not composited to screen
- **Verification**: Save framebuffer as BMP in flush callback: `SDL_SaveBMP(surface, "/tmp/frame.bmp")`
- **Status**: Does NOT affect embedded targets. Use BMP verification for development. On Linux or actual hardware, display works normally.

### P4: `lv_display_set_render_mode()` vs `lv_display_set_buffers()`
- PARTIAL mode with `lv_display_set_buffers()` is the reliable path
- DIRECT mode with `lv_display_set_draw_buffers()` + `lv_draw_buf_init()` can cause crashes
- If you need both, set `lv_display_set_buffers()` FIRST (PARTIAL), then override with `lv_display_set_draw_buffers()` — but this is fragile

### P5: `lv_snapshot_take()` returns `lv_draw_buf_t *` not `lv_image_dsc_t *`
- **Symptom**: Compiler warning "incompatible pointer type" when assigning to `lv_image_dsc_t *`
- **Reality**: NOT a crash bug. LVGL v9 intentionally made both structs binary-compatible — `lv_image_dsc_t` has `reserved`/`reserved_2` padding fields to match `lv_draw_buf_t`'s layout. Both structs have `data`, `data_size`, and `header` at the same offsets.
- **Result**: `snapshot->data` and `snapshot->data_size` access correct memory at runtime. Only a cosmetic warning.
- **Fix (cosmetic)**: Change variable type to `lv_draw_buf_t *`, or suppress with a cast. `lv_snapshot_free()` accepts `lv_image_dsc_t *` (deprecated signature), so free also works either way.
- **Verdict**: LOW priority — safe to leave as-is, fix when convenient.

## Debugging Techniques

### Signal handler for crash stack traces
```c
#include <signal.h>
#include <execinfo.h>
#include <unistd.h>
static void crash_handler(int sig) {
    void *frames[32];
    int n = backtrace(frames, 32);
    fprintf(stderr, "\n[CRASH] Signal %d:\n", sig);
    backtrace_symbols_fd(frames, n, 2);
    _exit(1);
}
// In main(): signal(SIGSEGV, crash_handler); signal(SIGABRT, crash_handler);
```

### Binary isolation for hang detection
1. Comment out all UI creation → just black screen → `lv_timer_handler()` works?
2. Add back statusbar only → works?
3. Add sidebar → works?
4. Add pages → HANGS → problem is in page creation
5. Test individual pages → all work individually → problem is container + hidden flags

### Framebuffer inspection via BMP
```c
// In flush callback, save first frame:
if (lv_display_flush_is_last(disp) && g_frame_count == 1) {
    SDL_Surface *surface = SDL_CreateRGBSurfaceFrom(
        g_fb, HOR_RES, VER_RES, 32, HOR_RES * 4,
        0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000);
    SDL_SaveBMP(surface, "/tmp/frame.bmp");
    SDL_FreeSurface(surface);
}
```

## macOS SDL2 Simulator Setup

### Dependencies
```bash
brew install sdl2
```

### CMakeLists.txt (minimal)
```cmake
cmake_minimum_required(VERSION 3.15)
project(lvgl_sim C)
set(CMAKE_C_STANDARD 11)
set(LVGL_DIR ${CMAKE_SOURCE_DIR}/../lvgl)
add_compile_definitions(LV_CONF_INCLUDE_SIMPLE LV_LVGL_H_INCLUDE_SIMPLE SDL_MAIN_HANDLED)
find_library(SDL2_LIB SDL2 HINTS /opt/homebrew/lib)
find_path(SDL2_INC SDL2/SDL.h HINTS /opt/homebrew/include)
file(GLOB_RECURSE LVGL_SOURCES ${LVGL_DIR}/src/*.c)
list(FILTER LVGL_SOURCES EXCLUDE REGEX ".*/drivers/(fbdev|drm|wayland|win32|x11|linux|dev/display|nuttx|gles|opengles).*")
add_executable(sim ${LVGL_SOURCES} src/main.c src/ui_*.c)
target_include_directories(sim PRIVATE . ${LVGL_DIR} ${LVGL_DIR}/src ${SDL2_INC})
target_link_libraries(sim PRIVATE ${SDL2_LIB})
target_compile_definitions(sim PRIVATE LV_USE_SDL=1)
```

### lv_conf.h key settings
```c
#define LV_COLOR_DEPTH 32
#define LV_USE_DRAW_SW 1
#define LV_USE_SDL 1
#define LV_SDL_RENDER_MODE LV_DISPLAY_RENDER_MODE_DIRECT
#define LV_SDL_ACCELERATED 0  // force software on macOS
#define LV_DRAW_BUF_STRIDE_ALIGN 1
#define LV_DRAW_BUF_ALIGN 4
```

## UI Design Patterns (UT285E reference)

Dark instrument theme:
- Background: `#000000`, Text: `#FFFFFF`
- Accent/selected: `#FF8C00` (orange)
- Warning: `#FF0000`, Phase colors: Yellow/Green/Red/Blue
- Layout: statusbar(28px) top + sidebar(152px) left + content area

Widget mapping for instrument UI:
| UI Element | LVGL Widget |
|---|---|
| Data table | `lv_table` |
| Line chart | `lv_chart` (LV_CHART_TYPE_LINE) |
| Bar chart | `lv_chart` (LV_CHART_TYPE_BAR) |
| Navigation tabs | `lv_btn` + event callback + page switch |
| Status indicators | `lv_label` + `lv_led` or styled labels |
| Dropdown select | `lv_dropdown` |
| Settings form | `lv_textarea` + `lv_checkbox` + `lv_btn` |

## HTML Prototype → LVGL C Conversion

When converting an HTML/CSS/JS mockup to LVGL C for a physical device:

1. **Map HTML structure to LVGL objects**
   - `display:flex` → `lv_obj_set_flex_flow()`
   - `<div>` → `lv_obj_create()`
   - `<button>` → `lv_btn_create()` + `lv_label_create()` child
   - `<table>` → `lv_obj_create()` rows + `lv_label_create()` cells

2. **Map colors exactly** — use `lv_color_hex(0xRRGGBB)` matching HTML hex values

3. **Map fonts** — generate bitmap fonts via `freetype` (see "Chinese Font Generation" below)

4. **CRITICAL: Panel merging rules**
   When merging UI panels (e.g., V Ratio + I Ratio → one panel):
   - Remove old panels from BOTH the `panels[]` array AND the `contents[]` array
   - Rename merged panels to reflect what they contain (e.g., "电压比·电流比")
   - Fix ALL panel index references (`cfg_ctx.panels[N]`) after removing items
   - NEVER leave placeholder/hint panels ("↑ 已合并到XXX") — delete them entirely
   - Adjust `CFG_PANEL_COUNT` and sidebar labels array to match

5. **Physical button navigation** — use LVGL groups (`lv_group_create`) + `lv_indev` keypad, NOT touch/mouse

## Chinese Font Generation (LVGL v9)

Use `freetype-py` to generate 1bpp bitmap fonts. See `scripts/gen_lvgl_font.py`.

### LVGL v9 font struct requirements
- `.glyph_bitmap` — single contiguous `uint8_t` array with all glyph bitmaps
- `.bitmap_index` — BYTE OFFSET into the bitmap array (NOT a pointer cast)
- LVGL v9 `lv_font_fmt_txt_dsc_t` does NOT have `.glyph_cnt` — remove it
- Align each glyph to 4-byte boundary before appending
- Cmap: use `FORMAT0_TINY` for continuous Unicode ranges

### macOS Chinese fonts
- Songti: `/System/Library/Fonts/Supplemental/Songti.ttc`
- Hiragino Sans GB: `/System/Library/Fonts/Hiragino Sans GB.ttc`

### Font size estimate
~90KB for ~270 glyphs at 18px 1bpp. Acceptable for 256MB+ embedded targets.

## References
- LVGL v9 docs: https://docs.lvgl.io/9.2/
- SDL2 simulator example: see `~/projects/lvgl-workspace/ut285e/` for complete 11-page working project
- **`references/lvgl-v9-api-cheatsheet.md`** — v8→v9 breaking API changes
- **`references/multi-platform-lv-conf.md`** — multi-platform lv_conf strategy
- **`references/macos-sdl2-issues.md`** — macOS SDL2 pitfalls
- **`scripts/gen_lvgl_font.py`** — Chinese bitmap font generator for LVGL v9
