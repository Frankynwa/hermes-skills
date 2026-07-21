---
name: embedded-lvgl-gui
description: "LVGL embedded GUI development — environment setup, cross-compilation, display/input driver integration, multi-platform CMake builds. Covers LVGL v9.x on ARM Linux boards (RK3568, STM32, ESP32) with DRM/KMS, framebuffer, SDL2 simulation, libinput/evdev touch."
triggers:
  - LVGL GUI development
  - embedded UI on ARM Linux
  - RK3568 / STM32 / ESP32 display
  - DRM/KMS LVGL
  - SDL2 LVGL simulator
  - cross-compile LVGL for aarch64
  - lv_conf.h configuration
  - embedded touchscreen UI
---

# LVGL Embedded GUI Development

## Overview

LVGL (Light and Versatile Graphics Library) v9.x is the standard open-source embedded GUI framework. This skill covers the full workflow from environment setup to deployed UI on ARM Linux boards.

## 1. Project Structure

```
project/
├── CMakeLists.txt              # Main build file
├── toolchain-<target>.cmake    # Cross-compilation toolchain
├── lv_conf.h                   # LVGL configuration (MUST be next to lvgl/ folder)
├── lvgl/                       # LVGL source (git submodule or clone)
├── src/
│   └── main.c                  # Application + UI code
├── drivers/
│   ├── drm_display.h/.c        # DRM/KMS display driver
│   ├── libinput_drv.h/.c       # libinput touch driver
│   ├── evdev_drv.h/.c          # evdev touch driver (simple)
│   └── sdl2_display.c          # SDL2 PC simulation driver
└── build/
```

## 2. lv_conf.h — CRITICAL Pitfalls

### Placement
LVGL CMake expects `lv_conf.h` **next to** the `lvgl/` directory (not inside it). The CMake system searches `CMAKE_SOURCE_DIR` for it.

### The `__ASSEMBLY__` guard is MANDATORY
LVGL v9 includes ARM Helium assembly files (`lv_blend_helium.S`) that `#include` system headers through lv_conf.h. Without the standard guard structure, macOS SDK `stdint.h` typedefs cause parse errors.

**Correct structure:**
```c
/* clang-format off */
#if 1

#ifndef LV_CONF_H
#define LV_CONF_H

/* If you need to include anything here, do it inside the __ASSEMBLY__ guard */
#if 0 && defined(__ASSEMBLY__)
#include "my_include.h"
#endif

// ... rest of config ...

#endif /* LV_CONF_H */
```

**WRONG (causes assembly compilation failures):**
```c
#ifndef LV_CONF_H
#define LV_CONF_H
#include <stdint.h>    // ← BREAKS ARM Helium .S files
// ...
#endif
```

### Multi-platform driver switches with `#ifndef` guards
To let CMake control driver enablement via `-D` flags, wrap each driver toggle:

```c
#ifndef LV_USE_LINUX_DRM
#define LV_USE_LINUX_DRM        0
#endif

#ifndef LV_USE_LINUX_FBDEV
#define LV_USE_LINUX_FBDEV      0
#endif

#ifndef LV_USE_LIBINPUT
#define LV_USE_LIBINPUT         0
#endif

#ifndef LV_USE_EVDEV
#define LV_USE_EVDEV            0
#endif

#ifndef LV_USE_SDL
#define LV_USE_SDL              0
#endif
```

Then in CMakeLists.txt:
```cmake
if(USE_SDL2)
    target_compile_definitions(app PRIVATE LV_USE_SDL=1)
endif()
if(USE_DRM)
    target_compile_definitions(app PRIVATE LV_USE_LINUX_DRM=1)
endif()
```

### Font sizes
Only enabled fonts are compiled. Enable what your UI uses:
```c
#define LV_FONT_MONTSERRAT_14       1
#define LV_FONT_MONTSERRAT_20       1   // default
#define LV_FONT_MONTSERRAT_24       1   // if used in UI
#define LV_FONT_MONTSERRAT_28       1   // if used in UI
```

## 3. CMakeLists.txt Pattern

```cmake
cmake_minimum_required(VERSION 3.16)
project(lvgl_app C CXX)
set(CMAKE_C_STANDARD 11)

set(LVGL_DIR ${CMAKE_SOURCE_DIR}/../lvgl)
add_subdirectory(${LVGL_DIR} lvgl_build)

find_package(PkgConfig REQUIRED)
pkg_check_modules(DRM libdrm)
pkg_check_modules(LIBINPUT libinput)
pkg_check_modules(UDEV libudev)
option(USE_SDL2 "SDL2 simulation" OFF)
if(USE_SDL2)
    pkg_check_modules(SDL2 sdl2)
endif()

# App sources — always compiled
file(GLOB APP_SOURCES "src/*.c")

# Driver sources — conditional
set(DRIVER_SOURCES "")
if(USE_SDL2)
    list(APPEND DRIVER_SOURCES drivers/sdl2_display.c)
endif()
if(USE_DRM OR (CMAKE_SYSTEM_NAME STREQUAL "Linux" AND NOT USE_SDL2))
    list(APPEND DRIVER_SOURCES drivers/drm_display.c)
endif()
if(USE_LIBINPUT)
    list(APPEND DRIVER_SOURCES drivers/libinput_drv.c)
endif()
if(USE_EVDEV)
    list(APPEND DRIVER_SOURCES drivers/evdev_drv.c)
endif()

add_executable(lvgl_app ${APP_SOURCES} ${DRIVER_SOURCES})

# Include paths — LVGL_DIR/.. needed for "lvgl/lvgl.h" includes
target_include_directories(lvgl_app PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${LVGL_DIR}/..
    ${LVGL_DIR}
    ${LVGL_DIR}/src
)

target_link_libraries(lvgl_app PRIVATE lvgl lvgl_thorvg m pthread)

# Platform-specific linking
if(USE_SDL2 AND SDL2_FOUND)
    target_link_directories(lvgl_app PRIVATE ${SDL2_LIBRARY_DIRS})
    target_link_libraries(lvgl_app PRIVATE ${SDL2_LIBRARIES})
    target_compile_definitions(lvgl_app PRIVATE USE_SDL2=1 LV_USE_SDL=1)
endif()
if(DRM_FOUND AND USE_DRM)
    target_link_libraries(lvgl_app PRIVATE ${DRM_LIBRARIES})
    target_compile_definitions(lvgl_app PRIVATE HAS_DRM=1 LV_USE_LINUX_DRM=1)
endif()
```

**Key pitfall:** `SDL2_LIBRARY_DIRS` must be linked on macOS (Homebrew installs to `/opt/homebrew/lib`). Without `target_link_directories`, the linker can't find `-lSDL2`.

## 4. DRM/KMS Display Driver (RK3568 Recommended)

Flow: `open(/dev/dri/card0)` → `drmModeGetResources` → find connector/encoder/CRTC → `create_dumb_buffer` → `mmap` → `drmModeSetCrtc` → LVGL `flush_cb` writes to mmap'd buffer.

```c
// flush callback
static void drm_flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map) {
    memcpy(g_drm.buffer, px_map, g_drm.width * g_drm.height * 4);
    lv_display_flush_ready(disp);
}
```

RK3568 device paths:
- `/dev/dri/card0` — DRM master
- `/dev/dri/card0-HDMI-A-1` — HDMI output
- `/dev/dri/card0-DSI-1` — MIPI-DSI output
- `/dev/input/eventX` — touchscreen (find via `cat /proc/bus/input/devices`)

## 5. SDL2 Simulator (PC Development)

Use the LVGL SDL2 driver. Key API: `sdl2_init()`, `sdl2_loop()`, `sdl2_deinit()`.

```c
#ifdef USE_SDL2
    extern int sdl2_init(void);
    extern bool sdl2_loop(void);
    extern void sdl2_deinit(void);
    sdl2_init();
    while (sdl2_loop()) {
        lv_timer_handler();
        usleep(5000);
    }
    sdl2_deinit();
#else
    while (running) {
        lv_timer_handler();
        usleep(5000);
    }
#endif
```

Build: `cmake .. -DUSE_SDL2=ON && make -j$(nproc)`

## 6. Cross-Compilation Toolchain (aarch64)

```cmake
# toolchain-rk3568.cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(TOOLCHAIN_PREFIX /path/to/aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-)
set(CMAKE_C_COMPILER ${TOOLCHAIN_PREFIX}gcc)
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PREFIX}g++)
set(CMAKE_C_FLAGS_INIT "-mcpu=cortex-a55 -mtune=cortex-a55 -O2")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

Build: `cmake .. -DCMAKE_TOOLCHAIN_FILE=toolchain-rk3568.cmake -DUSE_DRM=ON -DUSE_LIBINPUT=ON`

## 7. Board Setup (Debian/Ubuntu on ARM)

```bash
sudo apt install cmake gcc g++ pkg-config libdrm-dev libinput-dev libudev-dev
```

Check devices:
```bash
ls /dev/dri/card0          # DRM display
ls /dev/input/event*       # touch input
cat /proc/bus/input/devices # find touchscreen event number
modetest -M rockchip -c    # DRM connector info
```

## 8. Chinese Font Support

1. Use LVGL Font Converter (https://lvgl.io/tools/fontconverter)
2. Input: Chinese TTF (e.g., NotoSansSC-Regular.ttf)
3. Unicode range: `0x4E00-0x9FFF` (CJK) + `0x20-0x7F` (ASCII)
4. Output: C array file → add to project
5. In lv_conf.h: `#define LV_FONT_CUSTOM_DECLARE LV_FONT_DECLARE(lv_font_cn_16)`

## 9. Build Commands Quick Reference

| Mode | Command | Use case |
|------|---------|----------|
| PC sim | `cmake .. -DUSE_SDL2=ON` | UI development |
| Board local | `cmake .. -DUSE_DRM=ON -DUSE_LIBINPUT=ON` | Direct on ARM board |
| Cross | `cmake .. -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake -DUSE_DRM=ON` | macOS→RK3568 |

## 10. Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `xf86drmMode.h not found` | DRM dev headers missing | `apt install libdrm-dev` or disable DRM |
| `unexpected token` in stdint.h | Missing `__ASSEMBLY__` guard in lv_conf.h | Add `#if 1` / `#if 0 && defined(__ASSEMBLY__)` guard |
| `library 'SDL2' not found` | Missing link directory on macOS | Add `target_link_directories(... PRIVATE ${SDL2_LIBRARY_DIRS})` |
| `lv_font_montserrat_XX undeclared` | Font not enabled in lv_conf.h | Set `#define LV_FONT_MONTSERRAT_XX 1` |
| `lv_conf.h not found` | Wrong placement | Must be next to `lvgl/` folder, not inside it |
| Black screen on board | Wrong DRM device or no permission | Check `/dev/dri/card0`, run as root, verify connector |
| Touch coordinates wrong | evdev range mismatch | Read `EVIOCGABS` to get actual range, map to screen |
| `lvgl/lvgl.h not found` | Include path missing parent dir | Add `${LVGL_DIR}/..` to include directories |
| **Black screen on macOS M-series (Apple GPU)** | AGX GPU driver doesn't support ARGB8888 textures properly | Force software renderer: `SDL_SetHint(SDL_HINT_RENDER_DRIVER, "software");` then create `SDL_CreateSoftwareSurface(surface)` instead of `SDL_CreateTextureFromSurface`. See templates for details. |
| **100% CPU freeze on macOS M-series** | Full render mode + large buffer triggers AGX driver bug | Use partial render: `lv_display_set_buffers(disp, buf, NULL, width*40, LV_DISPLAY_RENDER_MODE_PARTIAL)` with ~40-line buffer |
| **Color mismatch (16-bit vs 32-bit)** | LVGL outputs RGB565 but SDL2 expects ARGB8888 | Set `LV_COLOR_DEPTH=32` in lv_conf.h when using SDL2 |
| `sdl2_display_init` undefined | Wrong function name for LVGL v9 | Correct API: `sdl2_init()`, `sdl2_loop()`, `sdl2_deinit()` |
| **RK3568 GPU driver missing** | Mali-G52 driver not loaded | `ls /dev/dri/card0` must exist; if not, install `mali-g610-firmware` or use fbdev fallback |

## Templates

- `templates/toolchain-rk3568.cmake` — Cross-compilation toolchain for RK3568 (Cortex-A55). Edit `TOOLCHAIN_PREFIX` before use.
- `templates/CMakeLists.txt` — Full multi-platform CMakeLists with conditional driver compilation. Drop into project root.
