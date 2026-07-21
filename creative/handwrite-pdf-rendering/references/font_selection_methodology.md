# Font Selection Methodology for Handwriting Rendering

## Chinese Font Selection (Google Fonts)

### Download from Google Fonts GitHub

```bash
cd ~/projects/handwrite-pdf-poc/fonts

# Use Python urllib (NOT curl — see Critical Pitfall below)
python3 -c "
import urllib.request
fonts = {
    'MaShanZheng-Regular.ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/mashanzheng/MaShanZheng-Regular.ttf',
    'LiuJianMaoCao-Regular.ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/liujianmaocao/LiuJianMaoCao-Regular.ttf',
}
for fname, url in fonts.items():
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
        with open(fname, 'wb') as f:
            f.write(data)
        print(f'{fname}: {len(data)} bytes')
"
```

**⚠️ CRITICAL — Silent Font Corruption**: curl downloads from GitHub raw URLs can produce a **partially downloaded TTF** that PIL loads without errors but renders **invisible glyphs** (zero-height bounding boxes). Symptoms: `font.getname()` returns `(None, None)`, `font.getbbox("你")` has `height=0`, all `draw.text()` output is blank. The file looks superficially valid (has glyf table) but is silently broken.

**Root cause**: curl sometimes gets truncated downloads or follows partial redirects. The file might be ~1MB when it should be ~6MB for a CJK font.

**Fix**: use Python `urllib` with User-Agent headers, then validate with fonttools AND a render test:

```python
# CORRECT download method
import urllib.request
url = 'https://raw.githubusercontent.com/google/fonts/main/ofl/mashanzheng/MaShanZheng-Regular.ttf'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
    with open('MaShanZheng-Regular.ttf', 'wb') as f:
        f.write(data)

# MANDATORY validation
from fontTools.ttLib import TTFont
f = TTFont('MaShanZheng-Regular.ttf')
cmap = f.getBestCmap()  # throws if tables corrupted
cjk = sum(1 for cp in cmap if 0x4E00 <= cp <= 0x9FFF)
assert cjk > 1000, f"Only {cjk} CJK glyphs — likely corrupted"
f.close()

# Render test — MUST produce non-zero dark pixels
from PIL import Image, ImageDraw, ImageFont
import numpy as np
font = ImageFont.truetype('MaShanZheng-Regular.ttf', 48)
img = Image.new('L', (200, 80), 255)
draw = ImageDraw.Draw(img)
draw.text((10, 10), '你好世界', font=font, fill=0)
nz = np.count_nonzero(np.array(img) < 250)
assert nz > 100, f"Only {nz} dark pixels — font renders nothing!"
```

### Validation Script (comprehensive)

```python
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import numpy as np
import os

for f in os.listdir('fonts/'):
    if not f.endswith('.ttf'):
        continue
    fp = os.path.join('fonts/', f)
    try:
        # 1. fonttools table validation
        tt = TTFont(fp)
        cmap = tt.getBestCmap()
        cjk = sum(1 for cp in cmap if 0x4E00 <= cp <= 0x9FFF)
        tt.close()

        # 2. PIL render validation (catches invisible glyph issue)
        font = ImageFont.truetype(fp, 48)
        name = font.getname()
        bbox = font.getbbox('你好世界')
        h = bbox[3] - bbox[1]  # height must be > 0!

        # 3. Actual pixel render test
        img = Image.new('L', (200, 80), 255)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), '你好世界', font=font, fill=0)
        nz = np.count_nonzero(np.array(img) < 250)

        if h == 0 or nz < 100:
            print(f'⚠️  CORRUPT: {f} -> name={name}, height={h}, pixels={nz}')
        else:
            print(f'OK: {f} -> {name[0]}, {cjk} CJK glyphs, height={h}, pixels={nz}')
    except Exception as e:
        print(f'FAIL: {f} -> {e}')
        os.remove(fp)
        print(f'  Removed invalid file')
```

### Font Comparison via Vision Analysis

Generate side-by-side comparison images, then use `vision_analyze` to pick the winner:

```python
from PIL import Image, ImageDraw, ImageFont

test_texts = [
    '数学作业 第五章',
    '1. 计算不定积分',
    '若 f(x) = x³ + 2x，求 f\'(x)',
    '答案：求根公式',
]

fonts = {
    'Candidate A': ImageFont.truetype('fonts/fontA.ttf', 32),
    'Candidate B': ImageFont.truetype('fonts/fontB.ttf', 32),
    'Baseline (STHeiti)': ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc', 32),
}

# Render each font's output in a column, save as comparison PNG
# Then use vision_analyze with question:
# "Which font most closely resembles student handwriting? Rate each 1-10."
```

### Chinese Font Ranking (empirically tested, macOS)

| Rank | Font | Style | Handwriting Score | Notes |
|------|------|-------|-------------------|-------|
| 1 | MaShanZheng (马善政) | 楷书 | 9/10 | Best: natural pen strokes, readable, student-like |
| 2 | LiuJianMaoCao (刘建毛草) | 草书 | 7/10 | Too artistic, low readability for math context |
| 3 | STHeiti | 黑体 (print) | 3/10 | System fallback, not handwriting at all |
| 4 | Songti SC | 宋体 (print) | 2/10 | Even more "printed" than STHeiti |

## Math Font Selection (matplotlib custom fontset)

### Testing Strategy

```python
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# Test each candidate
candidates = ['Bradley Hand', 'Comic Sans MS', 'Kalam']
formulas = [
    r'$E = mc^2$',
    r'$\int_0^\infty e^{-x^2} dx = \sqrt{\pi}$',
    r'$\frac{d}{dx} \int_0^x f(t) dt$',
    r'$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$',
    r'$\lim_{x \to 0} \frac{\sin x}{x} = 1$',
    r'$\alpha + \beta = \gamma$',
]

for font_name in candidates:
    # Register + configure
    fm.fontManager.addfont(font_paths[font_name])
    mpl.rcParams['mathtext.fontset'] = 'custom'
    mpl.rcParams['mathtext.rm'] = font_name
    mpl.rcParams['mathtext.it'] = font_name
    mpl.rcParams['mathtext.bf'] = font_name
    
    # Render all formulas, save as column in comparison image
```

### Math Font Ranking (empirically tested)

| Rank | Font | Math Score | Notes |
|------|------|------------|-------|
| 1 | Bradley Hand + perturbation | 8/10 | Best: natural handwriting feel, good readability |
| 2 | Bradley Hand (no perturbation) | 6/10 | Too uniform, "printed handwriting" feel |
| 3 | Kalam + perturbation | 5/10 | Symbols distort too much, readability drops |
| 4 | Comic Sans MS | 4/10 | Too cartoony, not professional enough |
| 5 | Computer Modern (default) | 2/10 | Perfect but completely not handwriting |

### Three-Version Comparison Pattern

Generate V1/V2/V3 comparison to demonstrate improvement:

- **V1**: Computer Modern (default LaTeX) — baseline
- **V2**: New math font + old Chinese font (STHeiti) — partial improvement
- **V3**: New math font + new Chinese font (MaShanZheng) — full improvement

Create a side-by-side image with labels and use Vision to confirm quality improvement.

## Font Registration Pitfalls

1. **matplotlib needs `fm.fontManager.addfont()`** — system fonts aren't auto-discovered for custom fontset
2. **Font name mismatch** — the name returned by `FontProperties(fname=...).get_name()` may differ from filename. Use the returned name for `mathtext.rm` etc.
3. **Bold font variant** — `Bradley Hand Bold.ttf` exists but `Bradley Hand` (without Bold) is the name to use. Don't set `mathtext.bf` to 'Bradley Hand Bold'.
4. **TTC vs TTF** — macOS system fonts are often `.ttc` (TrueType Collection). PIL handles them fine but fonttools may need special treatment.
5. **font_manager cache** — after adding fonts, they persist in the session. Don't add the same font twice (harmless but wasteful).
