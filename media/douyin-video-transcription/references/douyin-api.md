# Douyin Internal API Reference

## Video Detail API

Retrieves video metadata + download URLs. Works in browser context (carries cookies automatically).

**Endpoint:**
```
https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id={VIDEO_ID}&request_source=600&origin_type=video_page&update_version_code=1704
```

**How to get VIDEO_ID:** From `https://www.douyin.com/video/7655697006442089770`, the ID is `7655697006442089770`.

**Response structure (relevant fields):**
```json
{
  "aweme_detail": {
    "desc": "视频描述文字",
    "video": {
      "duration": 1214867,  // milliseconds
      "play_addr": {
        "url_list": [
          "https://v11-weba.douyinvod.com/.../video.mp4?...",  // CDN URL (preferred)
          "https://v95-web-sz.douyinvod.com/.../video.mp4?...", // CDN URL (backup)
          "https://www.douyin.com/aweme/v1/play/?video_id=..."  // Play API (slower, may truncate)
        ]
      }
    },
    "subtitles": {
      "enable": 1,
      "language_list": [
        {"language_code": "zh-Hans-CN", "language_id": 1},
        {"language_code": "en-US", "language_id": 2}
      ]
    }
  }
}
```

**Key notes:**
- `duration` is in milliseconds (divide by 1000 for seconds)
- Subtitles config exists in response but actual subtitle data is loaded separately (not in this API)
- CDN URLs are signed and may expire; extract fresh for each download attempt
- The play API URL may throttle downloads — prefer CDN URLs (index 0 and 1)

## Browser extraction script (copy-paste into browser_console)

**MUST be on the douyin.com video page** (same-origin requirement — CORS blocks cross-origin requests to this API).

**Two-step pattern** (fetch is async, result not immediately available):
```javascript
// Step 1: initiate fetch, store result on window
fetch('/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=VIDEO_ID_HERE&request_source=600&origin_type=video_page&update_version_code=1704', {
  credentials: 'include'
}).then(r => r.json()).then(data => {
  const v = data.aweme_detail?.video;
  window.__videoResult = JSON.stringify({
    desc: data.aweme_detail?.desc,
    duration: v?.duration,
    playUrls: (v?.play_addr?.url_list || []).slice(0, 3)
  });
}).catch(e => { window.__videoResult = 'ERROR: ' + e.message; });

// Step 2 (separate call): read the result
window.__videoResult
```

**Pitfalls:**
- `window.location.pathname.match(/\d+/)[0]` may return null if the URL pattern changed — hardcode the video ID instead
- Variable names persist across `browser_console` calls — use `window.*` to avoid redeclaration errors
- The old mobile API (`iesdouyin.com/web/api/v2/aweme/iteminfo/`) returns status 11110 as of 2026; don't use it
- `performance.getEntriesByType('resource')` only shows player JS files, not video stream URLs

## Downloading with curl

```bash
curl -L -o /tmp/douyin_video.mp4 "{CDN_URL}" \
  -H "Referer: https://www.douyin.com/" \
  --progress-bar
```

Always include the Referer header — Douyin CDN rejects requests without it.
