# macOS SDL2 Rendering Corruption Fix — Full Recipe

## Symptom
LVGL SDL2 simulator on Apple Silicon (ARM64) macOS shows severely corrupted UI:
- Garbled text with horizontal scanlines
- Repeated/mirrored elements ("Filter A", "Selected Apple")
- Color channels swapped or scrambled
- Looks like GPU memory corruption but is actually byte-order mismatch

## Root Cause
LVGL's `LV_COLOR_FORMAT_ARGB8888` stores pixels as [A,R,G,B] in 32-bit words.
On Apple Silicon (little-endian), the memory layout is [B,G,R,A] for the SDL2 format `SDL_PIXELFORMAT_ARGB8888`.

When using a custom `flush_cb` that does:
```c
memcpy(g_fb, px_map, w * h * 4);
SDL_UpdateTexture(g_texture, NULL, g_fb, HOR_RES * 4);
```
The bytes arrive in LVGL's [A,R,G,B] order but SDL interprets them as [B,G,R,A],
swapping R↔B and A↔B channels. This produces the scrambled appearance.

## Fix
Replace ALL custom SDL rendering with LVGL's built-in SDL driver:

```c
// main.c
#define SDL_MAIN_HANDLED
#include <SDL2/SDL.h>
#include "lvgl.h"

int main(void) {
    SDL_SetMainReady();
    setbuf(stdout, NULL);

    lv_init();
    lv_sdl_window_create(800, 480);       // Handles display + texture + format
    lv_sdl_mouse_create();                // REQUIRED for click input
    lv_sdl_keyboard_create();             // REQUIRED for keyboard input
    lv_sdl_mousewheel_create();           // REQUIRED for scroll
    lv_tick_set_cb(SDL_GetTicks);

    // UI creation...
    while (1) {
        lv_timer_handler();
        SDL_Delay(5);
    }
}
```

## What NOT to do
- Do NOT use `LV_DISPLAY_RENDER_MODE_PARTIAL` with custom flush
- Do NOT use `LV_DISPLAY_RENDER_MODE_DIRECT` with custom flush
- Do NOT write your own `flush_cb` with `SDL_UpdateTexture`
- Do NOT call `SDL_PollEvent()` in the main loop (LVGL's input drivers handle it)
- Do NOT set `LV_USE_SDL=1` in lv_conf and then write custom SDL code — use ONLY the built-in driver

## CMakeLists requirements
The macOS build must compile LVGL's SDL driver sources (at `drivers/sdl/`) and NOT exclude them:
```cmake
# macOS: exclude ALL non-SDL drivers, but KEEP SDL
list(FILTER LVGL_SOURCES EXCLUDE REGEX
    ".*/drivers/(display/(drm|fb)|evdev|libinput|fbdev|wayland|win32|x11|linux|nuttx|gles|opengles).*")
```
Note: `drivers/sdl/` is NOT in the exclusion list.

## Verification
The UI should render with:
- Pure black background
- Clean white text on dark elements
- Orange accent colors on selected sidebar items
- No artifacts, scanlines, or garbled text
