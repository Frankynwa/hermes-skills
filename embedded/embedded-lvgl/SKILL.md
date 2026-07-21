---
name: embedded-lvgl
description: Develop LVGL v9 embedded UIs for ARM Linux (RK3568/Buildroot) — dual-build
  (macOS simulator + cross-compile), DRM/KMS display, evdev input, Chinese fonts,
  CMake toolchain setup, and deploy workflow.
---

# Embedded LVGL v9 UI Development for ARM Linux

## Trigger
Use when developing an LVGL-based UI for ARM Linux embedded devices (Rockchip RK3568, Allwinner, etc.) running Buildroot/Yocto. Also triggers on keywords: LVGL, RK3568, Buildroot, embedded UI, DRM/KMS display, evdev, Chinese font LVGL.

## Quick Reference

| Task | Command/File |
|------|-------------|
| macOS build | `cmake -B build_macos -DPLATFORM=macos .. && make -j8` |
| RK3568 build | `./build_rk3568.sh` |
| Deploy to board | `./deploy.sh <ip>` |
| Syntax-check RK3568 code on macOS | `cmake -B build_check -DPLATFORM=check .. && make` |
| Generate Chinese font | `cd tools && python3 gen_font.py` (requires LVGL Font Converter) |

## Project Structure (Dual-Build Pattern)

```
project/
├── CMakeLists.txt          # Unified build: macOS simulator + RK3568
├── CMakeLists_rk3568.txt   # Standalone RK3568 build (for Buildroot integration)
├── lv_conf_macos.h         # LVGL config: SDL2, font sets
├── lv_conf_rk3568.h        # LVGL config: DRM/evdev, 800×480, Chinese
├── rk3568_toolchain.cmake  # Cross-compiler: aarch64-linux-gnu
├── build_rk3568.sh         # One-shot cross-compile script
├── deploy.sh               # scp + launch on target
├── src/
│   ├── main.c              # macOS SDL2 entry point
│   ├── main_rk3568.c       # RK3568 DRM/evdev entry point
│   ├── ui_page_*.c         # Per-page UI modules
│   ├── ui_statusbar.c      # Top status bar
│   ├── ui_sidebar.c        # Navigation sidebar
│   ├── ui_pages.c          # Page container & switching
│   ├── ui_data_emmc.c      # eMMC data source (RK3568 only)
│   ├── fonts/lv_font_cn_18.c  # Chinese bitmap font
│   └── ut285e.h            # Shared constants: colors, layout, page enum
└── tools/gen_font.py       # Font generation script
```

## Key LVGL v9 API Pitfalls

See **[references/lvgl-v9-pitfalls.md](references/lvgl-v9-pitfalls.md)** for the full list. Quick hits:

### lv_point_t → lv_point_precise_t
LVGL v9 changed `lv_line_set_points()` to require `lv_point_precise_t` instead of `lv_point_t`. Using `lv_point_t` causes incompatible-pointer-type warnings (and potential misalignment on 64-bit ARM).

```c
// WRONG (v8):
lv_point_t pts[2] = {{0, 0}, {100, 100}};
lv_line_set_points(line, pts, 2);

// CORRECT (v9):
lv_point_precise_t pts[2] = {{0, 0}, {100, 100}};
lv_line_set_points(line, pts, 2);
```

### Font include pattern for Chinese
Chinese bitmap fonts must be:
1. Declared in `lv_conf.h` via `LV_FONT_CUSTOM_DECLARE`
2. Declared in project header (e.g., `ui_font_cn.h`) via `extern lv_font_t lv_font_cn_18;`
3. Included in CMakeLists.txt as a source file
4. Used in code with `lv_obj_set_style_text_font(obj, &lv_font_cn_18, 0)`

### Color macro pattern
Define all colors as macros in a shared header for consistency across pages:
```c
#define COLOR_BG        lv_color_hex(0x000000)
#define COLOR_ACCENT    lv_color_hex(0xFF8C00)
#define COLOR_L1        lv_color_hex(0xFFD700)  /* Phase A (yellow) */
```

## CMakeLists Dual-Build Pattern

```cmake
set(PLATFORM "macos" CACHE STRING "Target platform: macos | rk3568")

# Shared APP_UI_SOURCES — all page modules
set(APP_UI_SOURCES ...)

if(PLATFORM STREQUAL "macos")
    # SDL2 display, exclude Linux drivers
    list(FILTER LVGL_SOURCES EXCLUDE REGEX ".*/drivers/(drm|fb|evdev).*")
    set(APP_MAIN main.c)
elseif(PLATFORM STREQUAL "rk3568")
    # DRM/evdev, exclude desktop drivers
    list(FILTER LVGL_SOURCES EXCLUDE REGEX ".*/drivers/(sdl|x11|wayland).*")
    set(APP_MAIN main_rk3568.c)
    set(EMMC_SOURCE ui_data_emmc.c)
    target_link_libraries(... m pthread rt drm)
endif()
```

## Cross-Compilation for RK3568 (Buildroot)

### Toolchain Detection
Auto-detect Buildroot or generic aarch64 toolchain:
```bash
for cc in "aarch64-buildroot-linux-gnu-gcc" "aarch64-linux-gnu-gcc"; do
    command -v "$cc" && break
done
```

### Sysroot
Required for libdrm headers. Sync from running board:
```bash
rsync -avz root@<ip>:/lib     /opt/rk3568-sysroot/lib
rsync -avz root@<ip>:/usr/lib /opt/rk3568-sysroot/usr/lib
rsync -avz root@<ip>:/usr/include /opt/rk3568-sysroot/usr/include
```

### Compiler Flags (Cortex-A55)
```cmake
-mcpu=cortex-a55 -mtune=cortex-a55 -march=armv8-a -O2
```

## Display: DRM/KMS Setup

Priority: DRM → fbdev fallback.
```c
g_disp = lv_linux_drm_create();
lv_linux_drm_set_file(g_disp, "/dev/dri/card0", -1);
lv_display_set_color_format(g_disp, LV_COLOR_FORMAT_ARGB8888);
```

For 24-bit RGB parallel LCD panels on RK3568, the LCDC (display controller) is exposed via DRM/KMS. No manual pin muxing needed — the kernel device tree handles the RGB signal routing.

## Input: evdev GPIO Keys

```c
g_kb = lv_evdev_create(LV_INDEV_TYPE_KEYPAD, "/dev/input/event0");
```

Key mapping in device tree (`.dts`):
```
MENU → KEY_MENU (139), BACK → KEY_BACK (158)
UP/DOWN/LEFT/RIGHT → KEY_UP/DOWN/LEFT/RIGHT
ENTER → KEY_ENTER (28)
```

## Data Source: eMMC

Mount pattern:
```c
mount("/dev/mmcblk0p1", "/mnt/emmc", "ext4", 0, NULL);
// Read CSV: /mnt/emmc/data/latest.csv
```

Graceful fallback to fake data generator when eMMC unavailable (useful for simulator testing).

## Deploy Workflow

1. Cross-compile: `./build_rk3568.sh`
2. Deploy: `scp build_rk3568/ut285e_rk3568 root@<ip>:/usr/bin/`
3. Run: `ssh root@<ip> /usr/bin/ut285e_rk3568`

Or one-shot: `./deploy.sh <ip>`

## Updating the Archive
After code changes, re-package for transfer:
```bash
tar -czf ut285e-final.tar.gz \
  --exclude='ut285e/build*' --exclude='ut285e/.git' ut285e/
```
