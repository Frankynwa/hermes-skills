---
name: embedded-hw-sw-gap-analysis
description: Use when integrating embedded Linux software with custom hardware — systematically cross-reference schematics, SoC datasheets, UI design PDFs, and codebase to extract hardware information gaps that block deployment.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [embedded, hardware, gap-analysis, linux, device-tree, lvgl]
    related_skills: []
---

# Embedded Hardware-Software Gap Analysis

## When to Use

- You're integrating software with a custom embedded board (RK3568, STM32, i.MX, etc.)
- User provides schematics (partial or full), SoC datasheet, UI design PDF, and existing code
- Need to identify what hardware info is confirmed vs missing vs uncertain before deployment
- User needs a clean list to send to hardware team

## Workflow

### 1. Collect All Sources

Gather every document the user has: schematics (images or PDFs), SoC datasheet, UI design specs, BOM, existing C code. Don't assume missing — cross-reference aggressively.

### 2. Extract from Schematics (Vision + Manual)

For each connector in the schematic:
- Read EVERY signal name exactly as written on each pin
- Note GPIO numbers embedded in signal names (e.g. `TP_INT_L_GPIO0_B5` → GPIO0_B5)
- Note bus names (e.g. `I2C4_SCL` → I2C4)
- Identify what's missing: signals without GPIO annotations, control circuits not on this page

### 3. Extract from SoC Datasheet (pypdf)

Search for:
- Display interface capabilities (VOP/LCDC, max resolution, pixel clock limits)
- Available IO multiplexing options for key peripherals
- Power/thermal constraints
- What the chip CAN do vs what this specific board DOES

### 4. Extract from UI Design PDF (pymupdf → vision)

- Convert PDF pages to PNG with pymupdf at 200 DPI
- Vision-analyze EACH page separately (don't batch — details get lost)
- For each page, extract: sidebar menu items (exact Chinese text), tab labels, table headers, button text, color coding
- Document page structure: what's shared across pages (status bar, sidebar) vs page-specific

### 5. Classify into Three Buckets

| Bucket | Meaning | Action |
|--------|---------|--------|
| **Confirmed** ✅ | Signal name + GPIO/bus/pin explicitly labeled in source docs | Use directly in code/device tree |
| **Missing** ❌ | Info required for function but NOT in any provided doc | User must get from hardware team |
| **Uncertain** ⚠️ | Signal visible but function/polarity/mapping unclear | List for hardware team to confirm |

### 6. For Missing Items — Specify Exact Source

Don't just say "LCD timing is missing." Say what document it comes from:
- "LCD timing table → LCD panel vendor datasheet"
- "Backlight GPIO → schematic page with LED driver circuit"
- "Touch chip model → BOM or FPC silkscreen"

### 7. Output Format

Present as three clear tables with Chinese labels for the user to forward to hardware colleagues. Keep it short — the user needs to copy-paste this into Feishu.

## Pitfalls

1. **Don't send documents as Feishu attachments for queries.** The user will tell you this explicitly. Send clean inline text they can forward directly.

2. **Don't use casual language when writing for the user's colleagues.** "拍过来就行" → wrong tone. "需确认具体的 GPIO 编号" → correct.

3. **Don't confuse SoC capability with board implementation.** The RK3568 datasheet says the chip CAN do 1920×1080 RGB — that doesn't tell you the LCD panel's timing parameters.

4. **Vision analysis of PDFs requires pymupdf conversion first.** PDFs can't be directly vision-analyzed. Use `fitz.open()` + `page.get_pixmap(dpi=200)`.

5. **Vision analysis of dense schematics needs multiple passes.** First pass: connector pinouts. Second pass: net labels and components. Third pass: any text in margins.

6. **Duplicate labels on schematic pins (e.g. same signal on 2 pins) are common in real schematics.** Note it but don't assume it's an error — it may be intentional redundancy.

## Verification Checklist

- [ ] Every connector pin signal name has been read and recorded
- [ ] GPIO numbers have been extracted from signal names where present
- [ ] SoC capability limits have been checked against board requirements
- [ ] UI design PDF has been fully analyzed page-by-page
- [ ] Differences between design spec and implementation are documented
- [ ] Missing items list specifies exact source document needed
- [ ] Uncertain items list is separated from missing items
