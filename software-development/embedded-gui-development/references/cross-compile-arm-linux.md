# Cross-Compilation: LVGL Simulator → ARM Linux Embedded

## Pattern: Multi-Platform CMakeLists + Platform-Specific lv_conf

### Critical Pitfall

**`lv_conf.h` unconditional `#define` overrides CMake `-D` compile flags.** When `lv_conf.h` says `#define LV_USE_SDL 1`, passing `-DLV_USE_SDL=0` on the command line has NO effect — the header's `#define` wins because it's parsed AFTER the command-line define.

**Solution:** Create separate lv_conf files per platform + use `LV_CONF_PATH`:

```cmake
if(PLATFORM STREQUAL "macos")
    add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_macos.h")
elseif(PLATFORM STREQUAL "rk3568")
    add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_rk3568.h")
endif()
```

Files:
- `lv_conf_macos.h` — `LV_USE_SDL=1`, all Linux drivers `=0`
- `lv_conf_rk3568.h` — `LV_USE_LINUX_DRM=1`, `LV_USE_EVDEV=1`, `LV_USE_SDL=0`
- `lv_conf_check.h` — all drivers `=0`, syntax-check only

### Multi-Platform CMakeLists Pattern

```cmake
set(PLATFORM "macos" CACHE STRING "Target: macos | rk3568 | check")

# Common sources (shared UI widgets)
set(APP_UI_SOURCES src/ui_page_*.c ...)

if(PLATFORM STREQUAL "macos")
    # SDL2 simulator — exclude Linux drivers
    list(FILTER LVGL_SOURCES EXCLUDE REGEX
        ".*/drivers/(display/(drm|fb)|evdev|libinput|...).*")
    # ...
elseif(PLATFORM STREQUAL "rk3568")
    # Embedded — exclude desktop drivers, include DRM/fbdev/evdev
    list(FILTER LVGL_SOURCES EXCLUDE REGEX
        ".*/drivers/(sdl|x11|wayland|windows|...).*")
    # Link: libdrm, m, pthread, rt
endif()
```

### ARM Linux Display: DRM/KMS

**v9.5.0 driver header paths** (nested, not flat):
```c
#include "lvgl.h"
#if LV_USE_LINUX_DRM
#include "drivers/display/drm/lv_linux_drm.h"   // NOT "lv_linux_drm.h"
#endif
#if LV_USE_LINUX_FBDEV
#include "drivers/display/fb/lv_linux_fbdev.h"
#endif
#if LV_USE_EVDEV
#include "drivers/evdev/lv_evdev.h"
#endif
```

**lvgl.h does NOT auto-include driver headers** — include them explicitly. Paths are relative to `lvgl/src/`.

**Required CMake include directories:**
```cmake
target_include_directories(your_target PRIVATE
    ${LVGL_DIR}/src/drivers/display/drm
    ${LVGL_DIR}/src/drivers/display/fb
    ${LVGL_DIR}/src/drivers/evdev)
```

// LVGL v9 built-in drivers (no custom code needed)
lv_display_t *disp = lv_linux_drm_create();
lv_linux_drm_set_file(disp, "/dev/dri/card0", -1); // -1 = auto-select connector
lv_display_set_color_format(disp, LV_COLOR_FORMAT_ARGB8888);
```

Fallback to framebuffer:
```c
lv_display_t *disp = lv_linux_fbdev_create();
lv_linux_fbdev_set_file(disp, "/dev/fb0");
```

### ARM Linux Input: evdev + GPIO Keys

Device tree binding:
```dts
gpio_keys: gpio-keys {
    compatible = "gpio-keys";
    button_up: up {
        label = "Up";
        linux,code = <KEY_UP>;
        gpios = <&gpio0 RK_PA2 GPIO_ACTIVE_LOW>;
        debounce-interval = <50>;
    };
};
```

LVGL evdev API (v9):
```c
lv_indev_t *kb = lv_evdev_create(LV_INDEV_TYPE_KEYPAD, "/dev/input/event0");
// Touchscreen (optional)
lv_indev_t *ts = lv_evdev_create(LV_INDEV_TYPE_POINTER, "/dev/input/event1");
```

**LVGL v9 API note:** `lv_indev_get_data()` does NOT exist in v9. Use:
- `lv_indev_get_key(indev)` for key code
- `lv_event_get_code(e)` for event type
- `lv_indev_get_key(indev)` for the LV_KEY_* value

### Syntax-Check Target (Cross-Compile Without Toolchain)

On macOS, validate embedded C code syntax without aarch64 toolchain:
```bash
clang -fsyntax-only -I. -I../lvgl -I../lvgl/src \
    -DLV_CONF_INCLUDE_SIMPLE -DLV_LVGL_H_INCLUDE_SIMPLE \
    -DLV_CONF_PATH="$(pwd)/lv_conf_check.h" \
    -std=c11 src/main_rk3568.c
```

Guard Linux-specific includes:
```c
#if LV_USE_EVDEV
#include <linux/input.h>
#endif
```

### RK3568-Specific (Rockchip, Cortex-A55)

- Display: LCDC Parallel RGB 24-bit → DRM `/dev/dri/card0`
- Toolchain: `aarch64-linux-gnu-gcc -mcpu=cortex-a55 -march=armv8-a`
- System: Buildroot, kernel 6.1
- Storage: eMMC mounted at `/mnt/emmc`
- Auto-start: systemd service (see ut285e.service template)
- macOS cross-compile: `brew` has `aarch64-elf-*` only (bare-metal), not linux-gnu.
  Use Ubuntu VM or `clang --target=aarch64-linux-gnu` with sysroot.
