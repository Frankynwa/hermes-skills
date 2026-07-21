# Fluke Power Quality Analyzer — Competitive UI Design Patterns

## Core Design Language

- **Phase colors**: Yellow (L1), Green (L2), Red (L3), Blue/Purple (N) — consistently applied across all views
- **Accent color**: Orange (#FF8C00) for selected items, highlights
- **Background**: Dark theme (#000000 / #1A1A1A / #252525)
- **Font**: Monospace on engineering instruments, clean sans-serif on newer models

## Key UI Patterns Worth Borrowing

### 1. Phase-Colored Data Cards
Each phase gets a bordered card with subtle phase-color background:
- Top-left: Phase label (L1/L2/L3/N) in phase color
- Large value in white
- Small unit label in dim gray
- Example: Fluke 435 overview screen

### 2. Event Count Badges
Color-coded badges showing event counts by type:
- Dip (Yellow), Swell (Green), Transient (Red), Harmonic (Orange)
- Large number + small label, arranged in a row
- Serves as both status indicator and navigation hint

### 3. Mini Trend Sparklines
Small embedded charts (60 data points) on the overview page:
- Phase-colored traces
- Shared Y-axis range
- Gives at-a-glance trend without switching pages

### 4. Central Frequency Readout
Large, centered frequency display (e.g., "50.01 Hz") in accent color:
- Positioned as the focal point between phase cards and power summary
- Common on Fluke 435/438

### 5. REC Indicator
Red-badge recording indicator in status bar:
- Red background (#FF4444) + white "REC" text
- Small rounded rectangle, always visible
- Optionally shows recording timer

### 6. Softkey Navigation (Fluke-specific)
Fluke uses F1-F4 softkeys at the bottom of the screen, not a sidebar.
UT285E uses a sidebar — this is a deliberate design choice, not a gap.

## Models Referenced

- Fluke 435 Series II: Power Quality and Energy Analyzer
- Fluke 438-II: Power Quality and Motor Analyzer
- Fluke 1770 Series: Touchscreen power quality analyzer

## UT285E Adaptations Made

| Fluke Pattern | UT285E Adaptation |
|--------------|-------------------|
| Phase-colored data cards | 4 cards in 2×2 grid on overview |
| Event count badges | 4 badges (Dip/Swell/Trans./Harm.) with phase colors |
| Mini trend chart | 60-point LVGL chart on overview |
| Central frequency | Large "50.01 Hz" in COLOR_ACCENT |
| REC indicator | Red-badge REC in status bar |
| Phase colors | COLOR_L1/L2/L3/N already match Fluke |
