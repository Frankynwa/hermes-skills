---
name: embedded-lvgl-arm
description: Use when developing LVGL v9 UIs for ARM Linux embedded systems (RK3568, Buildroot, DRM/KMS). Covers cross-compilation, GUI Guider designer workflow, device tree, backlight, and init scripts.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes-skills, embedded, lvgl, arm, linux, buildroot, rk3568, gui-guider]
    related_skills: []
---

# Embedded LVGL on ARM Linux

## Overview

Patterns for building LVGL v9-based UIs for ARM Cortex-A embedded systems running Buildroot Linux. Covers the full workflow: GUI Guider design → code merge → macOS simulation → cross-compilation → board deployment.

## When to Use

- Building an LVGL UI for RK3568, i.MX, STM32MP, or similar ARM Linux boards
- Integrating GUI Guider designer exports into a C project
- Setting up two-platform dev: macOS simulator + ARM cross-compile
- Configuring DRM/KMS display, backlight PWM, evdev input on embedded Linux
- Writing Buildroot-compatible init scripts (BusyBox init, not systemd)

## Two-Platform Workflow

```
┌──────────────────────┐        ┌──────────────────────┐
│  macOS (dev)          │        │  Ubuntu VM (build)    │
│                       │  push  │                       │
│  VS Code → simulator  │ ─────→ │  aarch64-gcc → board  │
│  5s compile, instant  │  pull  │  ./build_rk3568.sh    │
│  preview with SDL2    │ ←───── │  ./deploy.sh <ip>     │
└──────────────────────┘        └──────────────────────┘
```

**macOS simulator** for rapid UI iteration. **Ubuntu VM** only for final ARM binary.

## GUI Guider Integration

When a UI designer uses NXP GUI Guider, the exported `generated/` folder contains standard LVGL v9 C code. Merge it:

1. Copy `generated/` into `src/gui_guider/`
2. In `main.c`, replace manual UI creation with `setup_ui(scr)` — the auto-generated entry function
3. Keep driver code (backlight, eMMC, watchdog) separate — never modifies GUI Guider output
4. Add `src/gui_guider/` sources to CMakeLists.txt

This gives 100% design fidelity with zero manual rework.

## Cross-Compilation Toolchain

```bash
# Auto-detect in build_rk3568.sh
for cc in \
    "aarch64-buildroot-linux-gnu-gcc" \  # Buildroot SDK
    "aarch64-linux-gnu-gcc" \            # Ubuntu apt
    "aarch64-linux-gcc"; do
    command -v "$cc" && break
done
```

Key flags for Cortex-A55:
```cmake
target_compile_options(... -O2 -mcpu=cortex-a55 -mtune=cortex-a55 -march=armv8-a)
```

## LVGL Config for Embedded

Minimal widget set to save flash — only enable what's used:
```c
#define LV_USE_BUTTON   1
#define LV_USE_LABEL    1
#define LV_USE_CHART    1
#define LV_USE_TABLE    1
#define LV_USE_DROPDOWN 1
#define LV_USE_TEXTAREA 1
#define LV_USE_LINE     1
// All others: 0
```

Custom fonts via `LV_FONT_CUSTOM_DECLARE` — use `tools/gen_font.py` to generate bitmap fonts from TTF. Only generate the glyphs actually used to keep font files small.

## Display Drivers

RK3568 has LCDC with parallel RGB output (24-bit). Use DRM/KMS:

```c
#define LV_USE_LINUX_DRM   1   // Primary: /dev/dri/card0
#define LV_USE_LINUX_FBDEV 1   // Fallback: /dev/fb0
#define LV_USE_EVDEV       1   // GPIO keys + touch
#define LV_USE_LIBINPUT    0   // Not needed when evdev works
```

Kernel 6.1 is required for reliable DRM/KMS on RK3568.

## Backlight Control

Use sysfs backlight interface (requires `CONFIG_BACKLIGHT_CLASS_DEVICE`):
```c
#define BACKLIGHT_PATH "/sys/class/backlight/backlight/brightness"
void ui_backlight_set(int percent) {
    int raw = (percent * max_brightness) / 100;
    sysfs_write_int(BACKLIGHT_PATH, raw);
}
```

Auto-dim after inactivity (5-min timer), restore on user interaction.

## Init System: Buildroot ≠ systemd

Buildroot uses BusyBox init, not systemd. Write `/etc/init.d/S99ut285e`:

```sh
#!/bin/sh
DAEMON="/usr/bin/ut285e_rk3568"
PIDFILE="/var/run/ut285e.pid"
start() { start-stop-daemon -S -b -m -p "$PIDFILE" -x "$DAEMON"; }
stop()  { kill $(cat "$PIDFILE"); rm -f "$PIDFILE"; }
```

Install with `chmod +x /etc/init.d/S99ut285e`. Do NOT use `.service` files.

## Device Tree Overlay

LCD timing must come from the panel datasheet — never guess:
```dts
timing0: timing0 {
    clock-frequency = <28000000>;  /* Hz — from panel spec */
    hactive = <800>; vactive = <480>;
    hfront-porch = <40>; hback-porch = <88>; hsync-len = <48>;
    vfront-porch = <13>; vback-porch = <32>; vsync-len = <3>;
};
```

Touch on I2C4 with GT911 (most common):
```dts
gt911: touchscreen@5d {
    compatible = "goodix,gt911";
    reg = <0x5d>;
    interrupt-parent = <&gpio0>;
    interrupts = <RK_PB5 IRQ_TYPE_EDGE_FALLING>;
};
```

## Common Pitfalls

1. **`LV_OPA_15` does not exist.** LVGL opacity constants are only: 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, COVER, TRANSP. Use `LV_OPA_20`.

2. **`lv_point_t` vs `lv_point_precise_t`.** LVGL v9's `lv_line_set_points()` takes `lv_point_precise_t`, not `lv_point_t`. The signature changed from v8.

3. **PDF can't be fed to vision_analyze directly.** Use pymupdf to convert each page to PNG first: `pix = page.get_pixmap(dpi=200); pix.save(f"page_{i}.png")`.

4. **Schematic analysis for GPIO extraction.** Read signal names on connectors — net names like `TP_INT_L_GPIO0_B5` directly give the GPIO. But backlight/panel timings are on different schematic pages.

5. **Ubuntu ARM ISOs on cdimage.ubuntu.com.** The URL path changed for 24.04. Use UTM's built-in download gallery instead of manual curl — it uses Apple CDN and is faster.

6. **Formal communication with hardware team.** Never send MD file attachments for casual questions. Put the content directly in the message. Use formal tone: "烦请确认" not "拍过来".
