# UT285E Project Reference

## HTML Prototype

When the SDL2 simulator crashes, use the HTML prototype at `ut285e/ui_prototype.html` + `ut285e/ui_prototype.js`.

### Files
- `ut285e/ui_prototype.html` — HTML + CSS (dark theme matching LVGL)
- `ut285e/ui_prototype.js` — all JS logic, Chart.js charts, event delegation

### Opening
```bash
open ut285e/ui_prototype.html
```

### Pages included (all 11)
| Page | Navigation | Content |
|------|-----------|---------|
| Overview | 5 Tabs (Realtime/Record/Trend/Table/Verify) | Data table, record list, trend chart, detail table, verify table |
| V/A/Hz | Direct | Voltage/current bars + waveform chart + phasor placeholder |
| Power | Direct | Power table + trend chart |
| Dip/Swell | 2 Tabs (Dip/Swell) | Event tables |
| Harmonics | 2 Tabs (Bar/Table) | Bar chart |
| Transient | Direct | Transient waveform chart |
| Events | Direct + filter bar | Event table with All/Dip/Swell/Transient/Harmonic filter |
| Settings | 5 Tabs + inner sidebar | Instrument/Comm/Tools/Info(6 sub-pages)/Memory(records+USB export) |
| SimpleMeas | Inner sidebar (5 items) | Verify仪表/Verify相量/Verify波形 + Config page links |
| Config | Inner sidebar (12 items) | Connection/Voltage/Ratio/Current/Flicker/K-Factor/Wye/Dip/Rise/Interrupt/Wave Dev/Transient |
| Trends | Inner sidebar (3 items) | Flicker trend chart+stats+details, Unbalance trend chart+stats, Current trend chart |

### Key techniques used
- **Event delegation**: All button clicks use `data-*` attributes and `addEventListener('click', ...)` on parent containers — NO inline `onclick` with nested quotes
- **Chart.js**: Line and bar charts with dark theme styling (black background, gray ticks, no legend)
- **Shell heredoc**: File was written via `cat > file << 'HTMLEOF'...HTMLEOF` to avoid Python string escaping issues
