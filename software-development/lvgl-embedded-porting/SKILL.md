---
name: lvgl-embedded-porting
description: >-
  Port LVGL UIs from desktop simulators (SDL2) to embedded Linux targets
  (RK3568, STM32MP1, i.MX, etc.). Covers multi-platform CMake setups,
  DRM/fbdev display drivers, evdev input, cross-compilation, Buildroot
  integration, and LVGL v9 API migration. Trigger when the user wants to
  run an existing LVGL app on embedded hardware, set up cross-compilation,
  or create a dual-platform (desktop + embedded) LVGL project.
---

## LVGL Embedded Linux Porting

### Architecture Pattern

```
Desktop (SDL2)              Embedded (DRM/evdev)
     │                              │
main.c (SDL loop)          main_rk3568.c (DRM+evdev)
     │                              │
     └────── lv_conf_macos.h ────── lv_conf_embedded.h
              ↑                     ↑
              └─ CMakeLists (PLATFORM flag) ─┘
```

### Step 1: Split lv_conf into Platform Files

LVGL's `lv_conf.h` uses unconditional `#define` which **overrides** `-D` compile flags.
Never try to override via CMake — create separate files:

```
lv_conf_macos.h      # LV_USE_SDL=1,  LV_USE_LINUX_DRM=0, EVDEV=0
lv_conf_embedded.h   # LV_USE_SDL=0,  LV_USE_LINUX_DRM=1, EVDEV=1
lv_conf_check.h      # All drivers=0, used for syntax checking on macOS
```

Set via CMake:
```cmake
if(PLATFORM STREQUAL "macos")
    add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_macos.h")
elseif(PLATFORM STREQUAL "rk3568")
    add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_embedded.h")
endif()
```

### Step 2: Multi-Platform CMakeLists

```cmake
set(PLATFORM "macos" CACHE STRING "Target: macos|rk3568")

# Common sources (UI pages, shared logic)
set(APP_UI_SOURCES src/ui_page_overview.c ...)

if(PLATFORM STREQUAL "macos")
    list(FILTER LVGL_SOURCES EXCLUDE REGEX
        ".*/drivers/(display/(drm|fb)|evdev|libinput|fbdev|wayland|win32|x11|nuttx|gles|opengles).*")
    set(APP_MAIN src/main.c)
    target_link_libraries(... SDL2)

elseif(PLATFORM STREQUAL "rk3568")
    list(FILTER LVGL_SOURCES EXCLUDE REGEX
        ".*/drivers/(sdl|x11|wayland|windows|uefi|qnx|nuttx/mock).*")
    set(APP_MAIN src/main_rk3568.c)
    target_link_libraries(... drm m pthread rt)
endif()
```

**Pitfall**: The regex filter path must match the actual directory tree.
LVGL v9 has `drivers/display/drm/` (two levels deep), not `drivers/drm/`.
Use `.*/drivers/(display/(drm|fb)|evdev|...).*` not `.*/drivers/(drm|fbdev).*`.

### Step 3: Embedded main() — Display

```c
/* DRM/KMS first, fbdev fallback */
static int init_display(void) {
#if LV_USE_LINUX_DRM
    lv_display_t *disp = lv_linux_drm_create();
    if (disp) {
        lv_linux_drm_set_file(disp, "/dev/dri/card0", -1);
        lv_display_set_color_format(disp, LV_COLOR_FORMAT_ARGB8888);
        return 0;
    }
#endif
#if LV_USE_LINUX_FBDEV
    lv_display_t *disp = lv_linux_fbdev_create();
    if (disp) {
        lv_linux_fbdev_set_file(disp, "/dev/fb0");
        lv_linux_fbdev_set_force_refresh(disp, true);
        lv_display_set_color_format(disp, LV_COLOR_FORMAT_ARGB8888);
        return 0;
    }
#endif
    return -1;
}
```

### Step 4: Embedded main() — Input (evdev)

```c
#if LV_USE_EVDEV
#include <linux/input.h>
#include "lv_evdev.h"

static lv_indev_t *g_kb = NULL;
static lv_indev_t *g_touch = NULL;

static void key_event_cb(lv_event_t *e) {
    lv_indev_t *indev = lv_event_get_indev(e);
    uint32_t key = lv_indev_get_key(indev);

    /* LVGL handles navigation keys (LV_KEY_UP/DOWN/LEFT/RIGHT/ENTER)
       automatically via the evdev driver. Only intercept custom keys. */
    switch (key) {
    case LV_KEY_HOME:  /* MENU button */
        if (lv_event_get_code(e) == LV_EVENT_PRESSED) {
            /* your logic */
            lv_event_stop_bubbling(e);
        }
        break;
    case LV_KEY_END:   /* custom function key */
        /* ... */
        break;
    }
}

static void init_input(void) {
    g_kb = lv_evdev_create(LV_INDEV_TYPE_KEYPAD, "/dev/input/event0");
    if (g_kb)
        lv_indev_add_event_cb(g_kb, key_event_cb, LV_EVENT_ALL, NULL);
    else
        lv_evdev_discovery_start(NULL, NULL);  /* auto-find */

    g_touch = lv_evdev_create(LV_INDEV_TYPE_POINTER, "/dev/input/event1");
}
#endif
```

**Critical**: Do NOT intercept navigation keys (UP/DOWN/LEFT/RIGHT/ENTER) in
your callback. LVGL's evdev driver handles group focus navigation internally.
Intercepting them breaks D-Pad navigation.

### Step 5: LVGL Tick — Use clock_gettime, NOT clock()

```c
/* WRONG — clock() measures CPU time, not wall time */
#define LV_TICK_CUSTOM_SYS_TIME_EXPR (lv_tick_t)(clock() * 1000 / CLOCKS_PER_SEC)

/* CORRECT */
#define LV_TICK_CUSTOM          1
#define LV_TICK_CUSTOM_INCLUDE  <time.h>
#define LV_TICK_CUSTOM_SYS_TIME_EXPR \
    (lv_tick_t)({ \
        struct timespec __ts; \
        clock_gettime(CLOCK_MONOTONIC, &__ts); \
        __ts.tv_sec * 1000LL + __ts.tv_nsec / 1000000LL; \
    })
```

### Step 6: Cross-Compilation Toolchain

File `rk3568_toolchain.cmake`:
```cmake
set(CMAKE_SYSTEM_NAME      Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER       aarch64-linux-gnu-gcc)
set(CMAKE_C_FLAGS_INIT     "-mcpu=cortex-a55 -march=armv8-a")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

Build:
```bash
cmake -B build_rk -DPLATFORM=rk3568 \
  -DCMAKE_TOOLCHAIN_FILE=rk3568_toolchain.cmake \
  -DCMAKE_SYSROOT=/opt/rk3568-sysroot
cmake --build build_rk -j$(nproc)
```

### Step 7: Syntax Check on macOS (No Cross-Compiler Needed)

Create a minimal `lv_conf_check.h` with all drivers disabled, then:
```bash
clang -fsyntax-only -I. -I../lvgl -I../lvgl/src \
  -DLV_CONF_INCLUDE_SIMPLE -DLV_LVGL_H_INCLUDE_SIMPLE \
  -DLV_CONF_PATH='"'$(pwd)/lv_conf_check.h'"' \
  -std=c11 src/main_rk3568.c
```

### Step 8: Buildroot Integration

Files in `buildroot/`:
- `Config.in` — menuconfig entry
- `ut285e-ui.mk` — build recipe using `$(eval $(cmake-package))`

### Step 9: Device Tree for GPIO Keys

```dts
gpio_keys: gpio-keys {
    compatible = "gpio-keys";
    autorepeat;
    button_menu: menu {
        label = "Menu";
        linux,code = <KEY_MENU>;
        gpios = <&gpio0 RK_PA0 GPIO_ACTIVE_LOW>;
        debounce-interval = <50>;
    };
    /* ... UP, DOWN, LEFT, RIGHT, OK, BACK, CAPTURE, POWER ... */
};
```

Move the key declarations into the device tree, and configure the evdev path
(`/dev/input/event0`) in the application.

### Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `#include <linux/input.h>` fails on macOS | Guard with `#if LV_USE_EVDEV` |
| `mount()` 5-arg fails on macOS | Guard with `#ifdef __APPLE__` |
| CMake `list(FILTER)` doesn't match subdirs | Use full path: `drivers/display/drm` not `drivers/drm` |
| `-D` flag overridden by `lv_conf.h` `#define` | Use `LV_CONF_PATH` to pick a different file |
| `-DLV_CONF_PATH="path"` shell quoting | Use `-DLV_CONF_PATH='"'path'"'` |
| `-fsyntax-only` + CMake linking failure | Use separate manual clang invocation for syntax check |
| `lv_indev_get_data()` not found in v9 | Use `lv_indev_get_key(indev)` |

### Support Files

- `references/rk3568-checklist.md` — RK3568-specific hardware checklist
- `templates/lv_conf_embedded.h` — Template for embedded lv_conf
- `templates/main_embedded.c` — Template for embedded main() entry point
