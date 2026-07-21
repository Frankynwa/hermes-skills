# HTML to PDF with Embedded Mermaid Diagrams

For assignments requiring a PDF with diagrams (FSM, CFG, etc.), use
Mermaid rendered via `mermaid.ink` embedded in HTML, then convert to
PDF via Chrome headless.

## Why this approach

- **Mermaid in PDFs**: Chrome headless `--print-to-pdf` may not execute
  JavaScript in time to render Mermaid from a CDN `<script>` tag. The
  rendered images may appear blank.
- **mermaid.ink**: Free public API that renders Mermaid code to SVG/PNG
  via URL encoding. The resulting `<img>` tags load as standard images
  that Chrome can render statically.

## Step 1: Encode Mermaid diagrams

```python
import base64

def mermaid_img_url(code):
    """Encode Mermaid code to mermaid.ink image URL."""
    graphbytes = code.encode("utf-8")
    b64 = base64.urlsafe_b64encode(graphbytes).decode("utf-8").rstrip("=")
    return f"https://mermaid.ink/img/{b64}"
```

Example — CFG for a function:
```python
mermaid_code = """graph TD
    Start --> A{"a > b ?"}
    A -->|True| B["temp = a"]
    A -->|False| C["temp = b"]
    B --> D{"c > temp ?"}
    C --> D
    D -->|True| E["temp = c"]
    D -->|False| F["return temp"]
    E --> F
    F --> End"""

url = mermaid_img_url(mermaid_code)
```

Example — FSM (state diagram):
```python
mermaid_code = """stateDiagram-v2
    [*] --> Locked
    Locked --> PanelRevealed : openPanel() [key inserted]
    PanelRevealed --> Open : validate(correct)
    PanelRevealed --> Alarm : validate(incorrect)
    Alarm --> Open : validate(correct)"""

url = mermaid_img_url(mermaid_code)
```

## Step 2: Embed in HTML

```html
<img src="https://mermaid.ink/img/ENCODED_STRING"
     alt="Descriptive alt text"
     style="max-width:100%; display:block; margin:12px auto;">
```

The `alt` text is preserved in the PDF and can be searched.

## Step 3: Convert to PDF with Chrome Headless

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="/path/to/output.pdf" \
  --no-pdf-header-footer \
  "file:///path/to/solution.html"
```

**Important flags**:
- `--no-pdf-header-footer`: removes Chrome's default date/URL header and
  footer from each page (required for clean submission PDFs).
- Do NOT use `--no-margins` unless you want zero-margin edge-to-edge
  content. Default margins (~0.4in) produce standard academic-looking pages.

## Step 4: Verify

Check the PDF was generated and has correct page count:
```bash
mdls -name kMDItemNumberOfPages output.pdf
ls -lh output.pdf
```

Verify Mermaid images loaded:
```bash
curl -s -o /dev/null -w "HTTP %{http_code} Size: %{size_download}\n" "MERMAID_URL"
```

## CSS Tips for Academic PDFs

Use these in the `<style>` block:
```css
@page { margin: 2cm; size: A4; }
body {
  font-family: 'Times New Roman', Times, serif;
  font-size: 12pt;
  line-height: 1.6;
  max-width: 700px;
  margin: 0 auto;
}
h2 { page-break-before: always; }  /* Each question on new page */
h2:first-of-type { page-break-before: avoid; }  /* Don't break before Q1 */
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #555; padding: 6px 8px; }
pre { background: #f4f4f4; padding: 10px; white-space: pre-wrap; }
```

## Pitfalls

- **Mermaid CDN in headless Chrome**: The `--headless` flag may not wait
  for JavaScript to execute. Static `<img>` tags are reliable; `<script>`
  tags for client-side rendering are not.
- **mermaid.ink URL length**: Very long Mermaid code can produce URLs
  that hit server limits. Keep diagrams focused (under ~40 lines works).
- **Chrome headless errors**: `DEPRECATED_ENDPOINT` messages in stderr
  are harmless — the PDF still writes successfully.
- **Page count**: Complex content (tables, code blocks, diagrams) can
  produce 15-20 pages for a comprehensive assignment. This is normal.
