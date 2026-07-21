# Research-Driven Optimization Methodology

## Approach

Used arXiv API to search ~50 papers (2024-2026) across three domains:
1. Handwriting text generation & synthesis
2. Font generation & glyph synthesis
3. Document layout generation & synthetic documents

Papers were categorized by technique and mapped to specific optimization opportunities
in the existing pipeline, then prioritized by implementation cost vs. expected impact.

## Key Papers & Techniques Applied

### CASHG (2604.02103) — Context-Aware Stylized Handwriting Generation
- **Technique**: Bigram-aware sliding-window Transformer decoder
- **Applied as**: 3-character seed grouping for font variant selection
- **Why**: Adjacent characters sharing variant seeds creates visual continuity

### NIV (2606.05261) — Neural Axis Variations
- **Technique**: Neural prediction of glyph variation along design axes
- **Applied as**: Conceptual inspiration for meaningful perturbation directions
- **Future**: Replace random noise with stroke-direction-aware perturbation

### DiffInk (2509.23624) — Latent Diffusion Transformer
- **Technique**: First latent diffusion Transformer for full-line handwriting
- **Not applied**: Requires pretrained model, too heavy for current pipeline
- **Future**: Could replace Graves RNN for CJK handwriting synthesis

### One-DM (2409.04004) — One-Shot Diffusion Mimicker
- **Technique**: Single reference image → style transfer to all characters
- **Not applied**: Requires diffusion model infrastructure
- **Future**: Ultimate style transfer solution

## Optimization Priority Matrix

| Priority | Item | Cost | Impact | Status |
|----------|------|------|--------|--------|
| P0 | CJK font variant coverage | Low | High | ✅ Done |
| P0 | Markdown parsing | Low | High | ✅ Done |
| P0 | Paper texture | Low | Medium | ✅ Done |
| P1 | Bigram context | Medium | High | ✅ Done |
| P1 | InkType simulation | Medium | Medium | ✅ Done |
| P1 | CJK in mathtext | Medium | Medium | ✅ Done |
| P2 | Layout intelligence | Medium | High | ✅ Done |
| P2 | Meaningful axis perturbation | High | High | Pending |
| P2 | Style transfer (One-DM) | High | High | Pending |

## Lesson: Two-Layer Optimization Thinking

**Layer 1: Pixel-level simulation** (current approach)
- Take rendered glyphs → add noise/blur/jitter
- Simple, fast, controllable
- Ceiling: glyph structure unchanged

**Layer 2: Stroke-level / semantic-level simulation** (research frontier)
- Generate stroke trajectories from scratch
- Model understands "horizontal stroke: left-to-right, heavy start, light end"
- Much higher fidelity ceiling

The optimization roadmap is about gradually moving from Layer 1 toward Layer 2.
