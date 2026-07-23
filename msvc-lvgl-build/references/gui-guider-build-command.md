# GUI Guider Full Build Command

Single-command full build for NXP GUI Guider simulator on Windows with MinGW.

## Prerequisites
- MinGW GCC 13.x at `C:\mingw64\bin`
- LVGL 9.x at `GUI/lvgl`
- SDL2 DLL at `GUI/lvgl-simulator/SDL2.dll`
- Python for source list generation

## Build Steps

### 1. Generate source list
```bash
unset PYTHONPATH
python -c "
import os, glob
prj = r'C:\Users\Administrator\Desktop\ut285e-gui-update\GUI'
srcs = []
for root, dirs, files in os.walk(rf'{prj}\lvgl\src'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
    for f in files:
        if f.endswith('.c') and not f.startswith('._'):
            srcs.append(os.path.join(root, f))
for f in glob.glob(rf'{prj}\generated\*.c'): srcs.append(f)
for f in glob.glob(rf'{prj}\generated\guider_fonts\*.c'): srcs.append(f)
for f in glob.glob(rf'{prj}\generated\images\*.c'): srcs.append(f)
srcs.append(rf'{prj}\lvgl-simulator\main.c')
srcs.append(rf'{prj}\lvgl-simulator\simulator_icon.c')
srcs.append(rf'{prj}\custom\custom.c')
with open(r'C:\Users\Administrator\Desktop\srcs.txt', 'w') as f:
    for s in srcs: f.write(f'"{s}"\n')
print(f'{len(srcs)} source files written')
"
```

### 2. Compile
```bash
cd C:\Users\Administrator\Desktop\ut285e-gui-update\GUI\lvgl-simulator
export PATH="/c/mingw64/bin:$PATH"

PRJ="C:\\Users\\Administrator\\Desktop\\ut285e-gui-update\\GUI"
gcc -O2 -Wall \
    -I"$PRJ" -I"$PRJ\\lvgl" -I"$PRJ\\lvgl\\src" \
    -I"$PRJ\\lvgl-simulator" -I"$PRJ\\generated" -I"$PRJ\\custom" \
    -I"$PRJ\\lvgl-simulator\\modules\\SDL2\\include" \
    -DLV_CONF_INCLUDE_SIMPLE=1 -D_GNU_SOURCE \
    @C:\\Users\\Administrator\\Desktop\\srcs.txt \
    -o simulator64.exe \
    -L"$PRJ\\lvgl-simulator\\modules\\SDL2\\x86_64-w64-mingw32\\lib" \
    -lSDL2 -lpthread -lm
```

### 3. Copy runtime DLLs
```bash
cp /c/mingw64/bin/libgcc_s_seh-1.dll ./
cp /c/mingw64/bin/libwinpthread-1.dll ./
cp /c/mingw64/bin/libstdc++-6.dll ./
```

## GUI Guider API fixes required

### lv_sdl_window_set_icon — 4 args in LVGL v9
```diff
- lv_sdl_window_set_icon(disp, simulator_icon);
+ lv_sdl_window_set_icon(disp, simulator_icon, 48, 48);
```

### CLICKABLE flag — GUI Guider bug
GUI Guider sometimes generates `lv_obj_remove_flag(obj, LV_OBJ_FLAG_CLICKABLE)` for image buttons. Fix:
```diff
- lv_obj_remove_flag(ui->screen_main_imgbtn_5, LV_OBJ_FLAG_CLICKABLE);
+ lv_obj_add_flag(ui->screen_main_imgbtn_5, LV_OBJ_FLAG_CLICKABLE);
```
Affected files: setup_scr_screen_main.c, setup_scr_screen_14.c, setup_scr_screen_18.c