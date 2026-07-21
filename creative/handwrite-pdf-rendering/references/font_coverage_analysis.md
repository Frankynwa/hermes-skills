# Font Coverage Analysis & Tofu Prevention

## Problem: Tofu (□) in Rendered Output

When a font lacks a glyph for a character, the renderer shows □ (tofu). This is common with handwriting fonts that have limited Unicode coverage.

## Coverage Matrix (Tested Fonts)

| Character | Codepoint | Kalam | Bradley Hand | MaShanZheng | STHeiti | Notes |
|-----------|-----------|-------|-------------|-------------|---------|-------|
| Latin a-z | U+0041-7A | ✅ | ✅ | ✅ | ✅ | |
| Digits 0-9 | U+0030-39 | ✅ | ✅ | ✅ | ✅ | |
| ± | U+00B1 | ✅ | ✅ | ❌ | ❌ | |
| ∫ | U+222B | ✅ | ✅ | ❌ | ❌ | |
| ∞ | U+221E | ✅ | ✅ | ❌ | ❌ | |
| √ | U+221A | ✅ | ✅ | ❌ | ❌ | |
| ∑ | U+2211 | ✅ | ✅ | ❌ | ❌ | |
| ∏ | U+220F | ✅ | ✅ | ❌ | ❌ | |
| π | U+03C0 | ✅ | ✅ | ❌ | ❌ | |
| ≠ | U+2260 | ✅ | ✅ | ❌ | ❌ | |
| ∂ | U+2202 | ✅ | ✅ | ❌ | ❌ | |
| ′ (prime) | U+2032 | ❌ | ❌ | ❌ | ❌ | f'(x) — ALL fonts miss this! |
| → | U+2192 | ❌ | ❌ | ❌ | ❌ | lim x→0 |
| α | U+03B1 | ❌* | ❌ | ❌ | ❌ | *mathtext fallback handles it |
| β | U+03B2 | ❌* | ❌ | ❌ | ❌ | *mathtext fallback |
| γ | U+03B3 | ❌* | ❌ | ❌ | ❌ | *mathtext fallback |
| λ | U+03BB | ❌* | ❌ | ❌ | ❌ | *mathtext fallback |
| θ | U+03B8 | ❌* | ❌ | ❌ | ❌ | *mathtext fallback |
| ∈ | U+2208 | ❌ | ❌ | ❌ | ❌ | |
| ᵀ | U+1D40 | ❌ | ❌ | ❌ | ❌ | |
| ℝ | U+211D | ❌ | ❌ | ❌ | ❌ | |
| ℂ | U+2102 | ❌ | ❌ | ❌ | ❌ | |
| CJK (中文) | U+4E00-9FFF | ❌ | ❌ | ✅ | ✅ | |

## Font Coverage Check Script

```python
from fontTools.ttLib import TTFont

def check_font_coverage(font_path, test_chars):
    """Check which characters a font can render."""
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    if not cmap:
        return {c: False for c in test_chars}
    result = {c: (ord(c) in cmap) for c in test_chars}
    font.close()
    return result

# Test characters commonly needed in math homework
MATH_CHARS = set("∫∞√∑∏π≠∂±′→αβγλθ∈ᵀℝℂ")
CJK_CHARS = set("数学作业第五章计算不定积分求导数极限级数和解方程答案")

# Usage
coverage = check_font_coverage("Kalam-Regular.ttf", MATH_CHARS | CJK_CHARS)
missing = [c for c, ok in coverage.items() if not ok]
print(f"Missing: {''.join(missing)}")
```

## Font Download Validation Script

Google Fonts TTF files downloaded via curl from GitHub raw URLs are often truncated (1MB vs 6MB for CJK fonts). PIL/Pillow loads them without error but renders nothing.

```python
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
import os

def validate_font(font_path, test_char="你"):
    """Validate a downloaded font file is complete and functional."""
    issues = []

    # 1. File size check (CJK fonts should be >1MB)
    size = os.path.getsize(font_path)
    if size < 100_000:
        issues.append(f"File too small: {size} bytes (likely truncated)")

    # 2. fontTools can parse it
    try:
        font = TTFont(font_path)
        cmap = font.getBestCmap()
        if not cmap:
            issues.append("No cmap table found")
        elif len(cmap) < 100:
            issues.append(f"Suspiciously few cmap entries: {len(cmap)}")
        font.close()
    except Exception as e:
        issues.append(f"fontTools parse error: {e}")

    # 3. PIL can render with it
    try:
        pil_font = ImageFont.truetype(font_path, 48)
        bbox = pil_font.getbbox(test_char)
        h = bbox[3] - bbox[1]
        if h == 0:
            issues.append(f"getbbox('{test_char}') has zero height — glyph invisible")
    except Exception as e:
        issues.append(f"PIL load error: {e}")

    # 4. Actual rendering test
    try:
        pil_font = ImageFont.truetype(font_path, 48)
        img = Image.new('L', (200, 80), 255)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), test_char, font=pil_font, fill=0)
        import numpy as np
        dark_pixels = np.count_nonzero(np.array(img) < 250)
        if dark_pixels < 10:
            issues.append(f"Rendered {dark_pixels} dark pixels — likely blank")
    except Exception as e:
        issues.append(f"Render error: {e}")

    if issues:
        print(f"❌ FAIL: {font_path}")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ OK: {font_path} ({size:,} bytes, {len(cmap)} cmap entries)")
        return True
```

## Safe Font Download (Python urllib)

```python
import urllib.request
from fontTools.ttLib import TTFont
import os

def download_google_font(family_name, output_path):
    """Download a Google Font safely via Python urllib (handles redirects)."""
    # Find the font URL from Google Fonts CSS API
    css_url = f"https://fonts.googleapis.com/css2?family={family_name.replace(' ', '+')}"
    req = urllib.request.Request(css_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        css = resp.read().decode()
        import re
        urls = re.findall(r'url\((https://[^)]+)\)', css)
        if not urls:
            raise ValueError(f"No font URL found for {family_name}")

    # Download the TTF
    font_url = urls[0]
    req = urllib.request.Request(font_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(data)

    # Validate
    validate_font(output_path)
    return output_path
```

## Tofu Resolution Flowchart

```
□ appears in output
    │
    ├─ In MATH formula (matplotlib)?
    │   ├─ Check: Is Kalam registered? → addfont()
    │   ├─ Check: Is mathtext.fontset='custom'?
    │   └─ Check: Does the font have the char? → switch to Kalam
    │
    ├─ In TEXT (handright)?
    │   ├─ Check: Is the correct font being used? (CJK→MaShanZheng, EN→Kalam)
    │   ├─ Check: Is the font file valid? → run validate_font()
    │   └─ Check: Does the font have the char? → add fallback chain
    │
    └─ In PDF rendering?
        └─ Check: Is the font embedded? → PIL saves fonts by reference
```
