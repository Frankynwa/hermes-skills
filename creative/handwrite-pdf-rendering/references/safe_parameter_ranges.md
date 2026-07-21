# Safe Parameter Ranges for Handwrite Pipeline

These ranges were validated through extensive testing. Do NOT exceed the max values —
combining aggressive perturbation with scan effects destroys formula legibility.

## Perturbation Strength

| Rendering Path | Min | Recommended | Max | Notes |
|---|---|---|---|---|
| PIL per-char (simple formulas) | 0 | **0 (NONE)** | 0 | ⚠️ ZERO — per-char jitter is sufficient, any perturbation blurs |
| matplotlib (complex formulas) | 0 | **0 (NONE)** | 0 | ⚠️ ZERO — clean rendering only, perturbation destroys symbols |
| Text (English via handright) | 0.5 | 1.0 | 1.5 | handright's own perturbation is the primary mechanism |
| Text (Chinese via PIL v2) | 0 | **0 (NONE)** | 0 | Per-char jitter provides enough naturalness |

**v10 LESSON: Formula perturbation must be ZERO.** User was extremely frustrated
when perturbation+scan effects made formulas "完全难以辨认" (completely illegible).
The v10 pipeline renders ALL formulas clean with zero perturbation.

## Scan Effects — ⚠️ DISABLED IN PRODUCTION

**Scan effects are NOT applied in the production pipeline.** They exist as an
optional function but were disabled because JPEG compression destroys formula
legibility even at quality 90. If re-enabled in the future, use these ranges:

| Parameter | Min | Recommended | Max | Notes |
|---|---|---|---|---|
| JPEG quality | 90 | 95 | 97 | Below 90 introduces visible block artifacts on formulas |
| Rotation (degrees) | ±0.3 | ±0.5 | ±0.8 | Above ±1.0 makes text noticeably tilted |
| Sharpening multiplier | 1.0 | 1.05 | 1.15 | Above 1.2x creates visible halos around strokes |
| Vignette intensity | 0.05 | 0.10 | 0.15 | Max darkening at corners |

## Paper Aging

| Parameter | Min | Recommended | Max | Notes |
|---|---|---|---|---|
| Yellowing brightness | 10 | 18 | 25 | Below 10 invisible under text; above 25 too yellow |
| Crease darken value | 6 | 12 | 18 | Per-pixel darkening along crease lines |
| Coffee stain R intensity | 0.8 | 1.2 | 1.5 | Multiplier for red channel |
| Dog-ear fold darken | 15 | 25 | 35 | Per-pixel darkening in folded corner |

## Per-Character Jitter

| Parameter | Min | Recommended | Max | Notes |
|---|---|---|---|---|
| Rotation (degrees) | ±1.5 | ±3.0 | ±5.0 | Per-character rotation jitter |
| Position X σ (pixels) | 0.5 | 1.5 | 2.5 | Horizontal position noise |
| Position Y σ (pixels) | 0.5 | 1.5 | 2.5 | Vertical position noise |
| Scale variation σ | 0.02 | 0.05 | 0.08 | Per-character size variation |
| Baseline wave amplitude | 2.0 | 3.5 | 5.0 | Sine wave amplitude for baseline |

## StudentStyle

| Parameter | Min | Typical Range | Max | Notes |
|---|---|---|---|---|
| slant (degrees) | -3 | -1 to 6 | 8 | Right-leaning is common |
| pressure | 0.3 | 0.4–0.9 | 1.0 | 0=light, 1=heavy |
| speed | 0.1 | 0.2–0.8 | 0.9 | 0=slow/careful, 1=fast/sloppy |
| neatness | 0.1 | 0.2–0.7 | 0.9 | 0=very neat, 1=very messy |
| connect_prob | 0.05 | 0.15–0.5 | 0.7 | Probability of connected strokes |

## Tested Configurations

| Config | Formula Perturb | Text Perturb | JPEG | Rotation | Sharpen | Result |
|---|---|---|---|---|---|---|
| v8 (no scan) | 0 | handright native | none | none | none | 9.5/10 ✅ |
| v9 (mild scan) | 0.8–1.0 | handright native | 90–97 | ±0.5° | 1.0–1.15 | FORMULAS DAMAGED ⚠️ |
| v9 (aggressive) | 1.8 | handright native | 78–92 | ±1.5° | 1.1–1.4 | FORMULAS ILLEGIBLE ❌ |
| **v10 (production)** | **0 (NONE)** | handright native | **none** | **none** | **none** | **All clear ✅** |
