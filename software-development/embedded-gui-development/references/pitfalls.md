# LVGL + SDL2 Pitfalls (macOS)

## 1. Apple GPU (AGX) Texture Assertion

**Error:** `AGX: Texture read/write assertion failed: bytes_per_row >= used_bytes_per_row`

**Cause:** Apple's Metal-backed GPU driver has strict alignment requirements for texture formats. The SDL2 hardware renderer on macOS doesn't handle ARGB8888 textures correctly in some configurations.

**Fix:** Use `SDL_RENDERER_SOFTWARE` instead of `SDL_RENDERER_ACCELERATED`:
```c
renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);
```

**Note:** This only affects the desktop simulator. Embedded targets use their own display drivers.

---

## 2. Color Depth Mismatch (16-bit vs 32-bit)

**Symptom:** Corrupted/garbled display output, wrong colors, visual artifacts.

**Cause:** LVGL defaults to `LV_COLOR_DEPTH 16` (RGB565, 2 bytes/pixel), but `SDL_PIXELFORMAT_ARGB8888` expects 32-bit (4 bytes/pixel). The flush callback passes a 2-byte-per-pixel buffer to a 4-byte-per-pixel texture → bytes_per_row mismatch.

**Fix:** Set `LV_COLOR_DEPTH 32` in `lv_conf.h` when using SDL2:
```c
#define LV_COLOR_DEPTH 32
```

---

## 3. Full-Size Buffer + RENDER_MODE_FULL Hangs

**Symptom:** Process consumes 100% CPU and hangs at `lv_display_set_buffers()` with a full-frame buffer (e.g., 800×480×4 = 1.5MB).

**Cause:** `LV_DISPLAY_RENDER_MODE_FULL` with a buffer equal to the entire framebuffer can cause LVGL's internal rendering loop to spin indefinitely on certain configurations.

**Fix:** Use partial rendering with a smaller buffer:
```c
#define BUF_LINES 40
static uint8_t buf[800 * BUF_LINES * 4];
lv_display_set_buffers(disp, buf, NULL, sizeof(buf), LV_DISPLAY_RENDER_MODE_PARTIAL);
```

---

## 4. lv_display_set_default() Before lv_indev_create()

**Symptom:** Input devices don't work, or LVGL crashes when creating indevs.

**Cause:** In LVGL v9, `lv_indev_create()` attaches to the default display. If no default is set, it may attach to NULL or an invalid display.

**Fix:** Always call `lv_display_set_default(disp)` before creating input devices:
```c
lv_display_set_default(disp);  // ← FIRST
lv_indev_t *indev = lv_indev_create();
lv_indev_set_type(indev, LV_INDEV_TYPE_POINTER);
lv_indev_set_read_cb(indev, mouse_read_cb);
```

---

## 5. lv_port_pc_visual_studio is Windows-Only

**Symptom:** Trying to build on macOS/Linux, get .vcxproj errors.

**Fix:** Don't clone it for macOS/Linux. Create your own CMake project with SDL2 (as shown in the main skill).

---

## 6. Background Process Output Not Captured

**Symptom:** `terminal(background=true)` shows empty output despite process running.

**Fix:** Use `stdbuf -oL` to force line-buffered output, or `setbuf(stdout, NULL)` in main().

---

## 7. macOS screencapture Can't Find SDL2 Window

**Symptom:** `osascript` returns "cannot get window 1" for the SDL2 process.

**Fix:** Use full-screen capture instead:
```bash
screencapture -x /tmp/lvgl_screen.png
# Or crop to window region
screencapture -x -R455,281,800,512 /tmp/lvgl_crop.png
```

---

## 8. Duplicate Library Linker Warning

**Warning:** `ld: warning: ignoring duplicate libraries: 'liblvgl.a'`

**Fix:** Harmless, can ignore. To suppress: `target_link_options(simulator PRIVATE -Wno-duplicate-lib)`

---

## 9. lv_sdl_window_create() Crashes at lv_draw_sw_fill (macOS, v9.5.0)

**Error:** Segfault at `lv_draw_sw_fill + N` during the first `lv_timer_handler()` call.

**Cause:** `lv_sdl_window_create()` sets up the display with `LV_DISPLAY_RENDER_MODE_DIRECT` (default) and uses LVGL's internal SDL backend (`lv_sdl_sw.c`). On macOS Apple Silicon, the software renderer's fill function crashes when writing to the draw buffer — likely a stride/alignment mismatch between LVGL's internal buffer layout and what `lv_draw_sw_fill` expects. ASan masks the crash by changing memory layout.

**Fix:** Bypass `lv_sdl_window_create()` entirely. Create SDL2 window/renderer/texture manually, then register a LVGL display in PARTIAL mode:

```c
#define SDL_MAIN_HANDLED
#include <SDL2/SDL.h>
#include "lvgl.h"

#define HOR_RES 800
#define VER_RES 480
#define BUF_LINES 40

static uint8_t g_fb[HOR_RES * VER_RES * 4] __attribute__((aligned(64)));
static uint8_t g_buf[HOR_RES * BUF_LINES * 4] __attribute__((aligned(64)));

static void flush_cb(lv_display_t * disp, const lv_area_t * area, uint8_t * px_map)
{
    int32_t w = area->x2 - area->x1 + 1;
    int32_t h = area->y2 - area->y1 + 1;
    uint8_t * dst = g_fb + (area->y1 * HOR_RES + area->x1) * 4;
    for (int32_t y = 0; y < h; y++) {
        memcpy(dst, px_map, w * 4);
        dst += HOR_RES * 4;
        px_map += w * 4;
    }
    if (lv_display_flush_is_last(disp)) {
        SDL_UpdateTexture(texture, NULL, g_fb, HOR_RES * 4);
        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, texture, NULL, NULL);
        SDL_RenderPresent(renderer);
    }
    lv_display_flush_ready(disp);
}

int main(void)
{
    SDL_SetMainReady();
    SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER);
    // Create window, renderer (SOFTWARE), texture (ARGB8888, STREAMING)
    lv_init();
    lv_display_t * disp = lv_display_create(HOR_RES, VER_RES);
    lv_display_set_flush_cb(disp, flush_cb);
    lv_display_set_buffers(disp, g_buf, NULL, sizeof(g_buf), LV_DISPLAY_RENDER_MODE_PARTIAL);
    lv_display_set_color_format(disp, LV_COLOR_FORMAT_ARGB8888);
    lv_tick_set_cb(SDL_GetTicks);
    // Create UI, then main loop with SDL_PollEvent + lv_timer_handler
}
```

**Why this works:** PARTIAL mode renders in 40-line strips. Each strip is small enough that `lv_draw_sw_fill` doesn't hit the stride/alignment issue.

---

## 10. lv_conf.h Not Found by LVGL Internals

**Error:** `fatal error: 'lv_conf.h' file not found` when compiling LVGL source files.

**Cause:** LVGL v9's internal includes use `#include "../../lv_conf.h"` (relative to source file). If `lv_conf.h` is in your project directory (not the LVGL root), the relative path fails.

**Fix:** Symlink from LVGL root to your `lv_conf.h`:
```bash
ln -sf /path/to/your/project/lv_conf.h /path/to/lvgl/lv_conf.h
```

---

## 11. SDL Input Handlers Not in Public Headers

**Error:** `call to undeclared function 'lv_sdl_mouse_handler'` when building.

**Cause:** `lv_sdl_mouse_handler`, `lv_sdl_mousewheel_handler`, `lv_sdl_keyboard_handler` are defined in `.c` files but NOT declared in public `.h` headers. They're internal to LVGL's SDL driver.

**Fix:** Add extern declarations if bypassing `lv_sdl_window_create()`:
```c
extern void lv_sdl_mouse_handler(SDL_Event * event);
extern void lv_sdl_mousewheel_handler(SDL_Event * event);
extern void lv_sdl_keyboard_handler(SDL_Event * event);
```

Then call them from your SDL event loop.

---

## 12. API Name: lv_display_set_draw_buffers (plural)

**Error:** `call to undeclared function 'lv_display_set_draw_buf'`

**Fix:** Use the plural form:
```c
lv_display_set_draw_buffers(disp, &draw_buf, NULL);  // plural!
```

---

## 15. lv_conf.h `#define` Overrides CMake `-D` Flags

**Symptom:** Defining `-DLV_USE_LINUX_DRM=0` on the CMake command line has no effect — the header `xf86drmMode.h` is still included, causing compilation errors on macOS.

**Cause:** `lv_conf.h` unconditionally does `#define LV_USE_LINUX_DRM 1`. When the C preprocessor processes `lv_conf.h` (included after the `-D` flag), the `#define` redefines the macro, undoing the command-line override. The `-D` flag sets it to 0, but `lv_conf.h` re-sets it to 1.

**Fix:** Split into platform-specific `lv_conf` files and use `LV_CONF_PATH`:
```cmake
# In CMakeLists, BEFORE processing LVGL sources:
add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_macos.h")
```

Create separate files:
- `lv_conf_macos.h` — `LV_USE_SDL=1`, all Linux drivers `=0`
- `lv_conf_rk3568.h` — `LV_USE_LINUX_DRM=1`, `LV_USE_EVDEV=1`

**Why `LV_CONF_PATH` works but `-D` doesn't:** `LV_CONF_PATH` is read by `lv_conf_internal.h` via `#include LV_CONF_PATH`, and the platform-specific file is the ONLY source of macro definitions. No override happens.

## 16. LVGL v9: `lv_indev_get_data()` Does Not Exist

**Error:** `call to undeclared function 'lv_indev_get_data'`

**Fix:** LVGL v9 removed `lv_indev_get_data()`. Use instead:
- `lv_indev_get_key(indev)` — for key codes in key event callbacks
- `lv_event_get_code(e)` — for event type (`LV_EVENT_PRESSED`, `LV_EVENT_KEY`, etc.)
## 13. LVGL SDL Backend Selection

LVGL v9 selects the SDL rendering backend at compile time:
- `LV_USE_SDL=1 && !LV_SDL_USE_EGL && !LV_USE_DRAW_SDL` → `lv_sdl_sw.c` (software renderer)
- `LV_USE_DRAW_SDL=1` → `lv_sdl_texture.c` (GPU-accelerated via SDL_Renderer)
- `LV_SDL_USE_EGL=1` → `lv_sdl_egl.c` (OpenGL ES)

For macOS simulator, the software backend (`lv_sdl_sw.c`) is the safest choice. Set:
```c
#define LV_USE_SDL              1
#define LV_USE_DRAW_SDL         0
#define LV_SDL_RENDER_MODE      LV_DISPLAY_RENDER_MODE_DIRECT
#define LV_SDL_ACCELERATED      0  // force software renderer
```

---

## 14. lv_conf.h `#define` Overrides CMake `-D` Flags

**Symptom:** Defining `-DLV_USE_LINUX_DRM=0` on the CMake command line has no effect — the header `xf86drmMode.h` is still included, causing compilation errors on macOS.

**Cause:** `lv_conf.h` unconditionally does `#define LV_USE_LINUX_DRM 1`. When the C preprocessor processes `lv_conf.h` (included after the `-D` flag), the `#define` redefines the macro, undoing the command-line override.

**Fix:** Split into platform-specific `lv_conf` files and use `LV_CONF_PATH`:
```cmake
# In CMakeLists, BEFORE processing LVGL sources:
add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_macos.h")
```

Create separate files:
- `lv_conf_macos.h` — `LV_USE_SDL=1`, all Linux drivers `=0`
- `lv_conf_rk3568.h` — `LV_USE_LINUX_DRM=1`, `LV_USE_EVDEV=1`

**Why `LV_CONF_PATH` works but `-D` doesn't:** `LV_CONF_PATH` is read by `lv_conf_internal.h` via `#include LV_CONF_PATH`, and the platform-specific file is the ONLY source of macro definitions. No override happens.

---

## 15. LVGL v9: `lv_indev_get_data()` Does Not Exist

**Error:** `call to undeclared function 'lv_indev_get_data'`

**Fix:** LVGL v9 removed `lv_indev_get_data()`. Use instead:
- `lv_indev_get_key(indev)` — for key codes in key event callbacks
- `lv_event_get_code(e)` — for event type (`LV_EVENT_PRESSED`, `LV_EVENT_KEY`)
- `lv_indev_get_vect(indev, &point)` — for pointer coordinates

---

### 16. LVGL v9: `lv_display_set_draw_buffers` (Plural)

**Error:** `call to undeclared function 'lv_display_set_draw_buf'`

**Fix:** Use the plural form:
```c
lv_display_set_draw_buffers(disp, &draw_buf, NULL);  // plural!
```

## 17. Simulator Segfault — Check Debug Code Before Blaming SDL2

**Symptom:** macOS simulator crashes with `Segmentation fault: 11` every startup, right after "[UI] Ready. Looping..." but before the main loop runs.

**Most common cause:** Debug/navigation code left in `main.c` that force-switches to a specific page with a latent bug. The crash is NOT in SDL2 — it's in the target page's create/init code.

**Diagnostic — per-page smoke test:** Run the simulator with CLI page args to isolate:
```bash
./simulator overview      # if this works but default crashes → debug code issue
./simulator trends        # test each page individually
./simulator simplemeas    # find which page crashes
```

**Real example (UT285E):** Two lines of debug code in `main.c`:
```c
extern void ui_pages_switch(page_id_t page);
ui_pages_switch(PAGE_SIMPLE_MEASURE);  // ← force-navigate, triggers crash
```
Removing these fixed the "SDL2 crash". The SDL2 driver, display init, and input devices were all working correctly.

**Rule:** Before concluding SDL2 is broken, test each page separately. SDL2 driver failures are rare; page-specific UI bugs are common.

---

## 18. LVGL v9.5.0: Linux Driver Headers Are Nested, Not Flat

**Symptom:** `fatal error: 'lv_linux_drm.h' file not found` on RK3568 cross-compile.

**Cause:** In LVGL v9.5.0, the driver headers live in subdirectories under `src/drivers/`:
```
src/drivers/display/drm/lv_linux_drm.h
src/drivers/display/fb/lv_linux_fbdev.h
src/drivers/evdev/lv_evdev.h
```

A flat `#include "lv_linux_drm.h"` won't find them.

**Fix:** Use the full nested path, and add the subdirectories to your CMake include dirs:

```c
// Correct for v9.5.0:
#include "drivers/display/drm/lv_linux_drm.h"
#include "drivers/display/fb/lv_linux_fbdev.h"
#include "drivers/evdev/lv_evdev.h"
```

```cmake
target_include_directories(your_target PRIVATE
    ${LVGL_DIR}/src/drivers/display/drm
    ${LVGL_DIR}/src/drivers/display/fb
    ${LVGL_DIR}/src/drivers/evdev)
```

**Note:** `lvgl.h` does NOT auto-include driver headers. You must `#include` them explicitly.
