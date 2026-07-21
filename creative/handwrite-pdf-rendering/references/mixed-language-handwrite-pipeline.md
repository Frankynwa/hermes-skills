# Mixed-Language Handwriting Pipeline (Chinese + English + Math)

## Architecture

```
Input: mixed text with $inline$ and $$display$$ LaTeX
  │
  ├─ Chinese text → MaShanZheng (楷书) + handright perturbation
  ├─ English text → Kalam + handright perturbation
  └─ Math formulas → matplotlib mathtext (Kalam font) + RGBA composite
  │
  ▼
Lined paper with blue lines + red margin
```

## Font Selection

| Content | Font | Source | Coverage |
|---------|------|--------|----------|
| Chinese (CJK) | MaShanZheng | Google Fonts | 6763 CJK glyphs, NO math symbols |
| English (Latin) | Kalam | Google Fonts | Latin + ∫∑√∏π≠∂±, NO Greek |
| Math symbols | Noto Sans Math | Google Fonts | ALL math symbols (Greek, ∫∑√, arrows, etc.) |

### Per-Character Font Fallback (v10+)
For mixed-script text, use per-character font selection instead of a single font:

```python
def _get_best_font_for_char(char, size=28):
    """Font fallback: MaShanZheng (CJK) → Kalam (Latin) → Noto Sans Math (math)."""
    if _has_cjk(char) and _char_has_glyph(char, MASHAN_PATH):
        return ImageFont.truetype(MASHAN_PATH, size)
    if _char_has_glyph(char, KALAM_PATH):
        return ImageFont.truetype(KALAM_PATH, size)
    if _char_has_glyph(char, NOTO_MATH_PATH):
        return ImageFont.truetype(NOTO_MATH_PATH, size)
    return ImageFont.truetype(KALAM_PATH, size)  # fallback

def _char_has_glyph(char, font_path):
    from fontTools.ttLib import TTFont
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    result = ord(char) in cmap if cmap else False
    font.close()
    return result
```

This eliminates □ boxes for Greek letters and math symbols while keeping handwriting feel for Latin/CJK.

## Font Variant Pool (Per-Render Glyph Variation)

Problem: Same character looks identical every time (just shifted/rotated by handright).

Solution: Pre-generate N perturbed font variants, randomly pick one per render:

```python
from perturb_font import perturb_font_all_glyphs

# Generate 5 variants at startup
for i in range(5):
    perturb_font_all_glyphs("MaShanZheng.ttf", f"variant_{i}.ttf", seed=42+i*1000)

# At render time, randomly pick one
import random
variant = random.choice(["variant_0.ttf", ..., "variant_4.ttf"])
font = ImageFont.truetype(variant, 36)
```

- MaShanZheng: ~7012 glyphs perturbed per variant
- Kalam: ~1019 glyphs perturbed per variant
- Cache in `.font_cache/` directory

## Handright Rendering with Colored Paper

**Pitfall**: Cream paper (252,249,235) + handright noise → all pixels < 250 → cropping breaks.

**Fix**:
1. Render on WHITE background (255,255,255)
2. Crop with threshold 240 (not 250)
3. Replace white pixels with paper color before compositing

```python
bg = Image.new('RGB', (width, height), (255, 255, 255))  # WHITE, not paper color
tpl = handright.Template(background=bg, font=font, ...)
pages = list(handright.handwrite(text, template=tpl))

# Crop: <240 is ink on white background
arr = np.array(pages[0].convert('L'))
mask = arr < 240
# ... find bbox, crop ...

# Replace white with paper color
arr[white_mask] = PAPER_COLOR  # (252, 249, 235)
```

## Formula on Paper: RGBA Composite

**Pitfall**: Pasting formula as opaque image covers paper lines.

**Fix**: Render formula as transparent RGBA, composite onto paper:
```python
# Render formula with transparent background
fig.savefig('formula.png', transparent=True)
formula = Image.open('formula.png').convert('RGBA')

# Composite onto paper (lines show through ink)
paper_rgba = paper.convert('RGBA')
layer = Image.new('RGBA', paper.size, (0, 0, 0, 0))
layer.paste(formula, (x, y), formula)  # Use formula as its own alpha mask
paper_rgba = Image.alpha_composite(paper_rgba, layer)
```

## Formula Sizing: Match Human Writing

Students don't squeeze large formulas into one line. Size formulas to naturally span the right number of paper lines:

| Formula Type | Font Size | Lines Spanned | Example |
|-------------|-----------|---------------|---------|
| Simple (no fraction) | 26pt | 1 line | E=mc², a²+b²=c² |
| With fraction | 36pt | 2-3 lines | ∫₀¹x²dx = 1/3 |
| Complex (nested fractions) | 36pt | 3+ lines | Σ 1/n² = π²/6 |

Rule of thumb: `n_lines = round(formula_pixel_height / LINE_H)`

## Font Registration for matplotlib

```python
import matplotlib.font_manager as fm
import matplotlib as mpl

fm.fontManager.addfont("Kalam-Regular.ttf")
mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.rm'] = 'Kalam'
mpl.rcParams['mathtext.it'] = 'Kalam'
mpl.rcParams['mathtext.bf'] = 'Kalam'
```

This makes ∫∑√∏π render in Kalam style instead of Computer Modern.
Greek letters (αβγ) are handled by matplotlib's built-in fallback.

## Google Fonts Download (CJK)

CJK fonts are large (5-6MB). GitHub raw downloads may truncate via curl.

Safe download method:
```python
import urllib.request
url = "https://raw.githubusercontent.com/google/fonts/main/ofl/mashanzheng/MaShanZheng-Regular.ttf"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
    with open("MaShanZheng-Regular.ttf", "wb") as f:
        f.write(data)

# Validate
from fontTools.ttLib import TTFont
font = TTFont("MaShanZheng-Regular.ttf")
cmap = font.getBestCmap()
assert len(cmap) > 1000, f"Font corrupt: only {len(cmap)} glyphs"
assert sum(1 for cp in cmap if 0x4E00 <= cp <= 0x9FFF) > 5000, "Missing CJK"
```

## Testing: Always Separate Categories

Generate 4+ separate test images:
1. **Chinese**: 6-8 lines of common characters (数字学计算积分极限...)
2. **English**: 6-8 sentences with common words
3. **Math**: 10+ formulas covering ∫∑√, fractions, Greek, primes, subscripts
4. **Chemistry**: H2O, CO2, CH3COOH, reaction equations (2H2 + O2 → 2H2O)

Never mix them into one image — makes it impossible to identify which category has problems.

## Chemistry Formula Rendering

matplotlib doesn't support `\ce{}` (mhchem package). Render chemistry formulas with PIL instead:

```python
def parse_chemistry(formula):
    """Parse 'H2O' → [('H',False), ('2',True), ('O',False)]
    True = subscript, numbers after letters → subscript."""
    segments = []
    i = 0
    while i < len(formula):
        ch = formula[i]
        # Numbers after letter → subscript
        if ch.isdigit() and i > 0 and formula[i-1].isalpha():
            j = i
            while j < len(formula) and formula[j].isdigit():
                j += 1
            segments.append((formula[i:j], True))  # subscript
            i = j
            continue
        # Operators → normal
        if ch in '+-=→()':
            segments.append((ch, False))
        # Arrow notation
        elif formula[i:i+2] == '->':
            segments.append(('→', False))
            i += 2
            continue
        else:
            segments.append((ch, False))
        i += 1
    return segments
```

Render subscripts at 65% font size, positioned below baseline.

## Grayscale→RGB: Alpha Blending (NOT Hard Threshold)

**Pitfall**: `ink_mask = (arr < 240)` creates black blocks — antialiasing edges get captured as ink.

**Fix**:
```python
# WRONG — creates solid black rectangles
ink_mask = (arr < 240).astype(np.float32)
r_out = (paper_r * (1-ink_mask) + ink_r * ink_mask).astype(np.uint8)

# CORRECT — smooth alpha blending
alpha = np.clip((180 - arr) / 80.0, 0, 1)  # 180=full ink, 240=full paper
r_out = (paper_r * (1-alpha) + ink_r * alpha).astype(np.uint8)
```
