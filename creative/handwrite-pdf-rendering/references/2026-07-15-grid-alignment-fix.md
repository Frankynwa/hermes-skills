# Grid Alignment & Layout Fix — 2026-07-15

## Problem Summary

User generated an EWMA handwritten PDF. Three rounds of complaints:
1. "太烂了，可读性为0" — LiuJianMaoCao font producing invisible characters
2. "排版非常丑陋，莫名其妙空出两三行" — excessive spacing between sections
3. "又重叠在一起了，你的格子线判定有问题吗" — text not aligned to ruled lines

## Root Causes & Fixes

### Bug 1: LiuJianMaoCao Zero-Height Glyphs
ALL simplified CJK characters render with `bbox height=0` in LiuJianMaoCao.
fontTools cmap says glyph exists, PIL renders it as invisible.
Fix: Disable LiuJianMaoCao entirely, MaShanZheng only.

### Bug 2: `_char_has_glyph()` Exception Fallback
Old: `except: return True` — corrupted font = "has glyph"
Fix: `except: return False`

### Bug 3: `_is_simple_formula()` Missing LaTeX Detection
Formulas with `\alpha`, `_{t-1}` routed to PIL → garbled `[s-t]=a[x-t]`
Fix: `re.search(r'\\[a-zA-Z]', s)` and `re.search(r'[_^]\{', s)`

**Regex pitfall**: `r'\\\\[a-zA-Z]'` (4 backslashes) matches TWO literal backslashes.
Need `r'\\[a-zA-Z]'` (2 backslashes) to match ONE literal backslash.
Always verify: `re.search(pattern, chr(92) + 'alpha')` must match.

### Bug 4: Excessive Spacing
- `add_newline()` before AND after headings
- `para_break` = full `_advance_line()` (content height + gap)
- Stacking = 5-6 blank lines between sections

Fix: Remove all `add_newline()` around headings. `para_break` = `_advance_line()`.

### Bug 5: Grid Misalignment (the final fix)
`_advance_line()` used `self._current_line_max_h + gap` — content-height based.
Chinese text at font-size 32 ≈ 100px tall. Grid lines at 38px intervals.
One text line spanned ~2.7 grid cells — completely unanchored.

**Fix**: `_advance_line` = fixed `self.y += LINE_SPACING` (38px).
This requires `TEXT_FONT_SIZE=22` so text fits in one grid cell.

### Bug 6: Display Math Overflow
Display formulas via matplotlib can exceed 76px (2 grid lines).
Fix: Cap to `LINE_SPACING * 1.8` height.

## Final Parameter Values

| Parameter | Old | New | Reason |
|-----------|-----|-----|--------|
| TEXT_FONT_SIZE | 32 | 22 | Fit within 38px grid cell |
| pad (Chinese renderer) | fontsize | fontsize*0.6 | Reduce padding |
| Baseline wave | 12.0 | 4.0 | Prevent vertical bleed |
| _advance_line | content height + gap | LINE_SPACING | Snap to grid |
| para_break | add_newline() | _advance_line() | One grid line gap |
| Display math cap | uncapped | LINE_SPACING*1.8 | Prevent overflow |
| Heading spacing | ±add_newline() | none | Compact layout |

## Key Diagnostic Commands

```python
# Check if font renders CJK correctly
from PIL import Image, ImageDraw, ImageFont
test_img = Image.new('L', (1, 1), 255)
test_draw = ImageDraw.Draw(test_img)
font = ImageFont.truetype(font_path, 32)
bbox = test_draw.textbbox((0, 0), char, font=font)
height = bbox[3] - bbox[1]  # must be > 0

# Check if formula is classified correctly
import re
has_latex = bool(re.search(r'\\[a-zA-Z]', formula_str))
has_sub = bool(re.search(r'[_^]\{', formula_str))

# Verify grid alignment
# Rendered text height should be < LINE_SPACING (38px)
```
