/**
 * LVGL Simulator — Minimal main.c template for macOS + SDL2
 * Uses custom SDL2 renderer (bypasses LVGL's buggy SDL2 driver on macOS)
 *
 * Build: cd build && cmake .. && make -j$(sysctl -n hw.ncpu)
 * Run:   DYLD_LIBRARY_PATH=/opt/homebrew/lib ./simulator
 */

#define SDL_MAIN_HANDLED
#include <stdio.h>
#include <string.h>
#include <SDL2/SDL.h>
#include "lvgl.h"

#define HOR_RES 800
#define VER_RES 480
#define BUF_LINES 40

static SDL_Window   *g_window   = NULL;
static SDL_Renderer *g_renderer = NULL;
static SDL_Texture  *g_texture  = NULL;

/* Full framebuffer (800×480 ARGB8888) */
static uint8_t g_fb[HOR_RES * VER_RES * 4] __attribute__((aligned(64)));

/* LVGL partial buffer (40 lines at a time) */
static uint8_t g_buf[HOR_RES * BUF_LINES * 4] __attribute__((aligned(64)));

/* ── Flush callback: copies LVGL rendered strips to full framebuffer ── */
static void flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map)
{
    int32_t w = area->x2 - area->x1 + 1;
    int32_t h = area->y2 - area->y1 + 1;

    uint8_t *dst = g_fb + (area->y1 * HOR_RES + area->x1) * 4;
    for (int32_t y = 0; y < h; y++) {
        memcpy(dst, px_map, w * 4);
        dst += HOR_RES * 4;
        px_map += w * 4;
    }

    if (lv_display_flush_is_last(disp)) {
        SDL_UpdateTexture(g_texture, NULL, g_fb, HOR_RES * 4);
        SDL_RenderClear(g_renderer);
        SDL_RenderCopy(g_renderer, g_texture, NULL, NULL);
        SDL_RenderPresent(g_renderer);
    }

    lv_display_flush_ready(disp);
}

int main(void)
{
    SDL_SetMainReady();

    /* Init SDL2 */
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) != 0) {
        fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
        return 1;
    }

    g_window = SDL_CreateWindow("LVGL Simulator",
                                SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                HOR_RES, VER_RES, SDL_WINDOW_SHOWN);
    if (!g_window) { fprintf(stderr, "Window: %s\n", SDL_GetError()); return 1; }

    g_renderer = SDL_CreateRenderer(g_window, -1, SDL_RENDERER_SOFTWARE);
    if (!g_renderer) { fprintf(stderr, "Renderer: %s\n", SDL_GetError()); return 1; }

    g_texture = SDL_CreateTexture(g_renderer, SDL_PIXELFORMAT_ARGB8888,
                                  SDL_TEXTUREACCESS_STREAMING, HOR_RES, VER_RES);
    if (!g_texture) { fprintf(stderr, "Texture: %s\n", SDL_GetError()); return 1; }

    /* Init LVGL */
    lv_init();

    memset(g_fb, 0, sizeof(g_fb));
    memset(g_buf, 0, sizeof(g_buf));

    lv_display_t *disp = lv_display_create(HOR_RES, VER_RES);
    lv_display_set_flush_cb(disp, flush_cb);
    lv_display_set_buffers(disp, g_buf, NULL, sizeof(g_buf), LV_DISPLAY_RENDER_MODE_PARTIAL);
    lv_display_set_color_format(disp, LV_COLOR_FORMAT_ARGB8888);
    lv_tick_set_cb(SDL_GetTicks);

    /* ── Create UI ── */
    lv_obj_t *scr = lv_screen_active();
    lv_obj_set_style_bg_color(scr, lv_color_hex(0x000000), 0);
    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);

    /* TODO: Add your UI widgets here */

    /* Main loop */
    while (1) {
        uint32_t ms = lv_timer_handler();
        if (ms == LV_NO_TIMER_READY) ms = 5;
        if (ms > 100) ms = 16;
        SDL_Delay(ms);

        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) goto done;
        }
    }
done:
    SDL_Quit();
    return 0;
}
