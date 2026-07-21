---
name: draw-things-integration
description: Programmatically generate images using Draw Things (macOS local AI image generation app). Covers HTTP API, MCP server, gRPC, CLI tools, and JavaScript scripting API. Use when the user wants to generate images via Draw Things from the terminal or agent.
tags: [image-generation, draw-things, macos, ai-art, mcp, grpc]
---

# Draw Things Integration Guide

Draw Things is a macOS native app for local AI image generation (Stable Diffusion, FLUX, etc.) at `/Applications/Draw Things.app`.

## Prerequisites

1. Draw Things must be **running** with a **model loaded**
2. The **HTTP Server** must be enabled: Settings → Local Server (or API Server)
3. Default port: **7860** (Automatic1111 WebUI-compatible API)

## Method 1: HTTP API (Recommended for scripts)

Draw Things exposes an Automatic1111-compatible REST API on port 7860.

```bash
# Check if server is running
curl -s http://localhost:7860/  # returns current config JSON

# Generate image via txt2img (safe for SD 1.5 / SDXL models)
curl -X POST http://localhost:7860/sdapi/v1/txt2img \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cute chibi panda rabbit, white fluffy body, black ears, kawaii",
    "negative_prompt": "realistic, ugly, blurry",
    "width": 512,
    "height": 512,
    "steps": 20,
    "cfg_scale": 7.5,
    "seed": 42
  }'

# ⚠️ For FLUX models: remove negative_prompt, cfg_scale, sampler_name
# ⚠️ Use 1024x1024 for FLUX (or it may crash)
```

**Resize output with macOS sips:**
```bash
sips -z 256 256 input.png --out output.png
```

The response contains base64-encoded images in `images[]`.

## Method 2: MCP Server (for Hermes Agent)

Installed globally: `npm install -g mcp-drawthings`

```bash
# Binary location
/opt/homebrew/bin/mcp-drawthings

# Environment variables
DRAWTHINGS_HOST=localhost  # default
DRAWTHINGS_PORT=7860       # default
DRAWTHINGS_OUTPUT_DIR=~/Pictures/drawthings-mcp  # default
```

Tools available: `generate-image`, `check-status`, `get-config`, `transform-image`

To use with Hermes, add to config.yaml under `mcp.servers`:
```yaml
mcp:
  servers:
    drawthings:
      command: mcp-drawthings
      env:
        DRAWTHINGS_PORT: "7860"
```

## Method 3: gRPC Server

Draw Things has a built-in gRPC `ImageGenerationService`. Uses Bonjour/mDNS for service discovery (service type: `_grpc._tcp`).

Client tools:
- `stainboy/drawthings-cli` — Go CLI (`go install github.com/stainboy/drawthings-cli@latest`)
- `Jokimbe/ComfyUI-DrawThings-gRPC` — ComfyUI integration

## Method 4: JavaScript Scripting API

Draw Things supports JS scripts (menu: Scripts). File format:
```javascript
//@api-1.0
// Available objects: canvas, pipeline, filesystem

// Generate image
var result = pipeline.run({
  prompt: "your prompt here",
  negativePrompt: "negative prompt",
  configuration: {
    width: 256,
    height: 256,
    steps: 20,
    guidanceScale: 7.5,
    seed: 42
  }
});

// Save image
canvas.saveImage(filesystem.pictures.path + "/output.png");
canvas.clear();
```

Script docs: `/Applications/Draw Things.app/Contents/Resources/js-doc-header.js`

## ⚠️ CRITICAL: FLUX Model Crash Pitfall

**FLUX models (flux_1_schnell, flux_2_klein, etc.) WILL CRASH Draw Things when called via HTTP API with standard Stable Diffusion parameters.** This was discovered through repeated testing.

**DO NOT send these parameters with FLUX models:**
- `cfg_scale` — FLUX does not use classifier-free guidance the same way SD does
- `negative_prompt` — FLUX does not support negative prompts
- `sampler_name` — may be incompatible with FLUX's flow-matching scheduler
- Low resolution (256×256, 512×512) — FLUX is trained for 1024×1024

**Safe FLUX API request format (untested — may still crash):**
```json
{
  "prompt": "your prompt",
  "width": 1024,
  "height": 1024,
  "steps": 4,
  "seed": 42,
  "batch_size": 1
}
```

**Recommended approach for small sprites (≤512px):**
1. Switch to an **SD 1.5** or **SDXL Turbo** model in Draw Things first (lighter, more stable)
2. Or generate at 1024×1024 and resize with `sips -z 256 256 input.png --out output.png`
3. Every crash kills the Draw Things server — user must manually restart and re-enable HTTP Server

**Models confirmed to crash via HTTP API:** `flux_2_klein_base_4b_i8x.ckpt`, `flux_2_klein_4b_q6p.ckpt`

## Troubleshooting

- **No port open**: Server needs to be enabled in-app AND a model must be loaded
- **Server crashes on txt2img**: Usually FLUX + incompatible params. Switch to SD 1.5/SDXL model, or remove cfg_scale/negative_prompt
- **Preferences location**: `~/Library/Containers/com.liuliu.draw-things/Data/Library/Preferences/com.liuliu.draw-things.plist`
- **Check prefs**: `defaults read com.liuliu.draw-things` — look for `HTTPServerEnabled`, `ServerEnabled`, `LocalServerEnabled`
- **Account error**: `[UserAccount] bad response` in logs is normal for non-logged-in users
- **Port conflict**: If 7860 is taken, Draw Things may use a different port — check with `lsof -i -P -n | grep DrawThings`
- **Server not restarting after crash**: Must manually reopen Draw Things app and re-enable HTTP Server toggle

## Other Tools (GitHub)

- `daveschumaker/draw-things-proxy` — NodeJS Express proxy
- `Alexthestampede/dtline` — CLI for AI agents
- `james-see/mcp-drawthings` — MCP server source
