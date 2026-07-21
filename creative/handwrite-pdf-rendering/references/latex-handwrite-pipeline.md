# LaTeX → Handwritten PDF Pipeline Architecture

## Dual-Path Rendering

Text and math formulas require fundamentally different rendering approaches:

```
Input: Mixed text with $inline$ and $$display$$ math
  │
  ▼
Parser: Split into segments [text, math, text, math, ...]
  │
  ├─ Text segments → handright library + handwriting font
  │   (per-char position/rotation/size jitter)
  │
  └─ Math segments → matplotlib LaTeX → image post-processing
      (displacement field + pen pressure + ink bleed)
  │
  ▼
Compositor: Line wrapping, page breaks, baseline alignment
  │         A4 lined paper background (blue lines, red margin)
  ▼
Output: Multi-page PDF
```

## Why Two Engines?

| Engine | Strengths | Weaknesses |
|--------|-----------|------------|
| **handright** (text) | Genuine per-character jitter, CJK support, fast | Text only, no LaTeX |
| **matplotlib** (math) | Full LaTeX support (∫, ∑, fractions, etc.) | Output is "typeset + wobble", not true handwriting |

Combining both gives the best of each: natural-looking text + complete math support.

## Key Implementation Details

### Parser
- Detect `$...$` (inline math) and `$$...$$` (display math)
- Preserve text between math blocks as separate segments
- Newlines in text → line breaks

### handright Template (for text)
```python
handright.Template(
    font=font, font_size=24, line_spacing=50,
    perturb_x_sigma=2.0,      # position jitter
    perturb_y_sigma=2.0,
    perturb_theta_sigma=0.06,  # rotation jitter (radians)
    font_size_sigma=0.4,       # size variation
    word_spacing_sigma=1.0,    # spacing jitter
)
```

### matplotlib LaTeX (for math)
```python
matplotlib.use('Agg')
fig = plt.figure(figsize=(0.01, 0.01))
fig.text(0, 0, f'${latex}$', fontsize=16, ha='left')
fig.savefig('/tmp/formula.png', dpi=200, bbox_inches='tight', transparent=True)
```

### Post-Processing Chain (for math images)
1. **Displacement field**: `scipy.ndimage.zoom(low_res_noise, zoom_factor)` → smooth coherent wobble
2. **Pen pressure**: `PIL.ImageFilter.MaxFilter` on 12% of strokes (random selection)
3. **Ink bleed**: `PIL.ImageFilter.GaussianBlur(radius=0.5)`
4. **Paper texture**: Add Gaussian noise overlay (σ=3) via numpy

### Compositor
- A4 page: 2480×3508px at 300dpi
- Lined paper: blue horizontal lines every 50px, red vertical margin at 120px
- Content area: 120px left margin, 50px right margin
- Line wrapping: when next segment exceeds right boundary, advance to next line
- Page breaks: when vertical position exceeds page height, create new page
- Baseline alignment: all segments on a line vertically centered to line spacing

## Font Strategy

| Content | Font | Engine |
|---------|------|--------|
| Chinese text | System CJK font (STHeiti/SimSun) | handright |
| English text | Kalam (Google Fonts) or Caveat | handright |
| Math formulas | Kalam (perturbed) + matplotlib Computer Modern | matplotlib + post-processing |

## Bilingual Support (HK/Macau)
- Detect CJK characters via Unicode ranges
- Auto-switch font: CJK → Chinese font, Latin → English font
- handright handles mixed scripts if given a font with both ranges
- Alternative: use MF-Net to generate a unified CN+EN handwriting font from samples

## Quality Comparison: handright vs matplotlib Path

Real-world testing (handwrite-pdf-poc project) showed:
- `handright_text_0.png` (handright + Kalam): rated 75-80% handwriting realism
- `perturbed_comparison.png` (fonttools bezier perturbation): convincing wobble, "wobbly" feels natural
- `sample_math_homework.pdf` (matplotlib + pixel perturbation): rated 3/10 for handwriting realism — "obviously computer generated"

**Root cause**: matplotlib renders Computer Modern (a typeset font). Post-processing adds wobble but cannot change the fundamental glyph style. The handright and fonttools approaches work at the character/glyph level, producing genuine handwriting variation.

**Fix path**: Replace matplotlib's font with a handwriting font via `rcParams['mathtext.fontset'] = 'custom'` before applying displacement fields.

## Sample Outputs
Three demo PDFs demonstrating the pipeline:
1. `sample_math_homework.pdf` — Chinese math homework (integrals, limits, series)
2. `sample_english_math.pdf` — English calculus (Taylor, ODEs, vector calc)
3. `sample_bilingual.pdf` — Traditional Chinese + English + LaTeX (linear algebra)
