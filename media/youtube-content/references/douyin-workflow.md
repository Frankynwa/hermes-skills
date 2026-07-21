# Douyin/抖音 Video Summarization Workflow

## URL Patterns

- Share link: `https://v.douyin.com/xxxxx/` (short redirect, most common from mobile share)
- Web link: `https://www.douyin.com/video/xxxxxxxxxxxx`
- Both are handled by yt-dlp

## Step-by-Step

### 1. Download audio only (fastest)

```bash
yt-dlp -x --audio-format mp3 --no-playlist \
  -o "/tmp/douyin_%(id)s.%(ext)s" \
  "https://v.douyin.com/xxxxx/"
```

Output: `/tmp/douyin_<video_id>.mp3`

### 2. Extract video metadata

```bash
yt-dlp --dump-json --no-playlist "URL" 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'标题: {d.get(\"title\",\"\")}')
print(f'作者: {d.get(\"channel\",d.get(\"uploader\",\"\"))}')
print(f'时长: {d.get(\"duration_string\",\"\")}')
print(f'点赞: {d.get(\"like_count\",\"N/A\")} · 评论: {d.get(\"comment_count\",\"N/A\")} · 收藏: {d.get(\"save_count\",\"N/A\")} · 转发: {d.get(\"repost_count\",\"N/A\")}')
print(f'话题: {d.get(\"description\",\"\")[-200:]}')
"
```

Always include creator + engagement stats in the summary header — users find this useful context.

### 3. Transcribe with Whisper

```bash
# CLI (local) — base model is fine for short videos (< 60s)
whisper /tmp/douyin_<video_id>.mp3 --language zh --model base --output_format txt --output_dir /tmp/

# For longer videos (1min+), use medium model for better accuracy
whisper /tmp/douyin_<video_id>.mp3 --language zh --model medium --output_format txt --output_dir /tmp/

# Or via OpenAI API
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F file=@/tmp/douyin_<video_id>.mp3 \
  -F model=whisper-1 \
  -F language=zh
```

### 4. Summarize

Feed the transcript text to the LLM with a prompt like:

> 请总结以下视频内容，提取关键观点，用结构化格式输出：
> [transcript]

## Pitfalls

- **Short redirect links** (v.douyin.com): yt-dlp follows redirects automatically; no manual resolution needed.
- **Age-restricted content**: May need `--cookies-from-browser chrome` flag.
- **Very short videos** (< 30s): Whisper output may be too sparse for chapter extraction; go straight to summary. `--model base` is sufficient for short clips.
- **Music-heavy videos**: Whisper may pick up lyrics as speech. Note this to the user if the transcript seems musical.
- **No subtitles on Douyin**: Unlike YouTube, Douyin has no transcript API. Audio transcription is the only path.
- **Chinese language**: Always pass `--language zh` to Whisper for Douyin content to avoid mis-detection.
- **Whisper model choice**: `base` (139MB, ~10s for 26s clip on CPU) is fast and accurate enough for short Chinese videos. Only upgrade to `medium` if accuracy is poor on longer content.
- **Whisper FP16 warning**: `FP16 is not supported on CPU; using FP32 instead` is expected on macOS CPU — ignore it.
- **yt-dlp pip install**: Works fine (`pip install yt-dlp -q`). No brew needed.
- **Verified on macOS 26.5.1**: Full pipeline (yt-dlp → whisper base → LLM summary) works on Apple Silicon with CPU-only whisper. 26-second video: ~2s download, ~10s transcription.
- **Metadata field mapping**: `channel` = author display name, `uploader_id` = numeric user ID, `track` = original sound name, `tags` = hashtags. Engagement: `like_count`, `comment_count`, `save_count`, `repost_count`.
- **Truncated descriptions**: `yt-dlp --dump-json` returns truncated Douyin descriptions ending with `版本过低，升级后可展示全部信息`. Use Selenium headless Chrome for the complete text + comments (see "Full Page Metadata Extraction" section below).
- **Douyin anti-crawling**: Direct `curl` requests to `douyin.com` are blocked by `byted_acrawler` — returns a JS verification page. Use yt-dlp (handles it via API) or Selenium for web page access.
- **Safari/Chrome AppleScript**: Unreliable for Douyin — Safari needs "Allow JavaScript from Apple Events" enabled; Chrome AppleScript often times out. Prefer Selenium headless Chrome.

## Full Page Metadata Extraction (comments, complete description)

When `yt-dlp --dump-json` truncates the description, use Selenium to get full page content including comments:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=options)
driver.get("DOUYIN_WEB_URL")  # https://www.douyin.com/video/XXXXX
time.sleep(10)  # JS rendering
page_text = driver.find_element(By.TAG_NAME, "body").text
print(page_text)
driver.quit()
```

Output includes: full description (untruncated), hashtags, comment previews, author info, engagement stats, and related video titles.
