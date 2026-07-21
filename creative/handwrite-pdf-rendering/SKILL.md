---
name: handwrite-pdf-rendering
description: >
  Generate handwritten-style PDFs with math formulas, mixed Chinese/English text.
  Covers handright library, matplotlib math font customization, fonttools bezier
  perturbation, per-character PIL rendering with jitter, connected strokes,
  pen pressure gradients, StudentStyle personality system, paper aging effects,
  ink color variation, correction marks, ink type physics (ballpoint/fountain/pencil),
  bigram context consistency, paper texture overlay, markdown structural parsing
  (headings/lists/paragraphs), layout intelligence, and CJK font variant full coverage.
  CRITICAL: formulas must be rendered CLEAN (zero perturbation) — scan effects and
  pixel perturbation are DISABLED for formula images. Always test Chinese/English/math
  SEPARATELY before combining. Use when working on the handwrite-pdf-poc project
  or similar handwriting rendering tasks. See references/research-driven-optimization.md
  for the arXiv paper survey methodology.
triggers:
  - handwrite-pdf-poc project work
  - handwritten math formula rendering
  - fake handwriting PDF generation
  - handright library usage
  - matplotlib custom math font
  - fonttools bezier curve perturbation
  - Chinese handwriting font selection
  - StudentStyle handwriting personality
  - paper aging effects (creases, coffee stains)
  - connected strokes / ligature in handwriting
  - per-character rendering with jitter
  - separate Chinese/English/math testing workflow
  - formula legibility preservation (zero perturbation)
  - font coverage gap debugging (□ tofu)
  - ink type simulation (ballpoint/fountain/pencil)
  - markdown to handwritten PDF conversion
  - bigram context consistency in handwriting
  - paper texture overlay
  - CJK font variant perturbation
  - research-driven code optimization from arXiv papers
related_skills:
  - font-manipulation
---

# Handwritten PDF Rendering

## Project: `~/projects/handwrite-pdf-poc/`

WeChat mini-program PoC targeting Hong Kong/Macau market. Converts LaTeX + Chinese/English text into handwritten-style PDFs on lined paper.

## Architecture (Three-Tier Rendering)

```
输入文本（中英混排 + LaTeX公式）
    │
    ▼
┌───────────┐
│   解析器   │  parse_content(): 拆分 text / $inline$ / $$display$$
└─────┬─────┘
      │
      ▼ 五条渲染路径 ──────────────────────────────────────
      │
      ├─ 简单数学 → PIL + Kalam/NotoSansMath 逐字渲染 + 逐字抖动/旋转/缩放
      │   (无 \frac/\int/\lim/\sum/\sqrt 的公式)
      │   → 基线波浪 + 连笔连接 + 笔压渐变
      │   → Bigram 上下文一致性（3字组共享变体种子）
      │   → ⚠️ NO pixel perturbation — 保留清晰度
      │
      ├─ 复杂数学 → matplotlib mathtext(fontset=custom, font=Kalam, sf=NotoSansMath, tt=MaShanZheng)
      │   → CJK in \text{} 通过 mathtext.tt 渲染
      │   → ⚠️ CLEAN rendering — 无扰动、无模糊、无JPEG压缩
      │   → 只加公式连接线（可选）和墨水颜色
      │
      ├─ 中文文字 → MaShanZheng + Kalam/NotoSansMath 回退 + PIL 逐字渲染
      │   → 温和抖动 + 轻微连笔 + StudentStyle 参数
      │   → ⚠️ 逐字检查字体覆盖率，缺字回退Kalam→NotoSansMath
      │   → Bigram 上下文一致性（3字组共享变体种子）
      │
      ├─ 英文文字 → Graves RNN (长文本>25字符) 或 PIL per-char (短文本)
      │   → Graves RNN: SVG渲染 + 缩放适配 + 墨水颜色
      │   → PIL: render_math_pil_v2() + 基线波浪 + 连笔
      │
      ├─ 化学公式 → render_chemistry_formula() + _parse_chemistry()
      │   → 自动识别下标/上标 (H2O → H₂O, Fe2O3 → Fe₂O₃)
      │   → 支持 \ce{} LaTeX 语法
      │
      ▼
┌───────────┐
│  排版合成  │  PageCompositor: 老化横线纸 + 纸张纤维纹理 + 换行 + 分页
│            │  + 纸张老化(泛黄/折痕/咖啡渍/狗耳朵) + 蓝黑墨水色
│            │  + 修正痕迹(划掉/涂改液/caret)
│            │  + InkType 物理仿真(圆珠笔/钢笔/铅笔)
│            │  + Markdown 布局智能(标题字号/列表缩进/段落间距)
└─────┬─────┘
      ▼
  output.pdf（多页A4，蓝横线 + 红边距，带使用痕迹）

  ⚠️ NO scan effects in production — they destroy formula readability
  (apply_scan_effects() exists but must NOT be called on formula-heavy pages)
```

**CRITICAL DESIGN PRINCIPLE: Formulas must ALWAYS be rendered CLEAN.**
Any pixel perturbation, JPEG compression, or aggressive sharpening
on formula images makes them illegible. The user explicitly complained
"公式完全难以辨认" when perturbation+scan effects were active.
**Zero perturbation on formulas. Always.**

## Key Technique: matplotlib Custom Math Fontset

**This is the core breakthrough.** By default, matplotlib renders LaTeX with Computer Modern (印刷体). Using `mathtext.fontset='custom'`, you can inject handwriting fonts.

See `references/matplotlib_custom_math_fontset.md` for detailed reference and `references/font_selection_methodology.md` for font selection workflow. See `references/graves_rnn_integration.md` for Graves RNN setup and API details. See `references/chemistry_formula_rendering.md` for chemistry formula parsing and rendering.

```python
import matplotlib as mpl
import matplotlib.font_manager as fm

# Register font with matplotlib
fm.fontManager.addfont("Kalam-Regular.ttf")

# Configure custom math fontset
mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.rm'] = 'Kalam'
mpl.rcParams['mathtext.it'] = 'Kalam'
mpl.rcParams['mathtext.bf'] = 'Kalam'
```

**Result**: ALL math symbols (∫, ∑, √, π, α, β, ∞, fractions, subscripts) render in the handwriting font style instead of Computer Modern. Greek letters (αβγ) auto-fallback through mathtext even when the font lacks them. This is the single biggest improvement to formula realism.

### Font Candidates (macOS, in preference order for MATH rendering)

| Font | Path | Math Symbols | Greek | CJK | Notes |
|------|------|-------------|-------|-----|-------|
| **Kalam** ★ | `Kalam-Regular.ttf` (project dir) | ✅ ∫∑√∏π≠∂± | ✅ via mathtext fallback | ❌ | **Best for math** — covers all math symbols + matplotlib auto-fallback for Greek |
| Bradley Hand | `/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf` | ✅ basic | ❌ αβγλθ missing | ❌ | Misses 15 chars: Greek, prime ′, arrow →, ∈ᵀℝℂ — causes □ tofu |
| Comic Sans MS | `/System/Library/Fonts/Supplemental/Comic Sans MS.ttf` | ✅ basic | ❌ | ❌ | More "cartoony" |
| Snell Roundhand | `/System/Library/Fonts/Supplemental/SnellRoundhand.ttc` | limited | ❌ | ❌ | Elegant cursive |
| Brush Script | `/System/Library/Fonts/Supplemental/Brush Script.ttf` | limited | ❌ | ❌ | Too ornate |

**⚠️ CRITICAL: Do NOT use Bradley Hand as primary math font.** It misses Greek letters (αβγλθ), prime (′), arrows (→), and ∈ᵀℝℂ, producing □ tofu in rendered formulas. Use **Kalam** instead — it covers ∫∑√∏π≠∂± natively, and matplotlib's mathtext engine auto-falls back for Greek letters (αβγ) even when the font lacks them.

**Kalam + multi-scale perturbation + PIL per-char + StudentStyle + scan effects = best formula handwriting realism (9.2–9.5/10) with 0 tofu.**

## handright Library

For TEXT rendering (not math), handright is excellent:

```python
import handright

template = handright.Template(
    background=paper_image,
    font=font,           # Kalam for English, MaShanZheng for Chinese
    line_spacing=60,
    fill=(30, 30, 60),
    perturb_x_sigma=2.0,      # horizontal wobble
    perturb_y_sigma=2.0,      # vertical wobble
    perturb_theta_sigma=0.06, # rotation (radians)
    font_size_sigma=0.4,      # size variation
)
pages = list(handright.handwrite(text, template=template))
```

**Font selection strategy** (preference order):
- CJK characters (`_has_cjk()` check) → MaShanZheng (楷书, only working CJK font) → STHeiti (fallback)
  - **NOTE**: LiuJianMaoCao (草书) is DISABLED — all simplified CJK glyphs render with zero height
- English/other → Kalam-Regular.ttf

## Fonttools Bezier Perturbation (perturb_font.py)

For font-level perturbation (modifies the .ttf file itself):

1. Load font with `fontTools.ttLib.TTFont`
2. For each glyph's bezier control points, apply spatially-correlated noise
3. Use low-res noise grid (8×8) + cubic interpolation for smooth wobble
4. Per-glyph rotation (±1.5°) and scale (±2.5%) variation
5. CJK glyphs are skipped (left unmodified)
6. Per-render seeding from formula string hash for consistency

## Pixel Perturbation (v6+ Multi-Scale, in `perturb_image()`)

After rendering a formula image, apply this pipeline (see `references/advanced_perturbation.md` for full code):

1. **Multi-scale displacement** (3 layers, key v6 improvement):
   - Large-scale wobble (block = h//4, strength ×1.4–1.6): smooth line-level drift
   - Medium-scale jitter (block = strength×2.5, strength ×1.8–2.0): per-symbol wobble
   - Small-scale noise (block = medium//2, strength ×0.8): stroke texture
   - All three summed → single displacement field → pixel remapping
2. **Pen-lift gaps**: Random rectangular erasures (2–7px wide) where strokes would lift. Only erase regions that overlap with actual strokes (mask check).
3. **Speed-dependent thinning**: Sine wave across rows → "fast zones" where 15% of stroke pixels are erased. Simulates pen moving faster horizontally.
4. **Pen pressure**: 12% of strokes thickened via `binary_dilation(iterations=1)`.
5. **Ink bleed**: GaussianBlur(radius=0.5).
6. **Micro ink dots**: 2–3 small dark circles (r=1–3px) placed at random stroke intersections. Simulates ink pooling.
7. **Paper texture**: Gaussian noise (σ=3–5).
8. **Subtle rotation**: ±1.5° random tilt.

See `references/advanced_perturbation.md` for full code and strength guidelines.

**Result**: 9.2–9.5/10 realism with full v9 pipeline (up from 7–8/10 with single-scale perturbation).

## Font Coverage & Fallback Chains (Critical)

No single handwriting font covers all needed characters. **Must build fallback chains.**

### Character Coverage Matrix

| Character | Kalam | Bradley Hand | MaShanZheng | STHeiti |
|-----------|-------|-------------|-------------|---------|
| Latin (a-z, 0-9) | ✅ | ✅ | ✅ | ✅ |
| ∫∞√∑∏π≠∂± | ✅ | ✅ | ❌ | ❌ |
| αβγλθ (Greek) | ❌* | ❌ | ❌ | ❌ |
| ′ (prime) | ❌ | ❌ | ❌ | ❌ |
| → (arrow) | ❌ | ❌ | ❌ | ❌ |
| ∈ᵀℝℂ | ❌ | ❌ | ❌ | ❌ |
| CJK (中文) | ❌ | ❌ | ✅ | ✅ |
| ± ≠ | ✅ | ✅ | ❌ | ❌ |

*Greek letters: Kalam lacks them BUT matplotlib's mathtext engine auto-falls back to its built-in math rendering for Greek. So αβγ still renders correctly when using Kalam as `mathtext.rm`.

### Solution: Per-Character Font Fallback for CJK+Math Mixed Text

When rendering Chinese text that contains math symbols (², √, ≠, λ, ±), check each character against MaShanZheng's cmap and fall back to Kalam:

```python
def _char_has_glyph(char, font_path):
    """Check if font has a glyph for the given character."""
    try:
        from fontTools.ttLib import TTFont
        font = TTFont(font_path)
        cmap = font.getBestCmap()
        result = ord(char) in cmap if cmap else False
        font.close()
        return result
    except:
        return True  # assume available on error

# In render_chinese_pil_v2(), per character:
if _has_cjk(ch) and _char_has_glyph(ch, cn_font_path):
    use_font = cn_font   # MaShanZheng
else:
    use_font = kalam_font  # Kalam fallback
```

### Solution: Font Fallback Chain for Text Rendering (handright path)

For handright text rendering (not math), split text into runs by character type:

```python
def render_text_with_fallback(text, line_spacing):
    """Split text into CJK/non-CJK runs, render each with best font."""
    runs = split_by_character_type(text)  # CJK vs non-CJK
    rendered = []
    for text_run, is_cjk in runs:
        if is_cjk:
            font = MaShanZheng  # or STHeiti fallback
        else:
            font = Kalam
        rendered.append(render_text_segment(text_run, font, line_spacing))
    return composite_horizontal(rendered)
```

### Tofu (□) Debugging Checklist

When □ appears in rendered output:

1. **Identify the missing character**: `ord(char)` → check cmap
2. **Check which font is being used**: Is it the right font for that character type?
3. **Check font file integrity**: See "Font Download Validation" below
4. **Add fallback**: Either switch font or add to fallback chain

### Matplotlib Math Fallback Behavior

When using `mathtext.fontset='custom'`:
- Characters IN the custom font → rendered with custom font
- Characters NOT in the custom font → **matplotlib silently falls back to its built-in math rendering** (DejaVu-like)
- This means Greek letters (αβγ) work even if the custom font lacks them
- But this fallback is INVISIBLE — you get a mix of handwriting + print style for missing chars
- For consistent handwriting: use Kalam (covers ∫∑√∏π≠∂±) and accept fallback for Greek

## PIL Per-Character Math Rendering (v7 — for simple formulas)

**The problem**: matplotlib's vector math rendering is inherently too clean. Even with Kalam font + perturbation, complex vector paths stay geometrically perfect at the skeleton level.

**The solution**: For simple formulas (no `\frac`, `\int`, `\lim`, `\sum`, `\sqrt`), render each character individually with PIL + Kalam, applying per-character jitter:

```python
def render_math_pil_chars(text, fontsize=28, seed=42):
    """Per-character PIL rendering with jitter."""
    rng = np.random.RandomState(seed)
    font = ImageFont.truetype("Kalam-Regular.ttf", fontsize)
    # For each character:
    #   1. Render to individual sub-image
    #   2. Rotate ±3° randomly
    #   3. Offset x/y by Normal(0, 1.5) pixels
    #   4. Paste onto canvas sequentially
```

**Formula complexity routing** (`_is_simple_formula()`):** ⚠️ MUST use regex to detect LaTeX syntax. The original marker-list approach missed `\alpha`, `\beta`, `\cdot` and subscript `_{...}`, causing LaTeX formulas to be garbled by PIL rendering. Correct implementation:
```python
import re
if re.search(r'\\[a-zA-Z]', latex_str):  # any LaTeX command
    return False
if re.search(r'[_^]\{', latex_str):       # subscripts/superscripts
    return False
return True
```
- Simple (→ PIL per-char): `E = mc²`, `a² + b² = c²`, `f(x) = x³ + 2x` — NO backslash commands, NO `_{}` syntax
- Complex (→ matplotlib): anything with `\alpha`, `\frac`, `_{t-1}`, `\int`, `\sum`, `\sqrt`

**LaTeX → plain text conversion** for simple formulas:
```python
plain = clean.replace('\\neq', '≠').replace('\\alpha', 'α')  # etc.
plain = re.sub(r'\\[a-zA-Z]+', '', plain).strip()  # remove remaining \commands
```

**⚠️ FORMULAS MUST NOT BE PERTURBED.** The v10 lesson learned the hard way:
combining perturbation (strength≥1.0) with scan effects makes formulas
completely illegible. **Formulas are rendered CLEAN (zero perturbation).
Only TEXT gets per-character jitter via render_math_pil_v2().**

**Safe perturbation targets**:
- Text only (English via handright, Chinese via render_chinese_pil_v2)
- PIL-rendered simple formulas already have natural jitter from per-char rendering — NO additional perturbation needed
- matplotlib-rendered complex formulas: CLEAN, no perturbation at all

## Rendering Quality Hierarchy (from font-manipulation)

| Approach | Realism | Formula Support | How It Works |
|----------|---------|----------------|--------------|
| **handright library** | ★★★★★ | Text only (Unicode) | Per-character position/rotation/size jitter |
| **fonttools bezier perturbation** | ★★★★☆ | Text only (Unicode) | Modifies font file glyphs directly |
| **matplotlib + pixel post-processing** | ★★☆☆☆ | Full LaTeX | Renders perfect Computer Modern, then adds noise |

**The fundamental tension**: full LaTeX (`\frac`, `\int`, `\sum`) requires matplotlib's renderer, which produces perfect typeset shapes. Post-processing can only add noise — it cannot change the underlying glyph style. For best realism, prefer Unicode text rendered through handright with a handwriting font.

### How to improve the matplotlib path
Instead of pixel perturbation, replace the rendering font:
```python
matplotlib.rcParams['mathtext.fontset'] = 'custom'
matplotlib.rcParams['mathtext.rm'] = 'Kalam'
matplotlib.rcParams['mathtext.it'] = 'Kalam:italic'
```

## Few-Shot Font Generation (from font-manipulation)

For generating a complete handwriting font from a few samples:
- **clovaai/fewshot-font-generation**: FUNIT/MX-Font — 5-10 reference glyphs → full character set
- **zi2zi-pytorch**: Chinese calligraphy style transfer (font-to-font)
- **MF-Net**: Multilingual few-shot font generation (CN+EN simultaneously)
- All require GPU training; use Colab or cloud GPU

## StudentStyle — Personalized Handwriting System (v8)

**The problem**: All rendered text looks like the same person. Real homework submissions have distinct handwriting personalities.

**The solution**: A `StudentStyle` class defines 9 personality parameters, seeded deterministically for consistency within a document:

```python
class StudentStyle:
    def __init__(self, seed=42):
        rng = np.random.RandomState(seed)
        self.slant = rng.uniform(-3, 6)          # degrees, right-lean common
        self.pressure = rng.uniform(0.4, 0.9)     # 0=light, 1=heavy
        self.speed = rng.uniform(0.2, 0.8)         # 0=slow/careful, 1=fast/sloppy
        self.neatness = rng.uniform(0.2, 0.7)      # 0=neat, 1=messy
        self.size_var = rng.uniform(0.02, 0.08)    # per-char size consistency
        self.baseline_wave = rng.uniform(0.3, 0.8) # baseline adherence
        self.connect_prob = rng.uniform(0.15, 0.5) # connected stroke probability
        self.ink_base = rng.randint(15, 45)        # ink darkness base
        self.start_heavy = rng.uniform(0.3, 0.8)   # pen pressure at start of word
        self.ink_type = rng.choice(['ballpoint', 'fountain', 'pencil'])  # v9: ink tool
```

**Usage**: Create ONE StudentStyle per document, pass it through all render functions. This ensures consistent personality across Chinese text, English text, and math formulas.

## Connected Strokes (v8 — Ligatures)

Adjacent characters get subtle connecting lines to simulate continuous pen motion.

**⚠️ CRITICAL PITFALL: Draw bridges AFTER pasting characters, NOT before.**
If you draw the bridge line first and then paste the character image, the paste overwrites the bridge. The bridge must be drawn after both characters are on the canvas.

```python
# CORRECT order:
canvas.paste(ch_img, (paste_x, paste_y))    # paste char first
# THEN draw bridge to previous char
if prev_right_edge and rng.random() < style.connect_prob:
    for bx_ in range(prev_right_edge, paste_x):
        t = (bx_ - prev_right_edge) / bridge_w
        sag = int(2 * np.sin(t * np.pi))  # Bezier-like sag
        canvas.putpixel((bx_, bridge_y + sag), min(cur, 80))

# WRONG order (bridge gets overwritten by paste):
# draw bridge first → paste char → bridge invisible ❌
```

## Pen Pressure Gradient (v8, v10 fix)

Per-character horizontal gradient: stroke start (left) is heavier/darker, stroke end (right) is lighter.

**⚠️ CRITICAL: The grayscale multiplication approach DOES NOT WORK.** Most ink pixels are at value 0 (pure black). `0 × 0.65 = 0` — the gradient has zero effect on them. The pen pressure must be applied in RGB blend space using a binary ink mask.

**Working approach** (confirmed with pixel analysis: LEFT R=61 → MID R=92 → RIGHT R=122):

```python
def apply_pen_pressure(grayscale_img, ink_rgb, paper_rgb, seed=42, style=None):
    """Convert grayscale image to RGB with ink color and alpha blending.
    
    ⚠️ v10 FIX: Use alpha blending (threshold 180) NOT hard threshold (240).
    The old `ink_mask = (arr < 240)` approach included 22.7% of pixels as "ink"
    when only 2.9% were actual text — anti-aliased edges got treated as solid ink,
    causing massive dark blocks that obscured all text.
    
    Alpha blending with threshold 180 produces clean, readable output.
    """
    arr = np.array(grayscale_img, dtype=np.float32)
    
    # Alpha blending: 180 = fully ink, 240 = fully paper
    alpha = np.clip((180 - arr) / 80.0, 0, 1)
    
    ir, ig, ib = ink_rgb
    pr, pg, pb = paper_rgb
    r_out = (pr * (1 - alpha) + ir * alpha).astype(np.uint8)
    g_out = (pg * (1 - alpha) + ig * alpha).astype(np.uint8)
    b_out = (pb * (1 - alpha) + ib * alpha).astype(np.uint8)
    return Image.fromarray(np.stack([r_out, g_out, b_out], axis=-1))
```

**Four bugs fixed across v8-v10:**
1. **Grayscale multiply on dark pixels**: `arr * 0.65` on value-0 pixels = 0 (no effect). Fix: use binary threshold `arr < 240`.
2. **Gradient on full canvas width**: Characters are centered with white padding on sides. Gradient falls on padding, not ink. Fix: map gradient to `ink_left:ink_right` range only.
3. **Gradient formula direction**: `1 - (1-base)*exp(...)` creates a VALLEY (minimum at heavy_x), not a PEAK. Fix: use `base + (1-base)*(1-xs)` for left→right linear gradient.
4. **v10 — Hard threshold 240 includes anti-aliased edges**: `ink_mask = (arr < 240)` treated 22.7% of pixels as ink when only 2.9% were actual text. Anti-aliased gray edges (180-240) became solid ink blocks. **Final fix: alpha blending** `alpha = np.clip((180 - arr) / 80.0, 0, 1)` — smooth opacity gradient, no hard cutoff, clean output.

**Verification**: At fontsize=200, zoom 2x, vision model confirms "左边确实比右边颜色更深" (left side definitely darker than right). See `references/pen_pressure_debugging.md` for the full debugging session with root cause analysis of all three bugs.

## Paper Aging Effects (v8)

Applied to paper background BEFORE text overlay. Effects:

1. **Yellowing gradient**: Edges more yellow than center (brightness ×18)
2. **Crease lines** (1–3): Diagonal or horizontal dark lines, 2–3px wide
3. **Coffee stain** with ring pattern: Heavier at edge like real coffee (radius 20–50px)
4. **Fingerprint smudge**: Elliptical darkening (optional, 50% chance)
5. **Subtle noise**: Gaussian σ=2

**Visibility note**: Paper aging is subtle by design — it shouldn't distract from the text. Vision models sometimes miss it in full-page evaluations because text dominates attention. Effects are clearly visible when viewing the paper background alone.

## Ink Color Variation (v8)

Blue-black ink instead of pure black, with per-student variation:

```python
def ink_color(seed=42, style=None):
    rng = np.random.RandomState(seed)
    r = int(style.ink_base + rng.uniform(-5, 5))
    g = int(style.ink_base + rng.uniform(-5, 5))
    b = int(style.ink_base + 20 + rng.uniform(-5, 10))  # slightly blue
    return (clamp(r, 0, 50), clamp(g, 0, 50), clamp(b, 0, 80))
```

## Enhanced Per-Character Renderers (v8)

### `render_math_pil_v2()` — For simple formulas
- Per-character scale jitter (σ=size_var, clipped 0.9–1.1)
- Baseline wave: `sin(i * 0.7) * 3.5 * style.baseline_wave + noise`
- Variable spacing: `base_spacing + Normal(0, 1.5 * neatness)`
- Pen pressure gradient per character
- Connected strokes (drawn AFTER paste)

### `render_chinese_pil_v2()` — For Chinese text
- MaShanZheng font with per-character font fallback (math symbols → Kalam)
- Gentler slant (×0.3 of English slant)
- Baseline wave: `sin(linspace(0, 2.5π, n)) * 6.0 * style.baseline_wave + Normal(0, 2.0) * neatness` — confirmed 22px range programmatically
- Variable spacing: `3 + sin(linspace(0, 3π, n)) * 3.5 * neatness + Normal(0, 1.8) * neatness` — 0-10px range
- Per-character scale jitter (σ=size_var, clipped 0.93-1.07)
- Per-character rotation jitter (±1.0° * neatness)
- **NO internal pen pressure** — applied externally in RGB conversion via `apply_pen_pressure()`

## Correction Marks (v9)

Realistic correction marks simulate a student fixing mistakes. Applied per-page with ~15% chance per text region.

Three types:
1. **Strikethrough**: Wavy line through "wrong" text (sine wave + noise), sometimes double-struck
2. **White-out**: Off-white textured rectangle over erased area, with rewrite text on top (e.g., "修正", "corr.", "*")
3. **Caret mark**: `^` symbol below the line + small correction text in margin

```python
def add_correction_marks(paper, text_regions, seed=42):
    # text_regions: list of (x, y, w, h) for each rendered text line
    # Picks 1-3 random regions, applies random correction type
```

## Formula Connected Strokes (v9)

`add_formula_connections()` adds subtle ink bridges between adjacent formula elements (e.g., ∫ connecting to x², dx connecting to next symbol).

Algorithm:
1. Find horizontal gaps between character groups (columns with no ink → columns with ink)
2. Filter gaps 3–25px wide (worth connecting)
3. For each selected gap: find ink rows on left and right edges, draw Bezier-curved thin line

**⚠️ PITFALL: `rng.randint(0, 0)` raises ValueError.** When no qualifying gaps exist, `transitions` list is empty. Must guard with early return:
```python
if not transitions:
    return Image.fromarray(result)
n_connect = rng.randint(0, min(3, len(transitions)))
```

## Multi-Page Aging Variation (v9)

`apply_paper_aging_v2(paper, page_num, total_pages, seed)` — each page gets different aging:
- **Wear factor**: `1.0 - (page_num / (total_pages-1)) * 0.3` → first pages more worn
- **Unique creases**: Different positions per page (seed + page_num * 1000)
- **Coffee stain**: 40% × wear chance, unique position per page
- **Dog-ear corner fold**: 20% × wear chance, top-right or bottom-right

## Scan Effects (v9) — ⚠️ DISABLED IN PRODUCTION

`apply_scan_effects(img, seed)` simulates document scanner artifacts.
**However, scan effects are DISABLED in the production pipeline** because
JPEG compression and sharpening destroy formula legibility. They exist
as an optional function for future use on non-formula content only.

1. **Rotation**: ±0.5° (paper not perfectly aligned)
2. **Vignette**: Edge darkening (quadratic falloff, max 15% at corners)
3. **Scan bar**: Dark strip (3–8px) at top or bottom edge
4. **Brightness/contrast jitter**: ±3% brightness, ±5% contrast
5. **JPEG compression**: Save to JPEG (quality 90–97), reload — introduces subtle block artifacts
6. **Auto-sharpen**: Sharpness ×1.0–1.15 (scanners do this)

**⚠️ NEVER apply scan effects to formula-heavy content.** Even mild JPEG
compression (quality 90) destroys the fine strokes of mathematical symbols.
The user's exact complaint: "数学公式完全难以辨认" (formulas completely
illegible) when scan effects were active.

**If scan effects are ever re-enabled**, they must:
- Only apply to pages with NO math formulas
- Use the conservative ranges above (NOT the original quality 78–92)
- Be tested on formula-heavy pages first before shipping

## Inline Formula Scaling (v11)

**The problem**: Inline formulas like `$f(x) = x^2 + 2x$` are rendered at fontsize=28 via matplotlib (DPI=200), producing images much taller than the surrounding text (fontsize=32). This creates visual inconsistency — formulas "float" above the text baseline.

**The solution**: Scale inline formula images to match text line height after rendering.

```python
# In render_document(), after rendering inline math:
target_h = int(LINE_SPACING * 0.85)
if img.height > target_h and target_h > 0:
    scale = target_h / img.height
    new_w = max(1, int(img.width * scale))
    img = img.resize((new_w, target_h), Image.LANCZOS)
comp.add_segment(img)
```

**Display math (`$$...$$`)** is NOT scaled — it stays at natural size on its own line.

**Result**: Vision analysis confirms "inline formulas are well-sized and naturally integrated into the surrounding text."

## Page Numbers (v11)

Added to `PageCompositor.save_pdf()`. Only shown for multi-page documents.

```python
if total > 1:
    page_num = i + 1
    page_draw = ImageDraw.Draw(page)
    pn_text = f"- {page_num} -"
    pn_font = ImageFont.load_default()
    pn_bbox = page_draw.textbbox((0, 0), pn_text, font=pn_font)
    pn_w = pn_bbox[2] - pn_bbox[0]
    pn_x = (PAGE_W - pn_w) // 2
    pn_y = PAGE_H - MARGIN_BOTTOM + 15
    page_draw.text((pn_x, pn_y), pn_text, font=pn_font, fill=(120, 120, 120))
```

## Multi-Page Layout (v11)

`PageCompositor` handles:
- **Line wrapping**: auto-advances to next line when content exceeds `CONTENT_RIGHT`
- **Page breaks**: auto-creates new page when content exceeds `PAGE_H - MARGIN_BOTTOM`
- **Multi-page PDF**: `save_pdf()` merges all pages with `save_all=True`
- **Per-page aging**: `apply_paper_aging_v2()` with unique seed per page
- **Page numbers**: centered at bottom, only for multi-page documents
- **Dynamic line spacing**: uses actual rendered image height, not fixed LINE_SPACING

**Command line**: `python handwrite_pipeline.py --input content.txt --output result.pdf`

### ⚠️ LINE_SPACING Overlap Bug (CRITICAL)

`LINE_SPACING = 38px` but rendered Chinese/English text images are ~99px tall (fontsize=32 + padding + baseline wave). Using fixed `LINE_SPACING` for `_advance_line()` causes **every line to overlap by ~60px**, making the output completely unreadable.

**Root cause**: `_advance_line()` was hardcoded `self.y += LINE_SPACING` regardless of actual content height.

**Fix**: Track `_current_line_max_h` per line, use it for advancement:

```python
class PageCompositor:
    def __init__(self, ...):
        # ... existing init ...
        self._current_line_max_h = 0  # track max height of current line

    def add_segment(self, img, is_display_math=False):
        sw, sh = img.size
        # Track max height for line advancement
        self._current_line_max_h = max(self._current_line_max_h, sh)
        # ... rest of add_segment ...

    def _advance_line(self):
        self._flush_line()
        gap = max(2, int(LINE_SPACING * 0.1))
        advance = self._current_line_max_h + gap if self._current_line_max_h > 0 else LINE_SPACING
        self.y += advance
        self.x = CONTENT_LEFT
        self._current_line_max_h = 0
        if self.y + LINE_SPACING > PAGE_H - MARGIN_BOTTOM:
            self._new_page()

    def _new_page(self):
        # ... existing new_page code ...
        self._current_line_max_h = 0  # reset on new page
```

**Verification**: After fix, rendered Chinese text "test" = 99px height, `_advance_line()` advances by 99+8=107px → no overlap.

## Known Limitations

See `references/grid-aligned-rendering.md` for ruled paper grid alignment technique.

1. **Math layout precision**: Custom fontset causes slight misalignment of superscripts/subscripts (but this IS a feature for handwriting realism)
2. **Formula height**: Display math may not align with text baselines
3. **Single-column layout**: No margin notes or annotations support
4. **Coffee stain visibility**: Ring pattern can be too subtle in full-page context; needs aggressive intensity (intensity * 1.2 for R channel)
5. **Long paragraphs with inline math lose characters**: The markdown parser splits text at `$...$` boundaries. When a long paragraph contains multiple inline formulas, some text segments between formulas may be silently dropped during compositing. **Primary fix**: `_is_simple_formula()` now correctly detects ALL LaTeX syntax (commands + subscripts) and routes to matplotlib. **Secondary fix**: Use short sentences (one idea per line) and display math (`$$...$$`) instead of inline math (`$...$`) for formulas. Keep Chinese text lines under ~30 characters.

## File Structure

```
handwrite-pdf-poc/
├── handwrite_pipeline.py        # Main integrated pipeline (production, 2041 lines)
├── gen_v10_demos.py             # v10 test: Chinese/English/Math/Chemistry separate demos
├── gen_math_v6.py               # v6 math test: multi-scale perturbation
├── gen_math_v7.py               # v7 math test: PIL per-char + perturbation
├── gen_math_v8.py               # v8 test: StudentStyle + connected strokes + paper aging
├── gen_v9_effects.py            # v9 test: correction marks + scan effects + multi-page aging
├── gen_3_demos.py               # 3 separate demo images (Chinese/English/Math)
├── handwrite_math_renderer.py   # Standalone math renderer + comparison generator
├── handwrite_math.py            # Original PoC (two approaches)
├── perturb_font.py              # Fonttools bezier perturbation engine
├── font_variant_pool.py         # Font variant pool for per-render glyph variation
├── generate_synthetic_symbols.py # 30 synthetic handwritten math symbols
├── Kalam-Regular.ttf            # Original Kalam font (English handwriting)
├── Kalam-Handwrite.ttf          # Pre-perturbed Kalam font
├── fonts/
│   ├── MaShanZheng-Regular.ttf  # ★ Chinese handwriting font (楷书, primary CJK)
│   ├── LiuJianMaoCao-Regular.ttf # Chinese handwriting font (草书, DISABLED — zero-height simplified CJK glyphs)
│   └── NotoSansMath-Regular.ttf # ★ Math symbol font (comprehensive coverage)
├── libs/
│   ├── pytorch-handwriting-synthesis-toolkit/  # Graves RNN model + toolkit
│   │   └── checkpoints/Epoch_56/              # Pre-trained model (model.pt + meta.json)
│   └── Handwriting-Transformers/               # Style transfer (future use)
├── mathwriting_glyphs/          # 22 real symbols from Google MathWriting dataset
├── symbol_glyphs/               # 30 synthetic symbols (∫∑∏√∂∞+Greek+operators)
├── .font_cache/                 # Cached font variants (auto-generated)
└── output/
    ├── demo_v10_chinese.png     # Chinese-only demo
    ├── demo_v10_english.png     # English demo (Graves RNN + PIL hybrid)
    ├── demo_v10_math.png        # Math formulas demo
    ├── demo_v10_chemistry.png   # Chemistry formulas demo
    ├── demo_v10_science.pdf     # Science comprehensive (chemistry + physics)
    └── ... (previous demo outputs)
```

## Pitfalls

0. **⚠️ LiuJianMaoCao ALL simplified CJK glyphs have ZERO height (CRITICAL — 2026-07)** — Every simplified Chinese character renders with bbox height=0 (completely invisible) when using LiuJianMaoCao-Regular.ttf. fontTools cmap says the glyph exists, but PIL renders it as zero-height. `_char_has_glyph()` must check BOTH cmap AND actual render height. If fontTools throws exception (corrupted font tables), must return False, not True. **FIX: Disable LiuJianMaoCao entirely for CJK rendering, use MaShanZheng only.**
0b. **⚠️ `_is_simple_formula` must detect ALL LaTeX syntax (CRITICAL — 2026-07)** — The original check only looked for `\frac`, `\int`, `\sum` etc. Formulas with `\alpha`, `\beta`, `_{t-1}` were considered "simple" and sent to PIL per-char renderer, which output raw LaTeX syntax as garbled text like `[s-t]=a[x-t]`. **FIX: Also check `re.search(r'\\[a-zA-Z]', s)` and `re.search(r'[_^]\{', s)`.**
0c. **⚠️ Layout spacing: heading + para_break stacking creates massive gaps (CRITICAL — 2026-07)** — `add_newline()` before AND after headings + `para_break` using full `_advance_line()` stacks up to 5-6 lines of blank space between sections. **FIX: No add_newline() around headings. para_break uses 0.3×LINE_SPACING. _advance_line gap=0.15×LINE_SPACING.** User is extremely sensitive to spacing — "太烂了" and "垃圾死了" are direct complaints.
1. **Don't forget `fm.fontManager.addfont()`**
1. **⚠️ `_char_has_glyph()` must verify renderability, not just cmap (CRITICAL)** — A character can exist in a font's cmap but render with zero height (invisible). The original implementation only checked `ord(char) in cmap` and returned `True` on exception. **FIX**: (a) After cmap check, actually render the char with PIL and verify `bbox[3] - bbox[1] > 0`; (b) on exception from fontTools, return `False` (not `True`) — a corrupted font should not be trusted. This single bug caused ~50% of Chinese characters to silently disappear.
2. **⚠️ `_is_simple_formula()` must detect ALL LaTeX syntax (CRITICAL)** — The original only checked for `\frac`, `\int`, `\sum`, etc. Formulas containing `\alpha`, `\beta`, `\cdot`, or subscript syntax `_{...}` were classified as "simple" and routed to PIL per-char rendering, which output raw LaTeX as literal text (e.g., `$S_t = \alpha X_t$` rendered as `[s-t]=a[x-t]`). **FIX**: Add regex checks: `re.search(r'\\[a-zA-Z]', s)` for any LaTeX command, and `re.search(r'[_^]\{', s)` for subscripts/superscripts. Either → route to matplotlib. Only truly plain Unicode (like `E = mc²`, `a² + b² = c²`) should use PIL.
3. **⚠️ `add_segment()` image scaling can produce zero dimensions (CRITICAL)** — When `max_w` is 0 or very small, `int(sw * scale)` truncates to 0 → `ValueError: height and width must be > 0`. **FIX**: Guard with `if sw > max_w and max_w > 0` and use `max(1, int(sw * scale))` for both dimensions.
4. **Don't forget `fm.fontManager.addfont()`** — matplotlib won't find system fonts automatically for the custom fontset. Must register before setting `mathtext.fontset`.
2. **PIL anchor='mt' doesn't work with multiline text** — use manual positioning with `getbbox()` instead.
3. **`mathtext.fontset = 'custom'` requires all three** (`rm`, `it`, `bf`) to be set, even if to the same font.
4. **Pixel perturbation loop is slow** for large images (`for yi, xi in zip(ys, xs)` iterates every dark pixel). Consider vectorizing or limiting resolution.
5. **matplotlib `cm` fontset name** — setting `mathtext.rm = 'cm'` doesn't work; use `mathtext.fontset = 'cm'` instead.
6. **PDF preview**: Use PyMuPDF (`fitz`) to convert PDF pages to PNG for Vision analysis.
7. **⚠️ Silent font corruption (CRITICAL)**: curl downloads from GitHub raw URLs can produce truncated TTF files (~1MB instead of ~6MB for CJK fonts). PIL loads them without error but ALL glyphs render invisible (height=0). Always download with Python `urllib` + User-Agent header, then validate: (a) file size >1MB for CJK, (b) `TTFont.getBestCmap()` succeeds, (c) `font.getbbox("你")` has non-zero height, (d) `draw.text()` produces visible pixels. See `references/font_selection_methodology.md` for full validation script.
8. **⚠️ Tofu from font coverage gaps (CRITICAL)**: Bradley Hand misses 15 chars (Greek, prime, arrows, ∈ᵀℝℂ). MaShanZheng misses 19 math symbols. Using these as primary fonts WITHOUT fallback causes □ tofu. **Solution**: Use Kalam for math rendering (covers math symbols + mathtext handles Greek), build fallback chains for text. Always verify character coverage with `fontTools.ttLib.TTFont.getBestCmap()` before committing to a font.
9. **Don't use Bradley Hand for math** — despite looking more "handwritten" than Kalam, it produces tofu for Greek letters and common math symbols. Kalam is the correct choice.
10. **Vision model handwriting scores are inconsistent** — the same quality image can score 5.5/10 one evaluation and 8.5/10 the next. Complete page demos (text + math mixed) consistently score higher (8.5–9.2) than isolated formula images (5.5–8.5) because the full context creates a more convincing impression. When benchmarking, always evaluate full-page demos, not isolated formula strips.
11. **⚠️ Don't perturb formulas AT ALL (CRITICAL)** — v10 lesson: even strength=1.0 perturbation makes complex formulas (integrals, limits, fractions) unreadable when combined with other effects. PIL per-char rendering already has natural jitter (rotation ±3°, position σ=1.5) which is sufficient. matplotlib formulas should be rendered completely clean. **Zero perturbation on all formula paths.**
12. **⚠️ Connected strokes: draw AFTER paste (CRITICAL)** — If you draw bridge lines between characters before pasting the character images, the paste overwrites the bridges and they become invisible. Always paste characters first, then draw connecting strokes. See "Connected Strokes" section above.
13. **Vision model score inconsistency** — The same image can score 5.5/10 one evaluation and 9.5/10 the next. Full-page demos consistently score higher (8.5–9.5) than isolated formula images (5.5–8.5). When benchmarking, always evaluate full-page demos and average multiple evaluations. Don't over-index on a single score.
14. **Paper aging effects need amplification** — Yellowing (×18 brightness), crease lines (8–18px darken), and coffee stains (intensity ×1.2 for R) must be aggressive to survive text overlay. Subtle effects get lost under handwritten text. Test by rendering paper background alone to verify visibility.
15. **⚠️ Python environment on macOS** — The project requires specific Python installs. `matplotlib`/`PIL`/`scipy` are in Homebrew (`/opt/homebrew/bin/python3`). `handright` is in Anaconda (`/opt/anaconda3/bin/python3`). `gen_3_demos.py` and pipeline code that uses `handright` (via `render_text_with_fallback`) MUST run under anaconda Python. Install scipy to homebrew with `pip3 install --break-system-packages scipy`. If you get `ModuleNotFoundError: No module named 'handright'`, switch to `/opt/anaconda3/bin/python3`.
16. **`add_formula_connections()` empty transitions bug** — When the formula image has no qualifying horizontal gaps (e.g., single-character formulas or tightly spaced), the `transitions` list is empty and `rng.randint(0, 0)` raises `ValueError: high <= 0`. Must guard with `if not transitions: return Image.fromarray(result)` before the randint call.
17. **Correction marks text_regions alignment** — The `text_regions` parameter must track absolute coordinates on the paper canvas (not relative to the text image). When pasting text at `(paste_x, paste_y)`, offset each region by `paste_x + rx, paste_y + ry`.
18. **⚠️ MaShanZheng missing math symbols (CRITICAL)** — MaShanZheng does NOT support `²³√≠±λ` and other math symbols. When mixed into Chinese text (e.g., "若 a ≠ 0" or "x = (-b ± √(b²-4ac))/2a"), these render as □ tofu. **Fix**: In `render_chinese_pil_v2()`, check each character against MaShanZheng's cmap using `fontTools.ttLib.TTFont.getBestCmap()`. If `ord(char) not in cmap`, use Kalam font for that character instead. This requires per-character font selection, not per-text-block.
19. **⚠️ Perturbation + scan effects destroy formula legibility (CRITICAL — LESSON LEARNED THE HARD WAY)** — The user was extremely frustrated when formulas were "完全难以辨认" (completely illegible). Root cause: combining pixel perturbation with scan effects (JPEG compression + sharpening) destroyed all fine detail in mathematical symbols. **SOLUTION: Formulas must be rendered ZERO perturbation. Clean matplotlib/PIL output only.** Scan effects are DISABLED in production. The ONLY effects allowed on formulas are: (a) optional formula connection lines, (b) ink color tinting. Everything else (perturbation, JPEG, sharpening, rotation) is FORBIDDEN on formula images. TEXT can still use per-character jitter and light perturbation.
20. **⚠️ Test categories SEPARATELY before combining (CRITICAL)** — User has STRONG preference for testing Chinese-only, English-only, and math-only as separate images BEFORE generating any combined output. If any category has □ tofu or garbled output, STOP and fix before proceeding. Showing broken combined output causes severe user frustration. The testing workflow MUST be: (1) test_cn_only.png → verify no □, (2) test_en_only.png → verify no □, (3) test_math_only.png → verify no □, (4) THEN combine.
21. **⚠️ Pen pressure must be applied in RGB space, NOT inside render_chinese_pil_v2 (CRITICAL)** — `render_chinese_pil_v2()` returns a grayscale 'L' image. Pen pressure applied as grayscale multiplication inside this function has NO EFFECT because ink pixels are at value 0. The pen pressure gradient MUST be applied during the grayscale→RGB conversion step (the `apply_pen_pressure()` function). Do NOT add pen pressure logic inside `render_chinese_pil_v2()`. Keep the renderer clean (position jitter, rotation, baseline wave, spacing only), and apply pen pressure externally when converting to RGB for display.
22. **⚠️ Graves RNN output too wide (CRITICAL)** — The Graves RNN model generates stroke coordinates that can span 6000-11000px wide. MUST scale output to fit page content width (~1100px at 150 DPI) before compositing. Use `canvas.resize((max_width, int(canvas.height * scale)), Image.LANCZOS)`.
23. **⚠️ Graves RNN charset limitation** — The pretrained model only supports ASCII (79 chars). Characters like `^`, `{`, `}`, `~`, backtick are NOT in the charset. Text containing these characters will fail `_text_is_ascii()` check and fall back to PIL rendering. This is correct behavior — don't try to force Graves RNN on non-ASCII text.
24. **⚠️ git push timeout for large repos** — When the git pack is large (>10MB), `git push` may timeout repeatedly. Workaround: use `mcp_github_create_or_update_file` or `mcp_github_push_files` to push files via GitHub API instead. The MCP tools use a different auth mechanism that works reliably. For very large files (>75KB), the API may also fail — push smaller files first, then ask user to push the large file manually.
25. **⚠️ `apply_pen_pressure` hard threshold causes dark blocks (CRITICAL)** — The old approach `ink_mask = (arr < 240).astype(np.float32)` included 22.7% of pixels as "ink" when only 2.9% were actual text. Anti-aliased edges (gray values 180-240) were treated as solid ink, causing massive dark rectangular blocks that obscured all text. Vision model reported "black rectangles covering text" even though numpy showed zero pure-black pixels. **FIX**: Use alpha blending with threshold 180: `alpha = np.clip((180 - arr) / 80.0, 0, 1)`. This smoothly maps gray values to opacity — pure white (255) → 0% ink, mid-gray (200) → 25% ink, dark (100) → 100% ink. Produces clean, readable output. Always verify with `np.all(region < 10, axis=2).sum()` — if >1% of text region pixels are "black", the threshold is wrong.
26. **⚠️ Font variant pool: CJK font perturbation is slow** — Generating 5 variants of MaShanZheng (7012 glyphs) takes ~30 seconds. Cache to `.font_cache/` directory. Use `hashlib.md5(f"{cn_font}:{en_font}").hexdigest()[:8]` as cache key.
26. **⚠️ Vision model HALLUCINATES defects in handwritten images (CRITICAL)** — When evaluating handwritten images, the vision model may report "black rectangles covering text", "redacted text", "deep gray blocks", or "completely obscured lines" when the image has NO such defects. Verified in v10 session: model reported 6/10 lines "covered by dark gray rectangles" while numpy pixel analysis showed ZERO black pixels in the text region (all-0 check: 0 out of 109725 pixels). Root cause: the model pattern-matches handwriting rendering artifacts (ink pressure gradients, per-char jitter shadows) as intentional redaction blocks from its training data. **ALWAYS verify with pixel-level analysis BEFORE believing the vision model's defect reports:**
```python
arr = np.array(img)
text_region = arr[y1:y2, x1:x2]
black_pixels = np.all(text_region < 10, axis=2)
print(f"Black pixels: {black_pixels.sum()}/{black_pixels.size}")
```
If black pixel percentage is <1%, the image is FINE — the vision model is hallucinating. Trust numpy over the vision model for defect detection. Do NOT "fix" images based solely on vision model claims of black rectangles.
30. **⚠️ fontTools CJK glyph names must be STRINGS, not numpy int64 (CRITICAL)** — When sampling CJK characters for font variant perturbation, `target_codepoints.add(c)` adds the integer codepoint (e.g., `np.int64(19968)`). But `glyf[glyph_name]` expects a STRING glyph name from the cmap. Using an integer causes `KeyError: np.int64(24577)`. **FIX**: Always use `target_codepoints.add(cmap[c])` to store the glyph NAME, not the codepoint. This applies to any codepoint range (ASCII, CJK, math symbols). The ASCII loop already does this correctly (`cmap[c]`), but the CJK sampling loop must too.
31. **⚠️ `add_segment()` zero-dimension crash (CRITICAL)** — `img.resize((int(sw * scale), int(sh * scale)))` raises `ValueError: height and width must be > 0` when `max_w` is 0 or very small. This happens when `self.x` equals `CONTENT_RIGHT` (line is exactly full). **FIX**: `if sw > max_w and max_w > 0:` guard + `max(1, int(...))` for both dimensions:
```python
if sw > max_w and max_w > 0:
    scale = max_w / sw
    img = img.resize((max(1, int(sw * scale)), max(1, int(sh * scale))), Image.LANCZOS)
```
28. **⚠️ Subagent parameter name mismatch (delegate_task pitfall)** — When using `delegate_task` for parallel code changes, the subagent may generate calling code with wrong parameter names (e.g., `font_size=40` instead of `fontsize=40`). The subagent doesn't see the function signature at the same time as the caller. **FIX**: After subagent completes, verify all function call parameter names match the actual signatures. Search for the function name in the modified code and check each call site. The `except TypeError` pattern is a band-aid — fix the parameter name instead.
29. **⚠️ Network timeouts in Macau/China (environmental)** — Downloads from HuggingFace (huggingface.co), Google Drive, and some GitHub raw files consistently time out (>300s). GitHub API (api.github.com) and PyPI work fine. When downloading models/datasets, plan for potential timeouts and have fallback strategies (local cache, alternative mirrors, user-initiated download).
30. **⚠️ LiuJianMaoCao ALL simplified CJK glyphs render zero height (CRITICAL)** — LiuJianMaoCao-Regular.ttf has simplified Chinese characters in its cmap, but PIL renders ALL of them with `bbox height=0` (completely invisible). Verified: every CJK character (指,数,加,权,递,推,公,式,平,滑,值...) returns `bbox=(0, 29, 33, 29)` with `height=0`. fontTools may also throw `AssertionError` on cmap decompile. **FIX**: (a) DISABLE LiuJianMaoCao entirely in `_get_best_font_for_char()` — use MaShanZheng only for CJK. (b) Change `_char_has_glyph()` exception handler from `return True` to `return False`. (c) Add renderability check: render the char with PIL and verify `bbox[3]-bbox[1] > 0` before trusting the cmap. The mixed font (楷书/草书) technique documented in the skill is BROKEN until a working 草书 font replaces LiuJianMaoCao.
31. **⚠️ `_is_simple_formula` must detect ALL LaTeX syntax (CRITICAL)** — The original function only checked for `\frac`, `\int`, `\sum`, etc. It did NOT check for `\alpha`, `\beta`, `\cdot` or subscript syntax `_{...}`. This caused formulas like `$S_t = \alpha X_t + (1-\alpha) S_{t-1}$` to be classified as "simple" and routed through PIL per-char rendering, producing garbled output like `[s-t]=a[x-t]+(1-a)[s-t-1]`. **FIX**: Replace the marker list with regex: `re.search(r'\\[a-zA-Z]', latex_str)` catches any LaTeX command, and `re.search(r'[_^]\{', latex_str)` catches subscripts/superscripts. Either match → complex → use matplotlib path.
32. **⚠️ Ruled paper grid alignment (CRITICAL for lined paper)** — When rendering on lined paper (横线纸), content MUST snap to grid lines. `_advance_line()` must advance by exactly `LINE_SPACING` (not by content height + gap). `TEXT_FONT_SIZE` must be small enough that rendered text height < `LINE_SPACING` (e.g., 22px font → ~34px rendered < 38px grid). Display math formulas must be capped at `1.8×LINE_SPACING` height. Failure to align causes text drifting across grid lines and visual chaos. **Key parameters**: `LINE_SPACING=38`, `TEXT_FONT_SIZE=22`, `pad=int(fontsize*0.6)`, baseline wave amplitude `4.0` (not 12.0).
33. **⚠️ Don't optimize the wrong metric** — User never asked to compress to 1 page. Compressing layout to fit a self-imposed target caused overlapping text. Listen to the actual requirement ("fix spacing") not an imagined one ("make it shorter"). When user says "排版差劲" they mean spacing issues, not page count.
33. **⚠️ Regex escaping in `_is_simple_formula()` is fragile (CRITICAL)** — Python raw strings with backslashes are a common source of bugs. The correct regex to match a LaTeX command like `\alpha` is `r'\\[a-zA-Z]'` (2 backslashes in source = 1 literal backslash in regex). Using `r'\\\\[a-zA-Z]'` (4 backslashes) creates a regex that matches `\\` + letter (TWO backslashes), which never matches actual LaTeX input. This causes ALL LaTeX formulas to be misclassified as "simple" and rendered as garbled PIL text. **When editing regex patterns in this file, always verify with**: `re.search(r'your_pattern', chr(92) + 'alpha')` — must return a match. Also check `r'[_^]\{'` for subscript detection.

34. **⚠️ Content authoring for compact layout (USER PREFERENCE)** — The user strongly prefers compact, dense handwritten notes. When generating content for the pipeline: (a) Use short sentences (one idea per line, under ~30 Chinese characters); (b) Prefer display math (`$$...$$`) over inline math (`$...$`) — inline formulas get scaled down to match text height and look cramped; (c) Avoid empty lines between paragraphs — they add unnecessary vertical gaps; (d) Keep content under 20 lines per page to avoid forced page breaks mid-sentence. The user's exact complaint about sparse layout: "莫名其妙空出两三行，垃圾死了" (mysterious 2-3 line gaps, terrible). **Never add extra spacing "for breathing room" — the user wants dense notes, not airy layouts.**

36. **⚠️ Grid alignment: _advance_line MUST snap to LINE_SPACING (CRITICAL — 2026-07)** — The paper has ruled lines at `LINE_SPACING=38px` intervals. If `_advance_line()` uses content height (e.g., `self._current_line_max_h + gap`), text lines land BETWEEN grid lines — each line spans ~2.7 grid cells, looking completely unanchored. **FIX**: `_advance_line` must use fixed `self.y += LINE_SPACING`. This also requires `TEXT_FONT_SIZE=22` (not 32) so rendered text fits within one 38px grid cell. With fontsize=22 and `pad=int(fontsize*0.6)`, rendered Chinese text is ~30px tall — fits in 38px with room to spare. Display math formulas must also be capped: `max_display_h = int(LINE_SPACING * 1.8)`. Baseline wave amplitude should be reduced to `4.0` (from `12.0`) to prevent vertical bleed. **User complaint**: "又重叠在一起了，你的格子线判定有问题吗" (overlapping again, is your grid line logic broken?).

37. **⚠️ Display math formula height overflow (CRITICAL — 2026-07)** — Display formulas rendered via matplotlib can be taller than 2 grid lines (76px), causing overlap with the next text line. **FIX**: After rendering display math, cap height to `LINE_SPACING * 1.8`:
```python
max_display_h = int(LINE_SPACING * 1.8)
if img.height > max_display_h and max_display_h > 0:
    scale = max_display_h / img.height
    new_w = max(1, int(img.width * scale))
    img = img.resize((new_w, max_display_h), Image.LANCZOS)
``` — The original "Known Limitations" section mentioned "Long paragraphs with inline math lose characters". This is still true but the recommended workaround has changed: the primary fix is now `_is_simple_formula()` correctly detecting LaTeX (not content restructuring). Short sentences are still recommended for layout density, not for character loss prevention.

## Mixed Font Rendering (楷书/草书 Per-Character — DISABLED)

**⚠️ CRITICAL: LiuJianMaoCao (草书) is DISABLED for simplified Chinese rendering.**

**Original design**: Randomly switch between MaShanZheng (楷书) and LiuJianMaoCao (草书) per character for genuine structural variation.

**Why disabled**: LiuJianMaoCao's simplified CJK glyphs are ALL broken — PIL renders them with zero height (`bbox=(0, 29, 33, 29)` → `height=0`, `dark_px=0`). The font's cmap claims glyphs exist, but they produce invisible output. This affects EVERY simplified Chinese character tested (100+ characters, all zero height). The font file may only contain traditional Chinese glyphs or has corrupted simplified Chinese outlines.

**Impact if not disabled**: ~50% of Chinese characters randomly disappear from rendered output. The user's exact complaint: "太烂了，可读性为0" (terrible, readability is 0).

**Current implementation**: MaShanZheng only for CJK:
```python
def _get_best_font_for_char(char, size=28, _char_seed=None):
    # CJK chars → MaShanZheng only
    # NOTE: LiuJianMaoCao is DISABLED — all simplified CJK glyphs render with zero height
    if _has_cjk(char):
        if os.path.exists(cn_font_path) and _char_has_glyph(char, cn_font_path):
            return ImageFont.truetype(cn_font_path, size)
```

**Future re-enable checklist**: Before re-enabling LiuJianMaoCao, MUST verify:
1. `textbbox()` returns non-zero height for at least 10 common simplified CJK chars
2. Actual rendered pixel count > 0 for test characters
3. Test with `np.array(img)` dark pixel check, not just fontTools cmap

**⚠️ PITFALL: `_char_has_glyph()` trusting cmap blindly** — fontTools cmap says "glyph exists" but PIL renders it as zero height. The function MUST verify actual renderability:

```python
def _char_has_glyph(char, font_path):
    """Check cmap AND verify the glyph renders with non-zero height."""
    try:
        from fontTools.ttLib import TTFont
        font = TTFont(font_path)
        cmap = font.getBestCmap()
        if not cmap or ord(char) not in cmap:
            font.close()
            return False
        font.close()
        # Verify the glyph actually renders
        test_font = ImageFont.truetype(font_path, 32)
        bbox = _test_draw.textbbox((0, 0), char, font=test_font)
        return (bbox[3] - bbox[1]) > 0
    except:
        return False  # if fontTools can't read the font, don't trust it
```

**⚠️ PITFALL: `_char_has_glyph()` exception fallback was `return True`** — If fontTools throws (corrupted font tables), the old code assumed "glyph exists", causing invisible characters. Changed to `return False`. Any font that crashes fontTools is untrustworthy.

## Font Variant Pool (Per-Render Glyph Variation)

**The problem**: handright's perturbation only varies position/rotation/size. The same character's glyph shape is IDENTICAL every time — "数" rendered twice looks the same (just shifted). Real handwriting has different stroke shapes each time.

**The solution**: Pre-generate N perturbed font variants with `fonttools`, then randomly pick one per CHARACTER (not per text segment). Each character at a different position gets a genuinely different glyph shape.

### Implementation (v11 — Integrated into Main Pipeline)

The variant pool is now integrated directly into `handwrite_pipeline.py` (not a separate file).

**Key components:**
1. `generate_font_variant(source_path, variant_seed, amplitude)` — creates one perturbed font file
2. `get_font_variants(source_path, n_variants=8, amplitude=12.0)` — returns list of variant paths (cached)
3. `_pick_variant_font(source_path, char_seed)` — deterministic variant selection per character
4. `_perturb_glyph_bezier_fast(glyph, shared_noise_x, shared_noise_y, rng, amplitude)` — fast perturbation using pre-generated noise grid

### Performance Optimization (Critical)

**Problem**: Per-glyph noise generation is slow (~42ms/glyph × 1027 glyphs = 44s per font).

**Solutions:**
1. **Only perturb used glyphs** — ASCII printable (32-126) + common math/symbol codepoints (~125 glyphs, not all 1027)
2. **Shared noise grid** — pre-generate one 512×512 noise grid, sample from it per glyph with random offset
3. **Fast perturbation function** — `_perturb_glyph_bezier_fast()` uses shared grid instead of per-glyph noise

**Result**: Kalam variants: 9 variants in 1.8s (was ~45s). MaShanZheng: 9 variants in 35.8s (one-time, cached).

**⚠️ PITFALL: Two variant pool systems coexist** — There's an older `font_variant_pool.py` module (used by `_setup_math_font()` and `_variant_pool` global) AND the newer in-pipeline implementation (`get_font_variants()` / `_pick_variant_font()`). The old system is used by `render_text_with_fallback()` via `_variant_pool.get()`. The new system is used by `render_math_pil_v2()` and `render_chinese_pil_v2()`. They use different caches (`.font_cache/` vs `/tmp/hw_font_variants_*`). This doesn't cause bugs but is confusing — consider consolidating.

**⚠️ PITFALL: Amplitude > 15 causes glyph fragmentation** — At amplitude=18, bezier perturbation breaks glyph outlines into "vertical bars" / "pixelated" shapes. Vision model described output as "fragmented" and "digital appearance". Stick with amplitude=10-12 for subtle natural variation. Test with `debug_hello_variants.png` (5 instances of "hello" side by side) to verify differences are visible but not destructive.

```python
# Per-character variant selection
char_seed = doc_seed * 10007 + char_position * 137 + ord(char) * 31
variant_path = _pick_variant_font(base_font_path, char_seed)
font = ImageFont.truetype(variant_path, fontsize)
```

### Spatially-Correlated Noise (Not Random Per-Point)

**Critical**: Independent random per-point noise creates jagged edges. Use spatially-correlated noise via low-res grid + bicubic interpolation — neighboring control points move together for smooth, natural wobble.

```python
def _generate_smooth_noise_2d(width, height, amplitude=2.0, grid_size=6, rng=None):
    grid_x = rng.randn(grid_size, grid_size) * amplitude
    grid_y = rng.randn(grid_size, grid_size) * amplitude
    noise_x = scipy.ndimage.zoom(grid_x, (height/grid_size, width/grid_size), order=3)
    noise_y = scipy.ndimage.zoom(grid_y, (height/grid_size, width/grid_size), order=3)
    return noise_x, noise_y
```

### Glyph Perturbation Strategy

- **On-curve points** (flag & 1): 50% amplitude — maintains shape stability
- **Off-curve control points**: 100% amplitude — visible wobble
- **Per-glyph amplitude variation**: `amplitude * rng.uniform(0.6, 1.4)` for naturalness
- **Amplitude = 12.0** for subtle variation (recommended); **18.0** for strong (may cause fragmentation)

### Integration with renderers

Both `render_math_pil_v2()` and `render_chinese_pil_v2()` now use variant fonts:
1. For each character, compute `char_seed = seed * 10007 + idx * 137 + ord(ch) * 31`
2. Call `_pick_variant_font(base_font_path, char_seed)` to get variant path
3. Load variant as `ImageFont.truetype(variant_path, fontsize)`
4. Measure and render with the variant font

**Affine distortion is applied ON TOP of variant font** (scale ±6%, shear ±4%, rotation ±1.5°).

**Result**: Vision analysis confirms: "the letter shapes are genuinely different across instances" — 'l' varies in height/stroke weight, 'o' varies in roundness/size.

See `references/font_variant_pool.md` for full implementation details.

## Formula Compositing (Transparent Background)

**The problem**: matplotlib renders formulas with white/transparent background. When pasted onto cream-colored paper (252, 249, 235), white rectangles are visible — "穿帮" (caught out).

**The solution**: RGBA transparent compositing.

```python
# Render formula with transparent background
fig.savefig('/tmp/f.png', transparent=True)
img = Image.open('/tmp/f.png').convert('RGBA')

# Composite onto paper: transparent pixels show paper, opaque show formula
bg_strip = Image.new('RGB', img.size, PAPER_COLOR)
composite = Image.alpha_composite(bg_strip.convert('RGBA'), img).convert('RGB')
paper.paste(composite, (x, y))
```

**Pitfall**: handright adds noise to ALL pixels of the background, shifting values below 250. When using cream-colored paper as handright background, the entire image becomes "content" (no white pixels above 250 threshold). **Fix**: Use white (255,255,255) background for handright, then replace white pixels with paper color after compositing.

## Testing Methodology (MANDATORY WORKFLOW)

**⚠️ User has STRONG preference — violating this causes severe frustration.**

**Rule: Test Chinese, English, and formulas as SEPARATE images FIRST. Do NOT show combined output until each category passes verification.**

**Why**: Mixed output makes it impossible to evaluate each rendering path independently. Showing garbled combined output (□ tofu, illegible formulas) destroys user trust. The user explicitly said "先分中文，英文，公式，分成三个部分解决" (solve Chinese, English, formulas separately first).

**Workflow** (MUST follow in this order):
1. `test_cn_only.png` — Chinese text with math symbols mixed in → **verify no □**
2. `test_en_only.png` — English text → **verify no □**
3. `test_math_only.png` — Math formulas, one per line → **verify all legible**
4. **Only if all three pass** → generate combined output (PDF)
5. Show combined output to user for feedback

**Additional formula verification**: After generating, visually inspect rendered formulas with vision_analyze. Check that:
- Greek letters (α, β) appear as symbols, not as literal text "alpha"/"beta"
- Subscripts (S_t, X_{t-1}) render as proper subscript positioning, not `[s-t]`
- LaTeX commands are NOT visible in the output (no backslashes, braces)
- If any formula looks wrong, check `_is_simple_formula()` — it may be routing LaTeX to PIL

**Verification method**: Use `fontTools.ttLib.TTFont.getBestCmap()` to check character coverage BEFORE rendering. Report any missing characters proactively.

## Graves RNN Handwriting Synthesis (v10)

**New rendering path** for English text using stroke-based handwriting generation from `pytorch-handwriting-synthesis-toolkit`.

### Integration Pattern

```python
_graves_synthesizer = None

def _load_graves_model():
    """Lazy-load Graves RNN model."""
    global _graves_synthesizer
    if _graves_synthesizer is not None:
        return _graves_synthesizer
    import torch
    from handwriting_synthesis.sampling import HandwritingSynthesizer
    model_dir = "libs/pytorch-handwriting-synthesis-toolkit/checkpoints/Epoch_56"
    device = torch.device("cpu")
    _graves_synthesizer = HandwritingSynthesizer.load(model_dir, device, bias=0)
    return _graves_synthesizer

def render_english_graves(text, style=None, thickness=5):
    """Render ASCII English text via Graves RNN. Returns PIL Image or None."""
    if not _text_is_ascii(text) or len(text.strip()) < 25:
        return None  # Too short or non-ASCII → fall back to PIL

    synthesizer = _load_graves_model()
    c = synthesizer._encode_text(text + " ")  # space is sentinel
    sampled = synthesizer.model.sample_means(context=c, steps=1500, stochastic=True)
    sampled = sampled.cpu() * synthesizer.sd + synthesizer.mu

    # SVG rendering (round line caps) → cairosvg → PNG
    from handwriting_synthesis.utils import create_strokes_svg
    dwg = create_strokes_svg(sampled, '/tmp/_graves.svg', lines=True, thickness=thickness)
    if dwg: dwg.save()

    import cairosvg
    cairosvg.svg2png(url='/tmp/_graves.svg', write_to='/tmp/_graves.png', dpi=150)
    canvas = Image.open('/tmp/_graves.png').convert('L')

    # Scale to fit page width
    if canvas.width > 1100:
        scale = 1100 / canvas.width
        canvas = canvas.resize((1100, int(canvas.height * scale)), Image.LANCZOS)
    # ... crop, apply ink color ...
```

### Graves RNN Quality Characteristics

- **Charset**: ASCII only (79 chars: `a-zA-Z0-9 !"#$%&'()*+,-./:;<=>?@[\]^_` — NO `^`, `{`, `}`, `~`)
- **Best for**: Text >25 chars (short text looks unnatural, 3-4/10)
- **Long sentences**: 8/10 realism (e.g., "Problem 3: Solve the differential equation dy/dx + P(x)y = Q(x).")
- **Short text**: Falls back to PIL per-char rendering (`render_math_pil_v2`)
- **Model**: Pre-trained on IAM-OnDB (English handwriting dataset)
- **Output**: Very wide coordinates (6000-11000px) — MUST scale to fit page width (~1100px)
- **SVG rendering**: Use toolkit's `create_strokes_svg()` for round line caps (better than PIL `draw.line()`)
- **Dependencies**: `torch`, `h5py`, `svgwrite`, `cairosvg` (optional, for SVG→PNG)

### Hybrid Rendering Strategy

For English text, use Graves RNN for long lines and PIL for short/mixed:

```python
def render_text_with_fallback(text, style=None):
    # Graves RNN for pure ASCII English >25 chars
    if _text_is_ascii(text) and not _has_cjk(text):
        graves_img = render_english_graves(text, style=style)
        if graves_img is not None:
            return graves_img
    # Fallback: PIL per-char rendering for short/mixed text
    # ...
```

**⚠️ PITFALL: Mixing Graves RNN (cursive) with PIL (printed) creates visual inconsistency.** Vision model rated mixed output 6/10 vs 8/10 for pure Graves RNN. For consistent style, either use all-Graves or all-PIL for a document.

## Chemistry Formula Rendering (v10)

New rendering path for chemical formulas with proper subscripts/superscripts.

### `_parse_chemistry(formula)` — Chemistry Formula Parser

Parses chemistry notation into `(text, is_subscript, is_superscript)` segments:

```python
def _parse_chemistry(formula):
    """Parse: H2O → [('H',F,F), ('2',T,F), ('O',F,F)]
              Fe2O3 → [('Fe',F,F), ('2',T,F), ('O',F,F), ('3',T,F)]
              2H2 + O2 → [('2',F,F), ('H',F,F), ('2',T,F), (' + ',F,F), ('O',F,F), ('2',T,F)]
    """
```

Rules:
- Numbers after uppercase letter (possibly + lowercase) → **subscript** (H2, O2, Fe2)
- Numbers at start or after operator/space → **normal size** (stoichiometric coefficient)
- `^{...}` or `^digit` → **superscript** (charges like Na⁺)
- `_{...}` or `_digit` → **subscript**
- `->` → `→` (arrow)
- Operators `+-=()[]{}` → normal size

### `render_chemistry_formula(text, fontsize, seed, style)` — Renderer

Renders parsed chemistry with per-character font selection and subscript/superscript positioning:

```python
# Font sizes
font_normal = _get_best_font_for_char('H', fontsize)        # 100%
font_sub = _get_best_font_for_char('H', int(fontsize * 0.65))  # 65% for subscripts
font_super = _get_best_font_for_char('H', int(fontsize * 0.6)) # 60% for superscripts

# Positioning
if sub:
    paste_y = baseline_y + int(fontsize * 0.25)  # drop down
elif sup:
    paste_y = baseline_y - int(fontsize * 0.2)   # raise up
else:
    paste_y = baseline_y                         # normal baseline
```

### Integration with Pipeline

Chemistry formulas use `\ce{}` LaTeX syntax. The parser detects `\ce{` and routes to the chemistry renderer:

```python
# In render_document():
if '\\ce{' in seg.content:
    img = render_science_formula_segment(seg.content, position, style)
else:
    img = render_formula_segment(seg.content, position, style)
```

**Demo content**: `python handwrite_pipeline.py --demo science` generates chemistry + physics formulas.

## `_get_best_font_for_char()` — Three-Tier Font Fallback (v10)

**The key improvement**: Per-character font selection with 3-tier fallback chain.

```python
def _get_best_font_for_char(char, size=28):
    """MaShanZheng (CJK) → Kalam (Latin/handwriting) → Noto Sans Math (math symbols)."""
    # 1. CJK → MaShanZheng
    if _has_cjk(char) and _char_has_glyph(char, MASHAN):
        return ImageFont.truetype(str(MASHAN), size)
    # 2. Latin/basic → Kalam
    if _char_has_glyph(char, KALAM_FONT):
        return ImageFont.truetype(str(KALAM_FONT), size)
    # 3. Math symbols (Greek, ∫∑√) → Noto Sans Math
    if _char_has_glyph(char, NOTO_MATH):
        return ImageFont.truetype(str(NOTO_MATH), size)
    # 4. Fallback
    return ImageFont.truetype(str(KALAM_FONT), size)
```

**This replaces the old 2-tier chain** (MaShanZheng → Kalam). Noto Sans Math covers ALL math symbols including Greek letters, which Kalam misses.

### Noto Sans Math Integration

```python
NOTO_MATH = PROJECT_DIR / "fonts" / "NotoSansMath-Regular.ttf"
# Fallback path if primary doesn't exist:
if not NOTO_MATH.exists():
    NOTO_MATH = PROJECT_DIR / "fonts" / "NotoSansMath" / "full" / "ttf" / "NotoSansMath-Regular.ttf"
```

**For matplotlib**: Register Noto Sans Math as `mathtext.sf` for comprehensive symbol fallback:
```python
mpl.rcParams['mathtext.sf'] = 'Noto Sans Math'  # symbols fallback
mpl.rcParams['mathtext.rm'] = 'Kalam'            # Latin/Greek primary
```

**⚠️ PITFALL**: matplotlib's `findfont` may not find "Noto Sans Math" by name. Use `fm.fontManager.addfont(path)` to register explicitly.

## v9 Systematic Optimization (Research-Driven, 2024-2026 Papers)

Based on arXiv paper survey (~50 papers scanned), implemented systematic optimizations
inspired by: CASHG (2604.02103), One-DM (2409.04004), DiffInk (2509.23624),
NIV (2606.05261), The Cursive Transformer (2504.00051).

### CJK Font Variant Full Coverage (P0)

**Problem**: Bezier perturbation only covered ASCII + ~30 math symbols. Chinese text
(主体内容) had ZERO glyph variation — same character always identical.

**Solution**: Sample 3000 common CJK chars + CJK punctuation + fullwidth forms.

```python
# In generate_font_variant(), after ASCII + math symbols:
_cjk_rng = np.random.RandomState(variant_seed)
cjk_common = set()
for c in range(0x4E00, 0x9FA6):  # CJK Unified Ideographs
    if c in cmap:
        cjk_common.add(cmap[c])  # ⚠️ MUST use cmap[c] (string), NOT c (int)
if len(cjk_common) > 3000:
    cjk_sample = set(_cjk_rng.choice(list(cjk_common), 3000, replace=False))
else:
    cjk_sample = cjk_common
target_codepoints.update(cjk_sample)
```

### Markdown Structural Parsing (P0)

New `parse_markdown_structure()` function detects:
- `# `, `## `, `### ` → heading1/heading2/heading3
- `- `, `* ` → list_bullet (with indent level from leading spaces)
- `\d+. ` → list_number
- Empty lines → para_break

Returns `StructuredSegment(type, content, indent)` dataclass.

### Paper Texture Overlay (P0)

`generate_paper_texture(width, height, seed)` creates procedural fiber texture.
Applied to paper via `Image.alpha_composite()` in `create_lined_paper()`.
Alpha max 15/255 — very subtle, doesn't distract from text.

### Bigram Context Consistency (P1, CASHG-inspired)

**Problem**: Each character independently picks a font variant. Adjacent characters
have no visual continuity — breaks the illusion of continuous writing.

**Solution**: Group 3 adjacent characters to share a correlated seed:

```python
group_id = idx // 3  # every 3 chars share a group
char_seed = seed * 10007 + group_id * 137 + ord(ch) * 31
```

Applied in both `render_chinese_pil_v2()` and `render_math_pil_v2()`.

### InkType Physics Simulation (P1)

New `InkType` class with BALLPOINT/FOUNTAIN/PENCIL constants.
Added `ink_type` random parameter to `StudentStyle`.

In `perturb_image()`, ink bleed branches on ink_type:
- **Ballpoint**: GaussianBlur(0.4) + edge darkening (oil accumulation at stroke edges)
- **Fountain**: GaussianBlur(0.8) + vertical directional blur (ink flow)
- **Pencil**: grain noise instead of blur, lighter overall

### MaShanZheng for CJK in matplotlib mathtext (P1)

Register MaShanZheng as `mathtext.tt` for `\text{}` environments:

```python
mpl.rcParams['mathtext.tt'] = cn_font_name  # CJK in \text{中文} renders correctly
```

### Layout Intelligence (P2)

`render_document()` uses `parse_markdown_structure()` output:
- **heading1**: fontsize=48, NO extra spacing (just natural line wrap)
- **heading2**: fontsize=40, NO extra spacing
- **heading3**: fontsize=33, NO extra spacing
- **list_bullet**: "· " prefix + left indentation (2 chars per indent level)
- **list_number**: left indentation
- **para_break**: NO extra gap (pass — natural line break only)

**⚠️ CRITICAL: Heading/paragraph spacing was aggressively reduced.** The original code had `add_newline()` before and after headings, plus `para_break` adding a full blank line. This caused 2-3 lines of blank space between sections, pushing content across multiple pages unnecessarily (3 pages → 1 page after fix). The user complained: "莫名其妙空出两三行，垃圾死了" (mysterious 2-3 line gaps, terrible). **Do NOT re-add `add_newline()` around headings or para_breaks.** **Current grid-aligned spacing parameters (v12):**
- `TEXT_FONT_SIZE = 22` (was 32 — must fit within LINE_SPACING=38px grid cell)
- `pad = int(fontsize * 0.6)` in `render_chinese_pil_v2` (was `fontsize`)
- Baseline wave amplitude: `4.0` (was `12.0` — too much wave bleeds into adjacent grid cells)
- `_advance_line()`: fixed `self.y += LINE_SPACING` (was content-height-based — broke grid alignment)
- `para_break`: `comp._advance_line()` (one grid line gap)
- Display math: capped at `LINE_SPACING * 1.8` height
- No `add_newline()` around headings

`PageCompositor.add_segment()` accepts optional `font_size_hint` and `left_indent` params.

`render_text_with_fallback()` now accepts `fontsize` parameter (default None = TEXT_FONT_SIZE).

## Next Improvements

1. ~~Find a true Chinese handwriting font to replace STHeiti~~ → Done: MaShanZheng (Google Fonts)
2. ~~Fix math font tofu~~ → Done: Kalam + font fallback chains
3. ~~Multi-scale perturbation~~ → Done: v6 three-layer displacement + pen-lift + ink dots
4. ~~PIL per-char rendering for simple formulas~~ → Done: v7 `render_math_pil_chars()`
5. ~~Connected strokes~~ → Done: v8 Bezier bridges drawn AFTER paste
6. ~~Start-heavy/end-light pen pressure~~ → Done: v8 horizontal gradient per character
7. ~~Personalized handwriting models~~ → Done: v8 `StudentStyle` with 9 personality params
8. ~~Paper aging effects~~ → Done: v8 yellowing + creases + coffee stain + fingerprint
9. ~~Ink color variation~~ → Done: v8 blue-black per-student
10. ~~Correction marks~~ → Done: v9 strikethrough, white-out, caret
11. ~~Math ligature~~ → Done: v9 `add_formula_connections()`
12. ~~Multi-page aging variation~~ → Done: v9 `apply_paper_aging_v2()`
13. ~~Scan effects~~ → Done: v9 `apply_scan_effects()` (DISABLED in production)
14. ~~Font stacking with Noto Sans Math~~ → Done: v10 three-tier fallback
15. ~~Graves RNN handwriting synthesis~~ → Done: v10 stroke-based English
16. ~~Chemistry formula rendering~~ → Done: v10 `\ce{}` support
17. ~~CJK font variant coverage~~ → Done: v9 sampled 3000 common chars
18. ~~Markdown structural parsing~~ → Done: v9 headings/lists/paragraphs
19. ~~Bigram context consistency~~ → Done: v9 3-char groups share variant seed
20. ~~InkType physics simulation~~ → Done: v9 ballpoint/fountain/pencil
21. ~~Layout intelligence~~ → Done: v9 heading sizes, list indent, paragraph spacing
22. ~~Paper texture overlay~~ → Done: v9 procedural fiber texture
23. ~~CJK in mathtext~~ → Done: v9 MaShanZheng as mathtext.tt
24. Meaningful axis perturbation (perturb along stroke direction, not random noise)
25. Real handwriting style transfer (One-DM / DiffusionPen approach)
26. Use MathWriting dataset glyphs to replace matplotlib's default math symbol shapes
27. Web API (FastAPI) for WeChat mini-program integration
28. Train Chinese Graves RNN model for consistent CJK+English handwriting style

## ⚠️ Architecture Ceiling — Font + Perturbation vs Neural Network Generation

**CRITICAL LESSON**: The current architecture (font rendering + bezier perturbation + pixel noise) has a **fundamental quality ceiling**. No amount of parameter tweaking will produce the same quality as neural network-based handwriting generation. This was proven in a session where 50+ arXiv papers were researched, 8 optimizations implemented, and the visual difference was essentially zero.

**Root cause**: The approach modifies the SHAPE of existing font glyphs (adding noise), but the UNDERLYING glyph structure remains a font designer's creation. Real handwriting has different stroke order, connection patterns, and letter formation — not just noisy versions of print letters.

**What the research papers actually do** (fundamentally different architecture):
- **Diffusion models** (One-DM, DiffBrush, DiffInk): Generate handwriting images from scratch using learned stroke distributions
- **Stroke-based RNNs** (Graves, CASHG): Generate pen trajectories (x, y, pen_up/down) that are then rendered
- **Style transfer** (HWT, Emuru): Take a few reference handwriting samples and transfer the style to new text

**Neural network alternatives evaluated**:
| Model | Status | Quality | Language | Notes |
|-------|--------|---------|----------|-------|
| Graves RNN (integrated) | Working but poor | 3-4/10 | English ASCII only | Output is illegible for most text. Model trained on IAM, only 56 epochs. |
| HWT (Handwriting Transformers) | API unreliable | Unknown | English | HuggingFace Space times out. Needs pre-trained weights from Google Drive (~download fails). |
| OLHWG (ICLR 2025) | Not integrated | High (paper) | Chinese | Needs data download from HuggingFace + training. Best candidate for Chinese. |
| CASIA-OLHWDB | Not integrated | N/A | Chinese | Dataset only, needs model training. |

**Practical implication**: When the font+perturbation approach is the only option (no trained neural model available), the parameters MUST be aggressive AND the fonts MUST be mixed. The **mixed font rendering technique** (楷书/草书 per character) is the best achievable within this architecture — it changes the actual glyph structure, not just adds noise.

See `references/neural_model_evaluation.md` for detailed evaluation of Graves RNN, HWT, OLHWG, and CASIA-OLHWDB.

## Amplified Parameter Ranges (v9 — Visible Handwriting)

When using the font+perturbation architecture, these parameters produce **visible** handwriting characteristics:

| Parameter | Conservative (invisible) | Amplified (visible) | Location |
|-----------|------------------------|---------------------|----------|
| Bezier amplitude | 12.0 | **35.0** | `generate_font_variant()` |
| Paper texture alpha | 15 | **50** | `generate_paper_texture()` |
| StudentStyle neatness | 0.2-0.7 | **0.4-0.9** | `StudentStyle.__init__()` |
| StudentStyle size_var | 0.02-0.08 | **0.04-0.12** | `StudentStyle.__init__()` |
| StudentStyle baseline_wave | 0.3-0.8 | **0.5-1.0** | `StudentStyle.__init__()` |
| Baseline wave amplitude | 6.0px | **4.0px** (grid-aligned) | `render_chinese_pil_v2()` |
| Per-char rotation | ±1.0° × neatness | **±2.5°** × neatness | `render_chinese_pil_v2()` |
| Per-char position jitter | σ=0.6 | **σ=1.5** | `render_chinese_pil_v2()` |
| Affine scale jitter | σ=0.06 | **σ=0.10** | `render_chinese_pil_v2()` |
| Affine shear | σ=0.04 | **σ=0.08** | `render_chinese_pil_v2()` |
| perturb_image strength | 1.5+2.0×neatness | **2.5+4.0**×neatness | `perturb_image()` |
| Heading h1 size | 40pt | **48pt** | `render_document()` |
| Heading h2 size | 36pt | **40pt** | `render_document()` |

**⚠️ Amplitude > 15 on font variants may cause glyph fragmentation** (documented in pitfalls). But for VISUAL IMPACT on the final rendered page, the amplified parameters above produce clearly different output from regular printed text. The glyph fragmentation pitfall applies to the font file perturbation, not the pixel-level rendering parameters.

## User Expectations for This Project

**User expects QUALITATIVE visible differences**, not subtle parameter tweaks. When the user says "why did you read so many papers and make so many changes but the difference is basically zero?" — this means the changes were architecturally correct but parametrically invisible. The fix is to amplify parameters until the effect is undeniable, even if some glyphs look slightly distorted.

**User is direct and doesn't min words**. When output looks the same as before, they will say so immediately. Don't claim "improvements" unless there's a clear visual difference.

**"太烂了，可读性为0" is a quality RED LINE.** When the user says readability is zero, the output is fundamentally broken — not a style preference issue. Stop generating and debug the rendering pipeline immediately. Common causes: broken font (zero-height glyphs), wrong rendering path (PIL for LaTeX), font fallback chain failure. See `references/2026-07-15-font-formula-bugs.md` for the full debugging session.

**Excessive spacing is a layout RED LINE.** When the user complains about 2-3 line gaps between sections, the pipeline has too many `add_newline()` calls or `para_break` gaps. See `references/2026-07-15-layout-spacing-fix.md` for the spacing reduction recipe. The user wants DENSE handwritten notes, not airy layouts.

**When neural network models are not available** (no pre-trained weights, API timeouts, training not feasible), be honest about the limitation. Don't pretend parameter tweaking will produce the same quality as a trained diffusion model.
