---
name: lvgl-embedded-linux
description: Develop LVGL v9 UI apps for embedded Linux (RK3568/Buildroot) with macOS SDL2 simulator. Use when building LVGL UI, porting to ARM boards, setting up cross-compilation, fixing SDL2 rendering issues on macOS, or configuring LVGL drivers (DRM/fbdev/evdev).
---

# LVGL v9 Embedded Linux Development

Develop LVGL user interfaces with a macOS SDL2 simulator for fast iteration, then cross-compile to ARM embedded Linux (RK3568, Buildroot, kernel 6.x).

## Multi-Platform Architecture

```
ut285e/
├── lv_conf_macos.h      # SDL2 simulator (LV_USE_SDL=1, Linux drivers=0)
├── lv_conf_rk3568.h     # Embedded target (LV_USE_LINUX_DRM=1, SDL=0)
├── lv_conf_check.h      # Minimal config for syntax-check on macOS
├── CMakeLists.txt        # Single file, PLATFORM={macos|rk3568|check}
├── rk3568_toolchain.cmake
└── src/
    ├── main.c            # macOS entry (SDL2)
    └── main_rk3568.c     # RK3568 entry (DRM+evdev)
```

### Key CMakeLists Pattern

```cmake
set(PLATFORM "macos" CACHE STRING "macos | rk3568 | check")

# Platform-specific lv_conf via LV_CONF_PATH:
if(PLATFORM STREQUAL "macos")
  add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_macos.h")
elseif(PLATFORM STREQUAL "rk3568")
  add_compile_definitions(LV_CONF_PATH="${CMAKE_SOURCE_DIR}/lv_conf_rk3568.h")
endif()

# Filter driver sources per platform:
if(PLATFORM STREQUAL "macos")
  list(FILTER LVGL_SOURCES EXCLUDE REGEX ".*/drivers/(display/(drm|fb)|evdev|libinput|wayland|x11).*")
elseif(PLATFORM STREQUAL "rk3568")
  list(FILTER LVGL_SOURCES EXCLUDE REGEX ".*/drivers/(sdl|wayland|x11).*")
endif()
```

## Pitfall: macOS SDL2 Rendering Corruption

**DO NOT write a custom SDL2 flush callback** on Apple Silicon. LVGL's ARGB8888 byte order does not match `SDL_PIXELFORMAT_ARGB8888` on Apple Silicon, causing color channel swapping and screen corruption. Instead, always use LVGL's built-in SDL driver:

```c
// ✅ CORRECT: Use LVGL's built-in SDL driver
lv_sdl_window_create(800, 480);
lv_tick_set_cb(SDL_GetTicks);

// ❌ WRONG: Custom flush callback + SDL texture
// lv_display_set_flush_cb(disp, my_flush_cb);
// SDL_CreateTexture(..., SDL_PIXELFORMAT_ARGB8888, ...);
```

The built-in driver (`lv_sdl_window_create`) handles pixel format conversion internally.

## LVGL v9 API Changes from v8

| v8 (deprecated) | v9 (correct) |
|-----------------|--------------|
| `lv_scr_act()` | `lv_screen_active()` |
| `lv_disp_get_scr_act()` | `lv_screen_active()` |
| `lv_obj_set_style_pad_all(obj, v, 0)` | same (unchanged) |
| `lv_indev_get_data(indev)` | Does not exist. Use `lv_indev_get_key(indev)` for keypad, or read callback params |
| `LV_EVENT_PRESSED` | Same, but evdev sends `LV_EVENT_KEY` for key events |
| `lv_task_handler()` | `lv_timer_handler()` |
| `lv_obj_add_flag(obj, LV_OBJ_FLAG_HIDDEN)` | same (unchanged) |

## LVGL Display Modes

- **`LV_DISPLAY_RENDER_MODE_PARTIAL`**: Small buffer, good for memory-constrained targets. Can cause artifacts if buffer not properly initialized.
- **`LV_DISPLAY_RENDER_MODE_DIRECT`**: Requires full-screen buffer(s). More memory but no rendering artifacts.
- **`LV_DISPLAY_RENDER_MODE_FULL`**: Two full-screen buffers, renders complete frames.

For Rockchip RK3568 (2-8GB RAM): prefer DIRECT or FULL mode with full-screen buffers.

## Embedded Linux Drivers

### Display (ordered by preference)

```c
// 1. DRM/KMS (hardware-accelerated)
lv_display_t *disp = lv_linux_drm_create();
lv_linux_drm_set_file(disp, "/dev/dri/card0", -1);

// 2. Framebuffer (fallback, simpler)
lv_display_t *disp = lv_linux_fbdev_create();
lv_linux_fbdev_set_file(disp, "/dev/fb0");
lv_linux_fbdev_set_force_refresh(disp, true);
```

### Input: evdev for GPIO buttons

```c
// Keypad (GPIO buttons via DTS → /dev/input/event0)
lv_indev_t *kb = lv_evdev_create(LV_INDEV_TYPE_KEYPAD, "/dev/input/event0");

// Auto-discovery (scan all /dev/input/event*)
lv_evdev_discovery_start(NULL, NULL);
```

**Critical**: Do NOT intercept navigation keys (LV_KEY_UP/DOWN/LEFT/RIGHT/ENTER) in your event callback. LVGL's evdev driver handles group navigation automatically. Only intercept special keys:

```c
static void key_cb(lv_event_t *e) {
    uint32_t key = lv_indev_get_key(lv_event_get_indev(e));
    switch (key) {
    case LV_KEY_HOME:  // MENU button → custom action
        lv_event_stop_bubbling(e);
        break;
    default:
        // Let LVGL handle navigation keys
        break;
    }
}
```

## RK3568 GPIO Key DTS Pattern

```dts
gpio_keys: gpio-keys {
    compatible = "gpio-keys";
    autorepeat;
    button_up: up {
        label = "Up";
        linux,code = <KEY_UP>;
        gpios = <&gpio0 RK_PA2 GPIO_ACTIVE_LOW>;
        debounce-interval = <50>;
    };
    // ... DOWN, LEFT, RIGHT, ENTER, MENU, BACK, CAMERA, POWER
};
```

## LVGL Tick Configuration for Linux

**Always use `clock_gettime(CLOCK_MONOTONIC)`**, not `clock()`:

```c
// ✅ CORRECT: wall-clock time
#define LV_TICK_CUSTOM_SYS_TIME_EXPR \
    (lv_tick_t)({ \
        struct timespec __ts; \
        clock_gettime(CLOCK_MONOTONIC, &__ts); \
        __ts.tv_sec * 1000LL + __ts.tv_nsec / 1000000LL; \
    })

// ❌ WRONG: clock() measures CPU time, not wall time
// #define LV_TICK_CUSTOM_SYS_TIME_EXPR (lv_tick_t)(clock() * 1000 / CLOCKS_PER_SEC)
```

## Cross-Compilation for RK3568 aarch64

On **macOS**, clang can target aarch64 but you still need Linux sysroot headers:

```bash
# Syntax check on macOS (no cross-compiler needed):
cmake -B build_check -DPLATFORM=check
# or manually:
clang -fsyntax-only --target=aarch64-linux-gnu -I... main_rk3568.c

# Full cross-compile on Ubuntu:
rsync -avz root@<board-ip>:/lib     /opt/rk3568-sysroot/lib
rsync -avz root@<board-ip>:/usr/include /opt/rk3568-sysroot/usr/include
cmake -B build_rk -DPLATFORM=rk3568 \
  -DCMAKE_TOOLCHAIN_FILE=rk3568_toolchain.cmake \
  -DCMAKE_SYSROOT=/opt/rk3568-sysroot
```

## Buildroot Integration

```makefile
# package/ut285e-ui/ut285e-ui.mk
UT285E_UI_DEPENDENCIES = lvgl libdrm
UT285E_UI_CONF_OPTS = -DPLATFORM=rk3568 -DCMAKE_BUILD_TYPE=Release
$(eval $(cmake-package))
```

See also `references/Makefile.arm64` for a standalone Makefile-based cross-compilation approach.

## Syntax Checking Embedded Code on macOS

Create a minimal `lv_conf_check.h` with all drivers disabled, then:

```bash
clang -fsyntax-only -I. -I../lvgl -I../lvgl/src \
  -DLV_CONF_INCLUDE_SIMPLE -DLV_LVGL_H_INCLUDE_SIMPLE \
  -DLV_CONF_PATH='"path/to/lv_conf_check.h"' \
  -std=c11 src/main_rk3568.c
```

Wrap Linux-specific includes in `#ifdef` guards, and use `#ifdef __APPLE__` for macOS-incompatible syscalls like `mount()` with 5 args.

## More LVGL v9 API Pitfalls (Discovered in Practice)

| Cause | Symptom | Fix |
|-------|---------|-----|
| `lv_point_t` for line drawing | `incompatible pointer types … 'lv_point_t[2]' to 'lv_point_precise_t *'` | Use `lv_point_precise_t` for ALL `lv_line_set_points` calls |
| `LV_OPA_15` | `use of undeclared identifier 'LV_OPA_15'` | LVGL opa only in steps of 10: `LV_OPA_0`, `LV_OPA_10`, `LV_OPA_20`, … `LV_OPA_100`. Round to nearest valid constant. |
| `snprintf` without `<stdio.h>` | `call to undeclared library function 'snprintf'` on macOS/clang | Always `#include <stdio.h>` when using `snprintf` |

## Chinese Font Integration

1. Generate font with LVGL font converter or `tools/gen_font.py`
2. Declare in `lv_conf_rk3568.h`:
```c
#define LV_FONT_CUSTOM_DECLARE \
    LV_FONT_DECLARE(lv_font_cn_18)
```
3. Add `fonts/lv_font_cn_18.c` to CMake sources
4. Use: `lv_obj_set_style_text_font(obj, &lv_font_cn_18, 0);`
5. Do NOT forget to enable only the Latin fonts you need (e.g., `LV_FONT_MONTSERRAT_14` and `LV_FONT_MONTSERRAT_20`) to save flash space.

## Backlight Control via sysfs

Production embedded devices MUST control backlight. On RK3568 with Buildroot:

```c
// ui_backlight.c — sysfs PWM backlight
#define BACKLIGHT_PATH  "/sys/class/backlight/backlight/brightness"

int ui_backlight_init(void) {
    // Read max brightness, write test value, verify
    sysfs_write_int(BACKLIGHT_PATH, max / 2);
    // …
}

int ui_backlight_set(int percent) {
    int raw = (percent * max) / 100;
    if (raw < 1) raw = 1;  // never fully off to avoid dead-screen confusion
    return sysfs_write_int(BACKLIGHT_PATH, raw);
}
```

Add 5-minute inactivity auto-dim via `lv_timer_create(bl_dim_timer_cb, 5 * 60 * 1000, NULL)` and reset it on user interaction via `ui_backlight_activity()`.

Kernel requirement: `CONFIG_BACKLIGHT_CLASS_DEVICE=y`

## BusyBox init.d Startup Script

Buildroot default init is BusyBox, NOT systemd. Use `/etc/init.d/S99<name>`:

```sh
#!/bin/sh
DAEMON="/usr/bin/ut285e_rk3568"
PIDFILE="/var/run/ut285e.pid"

start() {
    start-stop-daemon -S -b -m -p "$PIDFILE" -x "$DAEMON" -- >> /var/log/ut285e.log 2>&1
    # Watchdog feeding loop:
    [ -c /dev/watchdog ] && (while kill -0 $(cat "$PIDFILE") 2>/dev/null; do echo > /dev/watchdog; sleep 5; done) &
}

stop() {
    [ -f "$PIDFILE" ] && kill $(cat "$PIDFILE") 2>/dev/null && rm -f "$PIDFILE"
}

case "$1" in start) start ;; stop) stop ;; restart) stop; sleep 1; start ;; esac
```

Install: `cp S99ut285e /etc/init.d/ && chmod +x /etc/init.d/S99ut285e`

## Device Tree Overlay (LCD + Touch + Backlight + Keys)

For RK3568 with 800×480 24-bit RGB parallel LCD + I2C4 capacitive touch:

```dts
/dts-v1/; /plugin/;

/* Backlight PWM */
backlight: backlight {
    compatible = "pwm-backlight";
    pwms = <&pwm0 0 50000 0>;
    brightness-levels = <0 … 100>;
    default-brightness-level = <36>;
};

/* LCD panel timing */
panel { compatible = "panel-simple";
    display-timings { native-mode = <&timing0>;
        timing0 { clock-frequency = <28000000>;
            hactive = <800>; vactive = <480>;
            hfront-porch = <40>; hback-porch = <88>; hsync-len = <48>;
            vfront-porch = <13>; vback-porch = <32>; vsync-len = <3>; };};};

/* I2C4 touch — GT911 or FT5x06 */
&i2c4 { status = "okay"; clock-frequency = <400000>;
    gt911: touchscreen@5d {
        compatible = "goodix,gt911"; reg = <0x5d>;
        irq-gpios = <&gpio0 RK_PB5 GPIO_ACTIVE_HIGH>;
        reset-gpios = <&gpio0 RK_PC2 GPIO_ACTIVE_LOW>;
        touchscreen-size-x = <800>; touchscreen-size-y = <480>;};};

/* GPIO keys */
gpio_keys: gpio-keys { compatible = "gpio-keys"; autorepeat;
    key_up { linux,code = <103>; gpios = <&gpio0 RK_PA2 GPIO_ACTIVE_LOW>; };
    /* … DOWN/LEFT/RIGHT/ENTER/MENU/BACK/CAMERA/POWER */ };
```

See `templates/rk3568-ut285e-lcd.dts` for full template.

## Fluke-Inspired Instrument UI Design

When building measurement/instrument dashboards (power analyzers, oscilloscopes, multimeters), Fluke's design patterns offer high data density with color-coded cognition:

| Pattern | Implementation |
|---------|---------------|
| **Phase color cards** | 4 cards in 2×2 grid: L1=Yellow(#FFD700), L2=Green(#00CC00), L3=Red(#FF3333), N=Blue(#4488FF). Semi-transparent bg (`LV_OPA_20`) with colored border. Each shows phase label, voltage (large font), current. |
| **Event badges** | Color-coded boxes with event type label (small, dim) + count (large, phase-colored). Fluke shows event counts prominently — users care about "how many dips" at a glance. |
| **Central frequency** | Large accent-colored readout in center. The single most important number on a power analyzer deserves prominence. |
| **Mini trend chart** | 60-point sparkline showing all 3 phases with matching colors. Not the primary view — a contextual trend for pattern recognition. |
| **REC indicator** | Red background + white text. Always visible in status bar during recording. |
| **Phase-colored chart series** | Every chart uses the same L1/L2/L3 color mapping. Users instantly map color to phase without reading legends. |

## Deploy Pattern

```bash
#!/bin/bash
# deploy.sh — scp binary + ssh launch
BIN="${SCRIPT_DIR}/build_rk3568/ut285e_rk3568"
ssh "root@${TARGET_IP}" "killall ut285e_rk3568 2>/dev/null; sleep 1" || true
scp "$BIN" "root@${TARGET_IP}:/usr/bin/"
ssh -t "root@${TARGET_IP}" "/usr/bin/ut285e_rk3568"
```

Support files: `templates/S99ut285e` (init.d), `templates/rk3568-ut285e-lcd.dts` (device tree overlay).
