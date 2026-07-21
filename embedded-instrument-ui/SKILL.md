---
name: embedded-instrument-ui
description: |
  Design and prototype UIs for embedded instruments with physical buttons
  (not touchscreen). Covers LVGL-style focus navigation, Chinese localization
  patterns for DOM/data-* consistency, readability sizing for small screens,
  and configuration panel layout optimization. Load when building or modifying
  instrument UI prototypes, especially those targeting 800×480 displays with
  D-pad + MENU/BACK physical button controls.
version: 1.0.0
metadata:
  hermes:
    tags: [embedded, ui, lvgl, instrument, button-navigation, prototyping]
    category: software-development
---

# Embedded Instrument UI Design

## Core Paradigm: Physical Buttons, Not Touch

Target devices typically use:
- **D-pad**: ↑↓←→ for focus navigation, center OK to confirm
- **MENU**: Opens context menu
- **BACK**: Returns to previous screen
- **SCREEN CAPTURE**: Hardware screenshot
- No touch, no mouse, no hover states

### What this means for UI design

| Touch/Mouse UI | Physical Button UI |
|---------------|-------------------|
| Click anywhere | D-pad moves focus step by step |
| hover CSS states | `:focus-visible` focus ring only |
| Free cursor movement | Discrete tab order between elements |
| Small text fine (close view) | ≥14px for instrument viewing distance |
| Scroll freely | Pagination or "More" buttons |

### Focus Navigation Architecture

Use `data-*` attributes with English values for DOM lookups, Chinese for display text:

```javascript
// ✅ CORRECT: data-tab stays English, display is Chinese
var tabs = ['Realtime','Record','Trend'];
tabs.map(function(t) {
  return '<button data-tab="'+t+'">' +
    ({'Realtime':'实时','Record':'记录','Trend':'趋势'})[t] +
    '</button>';
});

// Event listener uses English IDs
['Realtime','Record','Trend'].forEach(function(t) {
  var el = document.getElementById('ov-'+t); // ov-Realtime, ov-Record, etc.
});
```

This pattern applies to ALL tab systems: sidebar pages, settings tabs, info subtabs,
trend selection, config panels.

## Readability Sizing for 800×480 Displays

Critical sizing rules learned from real instrument testing:

| Element | Min Size | Reason |
|---------|---------|--------|
| Sidebar buttons | 38px height, 14px font | User stands at arm's length |
| Sidebar width | ≥152px | Accommodates CJK text |
| Table text | ≥12px | Data tables must be readable |
| Chart canvas | ≤140px height | Leaves room for stats tables below |
| Config inputs | ≥13px font | Technician needs to read values |

### Chart Overflow Prevention

On a 480px vertical display with 28px status bar, content area is ~452px.
A chart at 200px leaves only ~252px for tables + headers + spacing,
which overflows when there are multiple stat tables. Reduce to 140px max.

## Config Panel Layout Optimization

For dense configuration pages with many small items, merge related fields
into single compact rows:

```javascript
// ❌ BEFORE: Two rows, redundant labels
row('Primary:','<input>')+row('Secondary:','<input>'),
row('Primary:','<input>')+row('Secondary:','<input>'),

// ✅ AFTER: One row, compact, merged
'<div class="row"><label>电压比</label><input>:<input>  <label>电流比</label><input>:<input></div>',
```

Same pattern for limit groups:
```javascript
// ✅ Dip/Swell/Interrupt in one row
'<div class="row">Dip [90%]/[2%] Swell [110%]/[2%] 中断 [10%]/[2%]</div>',
```

This reduces a 3-row section to 1 row while keeping all editable values accessible.

## Chinese Localization Checklist

When translating an instrument UI from English to Chinese:

1. **Sidebar page names** — translate labels only
2. **Tab systems** — data-* stays English, display uses lookup map
3. **match() patterns** — add Chinese keyword alternatives: `l.match(/名称|Name/)`
4. **Table headers** — translate, but keep L1/L2/L3/N as-is
5. **Button labels** — translate text content only
6. **Status bar elements** — translate labels, keep universal (REC, MEM, WiFi)
7. **Events/data entries** — translate type values (Dip→骤降) — must match filter values
8. **Dialog headers** — translate h3 text
9. **Info/Sensor sub-labels** — translate but keep key patterns (SSID, MAC, IP)

## Common Pitfalls

### Pitfall 1: Translating data-* values
Never translate `data-tab`, `data-stab`, `data-sitab`, `data-trtab`, `data-cftab`
values to Chinese. These must match DOM IDs which are English. Only translate
the display text via a lookup map.

### Pitfall 2: match() patterns break after translation
Labels like "仪器名称:" won't match `/Name/`. Always use bilingual patterns:
`l.match(/名称|Name/)`.

### Pitfall 3: Soft key bars only useful for programmable F-keys
Devices with fixed-label buttons (MENU, BACK, SCREEN CAPTURE) don't need
soft key bars. Unlike Fluke 435 (F1-F4 programmable), UT285E has fixed functions
printed on each button. Adding on-screen labels that just repeat the printed label
is redundant.

### Pitfall 4: read_file in execute_code includes line prefixes
When using `read_file` inside `execute_code`, the returned `content` field
contains line number prefixes like `  123|content`. These must be stripped
before writing back. Use standalone Python scripts via `terminal` for file
transformations instead.
