# RK3568 Porting Checklist

## Hardware Verification (Before Any Code)

- [ ] SSH into board: `ssh root@<board-ip>`
- [ ] Check display: `ls /dev/dri/card*` (DRM) or `ls /dev/fb*` (fbdev)
- [ ] Check input: `ls /dev/input/event*`
- [ ] Identify input devices: `cat /sys/class/input/event*/device/name`
- [ ] Check compiler: `gcc --version` (for native build)
- [ ] Check cmake: `cmake --version`
- [ ] Check libdrm: `pkg-config --modversion libdrm`
- [ ] Check kernel: `uname -r` (should be 6.1+ for RK3568)
- [ ] Check memory: `free -h`
- [ ] Check eMMC: `ls /dev/mmcblk*`

## RK3568 Hardware Specs (from datasheet v2.1)

- CPU: Quad-core Cortex-A55 @ 2.0GHz (ARMv8-A)
- GPU: Mali-G52 1-Core-2EE (OpenGL ES 3.2, Vulkan 1.1, OpenCL 2.0)
- RAM: 2-8 GB LPDDR4/DDR4 (32-bit bus)
- Display outputs:
  - RGB Parallel (LCDC, up to 8-bit/pixel) — used in UT285E
  - MIPI DSI TX (2 channels, up to 2560x1600@60 dual-mode)
  - LVDS (dual, RGB888/RGB666, VESA/JEIDA)
  - HDMI 2.0a, eDP 1.3
- Note: LVDS and MIPI DSI share pins — can't use dual-MIPI + dual-LVDS simultaneously
- VOP: 3 Video Output Processors (max 4096x2304@60)
- Internal SRAM: 64KB system + 8KB PMU
- Storage: eMMC 5.1, SD 3.0, SPI Flash, NAND

## UT285E-Specific

### LCD Interface (from schematic)
- Type: Parallel RGB 24-bit (J22, 50-pin FFC)
- Pins: B7-B0, G7-G0, R7-R0 + HSYNC/VSYNC/DEN/CLK
- Bias: VGH/VGL/VCOM1/VCOM2/AVDD 9.8V
- Backlight: VLED+/VLED- (PWM-controlled)
- Orientation: L/R pulled high, U/D pulled low
- Resolution: 800x480

### Physical Buttons (from UI screenshot)
- MENU, BACK
- D-Pad: UP/DOWN/LEFT/RIGHT + OK
- SCREEN CAPTURE
- POWER

## Sysroot Sync (for cross-compilation)

```bash
# Required directories from the target board:
rsync -avz root@<ip>:/lib /opt/rk3568-sysroot/lib
rsync -avz root@<ip>:/usr/lib /opt/rk3568-sysroot/usr/lib
rsync -avz root@<ip>:/usr/include /opt/rk3568-sysroot/usr/include
```

Without sysroot, DRM build will fail (missing libdrm). Code auto-falls back to fbdev.

## Deploy & Run

```bash
# Native build on board (if gcc+cmake available):
rsync -avz ~/ut285e/ root@<ip>:/tmp/ut285e/
rsync -avz ~/lvgl/ root@<ip>:/tmp/lvgl/
ssh root@<ip>
cd /tmp/ut285e
cmake -B build -DPLATFORM=rk3568 -DCMAKE_BUILD_TYPE=Release
cmake --build build -j4
cp build/ut285e_rk3568 /usr/bin/

# Cross-compile on Ubuntu:
cd ut285e
cmake -B build_rk -DPLATFORM=rk3568 \
  -DCMAKE_TOOLCHAIN_FILE=rk3568_toolchain.cmake \
  -DCMAKE_SYSROOT=/opt/rk3568-sysroot
cmake --build build_rk -j$(nproc)
scp build_rk/ut285e_rk3568 root@<ip>:/usr/bin/

# Run:
ssh root@<ip> /usr/bin/ut285e_rk3568
```
