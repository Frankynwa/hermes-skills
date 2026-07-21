# Douyin Page Scraping via Selenium

## Problem

Douyin web pages are protected by `byted_acrawler` JavaScript anti-bot verification.
Plain HTTP requests (`curl`, `requests`, `urllib`) return a verification page with no video content.
The `yt-dlp --dump-json` description field is truncated (web version adds "版本过低，升级后可展示全部信息").

## Solution: Headless Selenium + Chrome

Install:
```bash
pip install selenium
```

Chrome must be installed on the system. No chromedriver download needed — Selenium 4+ manages it automatically.

### Minimal Script

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

driver = webdriver.Chrome(options=options)
driver.get("https://www.douyin.com/video/<VIDEO_ID>")
time.sleep(10)  # Wait for JS rendering

page_text = driver.find_element(By.TAG_NAME, "body").text
print(page_text)
driver.quit()
```

### What You Get from page_text

The `document.body.innerText` output includes (in order):

1. **Navigation bar** — 精选/推荐/搜索/关注 etc.
2. **搜索栏热词** — Often reveals the product/app name being promoted (e.g., "mirofish自动推演软件")
3. **Video title and full description** — Complete, not truncated
4. **Engagement stats** — 点赞/评论/收藏/转发 counts
5. **Creator info** — Name, follower count, total likes
6. **发布时间** — Exact publish timestamp
7. **评论区** — Top visible comments (limited without login)
8. **大家都在搜** — Related trending searches (often the product name)
9. **推荐视频** — Related video recommendations with descriptions
10. **Page footer** — Legal, links, etc.

### Key Patterns for Parsing

```
# Product/app name often appears in:
- "大家都在搜：" line
- Search bar placeholder text
- Video description hashtags

# Comments format:
username
comment text
time · location
```

### Anti-Crawler Notes

- The `byted_acrawler` system runs JS on page load to generate cookies and a signature.
- Selenium with a real Chrome binary handles this automatically.
- `--headless` mode works fine; no need for visible browser.
- `time.sleep(10)` is essential — Douyin's JS needs time to render the SPA content.
- For age-gated content, you may need to pass `--cookies-from-browser chrome`.

### Douyin Short Link Resolution

Short links like `https://v.douyin.com/xxxxx/` redirect to `https://www.douyin.com/video/<ID>`.
`yt-dlp` handles this automatically. For Selenium, resolve the short link first:

```python
import urllib.request
req = urllib.request.Request("https://v.douyin.com/xxxxx/", method='HEAD')
req.add_header('User-Agent', 'Mozilla/5.0')
resp = urllib.request.urlopen(req, timeout=10)
video_url = resp.url  # Full resolved URL
```

## Session-Verified On

- macOS 26.5.1, Apple Silicon, Chrome installed, Selenium 4
- Date: 2026-06-21
- Two Douyin videos successfully scraped with full metadata
