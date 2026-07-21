# matplotlib Custom Math Fontset — Detailed Reference

## The Problem

By default, matplotlib renders `$...$` math with **Computer Modern** (Donald Knuth's TeX font). This is a professional serif math font — perfect for papers, but terrible for handwriting simulation. Even with pixel perturbation, the result is "wobbly printed text" (评分 3/10).

## The Solution

```python
import matplotlib as mpl
import matplotlib.font_manager as fm

# MUST register font first — matplotlib won't find it otherwise
fm.fontManager.addfont("/path/to/handwriting-font.ttf")

mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.rm'] = 'Font Name'    # regular
mpl.rcParams['mathtext.it'] = 'Font Name'    # italic
mpl.rcParams['mathtext.bf'] = 'Font Name'    # bold
```

**Critical**: All three (`rm`, `it`, `bf`) must be set, even if to the same font name.
**Critical**: The font name must match what matplotlib's `FontProperties.get_name()` returns, NOT the filename.

## Font Registration Test

```python
import matplotlib.font_manager as fm
fm.fontManager.addfont("/path/to/font.ttf")
prop = fm.FontProperties(fname="/path/to/font.ttf")
print(f'Registered as: "{prop.get_name()}"')  # Use THIS name for mathtext
```

## What Changes with Custom Fontset

| Symbol | Computer Modern | Bradley Hand |
|--------|----------------|--------------|
| ∫ (integral) | Perfect serif curve, symmetric | Slightly tilted, variable thickness |
| ∑ (sum) | Precise geometric | Wider, slightly uneven |
| √ (sqrt) | Exact coverage | Shorter vinculum, natural curve |
| α β γ | Classic Greek | More casual, hand-drawn feel |
| ∞ | Precise loops | Slightly irregular loops |
| Superscripts/subscripts | Perfect alignment | Slight misalignment (realistic!) |
| Fractions | Exact horizontal rule | Slightly uneven rule |

The "imperfections" are features, not bugs — they add handwriting realism.

## macOS System Handwriting Fonts

| Font | Name (for mathtext) | Math Quality | Text Quality |
|------|---------------------|--------------|--------------|
| Bradley Hand Bold | `Bradley Hand` | ★★★★☆ Best | ★★★★☆ |
| Comic Sans MS | `Comic Sans MS` | ★★★☆☆ | ★★★☆☆ |
| Snell Roundhand | varies by .ttc index | ★★☆☆☆ | ★★★★★ |
| Brush Script MT | `Brush Script MT` | ★☆☆☆☆ Too ornate | ★★☆☆☆ |

**Winner: Bradley Hand** — best balance of readability and handwriting feel for math.

## Combined with Pixel Perturbation

After custom fontset rendering, apply pixel perturbation for maximum realism:

1. Smooth displacement (scipy.ndimage.zoom upsampled low-res noise)
2. Pen pressure (15% thicker strokes via dilation, 8% thinner via erosion)
3. Ink bleed (GaussianBlur radius=0.6)
4. Paper texture (Gaussian noise σ=2.5)

**Combined effect**: Bradley Hand + perturbation = 7-8/10 handwriting realism for formulas.

## Verification Command

```bash
cd ~/projects/handwrite-pdf-poc
python3 handwrite_math_renderer.py --compare  # 4-column comparison image
python3 handwrite_pipeline.py --demo math_homework  # Full PDF demo
```
