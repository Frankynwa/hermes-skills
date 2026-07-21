# Google MathWriting Dataset (2024)

## Overview
- **Source**: Google Research
- **Size**: 655,436 handwritten math expressions + 6,423 individual symbol glyphs
- **Format**: InkML (XML-based, stroke data as x,y coordinate sequences)
- **Labels**: LaTeX commands for each symbol/expression
- **License**: Free for research (check current terms)
- **Download**: HuggingFace `datasets` library or Google Storage

## Access Methods

### HuggingFace (preferred)
```bash
pip install datasets
python -c "from datasets import load_dataset; ds = load_dataset('google/mathwriting')"
```

### Direct Download
```bash
curl -L -o mathwriting-2024.tgz 'https://storage.googleapis.com/mathwriting/mathwriting-2024.tgz'
```

Note: The dataset may require login/agreement on HuggingFace. If HuggingFace download fails, try direct URL.

## Data Structure
```
mathwriting-2024/
├── symbols/           # Individual glyph strokes (6,423 files)
│   ├── *.inkml        # Each file = one symbol with stroke data
├── expressions/       # Full expression strokes (655K files)
└── metadata.json      # Symbol labels, LaTeX mappings
```

## InkML Format
```xml
<ink>
  <traceGroup>
    <trace> x1,y1 x2,y2 x3,y3 ... </trace>  <!-- stroke 1 -->
    <trace> x1,y1 x2,y2 ... </trace>          <!-- stroke 2 -->
  </traceGroup>
  <annotation type="label">\int</annotation>   <!-- LaTeX label -->
</ink>
```

## Extraction Workflow
1. Parse InkML XML → extract stroke coordinates
2. Convert strokes to SVG paths or rasterize to PNG
3. Normalize size (e.g., 200×200px)
4. Save with transparent background
5. Build manifest.json mapping LaTeX → image file

## Key Symbols Available
All standard math operators, Greek letters, and common notation:
- Calculus: ∫ ∑ ∏ ∂ ∇ ∞
- Greek: α β γ δ ε ζ η θ ι κ λ μ ν ξ π ρ σ τ υ φ χ ψ ω
- Operators: + - × ÷ = ≠ ≈ ≤ ≥ < >
- Set theory: ∈ ∉ ⊂ ⊃ ∪ ∩ ∅ ∀ ∃
- Arrows: → ← ↔ ⇒ ⇔
- Superscripts/subscripts: ⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉

## Best Use for Handwriting Pipeline
Extract individual high-quality symbol glyphs → vectorize (potrace/fontforge) → embed in TTF font alongside perturbed text glyphs. This gives REAL handwritten math symbols instead of algorithmically perturbed ones.

Quality priority: use real MathWriting glyphs for ∫ ∑ ∏ √ (complex shapes where perturbation looks artificial), use perturbed font glyphs for simple operators (+ - = < >).
