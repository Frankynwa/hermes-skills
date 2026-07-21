# UT285E-on-RK3568 Architecture Reference

## Hardware
- SoC: Rockchip RK3568 (Quad-core Cortex-A55 @ 2.0GHz, Mali-G52 GPU)
- Display: 800×480 Parallel RGB 24-bit LCD via LCDC (VOP_BT1120)
- Input: 9 physical buttons via GPIO → evdev
- Storage: eMMC (measurement data source)
- OS: Buildroot, kernel 6.1

## File Layout
```
ut285e/
├── CMakeLists.txt              # Three platforms: macos / rk3568 / check
├── lv_conf_macos.h             # SDL2=1, Linux drivers=0
├── lv_conf_rk3568.h            # DRM=1, FBDEV=1, EVDEV=1, SDL=0
├── lv_conf_check.h             # All drivers=0 (syntax check only)
├── rk3568_toolchain.cmake      # aarch64-linux-gnu cross-compiler
├── rk3568-keys.dts             # GPIO keys device tree snippet
├── ut285e.service              # systemd auto-start
├── build_rk3568.sh             # One-click cross-compile script
├── buildroot/                  # Buildroot package integration
│   ├── Config.in
│   └── ut285e-ui.mk
└── src/
    ├── main.c                  # macOS entry (lv_sdl_window_create)
    ├── main_rk3568.c           # RK3568 entry (lv_linux_drm_create + evdev)
    ├── ui_data_emmc.c          # eMMC CSV reader + fake data fallback
    ├── ui_font_cn.h            # Chinese font helper (Font Converter)
    ├── ui_statusbar.c          # Top bar: MEM, time, mode, REC, WiFi, battery
    ├── ui_sidebar.c            # Left nav: 8-page menu
    ├── ui_pages.c              # Lazy page container + switch
    ├── ui_page_overview.c      # Measurement table (V, I, THD, P, PF)
    ├── ui_page_va_hz.c         # Voltage/Current bars + waveform + phasor
    ├── ui_page_power.c         # Power analysis table + trend chart
    ├── ui_page_dip_swell.c     # Dip/Swell detection + event log
    ├── ui_page_harmonics.c     # Harmonic bar chart (1-25) + THD table
    ├── ui_page_transient.c     # Transient waveform capture
    ├── ui_page_events.c        # Event log table with category filters
    └── ui_page_settings.c      # Instrument settings (tabs + forms)
```

## Data Flow
```
eMMC (/dev/mmcblk0p1, ext4)
  → mount /mnt/emmc
  → read /mnt/emmc/data/latest.csv
  → fallback: emmc_generate_fake() with ±5% wobble
  → LVGL timer → UI update
```

## Build Matrix
| Platform | Command | Binary |
|----------|---------|--------|
| macOS simulator | `cmake -B build -DPLATFORM=macos && cmake --build build` | `ut285e_simulator` |
| RK3568 cross | `cmake -B build_rk -DPLATFORM=rk3568 -DCMAKE_TOOLCHAIN_FILE=...` | `ut285e_rk3568` |
| Syntax check | `cmake -B build_ck -DPLATFORM=check` | compiles only |
