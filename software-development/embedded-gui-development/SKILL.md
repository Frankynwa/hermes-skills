---
name: embedded-gui-development
description: "Set up and develop embedded GUI applications using LVGL (Light and Versatile Graphics Library) with desktop simulators and cross-compilation targets. Covers LVGL v9 API, SDL2/macOS simulator, CMake integration, and common pitfalls."
triggers:
  - "lvgl"
  - "embedded gui"
  - "embedded ui"
  - "gui simulator"
  - "lv_conf"
  - "sdl2 simulator"
  - "lv_display"
  - "lvgl widget"
---

# Embedded GUI Development (LVGL)

## When to Use

User wants to build GUI applications for embedded systems (MCU/displays) using LVGL, or needs a desktop simulator for prototyping before flashing to hardware.

## Overview

LVGL (v9.x) is the dominant open-source embedded GUI library. Development workflow:
1. Set up PC simulator (SDL2) for rapid iteration
2. Design UI with widgets and events
3. Cross-compile for target MCU when ready

## Prerequisites

- SDL2 (`brew install sdl2` on macOS)
- CMake >= 3.12
- C compiler (Apple Clang / GCC / arm-none-eabi-gcc)

## Step-by-Step Setup

### 1. Clone LVGL

```bash
mkdir -p ~/projects/lvgl-workspace && cd ~/projects/lvgl-workspace
git clone --depth 1 --branch v9.5.0 https://github.com/lvgl/lvgl.git
```

### 2. Create lv_conf.h

```bash
# Enable lv_conf.h from template — change #if 0 to #if 1
sed 's/^#if 0 \/\* Set this to "1" to enable content \*\//#if 1/' \
    lvgl/lv_conf_template.h > simulator/lv_conf.h
```

Critical settings for desktop simulator:
```c
#define LV_COLOR_DEPTH 32          // MUST match SDL pixel format
#define LV_FONT_MONTSERRAT_14 1    // Default font
#define LV_FONT_MONTSERRAT_20 1    // Enable if using larger text

// SDL-specific (macOS-safe)
#define LV_USE_SDL              1
#define LV_USE_DRAW_SDL         0
#define LV_SDL_RENDER_MODE      LV_DISPLAY_RENDER_MODE_DIRECT
#define LV_SDL_ACCELERATED      0    // force software renderer on macOS
#define LV_SDL_INCLUDE_PATH     <SDL2/SDL.h>
```

### 3. Create CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.12)
project(lvgl_sim LANGUAGES C CXX)

set(LV_BUILD_CONF_PATH "${CMAKE_CURRENT_SOURCE_DIR}/lv_conf.h")
set(CONFIG_LV_BUILD_DEMOS ON CACHE BOOL "" FORCE)
set(CONFIG_LV_BUILD_EXAMPLES ON CACHE BOOL "" FORCE)

find_package(PkgConfig REQUIRED)
pkg_check_modules(SDL2 REQUIRED sdl2)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../lvgl lvgl_build)

add_executable(simulator src/main.c src/sdl2_display.c)
target_include_directories(simulator PRIVATE
    ${SDL2_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}/..   # so #include "lvgl/lvgl.h" works
    ${CMAKE_CURRENT_SOURCE_DIR}/../lvgl/src
)
target_link_libraries(simulator PRIVATE lvgl lvgl::lvgl ${SDL2_LIBRARIES})
```

### 4. SDL2 Display — Use LVGL's Built-in Driver (RELIABLE)

On macOS (especially Apple Silicon), LVGL's built-in SDL driver is the **only** reliable approach.
Custom flush callbacks with SDL2 textures produce byte-order corruption in ARGB8888 mode.

```c
// ✅ CORRECT: LVGL's built-in SDL driver handles byte order correctly
lv_sdl_window_create(800, 480);         // display
lv_sdl_mouse_create();                  // mouse input (⚠️ may hang on macOS — see lvgl-development P7)
lv_sdl_keyboard_create();               // keyboard input
lv_sdl_mousewheel_create();             // scroll wheel (⚠️ same IOHID risk)
lv_tick_set_cb(SDL_GetTicks);           // tick timer

// ❌ AVOID: Custom flush callbacks with SDL_PIXELFORMAT_ARGB8888
// LVGL's internal ARGB8888 layout ≠ SDL's on Apple Silicon
// lv_display_set_flush_cb(disp, my_flush_cb);
// SDL_CreateTexture(..., SDL_PIXELFORMAT_ARGB8888, ...);
```

Also embed the SDL2 rpath so users don't need `DYLD_LIBRARY_PATH`:
```bash
install_name_tool -add_rpath /opt/homebrew/lib build/simulator
```

### 5. Main Entry (main.c)

```c
#include "lvgl/lvgl.h"
extern int sdl2_init(void);
extern bool sdl2_loop(void);  // returns false on quit

static void create_ui(void) {
    // Create widgets on lv_screen_active()
}

int main(void) {
    sdl2_init();
    create_ui();
    while (sdl2_loop()) { /* loop until window closed */ }
    return 0;
}
```

### 6. Build and Run

```bash
# CRITICAL: symlink lv_conf.h to LVGL root (see pitfall #10)
ln -sf $(pwd)/lv_conf.h ../lvgl/lv_conf.h

cd simulator/build && cmake .. && make -j$(sysctl -n hw.ncpu)
./simulator
```

## LVGL v9 Widget API Quick Reference

```c
// Create
lv_obj_t *btn = lv_button_create(parent);
lv_obj_t *label = lv_label_create(btn);
lv_label_set_text(label, "Hello");

// Layout & style
lv_obj_set_size(btn, 120, 50);
lv_obj_align(btn, LV_ALIGN_CENTER, 0, 0);
lv_obj_set_style_text_font(label, &lv_font_montserrat_20, 0);

// Events
lv_obj_add_event_cb(btn, my_cb, LV_EVENT_CLICKED, user_data);

// Slider
lv_obj_t *slider = lv_slider_create(parent);
lv_slider_set_range(slider, 0, 100);
lv_slider_set_value(slider, 50, LV_ANIM_OFF);

// Switch
lv_obj_t *sw = lv_switch_create(parent);
lv_obj_has_state(sw, LV_STATE_CHECKED);

// Dropdown
lv_dropdown_set_options(dd, "A\nB\nC");
lv_dropdown_get_selected_str(dd, buf, sizeof(buf));

// Bar
lv_bar_set_value(bar, 70, LV_ANIM_ON);

// Theme
lv_theme_default_init(disp, palette_main, palette_main, dark, font);
```

## Official Tools

| Tool | URL | Purpose |
|------|-----|---------|
| Project Creator | lvgl.io/tools/project-creator | Generate project from board template |
| Font Converter | lvgl.io/tools/fontconverter | TTF → C array |
| Image Converter | lvgl.io/tools/imageconverter | BMP/PNG → C array |
| LVGL Pro (Community) | lvgl.io/pro | XML UI editor, Figma import, CLI, $0 personal |
| SquareLine Studio | squareline.io | Drag-drop UI designer, $0 personal (10 screens) |

## Templates

Ready-to-use scaffolding files:
- `templates/CMakeLists.txt` — CMake build config for SDL2 simulator
- `templates/sdl2_display.c` — SDL2 display + input driver (macOS-safe defaults)
- `templates/main.c` — Minimal entry point with create_ui() stub

To bootstrap a new simulator project, copy these templates and edit create_ui().

## Pitfalls

See `references/pitfalls.md` for platform-specific gotchas (macOS AGX, color depth, buffer sizing, nested driver include paths for v9.5.0, etc.)

## Design-to-Code Gap Analysis

See `references/design-gap-analysis.md` for a systematic workflow to
compare UI design PDFs against source code — extract pages as images,
use vision analysis to read controls/labels, produce quantified
completion metrics. Includes verified bug-check methodology and
confirmed LVGL pitfalls.

See `references/html-prototyping.md` for the browser-based UI prototyping workflow — use this when the SDL2 simulator is unstable and you need rapid visual iteration without compilation.

## Cross-Compilation to ARM Linux

See `references/cross-compile-arm-linux.md` for the complete guide covering:
- Multi-platform CMakeLists with `PLATFORM` option
- Platform-specific `lv_conf` files (`lv_conf_macos.h`, `lv_conf_rk3568.h`)
- aarch64-linux-gnu toolchain setup
- LVGL built-in DRM/KMS + fbdev display drivers
- evdev input with GPIO key mapping (device tree)
- Buildroot package integration
- systemd auto-start service
- Syntax-check target for validation without toolchain

**Quick cross-compile:**
```bash
cmake -B build_rk -DPLATFORM=rk3568 \
  -DCMAKE_TOOLCHAIN_FILE=rk3568_toolchain.cmake \
  -DCMAKE_SYSROOT=/opt/rk3568-sysroot
cmake --build build_rk -j$(nproc)
```

## Per-Platform Targets

- ESP32: use ESP-IDF component registry
- STM32: arm-none-eabi-gcc + LVGL CMake with custom display driver
- NXP: use GUI Guider or Project Creator
- Raspberry Pi / Rockchip RK3568: Linux DRM/KMS + fbdev (see cross-compile reference)
