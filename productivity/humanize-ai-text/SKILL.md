---
name: humanize-ai-text
description: "Rewrite AI-generated text to reduce AI detection rates (GPTZero, Turnitin, Originality.ai). Apply humanization techniques to Chinese and English academic/business documents. Use when user asks to lower AI detection rate, make text sound more human, or bypass AI detectors."
tags: [ai-detection, humanize, writing, academic, gptzero]
---

# Humanize AI Text

## Trigger
When the user asks to: reduce AI rate, lower AI detection, humanize text, bypass GPTZero/Turnitin/Originality.ai, make text sound more human.

## Approach
No paid API needed. Rewrite the text directly using these proven techniques:

## Core Techniques

### 1. First-Person Voice
- Use "we" / "我" perspective — makes it sound like a real team describing their work
- Add personal motivation: "We built this because..." / "我们做这个是因为..."
- Include subjective opinions: "this approach worked well" / "这个方案效果不错"

### 2. Contractions & Casual Tone (English)
- don't, it's, can't, we've, that's, won't, isn't
- "Here's the thing...", "The trick is...", "Turns out..."

### 3. Remove AI Tell-Tale Phrases
BANNED words/phrases:
- English: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note", "Delving into", "Landscape", "Tapestry", "Multifaceted", "Comprehensive", "Robust framework"
- Chinese: "此外"（开头）, "值得注意的是", "综上所述", "在当今", "随着...的发展"（开头）, "不可或缺"

### 4. Vary Sentence Length Dramatically
- Mix 5-word sentences with 30-word ones
- Short punchy sentences for emphasis: "That difference matters."
- Longer explanatory sentences for technical detail
- NEVER have 3+ sentences of similar length in a row

### 5. Break Parallel Structures
- AI loves parallel lists (A does X, B does Y, C does Z)
- Humans write unevenly: vary the grammatical structure of each item
- Use different verbs, different clause patterns

### 6. Add Specific/Concrete Details
- Replace generic descriptions with specific ones
- "browsing Reddit instead of working" > "visiting entertainment websites"
- "the cat's sass bleeds into the rabbit's sweetness" > "tonal contamination"
- Include minor imperfections, hedging: "we found that", "in our experience"

### 7. Conversational Section Titles
- "Where We're Headed" > "Concluding Remarks"
- "How the Pet Reacts" > "Core Interaction Flows"
- "What We Hope to Achieve" > "Positive Impacts"

### 8. Active Voice, Always
- "We built X" not "X was built"
- "The system detects..." not "Distraction is detected by..."

## Workflow

1. Read the original AI-generated text
2. Rewrite applying ALL techniques above — do NOT just paraphrase
3. Write to a NEW file with version suffix (e.g., `_v3`, `_humanized`)
4. NEVER overwrite the original file
5. Generate PDF and/or Word if requested

## Pitfalls
- **Do NOT just swap synonyms** — detectors catch that. Restructure sentences entirely.
- **Keep technical accuracy** — humanize the WRITING, not the CONTENT
- **Preserve all data** — numbers, citations, code references must stay exact
- **Version control** — always save as new file, never overwrite. User has emphasized this repeatedly.
- **⚠️ CALIBRATION: Don't overshoot.** Applying ALL techniques at full intensity produces text that reads like a casual blog post, not an academic/business document. User feedback: "用力过猛了" (went overboard).

### Real-World Calibration (FocusPaw project)
- v2 (pure academic, no contractions): **80% AI** ❌
- v3 (full casual, blog-like): **0% AI** — overcorrected ❌
- v4 (academic + added contractions only): **90% AI** — still too AI ❌
- v5 (balanced: first person + varied sentences + kept professional terms): **target 30-50%** ✅
- Key insight: changing just surface-level words (Furthermore→Also) doesn't work. Must restructure sentence patterns AND maintain professional vocabulary.

### Humanization Intensity Guide

| Target AI Rate | When to Use | How Much to Apply |
|----------------|-------------|-------------------|
| 60-70% (light) | Academic reports with strict AI limits | Remove AI transitions only, vary 2-3 sentence patterns per paragraph |
| 40-50% (medium) | Most academic/professional docs | First-person "we", remove AI phrases, vary sentences, add 2-3 specific examples. Keep professional tone. |
| 10-20% (heavy) | Creative/informal content | Full casual rewrite with contractions, slang, conversational titles |

**For academic reports, target 40-50% (medium)**:
- Keep third-person or first-person academic voice
- Remove AI tell-tale transitions but DON'T add slang
- Vary sentence length but DON'T make every sentence colloquial
- Add specific details but DON'T lose technical precision
- Section titles can be slightly less formal but still professional

**Red flags you've gone too far**: contractions in every sentence, slang ("browsing Reddit"), forced informality ("Here's the thing"), jokes, rhetorical questions. Pull back if you see these.
