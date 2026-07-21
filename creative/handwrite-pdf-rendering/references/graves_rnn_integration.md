# Graves RNN Handwriting Synthesis Integration

## Model: pytorch-handwriting-synthesis-toolkit

Pre-trained on IAM-OnDB (English handwriting dataset). Generates stroke sequences (Δx, Δy, pen_state) from text input.

### Setup

```bash
cd ~/projects/handwrite-pdf-poc
pip install torch h5py svgwrite cairosvg  # in .venv

# Model location
libs/pytorch-handwriting-synthesis-toolkit/checkpoints/Epoch_56/
├── model.pt      # PyTorch model weights
└── meta.json     # Normalization params (mu, std) + charset
```

### Charset (79 chars)

```
 !"#%'()+,-./0123456789:;?ABCDEFGHIJKLMNOPQRSTUVWXYZ[abcdefghijklmnopqrstuvwxyz
```

**NOT in charset**: `^`, `{`, `}`, `~`, `` ` ``, `*`, `_`, `\`, `|`, `]`

### API

```python
import sys
sys.path.insert(0, 'libs/pytorch-handwriting-synthesis-toolkit')
from handwriting_synthesis.sampling import HandwritingSynthesizer

device = torch.device("cpu")
synthesizer = HandwritingSynthesizer.load('checkpoints/Epoch_56', device, bias=0)

# Generate handwriting
c = synthesizer._encode_text("Hello World ")  # space is sentinel
sampled = synthesizer.model.sample_means(context=c, steps=1500, stochastic=True)
sampled = sampled.cpu() * synthesizer.sd + synthesizer.mu  # undo normalization
```

### Stroke Rendering

```python
from handwriting_synthesis.utils import split_into_components, get_strokes, create_strokes_svg

# Option 1: SVG (round line caps, better quality)
dwg = create_strokes_svg(sampled, '/tmp/out.svg', lines=True, thickness=5)
dwg.save()
cairosvg.svg2png(url='/tmp/out.svg', write_to='/tmp/out.png', dpi=150)

# Option 2: PIL (faster, no round caps)
x, y, eos = split_into_components(sampled)
canvas = Image.new('L', (w, h), 255)
draw = ImageDraw.Draw(canvas)
for stroke in get_strokes(x_off, y_off, eos):
    points = [(float(p[0]), float(p[1])) for p in stroke]
    for j in range(len(points) - 1):
        draw.line([points[j], points[j+1]], fill=0, width=5)
    # Round caps at endpoints
    for px, py in [points[0], points[-1]]:
        r = max(1, 5 // 2)
        draw.ellipse([px-r, py-r, px+r, py+r], fill=0)
```

### Quality Characteristics

| Text Length | Realism | Notes |
|-------------|---------|-------|
| <25 chars | 3-4/10 | Too short, unnatural cursive |
| 25-50 chars | 6-7/10 | Decent but inconsistent |
| >50 chars | 8/10 | Best quality, natural flow |

### Scaling

Output coordinates can be 6000-11000px wide. MUST scale to page width:

```python
max_width = 1100  # content width at 150 DPI
if canvas.width > max_width:
    scale = max_width / canvas.width
    canvas = canvas.resize((max_width, int(canvas.height * scale)), Image.LANCZOS)
```

### Limitations

1. ASCII only (79 chars)
2. English only (no Chinese, no Greek)
3. Always cursive (can't produce print-style)
4. Output very wide (needs scaling)
5. Short text looks unnatural
6. SVG→PNG requires cairosvg (optional dependency)

### Hybrid Strategy

```python
def render_text_with_fallback(text, style=None):
    # Graves RNN for pure ASCII >25 chars
    if _text_is_ascii(text) and len(text.strip()) > 25:
        graves_img = render_english_graves(text, style=style)
        if graves_img: return graves_img
    # PIL fallback for short/mixed text
    return render_math_pil_v2(text, fontsize=28, seed=seed, style=style)
```

### Mixing Warning

Graves RNN (cursive) + PIL (printed) creates visual inconsistency (6/10 vs 8/10 for pure Graves). For consistent style, use all-Graves or all-PIL per document.
