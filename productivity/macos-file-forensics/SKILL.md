---
name: macos-file-forensics
description: Analyze a user's work/activity history by scanning local macOS files — Excel data, screenshots, PDFs, app containers. Use when the user asks "what did I do during X period" or "analyze my files from X to Y."
tags: [macos, forensics, file-analysis, screenshots, excel, wechat]
---

# macOS File Forensics — Analyzing User Activity from Local Files

## When to Use
- User asks to analyze what they did during a specific time period
- User wants to review work files, screenshots, or documents from a date range
- User wants to read WeChat/WeCom (企业微信) data from terminal

## Step-by-Step Approach

### 1. Discover Files by Date Range
```bash
# Find files modified in a date range, excluding noisy directories
find ~ -maxdepth 5 -type f -newermt "YYYY-MM-DD" ! -newermt "YYYY-MM-DD" \
  ! -path "*/Library/Caches/*" \
  ! -path "*/.cache/*" \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/Library/Logs/*" \
  ! -path "*/.conda/*" \
  ! -path "*/anaconda3/*" \
  ! -path "*/miniconda3/*" \
  2>/dev/null | head -200
```
Then separately search key locations (Desktop, Downloads, Documents) with shallower depth for faster results.

### 2. Read Excel Files
**PITFALL**: The `execute_code` sandbox does NOT have pandas/openpyxl/xlrd. Always use `terminal` for Excel reading.

**PITFALL**: File extension determines the engine:
- `.xlsx` → `engine='openpyxl'`
- `.xls` → `engine='xlrd'` (default, usually works)
- Some `.xlsx` files fail with xlrd and vice versa — try both

```python
# In terminal, one file at a time to avoid timeout
python3 -c "
import pandas as pd
df = pd.read_excel('/path/to/file.xlsx', engine='openpyxl', nrows=10)
print('Cols:', list(df.columns))
print(df.head(5).to_string(max_colwidth=40))
"
```
**PITFALL**: Large files (>10MB) can cause 180s terminal timeout. Read with `nrows` limit or use `xlrd` directly for `.xls` files with sheet-level iteration.

### 3. Analyze Screenshots with Vision
This is the **most productive** approach for understanding work context. Use `vision_analyze` on screenshots:
```python
vision_analyze(image_url="/path/to/screenshot.png", question="Describe all text and UI content on screen")
```
- Screenshots often contain MES systems, code, task assignments, VPN logins, etc.
- Can reveal work tools, platforms, and daily workflows

### 4. PDF Metadata (when pdftotext unavailable)
```bash
mdls /path/to/file.pdf  # macOS metadata — gets creation date, type, sometimes text content
```

### 5. WeChat/WeCom (企业微信) Data Access

**macOS 沙盒权限机制（重要）**：
- `~/Library/Containers/` 默认隔离，首次访问触发 TCC 弹窗
- 用户点击"允许"后，`~/Library/Application Support/com.apple.TCC/TCC.db` 记录授权
- 之后 find/stat/ls 等命令畅通无阻
- 如果未授权：`find` 报 Permission denied 或返回空结果
- Hermes 进程通过继承终端的 TCC 授权可访问这些目录

**两层限制**：
1. **TCC 权限** — 控制目录访问（用户弹窗授权后解决）
2. **SQLCipher 加密** — 控制数据库读取（无法绕过，需要密钥）

**Directory structure** (accessible, no timeout if you avoid recursion):
- WeChat: `~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/`
- WeWork: `~/Library/Containers/com.tencent.WeWorkMac/Data/Library/Application Support/WXWork/Data/<user_id>/`
- WeWork user data: `Data/` (encrypted dbs), `Index/` (FTS indexes), `Emotion/`, `Avator/`

**What DOES work**:
```bash
# Top-level ls — fast, no timeout
ls -la ~/Library/Containers/com.tencent.WeWorkMac/Data/Library/Application\ Support/

# List WeWork databases
ls ~/Library/Containers/com.tencent.WeWorkMac/.../Data/<user_id>/Data/*.db

# Check encryption status per database
for db in path/to/*.db; do
    header=$(xxd -l 16 "$db" 2>/dev/null | head -1)
    if echo "$header" | grep -q "5351 4c69 7465 2066"; then
        echo "✅ $(basename $db): SQLite (readable)"
    else
        echo "🔒 $(basename $db): SQLCipher (encrypted)"
    fi
done
```

**WeWork readable databases** (as of 2025-05):
- `avatar_store_v3.db` — avatar images (minimal data)
- `cloud_disk.db` — cloud disk metadata
- `mac_security_file.db` — file bookmarks
- Index databases (data_index.db etc.) — FTS schema exists but data typically empty

**WeWork encrypted databases** (SQLCipher, cannot read):
- `message.db`, `session.db`, `user.db`, `company.db`, `file.db`, `crm.db`, `kv.db`, etc.

**What does NOT work**:
- `find` with deep recursion → timeout
- `sqlite3` on encrypted .db files → returns empty
- `mdfind` for message content → not indexed

**Better alternatives for message content**:
1. WeChat/WeWork app's built-in file manager (GUI export)
2. [WeChatMsg](https://github.com/LC044/WeChatMsg) — needs Windows + key extraction
3. WeCom admin API (if user has admin access)

### 6. App Container Discovery
```bash
# Find all Tencent-related containers
ls ~/Library/Containers/com.tencent.* 2>/dev/null
ls ~/Library/Group\ Containers/ 2>/dev/null | grep tencent
# Check installed apps
ls /Applications/ | grep -i "wechat\|wecom\|企业"
```

### 7. SQLite Database Forensics
Many macOS apps store data in SQLite databases that are **readable** (unlike WeChat's encrypted ones). Check for these:
```bash
# iFLYAssistant (讯飞助手) — stores translation history, AI chat config
sqlite3 ~/iFLYAssistant/AIChat4.db ".tables"
sqlite3 ~/iFLYAssistant/translator.db "SELECT * FROM translator_data LIMIT 10;"

# Other apps — look for .db files in app directories
find ~/Library -maxdepth 3 -name "*.db" -not -path "*/Caches/*" 2>/dev/null | head -20
```
Translator databases often contain translated text that reveals work topics (e.g., AI/ML terminology, project-specific terms).

### 8. Corrupted Excel Files — xlrd Direct Iteration
When pandas raises `Unsupported format` or crashes on `.xlsx` files, try xlrd directly:
```python
import xlrd
wb = xlrd.open_workbook('/path/to/file.xlsx')  # works on some xlsx
sh = wb.sheet_by_name(wb.sheet_names()[0])
for r in range(min(10, sh.nrows)):
    row = [sh.cell_value(r, c) for c in range(min(12, sh.ncols))]
    print(row)
```
Also try `nrows` parameter with pandas to limit memory usage on large files.

### 9. Triage Screenshots with mdls Before Vision
Use `mdls` to get screenshot dimensions — this helps decide which to analyze:
```bash
mdls -name kMDItemPixelWidth -name kMDItemPixelHeight /path/to/screenshot.png
```
Large screenshots (e.g., 3420×2138) are full-desktop captures with rich context. Small ones (e.g., 1906×118) are cropped snippets — prioritize the large ones for `vision_analyze`.

### 10. Spotlight Search Caveats
- `mdfind` (Spotlight) works well for **user documents** but is unreliable for app container data (WeChat, WeCom)
- Spotlight indexes `kMDItemTextContent` for PDFs and some documents, but NOT encrypted databases
- Use `mdfind -onlyin <dir>` to scope searches and avoid timeout

## 11. iFLYAssistant (讯飞助手) Data
Installed on this machine at `~/iFLYAssistant/`. Contains:
- `AIChat4.db` — AI chat config, PPT templates, personal_details table
- `translator.db` — translation history (reveals work topics: AI/ML terms, project jargon)
- `config.ini` — engine settings (opus, dictation, translate, OCR engines)
- `speech/` — voice recordings with timestamps (PCM/WAV format)

SQLite3 can read these databases directly (NOT encrypted unlike WeChat):
```bash
sqlite3 ~/iFLYAssistant/translator.db "SELECT * FROM translator_data LIMIT 10;"
sqlite3 ~/iFLYAssistant/AIChat4.db "SELECT * FROM personal_details LIMIT 5;"
```

## 12. Triage: Large Screenshots vs Small Ones
Use `mdls` to get pixel dimensions before analyzing:
```bash
mdls -name kMDItemPixelWidth -name kMDItemPixelHeight /path/to/screenshot.png
```
- 3400×2000+ → full desktop capture, rich context, analyze first
- 1900×100 → narrow banner/snippet, low priority
- 800×1800 → phone-sized screen capture, moderate priority

## 13. Time-Range Directory Discovery
Use `find` with `-type d` for directories (faster than files):
```bash
find ~ -maxdepth 3 -type d -newermt "YYYY-MM-DD" ! -newermt "YYYY-MM-DD" \
  ! -path "*/Library/*" ! -path "*/.cache/*" ! -path "*/.conda/*" \
  2>/dev/null | sort
```

## Summary Pattern
1. `find` with date filters → file list
2. `terminal` + pandas → read Excel/doc contents (NOT execute_code)
3. `vision_analyze` → understand screenshots (most valuable for work context)
4. `mdls` → PDF/document metadata + screenshot triage
5. `sqlite3` → app databases (translation history, chat logs, config)
6. Combine findings into a chronological activity timeline

## Pitfalls (实战经验)

1. **execute_code sandbox** — 无 pandas/openpyxl/xlrd，Excel 读取必须用 terminal
2. **微信/企业微信目录** — 绝对不要递归 find，必超时(10-180s)。只用顶层 `ls -la`
3. **Excel 引擎** — `.xls` 用 xlrd，`.xlsx` 用 openpyxl。`.xlsx` 配 xlrd 会报 "Unsupported format"
4. **大 Excel 文件** (>10MB) — 先用 `nrows=5` 检查结构，60MB 文件可能 180s 超时
5. **vision_analyze** — 对 UI 截屏比 OCR 准确得多，优先分析大截屏 (3400×2000+)
6. **损坏 Excel** — 先试 xlrd 直接读，再试 openpyxl，再失败就跳过。工厂系统的 .xlsx 常有非标格式
7. **止损规则** — 同类超时/错误出现 **2 次**后立即换策略，不要反复尝试
8. **数据库加密** — iFLYAssistant 的 .db 可直接 sqlite3 读（未加密），但 WeChat/WeCom 是 SQLCipher 加密的，无法读取
9. **iCloud 文件卸载（dataless）** — 当 Desktop/Documents 启用 iCloud "优化存储"时，文件可能被卸载为 `dataless` 存根（仅保留占位符，实际内容在 iCloud）。症状：`cat`、`cp`、Python `open()` 均报 `Resource deadlock avoided (errno 11)`，且 `lsof` 看不到任何进程持有文件。诊断：`ls -laO <file>` 看 flags 是否含 `compressed,dataless`。修复：`brctl download <file>` 触发下载，等待几秒后即可读取。如 `brctl` 无效，`touch` 文件再等 10s 也能触发 iCloud 同步。根本解：活跃项目不要放 Desktop，用 `~/projects/` 或 `~/dev/`
