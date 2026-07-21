# LVGL macOS Simulator Pitfalls

Lessons from setting up LVGL v9.x SDL2 simulator on macOS (Apple Silicon + clang-17).

## Compiler Compatibility

LVGL v9.5.0 uses C23 features (`auto` type inference, `__builtin_assume`) that clang-17 cannot compile. 
LVGL v9.2.0 is the last version compatible with clang-17.

**Symptom**: 
```
error: 'auto' is a keyword in C23
error: use of unknown builtin '__builtin_assume'
```

**Fix**: Use LVGL v9.2.0 on macOS with clang-17, or upgrade to clang-18+.

## Apple GPU (AGX) Texture Bug

M-series GPU driver has a bug with ARGB8888 SDL2 textures. LVGL renders with corrupted/stretched colors.

**Symptom**: Yellow/blue garbled output, text unreadable.

**Fix**: Force software renderer:
```c
SDL_SetHint(SDL_HINT_RENDER_DRIVER, "software");
SDL_CreateWindowAndRenderer(width, height, 0, &window, &renderer);
```

## Color Depth Mismatch

LVGL default 16-bit (RGB565) doesn't match SDL2 default 32-bit (ARGB8888) textures.

**Fix in lv_conf.h**:
```c
#define LV_COLOR_DEPTH 32
```

## Full-Screen Buffer Freeze

Allocating a full-screen buffer (e.g., 1024x600 = 1.5MB) with `LV_DISPLAY_RENDER_MODE_FULL` causes a hang on macOS SDL2.

**Fix**: Use partial mode with a small line buffer:
```c
#define LV_DISPLAY_RENDER_MODE_PARTIAL
static lv_color_t buf1[LV_HOR_RES * 40]; // 40-line buffer
```

## Working CMakeLists.txt for macOS

```cmake
cmake_minimum_required(VERSION 3.16)
project(lvgl_simulator C)
set(CMAKE_C_STANDARD 11)  # NOT gnu2x — clang-17 can't handle it

# Find SDL2
find_package(SDL2 REQUIRED)

# LVGL
add_subdirectory(lvgl)
target_include_directories(lvgl PUBLIC ${CMAKE_SOURCE_DIR})
target_compile_options(lvgl PRIVATE -Wno-everything)

# App
add_executable(lvgl_simulator src/main.c src/sdl2_display.c)
target_link_libraries(lvgl_simulator lvgl SDL2::SDL2)
```
