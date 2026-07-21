---
name: lvgl-development
description: "LVGL embedded UI development — SDL2 simulator on macOS, rendering pipeline setup, CMake build, debugging crashes/hangs, common pitfalls. Use when building LVGL UIs, setting up simulators, or debugging rendering issues."
triggers:
  - "LVGL UI development or simulator"
  - "embedded graphics or display driver"
  - "SDL2 LVGL rendering issues"
  - "lv_timer_handler hangs or crashes"
---

# LVGL Development — SDL2 Simulator on macOS

## Overview

LVGL (Light and Versatile Graphics Library) is an open-source embedded graphics library. On macOS, use an SDL2-based simulator for development before deploying to hardware.

**Key version**: LVGL v9.5.0 (as of 2026-07). API changed significantly from v8.

## Quick Start — Minimal Working Setup

### 1. Project Structure
```
project/
├── lvgl/              # LVGL source (git submodule)
│   └── lv_conf.h      # ← symlink to your lv_conf.h
├── lv_conf.h          # actual config file
├── CMakeLists.txt
└── src/
    └── main.c
```

### 2. CMakeLists.txt Template
```cmake
cmake_minimum_required(VERSION 3.15)
project(my_lvgl_app C)
set(CMAKE_C_STANDARD 11)
set(LVGL_DIR ${CMAKE_SOURCE_DIR}/lvgl)

add_compile_definitions(LV_CONF_INCLUDE_SIMPLE LV_LVGL_H_INCLUDE_SIMPLE SDL_MAIN_HANDLED)

find_library(SDL2_LIB SDL2 HINTS /opt/homebrew/lib)
find_path(SDL2_INC SDL2/SDL.h HINTS /opt/homebrew/include)

file(GLOB_RECURSE LVGL_SOURCES ${LVGL_DIR}/src/*.c)
# Remove non-macOS drivers
list(FILTER LVGL_SOURCES EXCLUDE REGEX ".*/drivers/(fbdev|drm|wayland|win32|x11|linux|dev/display|nuttx|gles|opengles).*")

set(APP_SOURCES src/main.c)
add_executable(simulator ${LVGL_SOURCES} ${APP_SOURCES})
target_include_directories(simulator PRIVATE ${CMAKE_SOURCE_DIR} ${LVGL_DIR} ${LVGL_DIR}/src ${SDL2_INC})
target_link_libraries(simulator PRIVATE ${SDL2_LIB})
target_compile_definitions(simulator PRIVATE LV_USE_SDL=1)
```

### 3. lv_conf.h — Critical Settings
```c
#define LV_COLOR_DEPTH 32
#define LV_USE_DRAW_SW 1
#define LV_USE_SDL 1
#define LV_SDL_RENDER_MODE LV_DISPLAY_RENDER_MODE_PARTIAL
#define LV_SDL_ACCELERATED 0
#define LV_SDL_INCLUDE_PATH <SDL2/SDL.h>
```

### 4. Minimal main.c (Custom SDL2 Renderer)
```c
#define SDL_MAIN_HANDLED
#include <stdio.h>
#include <string.h>
#include <SDL2/SDL.h>
#include "lvgl.h"

#define HOR_RES 800
#define VER_RES 480
#define BUF_LINES 40

static SDL_Window *g_window = NULL;
static SDL_Renderer *g_renderer = NULL;
static SDL_Texture *g_texture = NULL;
static uint8_t g_fb[HOR_RES * VER_RES * 4] __attribute__((aligned(64)));
static uint8_t g_buf[HOR_RES * BUF_LINES * 4] __attribute__((aligned(64)));

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

int main(void) {
    SDL_SetMainReady();
    lv_init();

    SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER);
    g_window = SDL_CreateWindow("LVGL", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                HOR_RES, VER_RES, SDL_WINDOW_SHOWN);
    g_renderer = SDL_CreateRenderer(g_window, -1, SDL_RENDERER_SOFTWARE);
    g_texture = SDL_CreateTexture(g_renderer, SDL_PIXELFORMAT_ARGB8888,
                                  SDL_TEXTUREACCESS_STREAMING, HOR_RES, VER_RES);

    memset(g_fb, 0, sizeof(g_fb));
    memset(g_buf, 0, sizeof(g_buf));
    lv_display_t *disp = lv_display_create(HOR_RES, VER_RES);
    lv_display_set_flush_cb(disp, flush_cb);
    lv_display_set_buffers(disp, g_buf, NULL, sizeof(g_buf), LV_DISPLAY_RENDER_MODE_PARTIAL);
    lv_display_set_color_format(disp, LV_COLOR_FORMAT_ARGB8888);
    lv_tick_set_cb(SDL_GetTicks);

    // --- Create your UI here ---
    lv_obj_t *scr = lv_screen_active();
    lv_obj_set_style_bg_color(scr, lv_color_hex(0x000000), 0);
    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);

    while (1) {
        uint32_t ms = lv_timer_handler();
        if (ms == LV_NO_TIMER_READY) ms = 5;
        if (ms > 100) ms = 16;
        SDL_Delay(ms);
        SDL_Event e;
        while (SDL_PollEvent(&e)) { if (e.type == SDL_QUIT) goto done; }
    }
done:
    SDL_Quit();
    return 0;
}
```

## Pitfalls (Battle-Tested)

### P1: `lv_sdl_window_create()` Crashes on macOS (NULL Draw Buffer)
**Symptom**: SEGV at `lv_draw_sw_fill`, address 0x000000000000
**Root cause**: LVGL's built-in SDL2 driver (`lv_sdl_sw.c`) fails to initialize the draw buffer on macOS Apple Silicon.
**Fix**: Bypass `lv_sdl_window_create()` entirely. Create SDL2 window/renderer/texture manually, then register a custom LVGL display with `lv_display_set_buffers()` in PARTIAL mode and a custom `flush_cb` that copies strips to a full framebuffer.

### P2: `lv_timer_handler()` Hangs (Infinite Loop)
**Symptom**: First call to `lv_timer_handler()` blocks forever. Program prints "UI created" then freezes.
**Root cause**: Creating too many LVGL widgets at once (e.g., 8+ pages with charts/tables in a single `lv_obj_create` call) overwhelms the rendering pipeline.
**Fix**: Lazy loading — only create the currently visible page. Create additional pages on-demand when switching.

### P3: SDL2 Window Invisible on macOS
**Symptom**: Process runs (100% CPU), framebuffer has correct content (verified via BMP save), but `screencapture` captures a black screen.
**Root cause**: SDL2 software renderer (`SDL_RENDERER_SOFTWARE`) doesn't properly display on macOS with Apple Silicon. The window exists but pixels aren't composited to the screen.
**Impact**: Does NOT affect embedded targets. For simulator verification, save framebuffer as BMP:
```c
SDL_Surface *s = SDL_CreateRGBSurfaceFrom(g_fb, W, H, 32, W*4, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000);
SDL_SaveBMP(s, "/tmp/frame.bmp");
SDL_FreeSurface(s);
```

### P4: LVGL v9 API Changes from v8
- `lv_display_set_draw_buf()` → `lv_display_set_draw_buffers()` (plural, takes buf1+buf2)
- `lv_draw_buf_init()` signature: `(draw_buf, w, h, cf, stride, data, data_size)`
- `lv_scr_act()` → `lv_screen_active()`
- `LV_DISP_RENDER_MODE_*` → `LV_DISPLAY_RENDER_MODE_*`
- `lv_obj_set_style_local_*()` → `lv_obj_set_style_*()` (no "local")

### P5: lv_conf.h Not Found
**Symptom**: `fatal error: 'lv_conf.h' file not found`
**Fix**: Create symlink: `ln -sf /path/to/your/lv_conf.h /path/to/lvgl/lv_conf.h`

### P6: SDL_MAIN_HANDLED Redefinition Warning
**Fix**: Define it only once — either in CMakeLists.txt via `add_compile_definitions()` OR in main.c, not both.

### P7: SDL2 Mouse Input Hangs on macOS (IOHID cursorUpdate)
**Symptom**: Simulator starts fine, renders correctly, but clicking buttons with a physical mouse causes the app to freeze (beachball / unresponsive). Terminal shows no error output — it's a hang, not a crash.
**Root cause**: SDL2's mouse event thread calls Apple's `IOHIDSystem cursorUpdate`, which blocks indefinitely on some macOS versions (especially Apple Silicon). This is a known SDL2 + macOS IOHID driver incompatibility — not a bug in your LVGL code.
**How to confirm — two complementary techniques**:

Technique 1: Attach lldb to running process (determine exact blocked thread):
```bash
# Start simulator normally, let it freeze, then in another terminal:
ps aux | grep simulator   # find PID
lldb -p <PID>             # attach to running process
(lldb) bt all             # show ALL thread backtraces
# Look for the thread blocked on IOHIDSystem cursorUpdate
```
This gives you the EXACT stack trace of the frozen thread — no guessing.

Technique 2: Virtual event isolation (prove it's SDL2 input, not LVGL):
```c
// Send LVGL events programmatically — bypasses SDL2 entirely
extern lv_obj_t *some_button;
lv_event_send(some_button, LV_EVENT_CLICKED, NULL);
```
If virtual clicks work but physical mouse clicks freeze, the bug is 100% in SDL2's input layer, not your UI code. This is the definitive isolation test.

Technique 3: Check macOS hang reports:
```bash
ls -lt /Library/Logs/DiagnosticReports/*.hang | head -3
plutil -p /Library/Logs/DiagnosticReports/<name>.hang | grep -B2 -A8 "IOHIDSystem"
```

**Fix**: Disable SDL2 mouse and scrollwheel input devices entirely. Keep keyboard input for navigation:
```c
/* lv_sdl_mouse_create();      -- disabled: macOS IOHID hang */
lv_sdl_keyboard_create();
/* lv_sdl_mousewheel_create(); -- disabled */
```
With keyboard-only input, use Tab to cycle focus and Enter to activate.

**Alternative approaches that DID NOT work**:
- `SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_MODE_WARP, "0")` — no effect
- `SDL_SetHint(SDL_HINT_MOUSE_TOUCH_EVENTS, "1")` — no effect
- `SDL_SetHint(SDL_HINT_MOUSE_FOCUS_CLICKTHROUGH, "1")` — no effect
- The root cause is in Apple's IOHID framework; SDL2 hints cannot bypass it.

## Debugging Techniques

### macOS Hang Reports (`.hang` files)
When the simulator freezes without crashing (beachball), macOS generates `.hang` files in `/Library/Logs/DiagnosticReports/`. These capture the full stack trace of every thread at the moment of the hang:
```bash
# Find the latest hang report for your binary
ls -lt /Library/Logs/DiagnosticReports/ut285e_simulator*.hang | head -1
# Read key sections
plutil -p <file> | grep -E "(thread|IOHID|semaphore|HANG)"
```
The hang report tells you exactly which thread is blocked and on what call — far more useful than guessing.

### Signal Handler for Crash Stack Traces
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

### Incremental UI Isolation
When `lv_timer_handler()` hangs, comment out all UI creation and add back one module at a time:
1. Just `lv_screen_active()` + background color → should work
2. Add `lv_label_create()` → verify rendering
3. Add complex widgets one by one → find the culprit

### Framebuffer Verification
Save raw framebuffer to BMP for visual verification when SDL2 window is invisible:
```c
// In flush_cb, after full frame is ready:
SDL_Surface *s = SDL_CreateRGBSurfaceFrom(fb, W, H, 32, W*4, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000);
SDL_SaveBMP(s, "/tmp/frame.bmp");
SDL_FreeSurface(s);
```

## Templates

- `templates/CMakeLists.txt` — CMake build config for LVGL + SDL2 on macOS
- `templates/main_sdl2_template.c` — Minimal working main.c with custom SDL2 renderer

## Build & Run Commands
```bash
# Setup
cd project && mkdir build && cd build
cmake ..  # SDL2 auto-detected via homebrew
make -j$(sysctl -n hw.ncpu)

# Run
DYLD_LIBRARY_PATH=/opt/homebrew/lib ./simulator

# Debug with ASan (slow but catches memory errors)
cmake .. -DCMAKE_C_FLAGS="-fsanitize=address -g"
```
