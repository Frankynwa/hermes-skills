# PIL Affine Distortion for Per-Character Glyph Variation

## Problem
When rendering the same letter (e.g., 'e') multiple times with the same font, each instance is pixel-identical. This looks obviously artificial in handwriting — real humans never write the same letter exactly the same way twice.

## Solution: Per-Character Affine Transform
After rendering each character to a PIL image, apply a random affine transform with small parameters. This creates subtle shape differences between instances of the same letter.

## Implementation

```python
import numpy as np
from PIL import Image

def distort_character(ch_img, rng, neatness=0.5):
    """Apply random affine distortion to a character image.
    
    Args:
        ch_img: PIL Image (L mode) of a single rendered character
        rng: np.random.RandomState for deterministic randomness
        neatness: 0.0 (careful) to 1.0 (messy), controls distortion magnitude
    
    Returns:
        Distorted PIL Image (same size)
    """
    cw, ch = ch_img.size
    if cw < 4 or ch < 4:
        return ch_img
    
    # Random distortion parameters (scaled by neatness)
    sx = 1.0 + rng.normal(0, 0.04 * neatness)      # horizontal scale
    sy = 1.0 + rng.normal(0, 0.04 * neatness)      # vertical scale
    shear_x = rng.normal(0, 0.025 * neatness)       # horizontal shear
    shear_y = rng.normal(0, 0.015 * neatness)       # vertical shear
    
    # Build affine matrix (PIL convention: a,b,c,d,e,f)
    # x' = a*x + b*y + c
    # y' = d*x + e*y + f
    iw, ih = ch_img.size
    cx, cy = iw / 2, ih / 2  # center of transform
    a, b = sx, shear_y
    d, e = shear_x, sy
    c = cx - a * cx - b * cy  # translate to keep centered
    f = cy - d * cx - e * cy
    
    return ch_img.transform(
        (iw, ih), Image.AFFINE,
        (a, b, c, d, e, f),
        resample=Image.BICUBIC,
        fillcolor=255  # white background
    )
```

## Usage in Rendering Loop

```python
# In a per-character rendering loop:
for i, (ch, font, ...) in enumerate(char_infos):
    # Render character
    ch_img = Image.new('L', (cw + 12, ch_ + 12), 255)
    ch_draw = ImageDraw.Draw(ch_img)
    ch_draw.text((6 - bx, 6 - by), ch, font=font, fill=0)
    
    # Apply affine distortion BEFORE scaling
    ch_img = distort_character(ch_img, rng, neatness=style.neatness)
    
    # Then scale, rotate, etc.
    ch_img = ch_img.resize((sw, sh), Image.LANCZOS)
    ch_img = ch_img.rotate(angle, ...)
```

## Key Parameters

| Parameter | Typical Range | Effect |
|-----------|--------------|--------|
| `sx/sy` (scale) | 1.0 ± 0.04 | Makes letters slightly wider/narrower |
| `shear_x` | 0 ± 0.025 | Tilts letter slightly left/right |
| `shear_y` | 0 ± 0.015 | Subtle vertical skew |

## Important Notes

1. **Apply BEFORE scaling** — distort at original render size, then resize. Distorting after scaling produces blurry results.
2. **Use `fillcolor=255`** — white background for L-mode images, matches paper color.
3. **Canvas needs padding** — use `cw + 12` instead of `cw + 8` to prevent clipping after distortion.
4. **Scale with `neatness`** — neater handwriting = smaller distortion. `StudentStyle.neatness` ranges 0.2-0.7.
5. **Deterministic with seed** — use `rng = np.random.RandomState(seed + i * 13)` so same position always gets same distortion.

## Comparison with Bezier Curve Perturbation

| Aspect | PIL Affine Distortion | Bezier Curve Perturbation |
|--------|----------------------|--------------------------|
| Complexity | Simple (5 lines) | Complex (fonttools + per-point math) |
| Quality | Good — subtle shape changes | Better — organic stroke wobble |
| Font modification | None (image-level) | Modifies font file |
| Performance | Fast (per-image transform) | Slower (per-glyph outline edit) |
| CJK support | Works with any font | Need to handle composite glyphs |
| Best for | Quick wins, mixed scripts | High-quality single-script |

For most handwriting PDF pipelines, PIL affine distortion is sufficient. Use bezier perturbation only when you need the highest quality and are willing to maintain font-level code.
