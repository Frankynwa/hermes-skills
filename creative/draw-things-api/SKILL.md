---
name: draw-things-api
description: Generate images via Draw Things HTTP API on macOS. Covers connection, parameters, model pitfalls, and style-consistent sprite generation. Use when user wants to generate images locally via Draw Things or mentions Draw Things API/CLI/gRPC/MCP.
tags: [draw-things, image-generation, macos, api, sprites, local-ai]
triggers:
  - draw things
  - drawthings
  - draw-things api
  - local image generation
  - stable diffusion api
---

# Draw Things HTTP API Integration

## Prerequisites
- Draw Things app installed at `/Applications/Draw Things.app`
- HTTP Server enabled in Draw Things: **Settings → HTTP API 服务器 → Server Online toggle ON**
- Protocol must be set to **HTTP** (not gRPC)
- Default port: **7860**

## API Endpoints

### GET / — Get current config
```bash
curl -s http://localhost:7860/
```
Returns JSON with: `model`, `width`, `height`, `steps`, `sampler`, `guidance_scale`, `seed`, etc.

### POST /sdapi/v1/txt2img — Generate image
```python
requests.post("http://localhost:7860/sdapi/v1/txt2img", json={
    "prompt": "...",
    "width": 512,
    "height": 512,
    "steps": 4,
    "cfg_scale": 1.5,
    "seed": 42
})
```
Returns `{"images": ["<base64_png>", ...]}`.

### POST /sdapi/v1/img2img — Image-to-image
Same format as txt2img but with `init_images`, `denoising_strength`.

## Critical Pitfalls

### ❌ FLUX models crash the HTTP API
**Every** txt2img request to FLUX models (FLUX.1, FLUX.2 Klein, etc.) causes Draw Things to crash/disconnect. This happens regardless of parameters — even minimal requests with 5 steps at 512x512. Root cause is a bug in Draw Things' HTTP API implementation for FLUX, NOT memory.

**Workaround**: Use SDXL Turbo or SD 1.5 instead.

### ❌ FLUX-specific parameters
FLUX does NOT support:
- `negative_prompt` (ignored or crashes)
- `cfg_scale` (uses internal guidance, different mechanism)
- Standard SD samplers (uses DDIM Trailing internally)

### ✅ SDXL Turbo — Best choice for API use
- Model name in Draw Things: `sd_xl_turbo_q6p_q8p.ckpt` (8-bit quantized)
- Works perfectly with HTTP API
- Optimal params: `steps=4`, `cfg_scale=1.5`, `width/height=512`
- Very fast (~2-5 seconds per image)
- Good quality for 256x256 sprites

### ✅ SD 1.5 — Most stable fallback
- Best API compatibility
- Works with all standard parameters

## Style-Consistent Sprite Generation

To generate multiple sprites with consistent art style:

1. **Fix the seed**: Use same `seed` value for all images
2. **Same model + params**: Keep `model`, `cfg_scale`, `steps` identical
3. **Common style prefix**: Start every prompt with the same style description
4. **Vary only the pose**: Change only the pose/action description per sprite

```python
STYLE = "cute chibi cartoon panda rabbit, white body black ears, 2D flat vector, ..."

STATES = {
    "idle.png": "standing calmly, relaxed idle pose",
    "sleep.png": "sleeping peacefully, eyes closed, ZZZ",
    # ...
}

for fn, pose in STATES.items():
    prompt = f"{STYLE}, {pose}"
    # generate with fixed seed=42
```

## Post-Processing: Resize to Sprite Size

Use macOS `sips` to resize (no PIL needed):
```bash
sips -z 256 256 input.png --out output.png
```

## DashScope Wanx API (Alternative)

If Draw Things isn't available, DashScope's `wanx-v1` model works:
- Endpoint: `https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis`
- Async: Submit task → poll for result → download image
- Supports `ref_image_url` for style reference (base64 data URI works)
- **Limitation**: Style consistency is poor even with reference images; Draw Things with fixed seed is much better
