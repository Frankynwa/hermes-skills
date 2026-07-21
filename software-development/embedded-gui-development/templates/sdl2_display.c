/**
 * LVGL SDL2 Simulator - Display & Input Driver for macOS
 *
 * Key design decisions (see pitfalls.md for why):
 * - SDL_RENDERER_SOFTWARE (macOS AGX GPU incompatibility)
 * - LV_COLOR_DEPTH=32 (match ARGB8888)
 * - RENDER_MODE_PARTIAL with small buffer (full-size hangs)
 * - lv_display_set_default() BEFORE lv_indev_create()
 */

#include "lvgl/lvgl.h"
#include <SDL2/SDL.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#define SDL_HOR_RES 800
#define SDL_VER_RES 480
#define BUF_LINES   40

static SDL_Window *window = NULL;
static SDL_Renderer *renderer = NULL;
static SDL_Texture *texture = NULL;
static bool quit_requested = false;

static int last_x = 0, last_y = 0;
static bool mouse_pressed = false;
static uint32_t last_key = 0;
static bool key_pressed = false;

static void sdl_display_flush(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map)
{
    int32_t w = lv_area_get_width(area);
    int32_t h = lv_area_get_height(area);
    SDL_Rect r = { .x = area->x1, .y = area->y1, .w = w, .h = h };
    SDL_UpdateTexture(texture, &r, px_map, w * sizeof(lv_color_t));
    SDL_RenderClear(renderer);
    SDL_RenderCopy(renderer, texture, NULL, NULL);
    SDL_RenderPresent(renderer);
    lv_display_flush_ready(disp);
}

static void sdl_mouse_read(lv_indev_t *indev, lv_indev_data_t *data)
{
    (void)indev;
    data->point.x = last_x;
    data->point.y = last_y;
    data->state = mouse_pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

static void sdl_keyboard_read(lv_indev_t *indev, lv_indev_data_t *data)
{
    (void)indev;
    data->key = last_key;
    data->state = key_pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

static void sdl_event_handler(void)
{
    SDL_Event e;
    while (SDL_PollEvent(&e)) {
        switch (e.type) {
        case SDL_MOUSEMOTION:
            last_x = e.motion.x; last_y = e.motion.y; break;
        case SDL_MOUSEBUTTONDOWN:
            if (e.button.button == SDL_BUTTON_LEFT) {
                mouse_pressed = true; last_x = e.button.x; last_y = e.button.y;
            } break;
        case SDL_MOUSEBUTTONUP:
            if (e.button.button == SDL_BUTTON_LEFT) mouse_pressed = false; break;
        case SDL_KEYDOWN:
            key_pressed = true;
            switch (e.key.keysym.sym) {
            case SDLK_UP:        last_key = LV_KEY_UP; break;
            case SDLK_DOWN:      last_key = LV_KEY_DOWN; break;
            case SDLK_LEFT:      last_key = LV_KEY_LEFT; break;
            case SDLK_RIGHT:     last_key = LV_KEY_RIGHT; break;
            case SDLK_RETURN:    last_key = LV_KEY_ENTER; break;
            case SDLK_ESCAPE:    last_key = LV_KEY_ESC; break;
            case SDLK_BACKSPACE: last_key = LV_KEY_BACKSPACE; break;
            default:             last_key = (uint32_t)e.key.keysym.sym; break;
            } break;
        case SDL_KEYUP:  key_pressed = false; break;
        case SDL_QUIT:   quit_requested = true; break;
        default: break;
        }
    }
}

int sdl2_init(void)
{
    if (SDL_Init(SDL_INIT_VIDEO) < 0) { printf("SDL_Init: %s\n", SDL_GetError()); return -1; }

    window = SDL_CreateWindow("LVGL Simulator", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              SDL_HOR_RES, SDL_VER_RES, SDL_WINDOW_SHOWN);
    if (!window) { printf("Window: %s\n", SDL_GetError()); return -1; }

    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);  // see pitfalls #1
    if (!renderer) { printf("Renderer: %s\n", SDL_GetError()); return -1; }

    texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888,
                                SDL_TEXTUREACCESS_STREAMING, SDL_HOR_RES, SDL_VER_RES);
    if (!texture) { printf("Texture: %s\n", SDL_GetError()); return -1; }

    lv_init();

    static lv_color_t buf[SDL_HOR_RES * BUF_LINES];
    lv_display_t *disp = lv_display_create(SDL_HOR_RES, SDL_VER_RES);
    lv_display_set_flush_cb(disp, sdl_display_flush);
    lv_display_set_buffers(disp, buf, NULL, sizeof(buf), LV_DISPLAY_RENDER_MODE_PARTIAL);
    lv_display_set_default(disp);  // MUST be before indev creation

    lv_indev_t *indev = lv_indev_create();
    lv_indev_set_type(indev, LV_INDEV_TYPE_POINTER);
    lv_indev_set_read_cb(indev, sdl_mouse_read);

    lv_indev_t *kb = lv_indev_create();
    lv_indev_set_type(kb, LV_INDEV_TYPE_KEYPAD);
    lv_indev_set_read_cb(kb, sdl_keyboard_read);

    return 0;
}

bool sdl2_loop(void)
{
    sdl_event_handler();
    if (quit_requested) return false;
    lv_timer_handler();
    SDL_Delay(5);
    return true;
}

void sdl2_deinit(void)
{
    SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
}
