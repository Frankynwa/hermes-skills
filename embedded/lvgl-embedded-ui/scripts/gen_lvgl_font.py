#!/usr/bin/env python3
"""Generate LVGL v9 1bpp bitmap Chinese font for embedded UI.
Usage: python3 gen_lvgl_font.py
Requires: pip install freetype-py
Output: lv_font_cn_18.c — ready to #include in LVGL project
"""
import freetype, os

# === CONFIG ===
FONT_PATH = '/System/Library/Fonts/Supplemental/Songti.ttc'  # macOS Chinese font
OUTPUT = 'lv_font_cn_18.c'
FONT_SIZE = 18

# Character set — add/remove glyphs as needed for your UI
CHARS = (
    # UT285E UI required Chinese characters
    '电能质量分析仪设置简易测量谐波瞬变事件概览功率电压电流频率相位波形'
    '额定标称接线方式单相分相星形三角形自动触发幅度骤降骤升中断偏差浪涌'
    '快速变化限值滞回闪变系数配置参数标准信号存储状态趋势统计详情瞬时长期'
    '不平衡最大平均最小类型记录表格验证校正返回菜单截图开始记录导出刷新'
    '应用取消完成连接语言时区日期锁颜色以太网无线电热点远程显示序列校准'
    '温度工作偏差精度已安装更正产品注册固件升级复制数据直流偏置许可开源'
    '认证仪器通信工具信息存储已用剩余文件时长操作删除模板开启关闭'
    # ASCII + digits
    '0123456789'
    'VAHzWkvarWh% 123'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    '.-/:;,()[]{}@#&$*!?'
    # Special symbols
    '①②③Φφ±μΩ→↑↓←▲▼◀▶●⏻'
)

def build_font():
    face = freetype.Face(FONT_PATH)
    face.set_pixel_sizes(0, FONT_SIZE)

    glyphs = {}
    for ch in sorted(set(CHARS)):
        face.load_char(ch)
        bmp = face.glyph.bitmap
        w, h = bmp.width, bmp.rows
        if w == 0 or h == 0:
            glyphs[ord(ch)] = {
                'w': FONT_SIZE // 2, 'h': FONT_SIZE,
                'adv_w': FONT_SIZE // 2, 'ofs_x': 0, 'ofs_y': 0, 'data': b''
            }
            continue

        buf = bmp.buffer
        pitch = bmp.pitch
        data = bytearray()
        for y in range(h):
            row = 0
            for x in range(w):
                if buf[y * pitch + x] > 127:
                    row |= 1 << (7 - (x & 7))
                if (x & 7) == 7:
                    data.append(row)
                    row = 0
            if w & 7:
                data.append(row)

        glyphs[ord(ch)] = {
            'w': w, 'h': h,
            'adv_w': face.glyph.advance.x >> 6,
            'ofs_x': face.glyph.bitmap_left,
            'ofs_y': face.glyph.bitmap_top,
            'data': bytes(data)
        }

    # Build single contiguous bitmap with byte offsets
    uniq = sorted(glyphs.keys())
    bitmap = bytearray()
    offsets = {}
    for cp in uniq:
        d = glyphs[cp]['data']
        if not d:
            offsets[cp] = 0
            continue
        # Align to 4-byte boundary
        while len(bitmap) & 3:
            bitmap.append(0)
        offsets[cp] = len(bitmap)
        bitmap.extend(d)

    # Write C output
    with open(OUTPUT, 'w') as f:
        f.write(f'/* Auto-generated Chinese font {FONT_SIZE}px — {len(uniq)} glyphs, {len(bitmap)}B bitmap */\n')
        f.write('#include "lvgl.h"\n\n')

        # Single contiguous bitmap
        f.write('static LV_ATTRIBUTE_MEM_ALIGN const uint8_t cn_font_bmp[] = {')
        for i, b in enumerate(bitmap):
            if i % 16 == 0:
                f.write('\n    ')
            f.write('0x%02x, ' % b)
        f.write('\n};\n\n')

        # Glyph descriptors — bitmap_index is byte offset, NOT pointer
        f.write('static const lv_font_fmt_txt_glyph_dsc_t cn_font_glyphs[] = {\n')
        for cp in uniq:
            g = glyphs[cp]
            f.write('    {.bitmap_index = %d, .adv_w = %d, '
                    '.box_w = %d, .box_h = %d, .ofs_x = %d, .ofs_y = %d},\n'
                    % (offsets[cp], g['adv_w'], g['w'], g['h'], g['ofs_x'], g['ofs_y']))
        f.write('};\n\n')

        # Cmap — FORMAT0_TINY for continuous range
        f.write('static const lv_font_fmt_txt_cmap_t cn_font_cmap = {\n'
                '    .range_start = %d, .range_length = %d,\n'
                '    .glyph_id_start = 0,\n'
                '    .type = LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY\n'
                '};\n\n' % (uniq[0], uniq[-1] - uniq[0] + 1))

        # Font descriptor — NO .glyph_cnt in LVGL v9!
        f.write('static const lv_font_fmt_txt_dsc_t cn_font_dsc = {\n'
                '    .glyph_bitmap = cn_font_bmp,\n'
                '    .glyph_dsc = cn_font_glyphs,\n'
                '    .cmaps = &cn_font_cmap,\n'
                '    .kern_dsc = NULL,\n'
                '    .cmap_num = 1,\n'
                '    .bpp = 1,\n'
                '    .kern_scale = 0\n'
                '};\n\n')

        # Font object
        f.write('lv_font_t lv_font_cn_18 = {\n'
                '    .dsc = &cn_font_dsc,\n'
                '    .get_glyph_dsc = lv_font_get_glyph_dsc_fmt_txt,\n'
                '    .line_height = %d,\n'
                '    .base_line = 0,\n'
                '    .subpx = LV_FONT_SUBPX_NONE,\n'
                '    .fallback = NULL\n'
                '};\n' % (FONT_SIZE + 4))

    print('OK: %s — %d glyphs, %d bytes' % (OUTPUT, len(uniq), os.path.getsize(OUTPUT)))

if __name__ == '__main__':
    build_font()
