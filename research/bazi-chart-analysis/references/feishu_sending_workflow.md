# Feishu Long Content Sending Workflow

## Problem
Feishu messages have a ~4000 character limit. Long BaZi analysis (often 10,000+ chars) gets silently truncated. User sees nothing or partial content.

## Solution: File + Image Workflow

### Step 1: Save content as file
```python
# Save as .md for text analysis, .html for visualizations
write_file(path="/Users/wangruifan/Desktop/八字分析.md", content=full_text)
```

### Step 2: Send file via lark-cli
```bash
# CRITICAL: Use relative paths! cd to directory first.
cd /Users/wangruifan/Desktop && lark-cli im +messages-send --file "八字分析.md" --user-id ou_1e6a1b2ebfe154d5b0470b6f003ecd06 --as bot
```

### Step 3: For visual charts, screenshot and send image
```bash
# 1. Open HTML in browser
browser_navigate(url="file:///Users/wangruifan/Desktop/chart.html")

# 2. Take screenshot
browser_vision(question="截图")

# 3. Send screenshot
cd /Users/wangruifan/.hermes/cache/screenshots && lark-cli im +messages-send --image "screenshot.png" --user-id ou_1e6a1b2ebfe154d5b0470b6f003ecd06 --as bot
```

### User's Feishu ID
`ou_1e6a1b2ebfe154d5b0470b6f003ecd06`

## Pitfalls
- **Absolute paths rejected**: lark-cli `--file` and `--image` only accept relative paths. Always `cd` to the directory first.
- **User ID typo**: `ou_1e6a1b2ebfe154d5b0470b6f003ecd06` — note the `ebfe` not `befe`. One typo = 400 error.
- **Chart.js CDN**: Must load from CDN (`https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`). Won't work offline.
- **Browser screenshots**: Use `browser_vision` for screenshots, not terminal tools. The screenshot path is in the response.
