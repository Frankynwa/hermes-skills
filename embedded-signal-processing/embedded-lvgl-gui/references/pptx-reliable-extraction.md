# Reliable PPTX Text Extraction

## Problem

The built-in context extraction pipeline can silently truncate PPT presentations — some slides (especially later ones) may have only titles extracted, with body text completely missing. This happened with the 62-slide UT285E product definition file: slides 57-62 were empty in the extracted context, causing the agent to miss critical information (team division table, core algorithm ownership).

## Solution: python-pptx direct extraction

Use `python-pptx` via terminal to extract ALL slide text, 100% coverage:

```bash
python3 -c "
from pptx import Presentation
prs = Presentation('/path/to/file.pptx')
for i, slide in enumerate(prs.slides, 1):
    print(f'--- Slide {i} ---')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.strip()
                if text:
                    print(text)
    print()
"
```

Or as a reusable script:

```python
from pptx import Presentation
import sys

def extract_pptx(path):
    prs = Presentation(path)
    for i, slide in enumerate(prs.slides, 1):
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    t = para.text.strip()
                    if t:
                        texts.append(t)
        print(f'=== Slide {i} ===')
        print('\n'.join(texts))
        print()

if __name__ == '__main__':
    for path in sys.argv[1:]:
        extract_pptx(path)
```

## Standard Operating Procedure

When the user provides a PPTX file as an attachment:

1. **First, locate the file** — search the user's Desktop and Downloads:
   ```bash
   find ~/Desktop ~/Downloads -name '*.pptx' -mtime -7 | head
   ```

2. **Always use python-pptx directly** — do NOT rely on the context extraction pipeline. The pipeline is a convenience but known to fail silently.

3. **Only fall back to pipeline extraction** if python-pptx is unavailable (missing in the environment).

## Why python-pptx over zipfile+XML

Both work. python-pptx is preferred because:
- Handles grouped shapes, tables, and text frame hierarchy automatically
- Fewer lines of code
- Already installed in the hermes venv

If python-pptx is missing:
```bash
pip install python-pptx
```

## Pitfall from this session

Agent originally claimed the PPT didn't contain algorithm ownership info. User had to correct twice — the info was on slide 61 (project team table), but the pipeline extraction had dropped slides 57-62. Lesson: **never claim something is absent from a document without verifying with direct extraction.**
