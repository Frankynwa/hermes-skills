# Font Variant Pool — Per-Render Glyph Variation

## Problem

Digital fonts have fixed glyph shapes. When rendering "数学" twice with the same font, both instances are IDENTICAL — just position/rotation jitter from handright. Real handwriting has different stroke shapes each time.

handright's perturbation (position σ=2.0, rotation σ=0.06, size σ=0.4) only varies spatial placement, NOT the underlying glyph geometry. This produces "every character looks like a rubber stamp" — the biggest giveaway of digital handwriting.

## Solution Architecture

```
Startup:
  MaShanZheng-Regular.ttf
    → perturb_font_all_glyphs(seed=42)   → .font_cache/variant_00.ttf
    → perturb_font_all_glyphs(seed=1042) → .font_cache/variant_01.ttf
    → perturb_font_all_glyphs(seed=2042) → .font_cache/variant_02.ttf
    → ...

Per-render:
  text_segment → random.choice(variants) → handright.render(text, font=variant)
```

## Implementation

### 1. Add `perturb_font_all_glyphs` to perturb_font.py

```python
def perturb_font_all_glyphs(input_path, output_path, seed=42,
                             amplitude=DEFAULT_AMPLITUDE,      # 2.5
                             rotation_deg=DEFAULT_ROTATION_DEG, # 1.5
                             scale_var=DEFAULT_SCALE_VARIATION): # 0.025
    """Perturb ALL glyphs (CJK + Latin + math) in a font."""
    from fontTools.ttLib import TTFont
    font = TTFont(str(input_path))
    cmap = font.getBestCmap()
    glyf_table = font["glyf"]
    stats = {"total": 0, "perturbed": 0, "skipped": 0}

    for i, (code, glyph_name) in enumerate(sorted(cmap.items())):
        stats["total"] += 1
        try:
            g = glyf_table[glyph_name]
            if g.isComposite():
                glyph_seed = (seed * 31 + i * 7 + code) % (2**31)
                ok = _perturb_composite_glyph(g, glyph_seed, amplitude,
                                               rotation_deg, scale_var)
                stats["perturbed" if ok else "skipped"] += 1
                continue
            if not hasattr(g, "coordinates") or g.coordinates is None:
                stats["skipped"] += 1; continue
            if g.numberOfContours <= 0:
                stats["skipped"] += 1; continue
        except Exception:
            stats["skipped"] += 1; continue

        glyph_seed = (seed * 31 + i * 7 + code) % (2**31)
        ok = perturb_glyph_outline(font, glyph_name, seed=glyph_seed,
                                    amplitude=amplitude,
                                    rotation_deg=rotation_deg,
                                    scale_var=scale_var)
        stats["perturbed" if ok else "skipped"] += 1

    os.makedirs(os.path.dirname(str(output_path)) or ".", exist_ok=True)
    font.save(str(output_path))
    font.close()
    return stats
```

### 2. FontVariantPool class (font_variant_pool.py)

```python
class FontVariantPool:
    def __init__(self):
        self._pools = {}  # font_path -> [variant_paths]

    def load(self, font_path, num_variants=8, amplitude=2.5):
        """Pre-generate N variants (cached to .font_cache/)."""
        fid = hashlib.md5(f"{font_path}|{amplitude}|{num_variants}".encode()).hexdigest()[:8]
        cache_dir = Path(".font_cache") / fid
        cache_dir.mkdir(parents=True, exist_ok=True)

        existing = sorted(cache_dir.glob("variant_*.ttf"))
        if len(existing) >= num_variants:
            self._pools[font_path] = [str(p) for p in existing[:num_variants]]
            return

        variants = []
        for i in range(num_variants):
            out = str(cache_dir / f"variant_{i:02d}.ttf")
            perturb_font_all_glyphs(font_path, out, seed=42 + i * 1000, amplitude=amplitude)
            variants.append(out)
        self._pools[font_path] = variants

    def get(self, font_path):
        """Get a random variant (different glyph shapes each call)."""
        return random.choice(self._pools.get(font_path, [font_path]))
```

### 3. Integration with pipeline

```python
# In _setup_math_font():
pool = init_pool(chinese_font_path, kalam_path, num_variants=5)

# In render_text_with_fallback():
cn_font_path = pool.get(cn_font_path)  # Random MaShanZheng variant
kalam_path = pool.get(kalam_path)       # Random Kalam variant

# Each text segment gets a different variant → same character looks different
```

## Performance

| Font | Glyphs | Per-variant gen time | 5 variants total |
|------|--------|---------------------|-----------------|
| MaShanZheng (CJK) | 7015 | ~3s | ~15s |
| Kalam (Latin) | 1026 | ~1s | ~5s |

Cached to `.font_cache/` — subsequent runs are instant.

## Quality Results

Vision analysis of two runs with different variant pools:

- Same character ("数", "学") across renders: **visibly different** stroke shapes
- Same variable "x" in math formulas: **different** angles and thickness
- Overall: "差异足够大，容易被误认为是不同人写的"
  (differences significant enough to be mistaken for different people's writing)

## Pitfalls

1. **Don't forget to regenerate when font changes** — Delete `.font_cache/` if you change amplitude or font files
2. **CJK fonts are large** — MaShanZheng variants are ~6MB each. 5 variants = 30MB cache
3. **Random seed matters** — Use `seed=42 + i * 1000` (well-separated) not `seed=i` (produces similar variants)
4. **matplotlib variant fonts need re-registration** — Each new variant needs `fm.fontManager.addfont(variant_path)`. For math, just use the original Kalam (mathtext handles the rendering)
