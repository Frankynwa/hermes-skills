/**
 * LVGL SDL2 Simulator - Main Entry
 * Edit create_ui() to build your interface.
 */

#include "lvgl/lvgl.h"
#include <stdio.h>
#include <stdbool.h>

extern int sdl2_init(void);
extern bool sdl2_loop(void);
extern void sdl2_deinit(void);

static void create_ui(void)
{
    /* Set dark theme */
    lv_display_t *disp = lv_display_get_default();
    lv_theme_t *th = lv_theme_default_init(disp,
        lv_palette_main(LV_PALETTE_BLUE),
        lv_palette_main(LV_PALETTE_RED),
        true, LV_FONT_DEFAULT);
    lv_display_set_theme(disp, th);

    /* === Add your widgets here === */

    /* Title */
    lv_obj_t *title = lv_label_create(lv_screen_active());
    lv_label_set_text(title, "LVGL Simulator");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_20, 0);
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 10);
}

int main(void)
{
    if (sdl2_init() != 0) return 1;
    create_ui();
    while (sdl2_loop()) {}
    sdl2_deinit();
    return 0;
}
