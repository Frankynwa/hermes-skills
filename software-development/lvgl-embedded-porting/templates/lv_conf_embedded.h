/**
 * lv_conf_embedded.h — Template for embedded Linux LVGL config
 * ============================================================
 * How to use:
 *   1. Copy to your project directory
 *   2. Adjust LV_COLOR_DEPTH, LV_DPI_DEF, font sizes as needed
 *   3. Set LV_CONF_PATH in CMake to point to this file
 *   4. Also create lv_conf_macos.h for the simulator build
 *
 * Key differences from desktop config:
 *   - LV_USE_SDL = 0 (no SDL2 on embedded)
 *   - LV_USE_LINUX_DRM = 1 (DRM/KMS display)
 *   - LV_USE_LINUX_FBDEV = 1 (fbdev fallback)
 *   - LV_USE_EVDEV = 1 (GPIO key/pad input)
 *   - LV_USE_LIBINPUT = 0 (avoid extra dependency)
 *   - LV_TICK_CUSTOM with clock_gettime(CLOCK_MONOTONIC)
 */

#ifndef LV_CONF_EMBEDDED_H
#define LV_CONF_EMBEDDED_H

#include <stdint.h>
#include <stdio.h>  /* for LV_LOG_PRINTF */

/* ---- Color ---- */
#define LV_COLOR_DEPTH          32

/* ---- Memory ---- */
#define LV_MEM_CUSTOM           1
#define LV_MEM_CUSTOM_INCLUDE   <stdlib.h>
#define LV_MEM_CUSTOM_ALLOC     malloc
#define LV_MEM_CUSTOM_FREE      free
#define LV_MEM_CUSTOM_REALLOC   realloc

/* ---- DPI ---- */
#define LV_DPI_DEF              130

/* ---- Logging ---- */
#define LV_USE_LOG              1
#define LV_LOG_LEVEL            LV_LOG_LEVEL_WARN
#define LV_LOG_PRINTF           1

/* ---- Assertions ---- */
#define LV_USE_ASSERT_NULL          1
#define LV_USE_ASSERT_MALLOC        1
#define LV_USE_ASSERT_STYLE         1
#define LV_USE_ASSERT_MEM_INTEGRITY 1
#define LV_USE_ASSERT_OBJ           1

/* ---- Tick: MUST use clock_gettime, NOT clock() ---- */
#define LV_TICK_CUSTOM          1
#define LV_TICK_CUSTOM_INCLUDE  <time.h>
#define LV_TICK_CUSTOM_SYS_TIME_EXPR \
    (lv_tick_t)({ \
        struct timespec __ts; \
        clock_gettime(CLOCK_MONOTONIC, &__ts); \
        __ts.tv_sec * 1000LL + __ts.tv_nsec / 1000000LL; \
    })

/* ---- Fonts ---- */
#define LV_FONT_MONTSERRAT_14       1
#define LV_FONT_MONTSERRAT_16       1
#define LV_FONT_MONTSERRAT_20       1
#define LV_FONT_MONTSERRAT_24       1
#define LV_FONT_MONTSERRAT_28       1
#define LV_FONT_MONTSERRAT_32       1
#define LV_FONT_MONTSERRAT_36       1
#define LV_FONT_MONTSERRAT_40       1
#define LV_FONT_DEFAULT             &lv_font_montserrat_20

/* ---- Theme ---- */
#define LV_USE_THEME_DEFAULT        1
#define LV_THEME_DEFAULT_DARK       1

/* ---- Widgets ---- */
#define LV_USE_ARC              1
#define LV_USE_BAR              1
#define LV_USE_BUTTON           1
#define LV_USE_BUTTONMATRIX     1
#define LV_USE_CANVAS           1
#define LV_USE_CHART            1
#define LV_USE_CHECKBOX         1
#define LV_USE_DROPDOWN         1
#define LV_USE_IMAGE            1
#define LV_USE_LABEL            1
#define LV_USE_LED              1
#define LV_USE_LINE             1
#define LV_USE_LIST             1
#define LV_USE_MENU             1
#define LV_USE_MSGBOX           1
#define LV_USE_ROLLER           1
#define LV_USE_SCALE            1
#define LV_USE_SLIDER           1
#define LV_USE_SPAN             1
#define LV_USE_SPINBOX          1
#define LV_USE_SPINNER          1
#define LV_USE_SWITCH           1
#define LV_USE_TABLE            1
#define LV_USE_TABVIEW          1
#define LV_USE_TEXTAREA         1
#define LV_USE_TILEVIEW         1
#define LV_USE_WIN              1

/* ---- Drawing ---- */
#define LV_USE_DRAW_SW          1
#define LV_DRAW_SW_COMPLEX      1
#define LV_DRAW_SW_SHADOW_CACHE_SIZE    1
#define LV_DRAW_SW_CIRCLE_CACHE_SIZE    1

/* ---- Drives ---- */
#define LV_USE_LINUX_DRM        1
#define LV_USE_LINUX_FBDEV      1
#define LV_USE_EVDEV            1
#define LV_USE_LIBINPUT         0
#define LV_USE_SDL              0

/* ---- Misc ---- */
#define LV_USE_PERF_MONITOR     1
#define LV_USE_MEM_MONITOR      1
#define LV_USE_SNAPSHOT         1

#endif /* LV_CONF_EMBEDDED_H */
