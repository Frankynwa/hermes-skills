# macOS SDL2 + LVGL Rendering Issues

## Problem: SDL2 window invisible on macOS (Apple Silicon)
- SDL2 software renderer (`SDL_RENDERER_SOFTWARE`) creates a window that runs but is not composited to screen
- `screencapture` returns all-black image even though process is running at 100% CPU
- `osascript` cannot find the window: `get id of first window of process "simulator"` returns empty
- Tried: `SDL_WINDOW_ALWAYS_ON_TOP`, `SDL_WINDOW_OPENGL`, `SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC`, `SDL_RaiseWindow()`, `SDL_SetWindowInputFocus()` — none fix the visibility

## Problem: `lv_sdl_window_create()` crash
- LVGL v9.5.0's built-in SDL driver (`lv_sdl_sw.c`) initializes draw buffer but doesn't properly set up the framebuffer pointer
- `lv_draw_sw_fill()` receives NULL pointer → SEGV at address 0x0
- ASan build doesn't crash (changes memory layout), making debugging harder
- Crash stack: `lv_timer_handler → lv_display_refr_timer → refr_invalid_areas → refr_area → refr_configured_layer → refr_obj_and_children → lv_obj_refr → lv_obj_redraw → lv_obj_draw → lv_draw_rect → lv_draw_finalize_task_creation → lv_draw_dispatch → lv_draw_dispatch_layer → dispatch → execute_drawing → lv_draw_sw_fill → SEGV`

## Verified Working Approach
1. Manual SDL2 init (window + software renderer + ARGB8888 streaming texture)
2. LVGL display with PARTIAL mode, 40-line buffer, ARGB8888
3. Custom flush callback: copy strips to full framebuffer → `SDL_UpdateTexture` → `SDL_RenderPresent`
4. Verify rendering via `SDL_SaveBMP()` of framebuffer (bypasses window visibility issue)
5. Lazy page loading to avoid `lv_timer_handler()` hang

## Problem: SDL2 Mouse Clicks Freeze on macOS (IOHID cursorUpdate Hang)

**Symptom**: Simulator starts and renders correctly, but clicking with a physical mouse causes a beachball / freeze with no error output. The app is hung, not crashed.

**Root cause**: SDL2's mouse event thread calls Apple's `IOHIDSystem cursorUpdate`, which blocks indefinitely on some macOS versions (especially Apple Silicon). This is an SDL2 + macOS IOHID driver incompatibility — not a bug in LVGL code.

**How to confirm (definitive isolation test)**:

1. Send LVGL events programmatically — bypasses SDL2 entirely:
```c
extern lv_obj_t *some_button;
lv_event_send(some_button, LV_EVENT_CLICKED, NULL);
```
If virtual clicks work but physical mouse clicks freeze, the bug is 100% in SDL2's input layer.

2. Attach lldb to see the exact blocked thread:
```bash
ps aux | grep simulator   # find PID
lldb -p <PID>
(lldb) bt all             # look for IOHIDSystem cursorUpdate
```

3. Check macOS hang reports:
```bash
ls -lt /Library/Logs/DiagnosticReports/*.hang | head -3
plutil -p <file> | grep -B2 -A8 "IOHIDSystem"
```

**Fix**: Disable SDL2 mouse and scrollwheel input devices. Keep keyboard for navigation:
```c
/* lv_sdl_mouse_create();      -- disabled: macOS IOHID hang */
lv_sdl_keyboard_create();
/* lv_sdl_mousewheel_create(); -- disabled */
```
Use Tab to cycle focus and Enter to activate.

**What does NOT work** (tested, no effect):
- `SDL_SetHint(SDL_HINT_MOUSE_RELATIVE_MODE_WARP, "0")`
- `SDL_SetHint(SDL_HINT_MOUSE_TOUCH_EVENTS, "1")`
- `SDL_SetHint(SDL_HINT_MOUSE_FOCUS_CLICKTHROUGH, "1")`
The root cause is in Apple's IOHID framework — SDL2 hints cannot bypass it.

## BMP Verification Command
```bash
# After simulator saves /tmp/frame.bmp, view in browser:
# browser_navigate: file:///tmp/frame.bmp
```
