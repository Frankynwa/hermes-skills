---
name: video-content
description: "Video transcript extraction and summarization — YouTube, Douyin/TikTok, and other platforms. Covers transcript fetching, audio transcription via Whisper, and content transformation (summaries, threads, blogs, chapters)."
platforms: [linux, macos, windows]
---

# Video Content Tool

## When to use

Use when the user shares a video URL (YouTube, Douyin/抖音, TikTok, Bilibili, etc.), asks to summarize a video, requests a transcript, or wants to extract and reformat content from any video.

## Supported Platforms

| Platform | Transcript method | Notes |
|----------|------------------|-------|
| YouTube | `youtube-transcript-api` (direct) | Fast, no download needed |
| Douyin/抖音 | `yt-dlp` download → Whisper transcription | No API transcript; must extract audio |
| TikTok | `yt-dlp` download → Whisper transcription | Same as Douyin |
| Bilibili | `yt-dlp` download → Whisper transcription | CC subtitles may be available via API |

## Setup

```bash
# YouTube transcript (direct API)
pip install youtube-transcript-api

# Multi-platform video download
pip install yt-dlp

# Audio transcription (for platforms without API transcripts)
pip install openai-whisper  # or use OpenAI Whisper API
```

## Platform-Specific Workflows

### YouTube

Use the helper script for direct transcript extraction:

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

### Douyin/抖音 (and other non-transcript platforms)

See `references/douyin-workflow.md` for detailed steps. Summary:

1. **Extract video**: `yt-dlp -x --audio-format mp3 -o "/tmp/douyin_%(id)s.%(ext)s" "URL"`
2. **Transcribe**: Run Whisper on the extracted audio file
3. **Summarize**: Feed transcript to LLM for summarization

Key pitfalls:
- Douyin share links often redirect; yt-dlp handles this but may need `--cookies` for age-gated content
- Audio extraction preferred over full video download (smaller, faster)
- Short videos (< 60s) may have very sparse transcription — summarize directly
- Chinese-language videos: use Whisper with `--language zh` for better accuracy
- **Douyin anti-crawler**: `curl`/`requests` to Douyin pages are blocked by `byted_acrawler`. Use headless Selenium + Chrome for full page scraping. See `references/douyin-page-scraping.md` for complete technique.
- **Douyin metadata via Selenium**: Page text contains complete description, comments, "大家都在搜" trending searches (often reveals product names), creator stats, and related videos.

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Detect platform** from URL pattern.
2. **Fetch transcript**:
   - YouTube → helper script (`--text-only --timestamps`)
   - Douyin/TikTok/other → yt-dlp download + Whisper transcription
3. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled or audio is silent.
4. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
5. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
6. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run the appropriate pip install command and retry.
- **Douyin link expired/redirect fails**: ask user for a fresh share link.
