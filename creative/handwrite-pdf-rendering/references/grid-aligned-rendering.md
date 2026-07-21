# Grid-Aligned Rendering for Ruled Paper (横线纸)

## Problem

When rendering handwritten text on ruled/lined paper, content must align to the horizontal grid lines. Without alignment, text drifts across lines, creating visual chaos.

## Key Parameters (A4 at 150 DPI)

| Parameter | Value | Notes |
|-----------|-------|-------|
| `LINE_SPACING` | 38px | Distance between ruled lines |
| `TEXT_FONT_SIZE` | 22px | Must fit within LINE_SPACING |
| `MATH_FONTSIZE` | 28px | For inline/display math |
| Display math cap | `1.8 × LINE_SPACING` | ~68px max height |
| Inline math cap | `0.85 × LINE_SPACING` | ~32px max height |
| Baseline wave | 4.0px amplitude | Was 12.0 — too large for grid |
| Padding | `int(fontsize × 0.6)` | Was `fontsize` — too generous |

## The Grid Alignment Rule

`_advance_line()` must advance by exactly `LINE_SPACING`, NOT by content height:

```python
def _advance_line(self):
    self._flush_line()
    self.y += LINE_SPACING  # snap to grid, always
    self.x = CONTENT_LEFT
    self._current_line_max_h = 0
    if self.y + LINE_SPACING > PAGE_H - MARGIN_BOTTOM:
        self._new_page()
```

## Font Size vs Grid Constraint

With `LINE_SPACING=38px`:
- `TEXT_FONT_SIZE=32` → rendered height ~80px → spans 2+ grid lines → BROKEN
- `TEXT_FONT_SIZE=22` → rendered height ~34px → fits in one grid cell → OK

The rendered height of Chinese text ≈ `fontsize + 2×pad + baseline_wave` after cropping.
With `pad=int(fontsize*0.6)` and `fontsize=22`: pad=13, so canvas ~48px, after crop ~34px.

## Display Math Height Capping

Display formulas rendered by matplotlib can be 100+ pixels tall. Must cap:

```python
max_display_h = int(LINE_SPACING * 1.8)
if img.height > max_display_h:
    scale = max_display_h / img.height
    new_w = max(1, int(img.width * scale))
    img = img.resize((new_w, max_display_h), Image.LANCZOS)
```

## Paragraph Break Spacing

`para_break` should use `_advance_line()` (one grid line gap), NOT `add_newline()` (which was historically used and caused 2-3 line gaps). The old pattern of `add_newline()` before/after headings was removed.

## Pitfalls

1. **Don't over-compress**: Reducing gap to `0.1×LINE_SPACING` or using `pass` for para_break causes text overlap. The grid alignment approach (fixed `LINE_SPACING` advance) is the correct solution.
2. **Don't optimize page count**: User didn't ask to compress to 1 page. Fix spacing issues, don't change content density.
3. **Baseline wave must be small**: 12px amplitude on a 38px grid causes characters to cross into adjacent grid cells. 4px is safe.
