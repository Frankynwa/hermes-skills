---
name: embedded-ui-html-prototype
description: Use HTML/CSS/JS as primary prototyping tool for embedded UI (LVGL etc.) instead of native simulators. Avoids crashes, slow cycles. Include shell heredoc pattern for safe file writing.
version: 1.0.0
---

# Embedded UI HTML Prototype

When developing LVGL or embedded UI, use HTML/CSS/JS as the primary prototyping tool instead of native simulators. This avoids:
- Simulator crashes (memory, graphics driver, SDL issues)
- Slow compile-test cycles
- Debugging environment quirks instead of UI logic

## Workflow

1. Create HTML prototype matching the embedded device dimensions (e.g., 800×480)
2. Use a dark theme matching the target device aesthetic
3. Replicate all navigation levels and sub-pages
4. Use Chart.js CDN for chart widgets
5. Verify all interactions in the browser
6. Once design is finalized, translate to C/LVGL code

## Critical: File Writing Method

**NEVER use `write_file` for complex HTML/JS with nested quotes.** Python string escaping mangles `\\`, `\"`, `\'` across three nesting levels (Python → file → JS string literal).

**ALWAYS use shell heredoc:**

```bash
cat > /path/to/file.html << 'HTMLEOF'
...content here, no escaping needed...
HTMLEOF
```

The single-quoted heredoc delimiter (`'HTMLEOF'`) prevents all shell expansion — content is written exactly as-is.

## HTML/CSS Conventions for Embedded UI

- Container: fixed 800×480 or device dimensions
- Font: monospace (matches embedded font constraints)
- Dark theme: bg #000, bg2 #1a1a1a, accent #ff8c00
- Navigation: sidebar (130px) + content area
- Inner navigation: tabs or inner sidebar (120px)
- Use event delegation on parent container for click handling
- Separate HTML structure from JS logic (external .js file)

## JS Patterns

- Use `data-*` attributes for delegated click targets instead of inline `onclick`
- Attach one event listener to the page container, check `e.target.dataset.xxx`
- Use `function()` instead of arrow functions for broader compatibility
- Chart.js charts need `setTimeout` to ensure canvas elements exist
