# Multi-Platform lv_conf Strategy (UT285E pattern)

## Problem

When targeting both desktop simulator and embedded hardware, a single `lv_conf.h` with `#ifdef` guards becomes fragile. `-D` flags don't override `#define` values in lv_conf.h (C preprocessor rules: the last definition wins, but lv_conf.h is included before user code).

## Solution

Three separate config files + `PLATFORM` variable:

```
project/
├── lv_conf_macos.h     # SDL2 simulator, full debugging, all widgets
├── lv_conf_rk3568.h    # Embedded target, stripped down, framebuffer drivers
├── lv_conf_check.h     # Syntax-check only, minimal config
└── CMakeLists.txt       # Copy correct one to lvgl/lv_conf.h based on PLATFORM
```

## CMakeLists.txt pattern

```cmake
if(PLATFORM STREQUAL "rk3568")
    add_compile_definitions(PLATFORM_RK3568)
    configure_file(${CMAKE_SOURCE_DIR}/lv_conf_rk3568.h ${LVGL_DIR}/lv_conf.h COPYONLY)
elseif(PLATFORM STREQUAL "check")
    add_compile_definitions(PLATFORM_CHECK)
    configure_file(${CMAKE_SOURCE_DIR}/lv_conf_check.h ${LVGL_DIR}/lv_conf.h COPYONLY)
else()
    # default: macOS
    configure_file(${CMAKE_SOURCE_DIR}/lv_conf_macos.h ${LVGL_DIR}/lv_conf.h COPYONLY)
endif()
```

## Build commands

```bash
# macOS simulator
cd build && cmake .. && make

# RK3568 cross-compile
cd build_rk3568 && cmake .. -DPLATFORM=rk3568 -DCMAKE_TOOLCHAIN_FILE=... && make

# Syntax check (compile only, no link)
cd build_check && cmake .. -DPLATFORM=check && make
```

## Key rule

Each lv_conf variant defines the SAME set of macros (no missing defines that would fall back to lv_conf_internal.h defaults). This prevents platform-specific compilation failures.

## Pitfall: #define overrides -D

`lv_conf.h` uses `#define LV_USE_FOO 1`. If you try `-DLV_USE_FOO=0` on the command line, it won't work — the header's `#define` wins. This is why separate config files are safer than `-D` overrides.
