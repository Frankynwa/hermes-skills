---
name: douyin-video-transcription
description: "Download Douyin/TikTok videos and transcribe audio to text using yt-dlp + Whisper. Use when user shares a Douyin link and wants the content analyzed, summarized, or discussed."
platforms: [macos, linux]
---

# Douyin Video Transcription

## When to use

User shares a Douyin (抖音) or TikTok video link and wants to:
- Read/analyze the video content
- Get a transcript of what was said
- Discuss or critique the arguments in the video
- Extract key quotes or ideas

## Workflow

### Step 1: Download video with yt-dlp

```bash
cd /tmp && yt-dlp -o "douyin_video.%(ext)s" "https://v.douyin.com/XXXXX/" --no-check-certificates
```

- yt-dlp resolves Douyin short links automatically
- **⚠️ Douyin now requires fresh cookies (2026-06+).** Without cookies, you get: `Fresh cookies (not necessarily logged in) are needed`
- Workaround options:
  1. **API extraction (RECOMMENDED)** — use browser console to fetch video URL from Douyin's detail API. This works reliably even without login. See "Fallback: Browser API Extraction" section below.
  2. `--cookies-from-browser chrome` (may work if Chrome is installed and you've visited Douyin before)
  3. For content extraction without downloading: navigate browser to the Douyin page, read the "章节要点" section from the DOM (contains AI-generated chapter summaries)
- If download fails, the page DOM often contains useful metadata: title, tags, chapter summaries, engagement stats

### Step 2: Extract audio

```bash
ffmpeg -i douyin_video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 douyin_audio.wav -y
```

- 16kHz mono WAV is optimal for Whisper
- For long videos (>10 min), chunk the audio first (see below)

### Step 2.5: Detect language (CRITICAL)

**Do NOT assume the video is Chinese.** Many Douyin creators (especially overseas Chinese like 毕英杰Johnathan) speak English. Using `--language zh` on English audio produces complete garbage output.

Detection method: after extracting audio, transcribe the first 30 seconds with auto-detect:
```bash
# Extract first 30s for language detection
ffmpeg -i douyin_audio.wav -t 30 -c copy /tmp/lang_detect.wav -y

# Use Whisper WITHOUT --language flag to auto-detect
whisper /tmp/lang_detect.wav --model base --output_format txt --output_dir /tmp/lang_check 2>&1 | head -10

# Check output: if English text appears, use --language en; if Chinese, use --language zh
cat /tmp/lang_check/lang_detect.txt
```

Signs the video is **English**: recognizable English words, proper nouns in Latin script. Signs it's **Chinese**: CJK characters, or garbled output (which means you guessed wrong).

### Step 3: Transcribe with Whisper

**Model choice:**
- `tiny` — fastest, but **only use for Chinese**. On English audio it produces significantly worse output.
- `base` — good balance for English content. ~2x slower than tiny but much better quality. **Use this for English or unknown languages.**
- `small`/`medium` — better quality but TOO SLOW on CPU for videos >5 min.

**For short audio (<10 min):**
```bash
# Chinese video
whisper douyin_audio.wav --model tiny --language zh --output_format txt --output_dir /tmp/whisper_out

# English video (use base model!)
whisper douyin_audio.wav --model base --language en --output_format txt --output_dir /tmp/whisper_out
```

**For long audio (>10 min) — MUST chunk first:**
```bash
# Split into 5-minute segments
ffmpeg -i douyin_audio.wav -f segment -segment_time 300 -c copy /tmp/whisper_chunks/chunk_%03d.wav -y

# Transcribe each chunk (adjust --language based on Step 2.5)
for f in /tmp/whisper_chunks/chunk_*.wav; do
  whisper "$f" --model base --language en --output_format txt --output_dir /tmp/whisper_out
done

# Merge results
cat /tmp/whisper_out/chunk_*.txt > /tmp/full_transcript.txt
```

### Step 4: Clean up and deliver

- For Chinese: transcript will be in **traditional Chinese** (Whisper's default for `--language zh`). Convert to simplified if needed. Whisper `tiny` on Chinese produces readable but error-prone output (proper nouns, names, and uncommon terms will be mangled). For names mentioned in the video (e.g., guest names, brand names), cross-reference the video title/chapter summary from the browser extraction step to correct them.
- For English: clean up obvious transcription errors (proper nouns, technical terms).
- Present the key arguments in structured form to the user.
- If user wants Obsidian notes, combine with the `obsidian` skill (see "Video → Obsidian Notes Workflow" below).

**Workflow decision tree:**
1. **First**: Try quick content check (章节要点) — takes ~10s per video
2. If chapter summary is sufficient → stop, present to user
3. If user explicitly wants full transcript → proceed with download+transcription
4. Don't automatically download+transcribe when the user shares links — they may only need the summary

## Quick Content Check (No Download)

When the user shares a Douyin link and just wants to know what the video is about (not a full transcription), use the **browser approach** — much faster than downloading + Whisper:

```python
# 1. Navigate to the Douyin page
browser_navigate(url="https://v.douyin.com/XXXXX/")

# 2. Extract chapter summary + metadata via JS (preferred over snapshot)
browser_console(expression="""
const allText = document.body.innerText;
const idx = allText.indexOf('章节要点');
if (idx >= 0) {
  allText.substring(idx, idx + 3000);
} else {
  '章节要点 not found';
}
""")
```

**Why `browser_console` over `browser_snapshot(full=True)`**: The snapshot is often truncated at ~8000 chars and misses the chapter summary section. Direct JS extraction of `document.body.innerText` reliably captures: chapter timestamps, chapter titles, title/hashtags, engagement stats, and top comments.

The **"章节要点" (chapter summary)** section contains a concise AI-generated summary of the video content with timestamps. This is often sufficient to answer "what is this video about" or "is this claim true."

**PITFALL**: Douyin may show a CAPTCHA slider. Even with CAPTCHA visible, the page content (title, chapter summary, tags) is already loaded in the DOM and readable from `document.body.innerText`. Don't try to solve the CAPTCHA — just read the content around it.

## Fallback: Browser API Extraction (when yt-dlp fails)

When yt-dlp fails due to cookies, use the browser to extract the video download URL from Douyin's internal API.

**CRITICAL: Same-origin requirement.** The detail API fetch MUST run from within the douyin.com page context (same origin). If you've navigated away, the browser state may have changed — re-navigate to `https://www.douyin.com/video/{VIDEO_ID}` first. CORS blocks cross-origin requests to this endpoint.

**PITFALL: Variable reuse across browser_console calls.** Each `browser_console` call shares the same JS execution context. Declaring `const scripts` in one call and again in a later call throws `SyntaxError: Identifier 'scripts' has already been declared`. Always use unique variable names or wrap in an IIFE `(() => { ... })()`.

**PITFALL: RENDER_DATA exists but doesn't contain video URLs.** The `<script id="RENDER_DATA">` element on Douyin pages contains URL-encoded JSON with app-level metadata (browser info, config, etc.) but NOT the actual video stream URLs. Video data is loaded via XHR after page load. Don't waste time decoding it for video URLs.

**PITFALL: Performance entries don't capture video streams.** `performance.getEntriesByType('resource')` only shows player JS files (player-0.js through player-8.js), not the actual .mp4 stream URLs. The video is loaded via XHR/MSE into blob URLs, and those network entries aren't surfaced by the performance API.

**PITFALL: Mobile API (iesdouyin.com) no longer works.** The old endpoint `https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/` returns status 11110 with empty data. Use the web detail API instead.

```javascript
// 1. MUST be on the douyin.com video page first
// browser_navigate("https://www.douyin.com/video/{VIDEO_ID}")

// 2. Extract video URL from the detail API (runs in page context with cookies)
fetch('/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=VIDEO_ID_HERE&request_source=600&origin_type=video_page&update_version_code=1704', {
  credentials: 'include'
}).then(r => r.json()).then(data => {
  const video = data.aweme_detail?.video;
  window.__videoResult = JSON.stringify({
    desc: data.aweme_detail?.desc,
    duration: video?.duration,
    playUrls: (video?.play_addr?.url_list || []).slice(0, 3)
  });
});
```

**PITFALL: Fetch returns a Promise.** After calling `fetch(...)` in browser_console, the result isn't immediately available. Either use `await` (if the console supports top-level await) or store in `window.__videoResult` and read it in a second `browser_console` call.

Then download with curl using the Referer header:
```bash
curl -L -o /tmp/douyin_video.mp4 "{PLAY_URL}" -H "Referer: https://www.douyin.com/" --progress-bar
```

**PITFALL: Partial downloads.** The video URL is signed and may expire or throttle. If the downloaded file is shorter than expected (check with `ffprobe` or compare duration), try a different URL from the `playUrls` array, or re-extract fresh URLs. A 20-min video should be ~100-150MB at 720p.

When the user wants to save video content as structured notes in Obsidian, combine this skill with the `obsidian` skill:

1. Extract content via browser approach (chapter summary + comments)
2. For deeper content: delegate parallel subagent research on the topic
3. Write structured note to `~/Documents/Obsidian Vault/视频笔记/{platform}/{title}.md`
4. Use the template at `templates/视频笔记模板.md` (YAML frontmatter + sections)
5. Include wikilinks `[[related topics]]` for cross-referencing

**Note structure** (proven format): 核心观点 → 详细笔记(按章节) → 金句摘录 → 我的思考 → 相关链接.

- See `references/douyin-api.md` for Douyin internal API endpoint details, response structure, and copy-paste-ready browser extraction scripts.

## Pitfalls

- **yt-dlp "Fresh cookies needed" (2026+)**: As of mid-2026, Douyin requires fresh browser cookies that yt-dlp cannot obtain on its own. The error is: `ERROR: [Douyin] Fresh cookies (not necessarily logged in) are needed`. Workarounds:
  1. **Preferred**: Use "Browser API Extraction" section above to get video URL via Douyin's detail API, then download with curl.
  2. **For quick checks**: Use browser approach (see "Quick Content Check" above) to get title + chapter summary without downloading.
  3. `--cookies-from-browser safari` does NOT work on macOS — Safari's Cookies.binarycookies is sandboxed and unreadable (Operation not permitted). Chrome may work if installed.
- **Whisper language mismatch (CRITICAL)**: Using `--language zh` on English audio produces **completely garbage output** — not just poor quality, but nonsensical characters. ALWAYS detect language first (see Step 2.5). This is the #1 failure mode for non-Chinese Douyin creators.
- **Whisper models and speed**: `tiny` is fastest but only good for Chinese. `base` is the minimum for English content (~2x slower). `small`/`medium` are better quality but TOO SLOW on CPU for videos >5 min.
- **ALWAYS chunk long audio**: A 22-minute video produced 40MB WAV file. Whisper `tiny` timed out at 120s on the full file but processed 5-minute chunks in ~60s each. Rule: if audio > 10 min, chunk at 300s intervals.
- **Douyin requires JS rendering**: Direct `curl` to the Douyin page returns empty content. yt-dlp handles this internally — don't try to scrape the page with curl.
- **Short link resolution**: `curl -sL -o /dev/null -w '%{url_effective}' "https://v.douyin.com/XXX/"` resolves to the full Douyin URL.
- **Traditional vs Simplified Chinese**: Whisper outputs traditional Chinese (繁体) by default for `--language zh`. If the user expects simplified, post-process with OpenCC or just present as-is — the content is readable either way.
- **Video file size**: 22-min Douyin video = 72MB MP4. Download takes ~5s on typical connection. Audio extraction to WAV = ~40MB. Plan disk space accordingly.
- **Whisper availability**: Requires `openai-whisper` package (`pip3 install openai-whisper`) and `ffmpeg`. Both are typically pre-installed on the user's macOS setup.
- **Don't try `medium` or `large` models on CPU**: They will timeout. Use `tiny` for speed, `small` if you can afford 2-3 min per 5-min chunk.
- **blob: video URLs**: Douyin serves video via `blob:` URLs in the browser — these cannot be downloaded directly. The actual video stream is loaded via XHR/MSE. Don't try to `curl` or `wget` a blob URL.

## Translation & Formatting Preferences

When the video is in English but the user wants Chinese notes:
- **Chinese-dominant translation** with key English terms preserved where Chinese "doesn't have that flavor"
- Examples of terms to keep in English: instrumental goods, mimesis, leisure, download, memetic desire, predestination, Protestant ethic
- This applies to Obsidian notes too — the user wants bilingual notes, not pure translation

## Performance note: API URLs vs CDN URLs

The Douyin detail API returns 3 play URLs. The CDN URLs (e.g. `v11-weba.douyinvod.com/...`) download faster and more completely than the play API URL (`www.douyin.com/aweme/v1/play/?video_id=...`). The play API URL may throttle or truncate downloads. **Prefer the first CDN URL** from the playUrls array.

## Multiple Videos Workflow

When user shares 3+ Douyin video links for batch processing:

**PITFALL: Parallel delegation times out.** Using `delegate_task` with parallel workers for downloading multiple videos consistently times out at 600s per worker. The browser API extraction step is slow and each worker independently navigates pages.

**Recommended sequential approach:**
```
For each video URL:
  1. browser_navigate to the video page
  2. browser_console to extract playUrl via detail API
  3. curl download with Referer header
  4. ffmpeg extract audio
  5. whisper transcribe
```

This processes ~4 min of video in about 2-3 minutes total (download + extract + transcribe).

**Quick content check alternative:** If user only needs "what is this video about", skip downloading entirely — navigate to each page and extract the "章节要点" chapter summary from the DOM. This takes ~10 seconds per video vs ~3 minutes for full transcription.

## Delivering Transcripts to Feishu

When user wants transcripts sent to Feishu (飞书):
```bash
# Save transcript to file first, then send via lark-cli
lark-cli im +messages-send --file "transcript.md" --user-id {user_open_id} --as bot
```

User's Feishu open_id: `ou_1e6a1b2ebfe154d5b0470b6f003ecd06` (stored in memory).

## Real session examples

### Example 1: Chinese video (学院派Academia — "26年重读马克思之三：劳动")
- 22 min, Chinese language, 72MB MP4
- yt-dlp download: 5s (before cookie requirement)
- ffmpeg audio extraction: 2s
- Whisper tiny on 5 chunks (~4.5 min each): ~60s per chunk = ~5 min total
- Full transcript: ~6000 Chinese characters
- Result: Complete transcript with timestamps, key arguments extracted and analyzed

### Example 2: English video (毕英杰Johnathan — "只读这4本书，就能成为AI时代的赢家")
- 20:15, **English language** (overseas Chinese creator), ~150MB MP4
- yt-dlp FAILED (cookies required)
- **Used browser API extraction**: fetch from `aweme/v1/web/aweme/detail/` API → got 3 play URLs
- curl download: 102MB (partial — URL may have throttled), 12:58 of 20:15 audio extracted
- **First attempt with `--language zh` + `tiny`**: complete garbage (lesson: always detect language!)
- **Second attempt with `--language en` + `base`**: clean, readable transcript, ~2154 words
- 3 chunks × ~60s each = ~3 min transcription time
- Result: Full English transcript with speaker's actual arguments, quotes, and reasoning chain
