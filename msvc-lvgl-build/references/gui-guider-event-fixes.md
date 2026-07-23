# GUI Guider Event System — 7 Fixes for LVGL v9

The NXP GUI Guider generates code targeting LVGL 8.3 (despite using some v9 API names). When compiled against LVGL v9.x, the event system breaks silently — buttons show visual feedback but callbacks never fire.

## Root Cause

1. **LV_EVENT_ALL semantics changed** in v9 — no longer includes CLICKED events for image buttons
2. **Static event handlers** in events_init.c can't be referenced from setup files
3. **Deferred registration** (at end of setup function) allows style overrides to clobber input flags
4. **lv_screen_load_anim** with v8 enum names doesn't properly switch screens
5. **No old-screen deletion** causes memory leak on page switches

## The 7 Fixes

### 1. LV_EVENT_ALL → LV_EVENT_CLICKED

```bash
# In events_init.c — global sed
sed -i 's/add_event_cb(\\(.*\\), LV_EVENT_ALL,/add_event_cb(\\1, LV_EVENT_CLICKED,/g' events_init.c
```

### 2. Inline event registration (not deferred)

```c
// ❌ WRONG — registered at END of setup, after 200 lines of style code
void setup_scr_screen_main(lv_ui *ui) {
    ui->screen_main_imgbtn_5 = lv_imagebutton_create(...);
    // ... 200 lines of lv_obj_set_style_* ...
    events_init_screen_main(ui);  // ⬅ registers here — too late, styles clobbered flags
}

// ✅ RIGHT — registered IMMEDIATELY after creation
void setup_scr_screen_main(lv_ui *ui) {
    ui->screen_main_imgbtn_5 = lv_imagebutton_create(...);
    lv_obj_add_event_cb(ui->screen_main_imgbtn_5, handler, LV_EVENT_CLICKED, NULL); // ⬅ HERE
    // ... styles can follow safely ...
}
```

### 3. Non-static handlers with header declarations

```c
// ❌ Static — can't be referenced from other files
static void screen_main_imgbtn_5_event_handler(lv_event_t *e);

// ✅ Non-static + declaration in events_init.h
void screen_main_imgbtn_5_event_handler(lv_event_t *e);
```

### 4. add_flag CLICKABLE not remove_flag

```c
// ❌ GUI Guider output (4 imgbtns in screen_main, screen_14, screen_18)
lv_obj_remove_flag(ui->screen_main_imgbtn_5, LV_OBJ_FLAG_CLICKABLE);

// ✅ Fix
lv_obj_add_flag(ui->screen_main_imgbtn_5, LV_OBJ_FLAG_CLICKABLE);
```

### 5. Direct lv_screen_load, not animation wrapper

```c
// ❌ Animation function fails silently
ui_load_scr_animation(&guider_ui, &guider_ui.screen_PQinstru, ...);

// ✅ Direct load
setup_scr_screen_PQinstru(&guider_ui);
lv_screen_load(guider_ui.screen_PQinstru);
```

### 6. Delete old screen on switch (memory)

```c
lv_obj_t *old = lv_screen_active();
setup_scr_screen_PQinstru(&guider_ui);
lv_screen_load(guider_ui.screen_PQinstru);
if(old) lv_obj_del(old);  // ⬅ prevent memory leak
```

### 7. screen_main as startup, not screen_28

```c
// ❌ Original gui_guider.c loads screen_28 (last in list, likely debugging)
setup_scr_screen_28(ui);
lv_screen_load(ui->screen_28);

// ✅ Load actual main screen
setup_scr_screen_main(ui);
lv_screen_load(ui->screen_main);
```