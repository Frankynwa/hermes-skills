---
name: ai-sprite-generation
description: Generate consistent AI cartoon sprite sets for browser extensions, games, or desktop pets. Covers DashScope Wanx API, Draw Things local generation, and Pillow fallback. Use when generating character sprite sheets, game assets, or desktop pet images.
tags: [image-generation, sprites, dashscope, draw-things, wanx, cartoon, game-assets]
---

# AI Sprite Generation

Generate a set of consistent-style character sprites (e.g., idle, walk, sleep, reward states) for browser extensions or games.

## Approach 1: DashScope Wanx API (Recommended)

Best for consistent quality without local GPU. Uses `wanx-v1` model via DashScope async API.

### API Setup

```python
import requests, base64, os, time

API_KEY = '<DASHSCOPE_API_KEY>'
SUBMIT_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'
```

### Submit Task (txt2img)

```python
resp = requests.post(SUBMIT_URL,
    headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'X-DashScope-Async': 'enable'
    },
    json={
        'model': 'wanx-v1',
        'input': {'prompt': prompt},
        'parameters': {'n': 1, 'size': '1024*1024'}
    },
    timeout=30
)
task_id = resp.json()['output']['task_id']
```

### Poll for Result

```python
def poll_task(task_id, api_key, max_wait=120):
    for _ in range(max_wait // 3):
        time.sleep(3)
        r = requests.get(
            f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=15
        ).json()
        status = r['output']['task_status']
        if status == 'SUCCEEDED':
            return r['output']['results'][0]['url']
        elif status in ('FAILED', 'UNKNOWN'):
            return None
    return None
```

### CRITICAL: Use Reference Image for Style Consistency

**Without** a reference image, each generation produces a different art style. **With** `ref_image_url`, the model anchors to the reference style.

```python
# Read reference image as base64 data URI
with open('reference.png', 'rb') as f:
    ref_b64 = base64.b64encode(f.read()).decode()
ref_uri = f'data:image/png;base64,{ref_b64}'

# Submit with reference
resp = requests.post(SUBMIT_URL,
    headers={...},
    json={
        'model': 'wanx-v1',
        'input': {
            'prompt': 'the same character, sleeping pose with closed eyes',
            'ref_image_url': ref_uri  # <-- KEY PARAMETER
        },
        'parameters': {'n': 1, 'size': '1024*1024'}
    }, timeout=30)
```

### Pitfalls

1. **`wan2.7-image` model name does NOT work** — use `wanx-v1`
2. **Model is async** — must submit task, then poll for result
3. **Generate at 1024x1024**, then resize down (e.g., 256x256 with `sips`)
4. **Pose control is imprecise** — the model often ignores specific pose prompts (e.g., "sleeping" may still show open eyes). Use very explicit prompts like "eyes fully closed, sleeping face"
5. **Style drift still happens** even with reference images — some outputs may be 2D flat while others are 3D render
6. **No seed control** available in the API

### Resize with macOS sips

```python
import subprocess
subprocess.run(['sips', '-z', '256', '256', input_path, '--out', output_path],
               capture_output=True, timeout=10)
```

## Approach 2: Draw Things (Local macOS App)

Draw Things has an HTTP API server compatible with Automatic1111's `/sdapi/v1/txt2img`.

### Enable Server

In Draw Things: **Settings → HTTP API Server → Enable, Protocol: HTTP, Port: 7860**

### CRITICAL Pitfalls — Causes Crashes

**FLUX models WILL CRASH Draw Things** if you send incompatible parameters:

| Parameter | FLUX Safe? | SD 1.5/SDXL Safe? |
|-----------|-----------|-------------------|
| `cfg_scale` | ❌ CRASH | ✅ |
| `negative_prompt` | ❌ CRASH | ✅ |
| Resolution 256x256 | ❌ CRASH | ✅ |
| Resolution 512x512 | ❌ May crash | ✅ |

**For FLUX models**: Use native resolution (1024x1024), no cfg_scale, no negative_prompt.
**Or switch to SD 1.5/SDXL** model first, then use standard parameters.

### Safe Request Format (for SD models)

```python
payload = {
    "prompt": prompt,
    "negative_prompt": negative,
    "width": 512, "height": 512,
    "steps": 15, "cfg_scale": 7.5,
    "seed": 42
}
resp = requests.post("http://localhost:7860/sdapi/v1/txt2img", json=payload, timeout=180)
```

### MCP Tool

`mcp-drawthings` npm package provides an MCP server. Install: `npm install -g mcp-drawthings`

## Approach 3: Pillow Fallback (No API Needed)

For simple pixel/vector-style sprites when no AI API is available. Use `PIL.ImageDraw` to programmatically draw characters. Quality is basic but consistent.

## Adding a Character to FocusPaw Extension

When adding a new character to the FocusPaw browser extension:

1. **Create sprites** in `assets/<charname>/` (8 states: idle, attentive, remind, reward, pet, sleep, blink, walk)
2. **Register in `content/cat-ui.js`** — add to `CHARACTERS` object with name, avatar emoji, and sprite URLs
3. **Add panel button** — add `<button class="char-btn" data-char="<name>">` in the `createPanel()` HTML
4. **Add AI prompts** in `background/ai-provider.js` — update all 6 prompt functions: `chatSystemPrompt`, `sceneSystemPrompt`, `sceneUserPrompt`, `pageSystemPrompt`, plus error/catch messages
5. **Update `manifest.json`** — add `assets/<charname>/*` to `web_accessible_resources`
