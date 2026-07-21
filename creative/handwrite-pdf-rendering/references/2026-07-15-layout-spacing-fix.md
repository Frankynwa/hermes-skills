# Layout Spacing Fix (2026-07-15)

## Problem
PDF output had excessive blank space: 2-3 lines between sections, blank lines on new pages.
Content that should fit on 1 page was spread across 3 pages.

## Root Causes

### 1. Heading `add_newline()` before/after
```python
# BEFORE (BAD):
if seg.type == 'heading1':
    comp.add_newline()  # extra spacing before heading
    comp.add_segment(img)
    comp.add_newline()  # extra spacing after heading

# AFTER (FIXED):
if seg.type == 'heading1':
    comp.add_segment(img)
```
Heading2 also had `add_newline()` after — removed.

### 2. `_advance_line()` gap too large
```python
# BEFORE: gap = max(4, int(LINE_SPACING * 0.2))  # ~8px
# AFTER:  gap = max(2, int(LINE_SPACING * 0.1))  # ~4px
```

### 3. `para_break` adding full blank line
```python
# BEFORE: comp.add_newline()  # adds a full blank line
# AFTER:  pass  # no extra gap — natural line break only
```

## Result
- 3 pages → 1 page
- Content density matches natural handwritten notes
- Vision model confirmed: "排版紧凑自然" (compact and natural layout)

## User Feedback
- "莫名其妙空出两三行，垃圾死了" (mysterious 2-3 line gaps, terrible)
- "排版非常丑陋" (very ugly layout)
- User wants DENSE notes, not airy layouts with "breathing room"
