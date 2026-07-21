# Status Bar for Instrument UI

Reference implementation for an 800×480 instrument display status bar.

## Layout

```
┌──────────────────────────────────────────────────┐
│ MEM 12% ▓▓░░░  2025-11-11 14:54:51  三相星形 REC ⋰ ⏻│
└──────────────────────────────────────────────────┘
```

## HTML Structure

```html
<div class="bar">
  <!-- MEM with mini progress bar -->
  <span class="bar-mem">
    <span class="mem-label">MEM</span>
    <span class="mem-pct">12%</span>
    <span class="bar-mem-bar"><span class="fill" style="width:12%"></span></span>
  </span>
  <!-- Flex spacer pushes time to center -->
  <span class="time">2025-11-11 14:54:51</span>
  <!-- Connection mode -->
  <span class="bar-mode">三相星形</span>
  <!-- REC indicator: red background -->
  <span class="bar-rec">REC</span>
  <!-- WiFi icon: CSS arcs + dot -->
  <span class="bar-wifi">
    <span class="arc arc3"></span>
    <span class="arc arc2"></span>
    <span class="arc arc1"></span>
    <span class="dot"></span>
  </span>
  <!-- Battery: CSS rectangle -->
  <span class="bar-batt">
    <span class="batt-body"><span class="batt-fill" style="width:100%"></span></span>
    <span class="batt-cap"></span>
  </span>
</div>
```

## CSS Sizing Reference

- Bar height: 28px
- Content area: flex:1 (fills remaining after bar + possible soft keys)
- Total sim height: 480px
- Bar uses flexbox row with no-wrap items

## Dynamic Updates (JS)

```javascript
// Time: update every second
setInterval(function() {
  document.getElementById('bar-time').textContent =
    '2025-11-11 '+new Date().toTimeString().slice(0,8);
}, 1000);

// Memory: simulate 10-15% fluctuation every 3s
setInterval(function() {
  var pct = 10 + Math.floor(Math.random() * 6);
  document.getElementById('mem-pct').textContent = pct + '%';
  document.getElementById('mem-fill').style.width = pct + '%';
}, 3000);
```
