/**
 * main_embedded.c — Template for embedded Linux LVGL main()
 * ==========================================================
 * Replace: HOR_RES, VER_RES with actual screen dimensions
 * Replace: UI creation calls with your own UI modules
 * Replace: /dev/input/event0 with actual evdev device path
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#if LV_USE_EVDEV
#include <linux/input.h>
#endif

#include "lvgl.h"

#if LV_USE_LINUX_DRM
#include "lv_linux_drm.h"
#endif
#if LV_USE_LINUX_FBDEV
#include "lv_linux_fbdev.h"
#endif
#if LV_USE_EVDEV
#include "lv_evdev.h"
#endif

/* ============================================================
 * Application UI modules (replace with yours)
 * ============================================================ */
extern void ui_statusbar_create(lv_obj_t *parent);
extern void ui_sidebar_create(lv_obj_t *parent);
extern void ui_pages_create(lv_obj_t *parent);

/* ============================================================
 * Global state
 * ============================================================ */
static lv_display_t *g_disp  = NULL;
static lv_indev_t   *g_kb    = NULL;
static lv_indev_t   *g_touch = NULL;
static int           g_running = 1;

/* ============================================================
 * Signal handler
 * ============================================================ */
static void signal_handler(int sig) {
    (void)sig;
    g_running = 0;
}

/* ============================================================
 * Display: DRM first, fbdev fallback
 * ============================================================ */
static int init_display(void) {
#if LV_USE_LINUX_DRM
    printf("[DISP] Trying DRM/KMS...\n");
    g_disp = lv_linux_drm_create();
    if (g_disp) {
        lv_linux_drm_set_file(g_disp, "/dev/dri/card0", -1);
        lv_display_set_color_format(g_disp, LV_COLOR_FORMAT_ARGB8888);
        printf("[DISP] DRM OK: %dx%d\n",
               lv_display_get_horizontal_resolution(g_disp),
               lv_display_get_vertical_resolution(g_disp));
        return 0;
    }
#endif
#if LV_USE_LINUX_FBDEV
    printf("[DISP] Trying fbdev...\n");
    g_disp = lv_linux_fbdev_create();
    if (g_disp) {
        lv_display_set_color_format(g_disp, LV_COLOR_FORMAT_ARGB8888);
        lv_linux_fbdev_set_file(g_disp, "/dev/fb0");
        lv_linux_fbdev_set_force_refresh(g_disp, true);
        printf("[DISP] FBDEV OK: %dx%d\n",
               lv_display_get_horizontal_resolution(g_disp),
               lv_display_get_vertical_resolution(g_disp));
        return 0;
    }
#endif
    fprintf(stderr, "[DISP] FATAL: No display available!\n");
    return -1;
}

/* ============================================================
 * Key handler — only custom keys, navigation is automatic
 * ============================================================ */
#if LV_USE_EVDEV
static void on_key(lv_event_t *e) {
    uint32_t key = lv_indev_get_key(lv_event_get_indev(e));
    if (lv_event_get_code(e) != LV_EVENT_PRESSED) return;

    switch (key) {
    case LV_KEY_HOME:
        printf("[KEY] MENU\n");
        lv_event_stop_bubbling(e);
        break;
    case LV_KEY_END:
        printf("[KEY] CAPTURE\n");
        /* add screenshot logic here */
        lv_event_stop_bubbling(e);
        break;
    }
}

static void init_input(void) {
    g_kb = lv_evdev_create(LV_INDEV_TYPE_KEYPAD, "/dev/input/event0");
    if (g_kb) {
        lv_indev_add_event_cb(g_kb, on_key, LV_EVENT_ALL, NULL);
        printf("[INPUT] evdev OK\n");
    } else {
        printf("[INPUT] Trying auto-discovery...\n");
        lv_evdev_discovery_start(NULL, NULL);
    }
    g_touch = lv_evdev_create(LV_INDEV_TYPE_POINTER, "/dev/input/event1");
}
#else
static void init_input(void) { printf("[INPUT] Skipped\n"); }
#endif

/* ============================================================
 * Tick (only needed if not using LV_TICK_CUSTOM)
 * ============================================================ */
#if !LV_TICK_CUSTOM
static uint32_t tick_cb(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}
#endif

/* ============================================================
 * Main
 * ============================================================ */
int main(void) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    lv_init();
#if !LV_TICK_CUSTOM
    lv_tick_set_cb(tick_cb);
#endif

    if (init_display() != 0) return 1;
    init_input();

    /* Dark background */
    lv_obj_t *scr = lv_screen_active();
    lv_obj_set_style_bg_color(scr, lv_color_hex(0x000000), 0);
    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);

    /* Build UI */
    ui_statusbar_create(scr);
    ui_sidebar_create(scr);
    ui_pages_create(scr);

    /* Main loop */
    while (g_running) {
        uint32_t ms = lv_timer_handler();
        if (ms == LV_NO_TIMER_READY) ms = 5;
        if (ms > 100) ms = 16;
        usleep(ms * 1000);
    }

    /* Cleanup */
#if LV_USE_EVDEV
    if (g_kb)    lv_evdev_delete(g_kb);
    if (g_touch) lv_evdev_delete(g_touch);
#endif
    if (g_disp)  lv_display_delete(g_disp);
    lv_deinit();
    return 0;
}
