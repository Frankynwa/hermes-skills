# SDL2 Simulator on macOS (Apple M-series) — Pitfalls

## Problem: Black Screen / Freezing

On Apple M-series chips (AGX GPU driver), the default SDL2 hardware-accelerated renderer
causes LVGL to show a black screen or freeze at 100% CPU. This is a known Apple GPU
texture rendering incompatibility with LVGL's ARGB8888 pixel format.

## Solution: Software Renderer

```c
// Force SDL2 software rendering (bypasses AGX GPU driver)
SDL_Window *window = SDL_CreateWindow("LVGL", SDL_WINDOWPOS_CENTERED,
    SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_SHOWN);
SDL_Surface *surface = SDL_GetWindowSurface(window);

// In flush_cb:
SDL_LockSurface(surface);
memcpy(surface->pixels, px_map, width * height * 4);
SDL_UnlockSurface(surface);
SDL_UpdateWindowSurface(window);
```

## Solution: Partial Render Mode

Full-screen buffer (1.5MB for 1024x600@32bit) + RENDER_MODE_FULL triggers the bug.
Use partial rendering with a small buffer:

```c
#define BUF_LINES 40
static lv_color_t buf[1024 * BUF_LINES];

lv_display_t *disp = lv_display_create(1024, 600);
lv_display_set_flush_cb(disp, flush_cb);
lv_display_set_buffers(disp, buf, NULL, sizeof(buf), LV_DISPLAY_RENDER_MODE_PARTIAL);
```

## Solution: Color Depth Match

LVGL color depth must match SDL2 surface format:

```c
// lv_conf.h — use 32-bit for SDL2
#define LV_COLOR_DEPTH 32
```

If you set LV_COLOR_DEPTH=16, LVGL outputs RGB565 but SDL2 expects ARGB8888 → corrupted colors.

## SDL2 Initialization (LVGL v9.x API)

LVGL v9 built-in SDL2 driver API:

```c
// Correct functions (v9):
extern int sdl2_init(void);      // NOT sdl2_display_init
extern bool sdl2_loop(void);     // returns false when window closed
extern void sdl2_deinit(void);
```

## Build

```bash
# macOS requires SDL2_LIBRARY_DIRS for Homebrew
# (installed to /opt/homebrew/lib, not /usr/lib)
cmake .. -DUSE_SDL2=ON
make -j$(sysctl -n hw.ncpu)

# Run
./lvgl_simulator
```

## RK3568 Display Device Paths

```
/dev/dri/card0          — DRM master device
/dev/dri/card0-HDMI-A-1 — HDMI output
/dev/dri/card0-DSI-1    — MIPI-DSI output
/dev/fb0                — Framebuffer (fbdev mode)
/dev/input/eventX       — Touch input (find via: cat /proc/bus/input/devices)
```

## Cross-Compilation: macOS → RK3568

```bash
# Toolchain: ARM GNU 13.3 or Rockchip SDK toolchain
cmake .. \
  -DCMAKE_TOOLCHAIN_FILE=toolchain-rk3568.cmake \
  -DUSE_DRM=ON \
  -DUSE_LIBINPUT=ON
make -j$(sysctl -n hw.ncpu)

# Deploy
scp rk3568_lvgl_app root@<board-ip>:/opt/
ssh root@<board-ip> /opt/rk3568_lvgl_app
```
