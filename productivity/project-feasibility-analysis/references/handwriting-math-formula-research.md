# Handwriting Rendering & Math Formula Research (2026-06)

> Domain knowledge bank from feasibility analysis of a "LaTeX → handwritten PDF" WeChat mini-program.

## Existing Tools & Approaches

### Text Handwriting Tools (ALL lack math support)

| Tool | Stars | Approach | Math? |
|------|-------|----------|-------|
| text-to-handwriting | ~12K | Pure font + html2canvas, zero perturbation | ❌ |
| kivvi3412/HandWrite | Medium | `handright` lib: per-char Gaussian x/y/theta/fontsize perturbation | ❌ |
| HandwritingGenerator | Small | PyQt6 + TTF fonts + background | ❌ |
| theSage21/handwritten | ~100 | RNN (Alex Graves model) via external API | ❌ |

**Core technique (font-based)**: Render text with a handwriting TTF font, then apply per-character random perturbation:
- `perturb_x_sigma` / `perturb_y_sigma` — stroke offset
- `perturb_theta_sigma` — rotation jitter
- `font_size_sigma` — size jitter
- `line_spacing_sigma` / `word_spacing_sigma` — layout jitter

The `handright` Python library (used by kivvi3412/HandWrite) is the most mature implementation of this approach.

### Math Formula Rendering — THE Gap

**No existing open-source tool renders LaTeX math formulas in handwriting style.** This is the core market gap.

The challenge: math symbols have **structure** (integrals stretch to match integrand height, fractions adapt to numerator/denominator width, square roots wrap their content). Simple font substitution doesn't work.

### Academic / GAN Approaches

| Project | Description | Usability |
|---------|-------------|-----------|
| TIBHannover/formula_gan | GAN with self-attention for handwritten formula images | Generates images for recognition training, NOT a rendering pipeline |
| sjvasquez/handwriting-synthesis | RNN stroke generation (Graves 2013) | English text only, no math |
| Google MathWriting dataset | 500K+ handwritten formula images | Recognition dataset, shows what handwritten math looks like |

### Few-Shot Font Generation (for custom student handwriting)

| Project | Method | Key Feature |
|---------|--------|-------------|
| clovaai/fewshot-font-generation | FUNIT / MX-Font / LF-Font | Image-based input, 5-10 samples sufficient |
| MF-Net | Multilingual few-shot | Chinese + English simultaneously |
| zi2zi-pytorch (EuphoriaYan fork) | AC-GAN + pix2pix | Chinese calligraphy style transfer |
| HeuteNacht/zi2zi-pytorch | macOS/Colab fix | Fixes for Apple Silicon |

**Best path for custom student fonts**: clovaai/fewshot-font-generation with MX-Font — accepts image input (scanned handwriting), needs only 5-10 reference glyphs.

## Four-Layer Architecture for Handwritten Math

### Layer 1: Symbol-level Handwritten Font
Create/use a font covering LaTeX math symbols (∫, ∑, ∏, ∂, Greek letters, operators) in handwriting style. Use FontForge or zi2zi to generate missing symbols from existing handwriting style.

### Layer 2: Bézier Curve Perturbation
Perturb font outline control points with Gaussian noise (amplitude ~1.5px). Each symbol gets a different random seed so the same ∫ looks slightly different each time.

```python
def perturb_glyph(glyph, amplitude=1.5):
    for contour in glyph:
        for point in contour:
            point.x += random.gauss(0, amplitude)
            point.y += random.gauss(0, amplitude)
```

### Layer 3: Layout-level Handwriting Simulation
- Baseline jitter: ±0.8px vertical
- Kerning jitter: ±0.5px horizontal
- Superscript/subscript offset: ±1.5px
- Fraction line tilt: ±0.5°
- Integral height variation: ±2px

### Layer 4: Ink/Texture Post-processing
- Stroke thickness variation (heavy start, light end)
- Ink density variation (slight opacity changes)
- Paper texture overlay (multiply blend mode)
- Light noise (simulate scan artifacts)

## Rendering Pipeline

```
LaTeX text → Parse (regex + grammar) → Symbol tree
  → Render each symbol from handwritten font + Bézier perturbation
  → Structural layout (fractions, superscripts, roots) + layout jitter
  → Ink/texture post-processing
  → Composite into page with lined paper background
  → Export PDF (reportlab)
```

## HK/Macau Market Considerations
- English handwriting fonts needed (Caveat, Satisfy, Patrick Hand)
- Bilingual Chinese + English in same document
- Traditional Chinese character set (港澳用繁体)
- MF-Net can generate both CN+EN fonts from the same handwriting samples

## Key Fonts & Resources
- Chinese handwriting fonts (free, commercial-use): 鸿雷板书简体, 江西拙楷, 杨任东竹石体
- English handwriting fonts: Caveat, Satisfy, Patrick Hand, Indie Flower
- Python libraries: handright, fonttools, PIL/Pillow, matplotlib (Agg mode), reportlab
