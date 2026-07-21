# Advanced Pixel Perturbation (v6+)

Full implementation used in `handwrite_pipeline.py` `perturb_image()` and `gen_math_v6.py`.

## Complete Pipeline

```python
def perturb_image(img, seed=42, strength=1.8):
    """v6 perturbation: multi-scale displacement, pen-lift, speed thinning, ink dots."""
    from scipy.ndimage import zoom as ndzoom, binary_dilation
    rng = np.random.RandomState(seed)

    # Convert to grayscale mask
    gray = img.convert('L')  # (handle RGBA→L if needed)
    arr = np.array(gray)
    mask = arr < 180
    h, w = arr.shape
    result = np.ones((h, w), dtype=np.uint8) * 255

    # ── 1. Multi-scale displacement (3 layers) ──
    block_lg = max(4, h // 4)
    nlx = rng.randn(h//block_lg+2, w//block_lg+2) * strength * 1.4
    nly = rng.randn(h//block_lg+2, w//block_lg+2) * strength * 1.6
    dx_lg = ndzoom(nlx, (h/nlx.shape[0], w/nlx.shape[1]), order=2)[:h,:w]
    dy_lg = ndzoom(nly, (h/nly.shape[0], w/nly.shape[1]), order=2)[:h,:w]

    block = max(3, int(strength * 2.5))
    noise_x = rng.randn(h//block+2, w//block+2) * strength * 2.0
    noise_y = rng.randn(h//block+2, w//block+2) * strength * 1.8
    dx_md = ndzoom(noise_x, (h/noise_x.shape[0], w/noise_x.shape[1]), order=1)[:h,:w]
    dy_md = ndzoom(noise_y, (h/noise_y.shape[0], w/noise_y.shape[1]), order=1)[:h,:w]

    block_sm = max(2, block // 2)
    nsx = rng.randn(h//block_sm+2, w//block_sm+2) * strength * 0.8
    nsy = rng.randn(h//block_sm+2, w//block_sm+2) * strength * 0.8
    dx_sm = ndzoom(nsx, (h/nsx.shape[0], w/nsx.shape[1]), order=1)[:h,:w]
    dy_sm = ndzoom(nsy, (h/nsy.shape[0], w/nsy.shape[1]), order=1)[:h,:w]

    dx = dx_lg + dx_md + dx_sm
    dy = dy_lg + dy_md + dy_sm

    ys, xs = np.where(mask)
    for yi, xi in zip(ys, xs):
        ny = int(np.clip(yi + dy[yi, xi], 0, h-1))
        nx = int(np.clip(xi + dx[yi, xi], 0, w-1))
        result[ny, nx] = 0

    # ── 2. Pen-lift gaps ──
    n_gaps = rng.randint(2, max(3, int(w * 0.02)))
    for _ in range(n_gaps):
        gx, gy = rng.randint(0, w), rng.randint(0, h)
        gw, gh = rng.randint(2, 7), rng.randint(1, 3)
        region = mask[max(0,gy):min(h,gy+gh), max(0,gx):min(w,gx+gw)]
        if region.any():
            result[max(0,gy):min(h,gy+gh), max(0,gx):min(w,gx+gw)] = 255

    # ── 3. Speed-dependent thinning ──
    speed_pattern = np.sin(np.arange(h)/14.0*np.pi + rng.uniform(0, 2*np.pi))
    for y_i in range(h):
        if speed_pattern[y_i] > 0.3:
            thin_px = rng.random(w) < 0.15
            result[y_i, :][mask[y_i, :] & thin_px] = 255

    # ── 4. Pen pressure ──
    pressure = rng.random((h, w))
    thick = (pressure < 0.12) & mask
    dilated = binary_dilation(thick, iterations=1)
    result[dilated] = np.minimum(result[dilated], 40)

    # ── 5. Ink bleed ──
    result_img = Image.fromarray(result, mode='L')
    result_img = result_img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # ── 6. Ink dots ──
    result_arr = np.array(result_img, dtype=np.float32)
    n_dots = rng.randint(2, max(3, int(mask.sum() * 0.002)))
    for _ in range(n_dots):
        dy_, dx_ = rng.randint(0, h), rng.randint(0, w)
        if mask[min(dy_,h-1), min(dx_,w-1)]:
            r = rng.randint(1, 3)
            for yy in range(max(0,dy_-r), min(h,dy_+r+1)):
                for xx in range(max(0,dx_-r), min(w,dx_+r+1)):
                    if (yy-dy_)**2 + (xx-dx_)**2 <= r*r:
                        result_arr[yy, xx] = min(result_arr[yy, xx], rng.randint(15, 50))
    result_img = Image.fromarray(np.clip(result_arr, 0, 255).astype(np.uint8), mode='L')

    # ── 7. Paper texture ──
    noise_arr = np.array(result_img, dtype=np.float32)
    noise_arr += rng.normal(0, 3, noise_arr.shape)
    final = Image.fromarray(np.clip(noise_arr, 0, 255).astype(np.uint8), mode='L')

    # ── 8. Rotation ──
    angle = rng.uniform(-1.5, 1.5)
    return final.rotate(angle, resample=Image.BICUBIC, fillcolor=255, expand=True)
```

## PIL Per-Character Rendering

```python
def render_math_pil_chars(text, fontsize=28, seed=42):
    """Per-char rendering with jitter for simple math."""
    rng = np.random.RandomState(seed)
    font = ImageFont.truetype("Kalam-Regular.ttf", fontsize)
    # Measure each character
    # For each: render to sub-image → rotate ±3° → offset Normal(0,1.5) → paste
    # Returns cropped L-mode image
```

## Formula Complexity Detection

```python
def _is_simple_formula(latex_str):
    """Simple = no \\frac, \\int, \\lim, \\sum, \\sqrt, \\prod."""
    complex_markers = ['\\frac', '\\int', '\\lim', '\\sum', '\\sqrt', '\\prod']
    return not any(m in latex_str for m in complex_markers)
```

## Strength Guidelines

| Rendering path | Perturb strength | Why |
|---|---|---|
| PIL per-char (simple math) | 0.8 | Per-char jitter already provides naturalness |
| matplotlib (complex math) | 1.8 | Need heavy perturbation to overcome vector perfection |
| handright text | 0 (handright handles it) | handright has its own perturbation params |

## Benchmark Scores (Vision Analysis)

| Version | Approach | Score |
|---|---|---|
| v5 | Single-scale perturbation, all matplotlib | 8.5/10 |
| v6 | Multi-scale + pen-lift + ink dots | 8.5–9.2/10 |
| v7 | v6 + PIL per-char for simple formulas | 8.5–9.2/10 |

Note: Vision model scores are inconsistent (±2 points). Full-page demos score higher than isolated formula images. Always evaluate complete pages.
