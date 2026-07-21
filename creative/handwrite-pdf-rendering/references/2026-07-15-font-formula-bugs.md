# 2026-07-15 Session: Font + Formula Rendering Bugs

## Summary
User generated EWMA filter handwritten PDF. Output had **zero readability** — Chinese characters silently disappeared and LaTeX formulas rendered as literal text `[s-t]=a[x-t]`.

## Bug 1: LiuJianMaoCao (草书) All CJK Glyphs Zero Height

**Symptom**: ~50% of Chinese characters invisible in rendered output.
**Root cause**: `_get_best_font_for_char()` randomly assigned MaShanZheng (楷书) or LiuJianMaoCao (草书) 50/50. LiuJianMaoCao's simplified CJK glyphs ALL render with `bbox=(0, 29, 33, 29)` → height=0, dark_pixels=0.
**Verification**: Tested all 100+ CJK chars in document — ALL zero height with LiuJianMaoCao.
**fontTools error**: `AssertionError` when reading cmap (corrupted font file).
**Fix**: Disabled LiuJianMaoCao in `_get_best_font_for_char()`, CJK now uses MaShanZheng only.

## Bug 2: `_char_has_glyph()` Returns True for Broken Fonts

**Symptom**: Even with Bug 1 discovered, `_char_has_glyph('指', liujian_path)` returned True.
**Root cause**: 
- Original code: `ord(char) in cmap` — cmap check passed (glyph "exists" in font)
- Exception handler: `return True` — fontTools crash → assume glyph available
**Fix**: 
- After cmap check, actually render with PIL and verify `bbox[3]-bbox[1] > 0`
- Exception handler: `return False` — corrupted font should not be trusted

## Bug 3: `_is_simple_formula()` Missing LaTeX Detection

**Symptom**: Formula `$S_t = \alpha X_t + (1-\alpha)S_{t-1}$` rendered as literal text `[s-t]=a[x-t]+(1-a)[s-t-1]`.
**Root cause**: `_is_simple_formula()` only checked for `\frac`, `\int`, `\sum`, etc. Missed:
- `\alpha`, `\beta`, `\cdot` (any LaTeX command)
- `_{...}` (subscript syntax)
So formula was routed to PIL per-char renderer which output raw LaTeX characters.
**Fix**: Added regex checks:
- `re.search(r'\\[a-zA-Z]', s)` → any LaTeX command → complex
- `re.search(r'[_^]\{', s)` → subscripts/superscripts → complex

## Bug 4: `add_segment()` Zero-Dimension Resize Crash

**Symptom**: `ValueError: height and width must be > 0`
**Root cause**: When `max_w` is 0 or very small, `int(sw * scale)` truncates to 0.
**Fix**: Guard `if sw > max_w and max_w > 0` and `max(1, int(sw * scale))`.

## Escape Sequence Pitfall
First attempt at fixing `_is_simple_formula` quadrupled backslashes (`\\\\\\\\frac` instead of `\\\\frac`) due to patch tool escaping. Verified with `sed -n 'Np' file` and `python3 -c "import re; ..."` before declaring fix complete.
