---
name: lvgl-embedded-gui
description: >
  LVGL v9.x embedded GUI development — cross-platform build (macOS SDL2 simulator +
  Linux DRM/fbdev/evdev), lv_conf per-platform management, Apple Silicon byte-order
  fixes, tick timer setup, cross-compilation to ARM boards (RK3568/Buildroot).
  Use when building or porting LVGL-based UIs for embedded Linux, fixing SDL2
  rendering corruption on macOS, or setting up DRM/evdev display drivers.
---

# LVGL v9 Embedded GUI Development

## Quick Start

```bash
# macOS simulator
cmake -B build -DPLATFORM=macos && cmake --build build -j$(sysctl -n hw.ncpu)

# RK3568 cross-compile (on Ubuntu)
cmake -B build_rk -DPLATFORM=rk3568 \
  -DCMAKE_TOOLCHAIN_FILE=rk3568_toolchain.cmake \
  -DCMAKE_SYSROOT=/opt/rk3568-sysroot
cmake --build build_rk -j$(nproc)
```

## Pitfalls

### 1. Apple Silicon SDL2 byte-order corruption (ARGB8888)

**Symptom**: LVGL UI appears scrambled, garbled, with scanlines and repeated elements on Apple Silicon Macs.

**Root cause**: LVGL's `LV_COLOR_FORMAT_ARGB8888` byte layout does not match SDL2's `SDL_PIXELFORMAT_ARGB8888` on Apple Silicon (little-endian). Custom flush callbacks with `memcpy` into a manual SDL texture produce corrupted frames.

**Fix**: Do NOT write custom SDL2 flush callbacks. Use LVGL's built-in SDL driver:
```c
#include <SDL2/SDL.h>
#include "lvgl.h"

int main(void) {
    lv_init();
    lv_sdl_window_create(800, 480);       // display
    lv_sdl_mouse_create();                // mouse input
    lv_sdl_keyboard_create();             // keyboard input
    lv_sdl_mousewheel_create();           // scroll wheel
    lv_tick_set_cb(SDL_GetTicks);
    // ... create UI ...
    while (1) {
        lv_timer_handler();
        SDL_Delay(5);
    }
}
```

This is the ONLY reliable approach on macOS. Avoid `LV_DISPLAY_RENDER_MODE_PARTIAL` with custom flush — it produces rendering artifacts even with full double-buffering on Apple Silicon.

### 2. LVGL v9 Tick Timer — use `clock_gettime(CLOCK_MONOTONIC)`, NOT `clock()`

`clock()` measures CPU time consumed by the process, not wall-clock time. On embedded Linux, this causes LVGL to run at inconsistent speed.

```c
// lv_conf.h — CORRECT
#define LV_TICK_CUSTOM          1
#define LV_TICK_CUSTOM_INCLUDE  <time.h>
#define LV_TICK_CUSTOM_SYS_TIME_EXPR \
    (lv_tick_t)({ \
        struct timespec __ts; \
        clock_gettime(CLOCK_MONOTONIC, &__ts); \
        __ts.tv_sec * 1000LL + __ts.tv_nsec / 1000000LL; \
    })
```

### 3. Per-platform lv_conf files — use `LV_CONF_PATH`, not compile definitions

`-DLV_USE_LINUX_DRM=0` via compile flag is OVERRIDDEN by `#define LV_USE_LINUX_DRM 1` in `lv_conf.h`. Compile-time `-D` macros lose to header `#define` statements.

**Correct approach**: Separate config files per platform:
```
lv_conf_macos.h   → SDL=1, DRM=0, FBDEV=0, EVDEV=0
lv_conf_rk3568.h  → SDL=0, DRM=1, FBDEV=1, EVDEV=1
lv_conf_check.h   → all drivers=0 (syntax check only)
```

CMakeLists.txt:
```cmake
if(PLATFORM STREQUAL "macos")
    add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_macos.h")
elseif(PLATFORM STREQUAL "rk3568")
    add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_rk3568.h")
endif()
```

### 4. LVGL v9 evdev key handling — do NOT intercept navigation keys

LVGL's evdev driver automatically handles `LV_KEY_UP/DOWN/LEFT/RIGHT/ENTER/ESC` and routes them to the focused group. Writing a callback that overrides these keys DISABLES built-in navigation.

**Correct pattern**: Only intercept custom keys (MENU, SCREEN CAPTURE), let LVGL handle the rest:
```c
static void key_event_cb(lv_event_t * e) {
    uint32_t key = lv_indev_get_key(lv_event_get_indev(e));
    lv_event_code_t code = lv_event_get_code(e);
    switch (key) {
    case LV_KEY_HOME:   /* MENU — custom action */
        if (code == LV_EVENT_PRESSED) { /* handle menu */ }
        break;
    default:
        /* Direction keys/ENTER/ESC → LVGL handles automatically */;
        break;
    }
}
```

### 5. Empty event callbacks freeze the UI

Every `lv_obj_add_event_cb()` call MUST have a non-empty handler. An empty `{}` callback on dropdowns, buttons, or checkboxes causes the UI thread to hang when the widget is interacted with:

```c
// ❌ CAUSES FREEZE on click
static void dropdown_cb(lv_event_t *e) {}

// ✅ SAFE
static void lang_changed_cb(lv_event_t *e) {
    int idx = lv_dropdown_get_selected(lv_event_get_target(e));
    printf("Selected: %d\n", idx);
}
```

### 6. SDL2 rpath — embed library path in the binary

Users should not need `DYLD_LIBRARY_PATH` to launch the simulator:

```bash
# After linking, embed the homebrew SDL2 path
install_name_tool -add_rpath /opt/homebrew/lib ut285e_simulator
```

### 7. Sidebar navigation guard — prevent re-switching to current page

Clicking a sidebar item that's already active should be a no-op:

```c
if (idx == (int)current_page) return;  /* already on this page */
```

### 8. LVGL v9 DRM display — fallback chain

On embedded Linux, try DRM first, then fbdev:
```c
lv_display_t * disp = NULL;
#if LV_USE_LINUX_DRM
    disp = lv_linux_drm_create();
    if (disp) lv_linux_drm_set_file(disp, "/dev/dri/card0", -1);
#endif
#if LV_USE_LINUX_FBDEV
    if (!disp) {
        disp = lv_linux_fbdev_create();
        lv_linux_fbdev_set_file(disp, "/dev/fb0");
        lv_linux_fbdev_set_force_refresh(disp, true);
    }
#endif
```

### 6. Source file excludes in CMake for embedded builds

LVGL's driver directories are nested: `drivers/display/drm/`, `drivers/evdev/` etc. Regex filters must match the full path:
```cmake
# macOS: exclude ALL non-SDL drivers
list(FILTER LVGL_SOURCES EXCLUDE REGEX
    ".*/drivers/(display/(drm|fb)|evdev|libinput|fbdev|wayland|win32|x11|linux|nuttx|gles|opengles).*")

# RK3568: exclude desktop drivers, keep Linux drivers
list(FILTER LVGL_SOURCES EXCLUDE REGEX
    ".*/drivers/(sdl|x11|wayland|windows|uefi|qnx|nuttx/mock).*")
```

### 9. LVGL v9 Common API Mistakes (agents frequently get these wrong)

When delegating LVGL code to subagents, ALWAYS specify "LVGL v9 ONLY" and list these banned APIs:

| ❌ Deprecated/Removed (v8) | ✅ LVGL v9 Correct API |
|---|---|
| `lv_table_set_col_count()` | `lv_table_set_column_count()` |
| `lv_canvas_draw_line()` | Use `lv_line` widget + `lv_line_set_points()` or draw layer API |
| `lv_canvas_draw_arc()` | Use `lv_line` or draw layer; canvas drawing is low-level in v9 |
| `lv_indev_get_data()` | `lv_indev_get_key(indev)` for keypad; `lv_event_get_code(e)` for event type |
| `lv_scr_act()` | `lv_screen_active()` |
| `lv_obj_set_style_size(obj, 0, part)` | Needs 4 args: `lv_obj_set_style_width(obj, 0, part)` + `lv_obj_set_style_height(obj, 0, part)` |

**Font availability**: Only `lv_font_montserrat_14/16/20/24/28/32/36/40` are enabled by default. `lv_font_montserrat_10` and `lv_font_montserrat_12` do NOT exist unless explicitly added to lv_conf. Always use font size ≥ 14.

**Canvas drawing in v9**: `lv_canvas` is a low-level buffer. Drawing requires `lv_canvas_init_layer()` → `lv_draw_line()` with `lv_layer_t` → `lv_canvas_finish_layer()`. For simple vector diagrams (phasors, axes), prefer `lv_line` widgets directly — much simpler and v9-compatible.

**Static array initialization**: `static lv_point_t pts[2] = {{cx, cy}, {ex, ey}}` fails if `cx`, `cy`, `ex`, `ey` are runtime values. Use `lv_point_t pts[2]` (non-static) instead.

### 10. `lv_event_get_target` vs `lv_event_get_current_target` — label clicks break tab switching

When a user clicks a button with a label child, `LV_EVENT_CLICKED` bubbles up from the label. `lv_event_get_target(e)` returns the **original target** — the label, not the button. If your callback compares this pointer against stored button pointers (`ctx->tab_btns[i]`), the match fails silently and tab switching breaks.

```c
// ❌ BROKEN — target may be a label child, not the button
lv_obj_t *btn = lv_event_get_target(e);
for (int i = 0; i < 3; i++) {
    if (ctx->tab_btns[i] == btn) { idx = i; break; }  // label ≠ button
}

// ✅ CORRECT — current_target is always the object the event handler was registered on
lv_obj_t *btn = lv_event_get_current_target(e);
for (int i = 0; i < 3; i++) {
    if (ctx->tab_btns[i] == btn) { idx = i; break; }  // always matches
}
```

**Rule**: Use `lv_event_get_current_target(e)` whenever you need the widget you registered the callback on. Use `lv_event_get_target(e)` only when you specifically want the deepest child that was clicked (e.g., for `lv_dropdown_get_selected()` on a dropdown that IS the target).

### 11. Macro redefinition — don't duplicate shared constants in page files

When a project header (`ut285e.h`) already defines shared constants like `CONTENT_W`, `CONTENT_H`, `TABBAR_H`, and `COLOR_*`, individual page `.c` files should NOT redefine them locally. This creates silent maintenance hazards:
- Changing a value in the header won't affect the local copy
- The two copies drift apart over time
- Double-wrapping: if the header defines `COLOR_ACCENT` as `lv_color_hex(0xFF8C00)` and the page file calls `lv_color_hex(COLOR_ACCENT)`, you get `lv_color_hex(lv_color_hex(...))` — a type error

**Fix**: Delete the local `#define` block from page files. If the header is already `#include`d, the macros are available. Remove any `lv_color_hex(COLOR_*)` wrappers in code since the macro itself already expands to `lv_color_t`.

```c
// ❌ DON'T — duplicate in each page .c file
#define CONTENT_W  682
#define COLOR_ACCENT lv_color_hex(0xFF8C00)
// later: lv_color_hex(COLOR_ACCENT)  // double-wrapped!

// ✅ DO — rely on the project header
#include "ut285e.h"
// COLOR_ACCENT is already lv_color_hex(0xFF8C00), use directly
lv_obj_set_style_bg_color(obj, COLOR_ACCENT, 0);
```

### 13. SDL2 macOS mouse hang — IOHID cursorUpdate deadlock

**Symptom**: SDL2 simulator window appears but freezes/hangs when the user clicks with a physical mouse. Process is still alive but unresponsive. No crash, no segfault — just a silent hang.

**Root cause**: SDL2's mouse event thread on macOS calls into `IOHIDSystem cursorUpdate`, which can deadlock on Apple Silicon Macs. This is an SDL2 + macOS IOHID compatibility issue, not an LVGL bug.

**How to confirm it's IOHID (not your code)**:

1. Check macOS hang reports: `~/Library/Logs/DiagnosticReports/` — look for `.hang` files. These are binary plists; read with `plutil -p <file>`.
2. Use `lldb` to attach and get a live stack trace:
   ```bash
   lldb ./ut285e_simulator -o run
   # Wait for hang, then Ctrl+C
   (lldb) bt
   # Look for: semaphore_wait_trap → IOHIDSystem cursorUpdate
   ```

**Key insight**: Programmatic clicks via `lv_event_send(obj, LV_EVENT_CLICKED, NULL)` do NOT trigger this because they bypass SDL2's input layer entirely. Only physical mouse movements/clicks go through `IOHIDSystem`. This means automated tests will pass while manual clicking hangs.

**Fix**: Force SDL2 to use touch event mode instead of mouse events:
```c
#include <SDL2/SDL.h>

// BEFORE lv_sdl_mouse_create():
SDL_SetHint(SDL_HINT_MOUSE_TOUCH_EVENTS, "1");
SDL_SetHint(SDL_HINT_TOUCH_MOUSE_EVENTS, "0");

lv_sdl_mouse_create();
```

This tells SDL2 to emit touch events instead of mouse events, bypassing the IOHID cursor update path entirely. For a touchscreen-targeted embedded UI, this is functionally equivalent and avoids the macOS IOHID deadlock.

**Alternative**: Disable mouse entirely and rely on keyboard-only navigation during development (up/down/enter via `lv_sdl_keyboard_create()`). Less convenient but guaranteed not to hang.

### 12. evdev keycode → LVGL key mapping for physical buttons

Physical GPIO buttons → Linux evdev keycodes → LVGL navigation:
| Button | Keycode | LVGL Key |
|--------|---------|----------|
| UP | KEY_UP (103) | LV_KEY_UP |
| DOWN | KEY_DOWN (108) | LV_KEY_DOWN |
| LEFT | KEY_LEFT (105) | LV_KEY_LEFT |
| RIGHT | KEY_RIGHT (106) | LV_KEY_RIGHT |
| OK | KEY_ENTER (28) | LV_KEY_ENTER |
| MENU | KEY_MENU (139) | LV_KEY_HOME |
| BACK | KEY_BACK (158) | LV_KEY_ESC |
| SCREEN CAPTURE | KEY_CAMERA (212) | LV_KEY_END |

The evdev driver maps Linux keycodes to LVGL key codes automatically via its internal table. You only need to map custom keys (MENU→LV_KEY_HOME, SCREEN_CAPTURE→LV_KEY_END) in your callback.

## Buildroot Integration

Package files go in `buildroot/package/ut285e-ui/`:
- `Config.in` — menuconfig entry with `depends on BR2_PACKAGE_LVGL`
- `ut285e-ui.mk` — cmake-package with `-DPLATFORM=rk3568`

## Syntax Check on macOS (no cross-compiler)

```bash
clang -fsyntax-only -I. -I../lvgl -I../lvgl/src \
    -DLV_CONF_INCLUDE_SIMPLE -DLV_LVGL_H_INCLUDE_SIMPLE \
    -DLV_CONF_PATH='"path/to/lv_conf_check.h"' \
    -std=c11 src/main_rk3568.c
```

Note: `LV_CONF_PATH` MUST be passed as a properly-quoted string. Shell quoting:
```bash
-DLV_CONF_PATH='"'$(pwd)/lv_conf_check.h'"'
```
