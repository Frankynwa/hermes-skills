# v9 Effects Reference — Correction Marks, Formula Connections, Scan Effects, Multi-Page Aging

## Correction Marks

Three types with probability distribution:

### Strikethrough (most common)
```python
# Wavy line through text region
y_mid = ry + rh // 2
x_start = rx + rng.randint(0, rw // 4)
x_end = rx + rw - rng.randint(0, rw // 4)
points = [(x, y_mid + int(2 * sin((x-x_start)*0.15) + rng.normal(0,1)))
          for x in range(x_start, x_end, 2)]
draw.line(points, fill=(30, 30, 60), width=2)
# 40% chance: double strike (second line 2-5px below)
```

### White-out
```python
# Off-white rectangle (slightly textured, not pure white)
for dy in range(wo_h):
    for dx in range(wo_w):
        noise = rng.randint(-3, 3)
        paper.putpixel((px, py), (250+noise, 248+noise, 240+noise))
# Rewrite text on top: '修正', '更正', 'corr.', '*'
```

### Caret
```python
# V-shape below the line + margin text
draw.line([(caret_x, caret_y+6), (caret_x+5, caret_y),
           (caret_x+10, caret_y+6)], fill=(30,30,60), width=1)
draw.text((caret_x+12, caret_y), '+', font=font)
```

## Formula Connections

```python
def add_formula_connections(formula_img, seed=42):
    # 1. Find ink mask per column
    col_has_ink = np.any(mask, axis=0)
    # 2. Find ink→gap→ink transitions with 3 < gap_width < 25
    # 3. For each selected gap:
    #    - Find ink rows on left/right edges
    #    - Draw Bezier bridge: sag = int(1.5 * sin(t * π))
    #    - Ink value: 120 (thin, like pen lift-and-continue)
    # CRITICAL: guard empty transitions with early return
```

## Scan Effects (apply AFTER everything else)

```python
def apply_scan_effects(img, seed=42):
    # 1. Rotation: ±1.5° (fill with paper color)
    img = img.rotate(angle, fillcolor=(245, 242, 230))

    # 2. Vignette: quadratic edge darkening
    vignette = 1.0 - (x_coords**2 * 0.15 + y_coords**2 * 0.12)
    vignette = np.clip(vignette, 0.85, 1.0)

    # 3. Scan bar: 3-8px dark strip at top or bottom
    arr[bar_y:bar_y+bar_h, :, :] *= rng.uniform(0.92, 0.97)

    # 4. Brightness ±3%, contrast ±5%

    # 5. JPEG compression (quality 78-92) → introduces block artifacts
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality)
    img = Image.open(buffer).convert('RGB')

    # 6. Auto-sharpen ×1.1-1.4
    img = ImageEnhance.Sharpness(img).enhance(rng.uniform(1.1, 1.4))
```

## Multi-Page Aging

```python
def apply_paper_aging_v2(paper, page_num=0, total_pages=1, seed=42):
    # Wear factor: first pages handled more
    wear = 1.0 - (page_num / max(1, total_pages - 1)) * 0.3

    # Per-page unique seed
    rng = np.random.RandomState(seed + page_num * 1000)

    # All effects scaled by wear:
    # - Yellowing: 15 * wear
    # - Creases: darken 6-14 * wear
    # - Coffee: 40% * wear chance
    # - Dog-ear: 20% * wear chance

    # Dog-ear corner fold:
    corner = rng.choice(['top_right', 'bottom_right'])
    fold_size = rng.randint(15, 35)
    # Triangular region darkened by 25 units
```

## Integration Order

1. Render text + math on each page
2. Add correction marks per page (after text is placed)
3. Apply paper aging per page (before or after text, before scan)
4. Apply scan effects per page (LAST step, after everything)
5. Save to PDF
