---
name: msvc-lvgl-build
description: "MSVC compiler workflow for LVGL v9 Windows simulator — compilation, linking, and troubleshooting the UT285E UI project"
triggers:
  - user asks to build/compile UT285E project
  - user mentions MSVC or cl.exe
  - build errors with LVGL on Windows
  - SDL2 linking issues
autorun: false
---

# MSVC + LVGL Windows Simulator Build

Complete build pipeline for UT285E UI project using Microsoft Visual C++ compiler on Windows.

## Prerequisites

```bash
# Verify MSVC
ls "/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe"

# Verify SDL2
ls "/c/Users/Administrator/Desktop/SDL2/SDL2-2.30.12/x86_64-w64-mingw32/include/SDL.h"

# Verify LVGL
ls "/c/Users/Administrator/Desktop/lvgl/lvgl.h"
```

## Build Commands

### Full Rebuild

```bash
cmd.exe //c "C:\\Users\\Administrator\\Desktop\\rebuild_all.bat"
```

### Quick Rebuild (single file changed)

```bash
CL="/c/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe"
LINK=".../link.exe"
export INCLUDE="C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Tools\\MSVC\\14.44.35207\\include;C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.26100.0\\ucrt;C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.26100.0\\shared;C:\\Program Files (x86)\\Windows Kits\\10\\Include\\10.0.26100.0\\um"
export LIB="C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Tools\\MSVC\\14.44.35207\\lib\\x64;C:\\Program Files (x86)\\Windows Kits\\10\\Lib\\10.0.26100.0\\ucrt\\x64;C:\\Program Files (x86)\\Windows Kits\\10\\Lib\\10.0.26100.0\\um\\x64"

cd /c/Users/Administrator/Desktop
INC="-IC:\\Users\\Administrator\\Desktop\\SDL2\\SDL2-2.30.12\\x86_64-w64-mingw32\\include -IC:\\Users\\Administrator\\Desktop\\lvgl -IC:\\Users\\Administrator\\Desktop\\lvgl\\src -IC:\\Users\\Administrator\\Desktop\\ut285e-ui -IC:\\Users\\Administrator\\Desktop\\ut285e-ui\\src"
DEF="-DLV_CONF_INCLUDE_SIMPLE -DLV_LVGL_H_INCLUDE_SIMPLE -D_CRT_SECURE_NO_WARNINGS -D_USE_MATH_DEFINES"

# Compile single file
"$CL" -nologo -c -utf-8 $INC $DEF -Fo<file>.obj "C:\\Users\\Administrator\\Desktop\\ut285e-ui\\src\\<file>.c"

# Relink
"$LINK" -nologo -out:ut285e_simulator.exe *.obj SDL2.lib user32.lib gdi32.lib shell32.lib -SUBSYSTEM:CONSOLE
```

## Project Structure

```
Desktop/
├── ut285e-ui/          # Project source (SKILL: embedded-intern-helper)
│   ├── src/            # C source files (15 page modules)
│   ├── CMakeLists.txt  # macOS + RK3568 build (NOT used on Windows)
│   ├── lv_conf.h       # LVGL config (copy of lv_conf_windows.h)
│   └── lv_conf_windows.h  # Windows-specific LVGL config
├── lvgl/               # LVGL v9.5.0 (463 .c files)
├── SDL2/               # SDL2 2.30.12 MinGW x86_64
├── SDL2.dll            # Runtime DLL
├── SDL2.lib            # MSVC import library (generated from DLL)
├── rebuild_all.bat     # Full rebuild script
└── ut285e_simulator.exe # Compilation output (~1.9MB)
```

## Common Errors

### GUI Guider Event System — CRITICAL

When building GUI Guider-generated projects with LVGL v9, the event system needs 7 specific fixes. See full details in: `references/gui-guider-event-fixes.md`

Quick summary:
1. `LV_EVENT_ALL` → `LV_EVENT_CLICKED`
2. Inline registration (not deferred to end of setup)
3. Non-static handlers with header declarations
4. `add_flag(CLICKABLE)` not `remove_flag(CLICKABLE)`
5. `lv_screen_load` not `lv_screen_load_anim`
6. Delete old screen on switch (memory leak)
7. `screen_main` as startup, not `screen_28`

## LVGL v9 SDL Event Handling — CRITICAL

**LVGL v9 has its own internal SDL event loop** via `lv_timer_create(sdl_event_handler, 5, NULL)` in `lv_sdl_window.c:67`.

DO NOT add manual `SDL_PollEvent()` in your main loop — it will **consume mouse/keyboard events before LVGL's internal handler gets them**, causing UI to appear but be unclickable.

LVGL's internal handler calls `lv_sdl_mouse_handler()`, `lv_sdl_keyboard_handler()`, etc. — these translate SDL events to LVGL input events. Your manual `SDL_PollEvent()` races with and starves the LVGL handler.

```c
// ❌ WRONG — conflicts with LVGL v9 internal handler
while(keep_running) {
    SDL_Event event;
    while (SDL_PollEvent(&event)) { if (event.type == SDL_QUIT) keep_running = 0; }
    lv_timer_handler();
    usleep(5000);
}

// ✅ CORRECT — let LVGL handle all SDL events
while(keep_running) {
    lv_timer_handler();
    usleep(5000);
}
```

This applies to **LVGL v9 only**. LVGL v8 requires manual `SDL_PollEvent`.

### SDL2 architecture mismatch

If the EXE is 64-bit but SDL2.dll is 32-bit (or vice versa), the program crashes silently with exit code 127 (0xC000007B = STATUS_INVALID_IMAGE_FORMAT).

Always verify architecture matches:
```bash
file simulator64.exe  # PE32+ = 64-bit
file SDL2.dll         # PE32  = 32-bit → MISMATCH!
```

The GUI Guider project ships with 32-bit SDL2. For 64-bit MinGW, use the SDL2 from `SDL2-2.30.12/x86_64-w64-mingw32/bin/SDL2.dll` instead.

### SDL window blank / no rendering (LVGL v8)
**Fix:** Main loop needs `SDL_PollEvent()` for Windows — LVGL v8 does NOT auto-handle SDL events through internal timers. See ut285e-ui project's main_windows.c for the fix pattern.

### fatal error C1083: Cannot open include file "SDL2/SDL.h"
**Fix:** Include path must be `.../include` NOT `.../include/SDL2`.

### error LNK2019: unresolved external symbol main
**Fix:** main_windows.obj not linked — check if file compiled and is in *.obj list.

### error C4819: file contains characters not in current code page
**Fix:** Source file must be UTF-8 with BOM. Use `/utf-8` flag.

### lv_realloc: couldn't reallocate memory
**Fix:** `LV_MEM_SIZE` too small. Set to `(4 * 1024 * 1024)` in lv_conf.h.

### SDL window blank / no rendering
**Fix:** Main loop needs `SDL_PollEvent()` for Windows. See main_windows.c fix.

## LVGL Config (lv_conf_windows.h)

Key settings for Windows MSVC:
```c
#define LV_COLOR_DEPTH 32
#define LV_MEM_CUSTOM 0         // Use LVGL built-in allocator
#define LV_MEM_SIZE (4*1024*1024) // 4MB pool
#define LV_USE_SDL 1            // SDL2 display driver
#define LV_USE_LOG 1
```

Chinese font support:
```c
// Compile and link: lvgl/src/font/lv_font_source_han_sans_sc_16_cjk.c
// Font: &lv_font_source_han_sans_sc_16_cjk
```

## New_GUI Project Specific Traps

See `references/new-gui-compile-traps.md` for details on:
- `-DLV_FONT_FMT_TXT_LARGE=1` must be in compiler flags, not just lv_conf.h
- `init_keyboard()` must be disabled (replaced with no-op)
- Duplicate font .o files (font_ prefix + non-prefix) cause linker errors
- LVGL `lv_font_fmt_txt.c` must be explicitly compiled for large Chinese fonts

## MinGW Build Alternative

The GUI Guider project also ships with a native MinGW simulator (`lvgl-simulator/`). This is often easier than MSVC for initial compilation.

### Prerequisites
```bash
# MinGW GCC 13.x
export PATH="/c/mingw64/bin:$PATH"
gcc --version  # gcc.exe (MinGW-Builds) 13.2.0
```

### SDL2 include path - CRITICAL
The include must point to the parent of the SDL2 directory:
```bash
# CORRECT
-I"modules/SDL2/include"
# WRONG (doubled SDL2/)
-I"modules/SDL2/include/SDL2"
```
The code uses `#include <SDL2/SDL.h>`, so the include path must stop at `include/`.

### LVGL 9.x API Fix
GUI Guider generates LVGL 9.x code (NOT 8.3 as SCR.txt claims). Key API difference:
```c
// LVGL 8.3 (old)
lv_sdl_window_set_icon(disp, simulator_icon);

// LVGL 9.x (new) — needs width + height
lv_sdl_window_set_icon(disp, simulator_icon, 48, 48);
```

### Include Paths (MinGW)
```bash
-I"$PRJ"           # for "lvgl/lvgl.h" includes
-I"$PRJ/lvgl"     
-I"$PRJ/lvgl/src"
-I"$PRJ/lvgl-simulator"
-I"$PRJ/generated"
-I"$PRJ/custom"    # for lv_conf_ext.h
-I"$SDL_INC"       # modules/SDL2/include
```

### Compile Command
```bash
gcc -O2 -Wall -DLV_CONF_INCLUDE_SIMPLE=1 -D_GNU_SOURCE \
    $INCLUDES @/tmp/all_srcs.txt \
    -o simulator.exe \
    -L"$SDL_LIB" -lSDL2 -lpthread -lm
```

## SDL2 Import Library Generation

### For MSVC
```bash
# From SDL2.dll, generate SDL2.def and SDL2.lib for MSVC linking
dumpbin /EXPORTS SDL2.dll > exports.txt
# Extract function names → SDL2.def → lib /def:SDL2.def /machine:x64 /out:SDL2.lib
```

### For MinGW
```bash
# From SDL2.dll, generate libSDL2.a using gendef + dlltool
gendef SDL2.dll                # generates SDL2.def
dlltool -d SDL2.def -l libSDL2.a -D SDL2.dll   # generates libSDL2.a (509KB)
cp libSDL2.a x86_64-w64-mingw32/lib/
```

## GUI Guider Project — MinGW Full Build

This covers the complete NXP GUI Guider simulator compilation with 500+ source files, Chinese fonts, and image assets.

### Source file list generation (Python)

Command-line length limits make @response files necessary. Generate with Python to avoid path mangling:

```python
import os, glob

prj = r'C:\Users\Administrator\Desktop\ut285e-gui-update\GUI'
srcs = []

for root, dirs, files in os.walk(rf'{prj}\lvgl\src'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
    for f in files:
        if f.endswith('.c') and not f.startswith('._'):
            srcs.append(os.path.join(root, f))

for f in glob.glob(rf'{prj}\generated\*.c'):
    srcs.append(f)
for f in glob.glob(rf'{prj}\generated\guider_fonts\*.c'):
    srcs.append(f)
for f in glob.glob(rf'{prj}\generated\images\*.c'):
    srcs.append(f)

srcs.append(rf'{prj}\lvgl-simulator\main.c')
srcs.append(rf'{prj}\lvgl-simulator\simulator_icon.c')
srcs.append(rf'{prj}\lvgl-simulator\event_stubs.c')
srcs.append(rf'{prj}\custom\custom.c')

with open('srcs.txt', 'w') as f:
    for s in srcs:
        f.write(f'"{s}"\n')
```

### widgets_init.c — MUST compile (Chinese IME + real event callbacks)

The file `generated/widgets_init.c` contains:
- `kb_event_cb()` — real keyboard event callback (with pinyin IME support)
- `ta_event_cb()` — real textarea event callback
- `gg_pinyin_dict[]` — Chinese pinyin input dictionary (~400 entries)

If this file is not compiled, `lv_ime_pinyin_set_dict()` in `gui_guider.c` will fail, and keyboard input won't work.

**CRITICAL: Do NOT create event_stubs.c** that defines `kb_event_cb` or `ta_event_cb` — these will **shadow** the real implementations in `widgets_init.c` at link time. The linker won't warn about this silent override.

```python
# MUST include widgets_init.c in source list
srcs.append(rf'{prj}\generated\widgets_init.c')
```

### Missing event callbacks

If any event callbacks are still unresolved after compiling `widgets_init.c`, create stubs for ONLY the still-missing ones:

```c
// event_stubs.c
#include "lvgl.h"
void kb_event_cb(lv_event_t *e) { /* keyboard event stub */ }
void ta_event_cb(lv_event_t *e) { /* textarea event stub */ }
```

### Runtime DLLs required

Copy these from MinGW to the executable directory:
```
libgcc_s_seh-1.dll      # from /c/mingw64/bin/
libwinpthread-1.dll     # from /c/mingw64/bin/
libstdc++-6.dll         # from /c/mingw64/bin/
SDL2.dll                # from modules/SDL2/lib/
```