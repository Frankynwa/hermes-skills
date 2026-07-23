# New_GUI 编译陷阱

> 从 2026-07-22 的 131 屏 New_GUI 编译会话中总结

## 字体：LV_FONT_FMT_TXT_LARGE

### 问题
中文字体（SIYUANHEITI_22、SourceHanSansSCBold_24 等）编译时报错：
```
#error "Too large font or glyphs in LV_FONT_SIYUANHEITI_22. Enable LV_FONT_FMT_TXT_LARGE in lv_conf.h"
```

### 根因
即使 `lv_conf.h` 里 `#define LV_FONT_FMT_TXT_LARGE 1`，编译器也看不到——因为字体源文件里用 `#if LV_FONT_FMT_TXT_LARGE` 检查，而 `LV_CONF_INCLUDE_SIMPLE` 的 include 路径解析有问题。

### 修复
**必须通过 `-D` 传给编译器：**
```bash
gcc -DLV_FONT_FMT_TXT_LARGE=1 -DLV_CONF_INCLUDE_SIMPLE=1 -D_GNU_SOURCE ...
```
仅靠 `lv_conf.h` 里的 `#define` 不够。

## 键盘/拼音：禁用模拟器不需要的模块

### 问题
`gui_guider.c` 的 `init_keyboard()` 调用了 `lv_keyboard_create()`、`lv_ime_pinyin_create()` 等，需要编译 LVGL 的 keyboard 和 pinyin 模块。pinyin 模块还依赖 `LV_KEYBOARD_MODE_*` 常量，编译链很长。

### 修复
直接把 `init_keyboard()` 改成空函数：
```c
void init_keyboard(lv_ui *ui) {
    (void)ui;
    /* Keyboard disabled for simulator */
}
```
模拟器不需要物理键盘输入。

## 字体 .o 文件重复

### 问题
两次编译字体文件时用了不同命名：
```
build_obj/lv_font_SIYUANHEITI_22.o       (直接命名)
build_obj/font_lv_font_SIYUANHEITI_22.o  (font_ 前缀)
```
链接时报 `multiple definition of 'lv_font_SIYUANHEITI_22'`。

### 修复
删除所有 `font_` 前缀的重复文件：
```bash
rm -f build_obj/font_lv_font_*.o
```

## lv_font_fmt_txt.c 必须显式编译

### 问题
启用 `LV_FONT_FMT_TXT_LARGE` 后，字体文件引用 `lv_font_get_glyph_dsc_fmt_txt` 等函数，这些在 `lvgl/src/font/lv_font_fmt_txt.c` 中定义。如果没显式编译这个文件，会报 undefined reference。

### 修复
```bash
gcc -c -O2 -DLV_FONT_FMT_TXT_LARGE=1 $DEFS $INCS \
    "$PRJ/lvgl/src/font/lv_font_fmt_txt.c" -o build_obj/lv_font_fmt_txt.o
```

## lv_conf_ext.h 缺失

### 问题
New_GUI 的 lv_conf.h 末尾有 `#include "lv_conf_ext.h"`，文件不存在时编译失败。

### 修复
创建空文件：
```bash
echo "/* Empty */" > lvgl/lv_conf_ext.h
```

## 编译耗时说明
131 屏幕 + LVGL core + ~60 字体 + ~50 图片 = **600+ 源文件**。全量编译约 2-3 分钟（MinGW）。使用后台编译避免超时：
```bash
hermes terminal --background --notify-on-complete "make -j8"
```