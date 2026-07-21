# macOS SDL2 Hang Debugging

## Quick diagnostic when SDL2 simulator freezes

### 1. Check if process is alive
```bash
pgrep -l ut285e_simulator
```

### 2. Read macOS hang reports
macOS writes hang (unresponsive) reports to:
```
~/Library/Logs/DiagnosticReports/
```
Files have `.hang` extension and are binary plists.

```bash
# List recent hang reports
ls -lt ~/Library/Logs/DiagnosticReports/*.hang 2>/dev/null | head -5

# Read the latest one
plutil -p "$(ls -t ~/Library/Logs/DiagnosticReports/*.hang 2>/dev/null | head -1)" | head -100
```

Key search terms in hang output:
- `"threadSnapshot"` — shows all threads
- `"IOHIDSystem"` — deadlock in Apple's input hardware abstraction
- `"semaphore_wait_trap"` — main thread waiting (normal LVGL idle)
- `"cursorUpdate"` — SDL2 mouse cursor thread stuck

### 3. Live debug with lldb
```bash
lldb ./ut285e_simulator -o run
# When window hangs, press Ctrl+C
(lldb) bt          # stack trace of current thread
(lldb) bt all      # stack traces of ALL threads
```

Look for the thread stuck in `IOHIDSystem`. If found, it's an SDL2/IOHID issue — not your LVGL code.

### 4. Verify: virtual clicks vs physical clicks

Physical mouse click path (can hang):
```
Hardware mouse → SDL2 → IOHID → cursorUpdate (HANGS HERE) → LVGL
```

Virtual click path (never hangs):
```
lv_event_send(obj, LV_EVENT_CLICKED, NULL) → LVGL (direct)
```

If automated tests pass but manual clicking hangs, it's IOHID.

## Fix

```c
// In main.c, BEFORE lv_sdl_mouse_create():
SDL_SetHint(SDL_HINT_MOUSE_TOUCH_EVENTS, "1");
SDL_SetHint(SDL_HINT_TOUCH_MOUSE_EVENTS, "0");
lv_sdl_mouse_create();
```

This routes SDL2 input through touch events instead of mouse events, bypassing IOHID cursorUpdate.
