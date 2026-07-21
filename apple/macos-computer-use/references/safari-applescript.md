# Safari AppleScript reference (macOS)

Quick-reference for AppleScripting Safari when `computer_use` tool is unavailable.

## Window & Tab Management

```applescript
-- List all windows and their tabs
tell application "Safari"
    repeat with i from 1 to count of windows
        repeat with j from 1 to count of tabs of window i
            log "Win " & i & " Tab " & j & ": " & name of tab j of window i
        end repeat
    end repeat
end tell

-- Count windows
tell application "Safari" to return count of windows

-- Bring window N to front
tell application "Safari"
    set index of window N to 1
    activate
end tell

-- Switch to tab J in window I
tell application "Safari"
    set current tab of window I to tab J of window I
end tell

-- Get current tab in front window
tell application "Safari"
    return name of current tab of window 1
end tell
```

## Getting Page Content

```applescript
-- Static HTML source (NO JS-rendered content)
tell application "Safari"
    set docSource to source of document 1
end tell

-- URL of current tab
tell application "Safari"
    return URL of current tab of window 1
end tell
```

## Working Around Safari Limitations

### "Allow JavaScript from Apple Events" is OFF by default
Without it, `do JavaScript` always fails. The user must:
1. Safari → Settings → Advanced → check "Show features for web developers"
2. Develop menu → "Allow JavaScript from Apple Events"

### System Events accessibility is shallow
`UI elements of front window` for Safari returns 0 children. Safari uses
custom rendering that bypasses the standard AX hierarchy.

### Popup blocker
Safari silently blocks `window.open()` calls. Checked by looking for empty
windows (no tabs) after clicking a button that should open a popup.
To fix: Safari → Settings → Websites → Pop-up Windows → Allow for the site.

## Full Multi-Window Exploration Workflow

When navigating a site that opens popups or new windows (Moodle+LAMS,
single sign-on flows, external lesson content), follow this sequence:

### Step 1: Navigate to target page
```applescript
tell application "Safari"
    set URL of front document to "https://moodle.must.edu.mo/course/view.php?id=112049"
end tell
```

### Step 2: Wait for load, extract static source
```bash
sleep 3
osascript -e 'tell application "Safari" to return source of document 1'
```
Static source reveals element IDs (`id="action_link...""`) and their
associated JavaScript — e.g., a `window.open()` call with a constructed
SSO URL. Extract the URL from source if possible; it may be inside a
`<script>` tag as part of a data payload.

### Step 3: Click JS-driven buttons
```applescript
tell application "Safari"
    do JavaScript "document.getElementById('action_linkXXXXX').click();" in front document
end tell
```

### Step 4: Enumerate ALL windows (not just window 2)
Popup windows may land in ANY window position, not just the second one.
```bash
sleep 2
osascript -e '
tell application "Safari"
    set output to ""
    repeat with w in windows
        repeat with t in tabs of w
            set output to output & "Window:" & (index of w) & " Tab:" & (index of t) & " URL:" & (URL of t) & " Title:" & (name of t) & "\n"
        end repeat
    end repeat
    return output
end tell'
```

### Step 5: Switch to the correct window/tab and extract content
```applescript
-- Switch to Window 3, Tab 2
tell application "Safari"
    set current tab of window 3 to tab 2 of window 3
end tell

sleep 2
-- Extract rendered content (NOT static source — use JS for dynamic pages)
tell application "Safari"
    set pageText to do JavaScript "document.body.innerText" in tab 2 of window 3
end tell
```

**PITFALL:** `source of document` returns static HTML. For JavaScript-rendered
pages (React, Svelte, LAMS, Moodle), use `do JavaScript "document.body.innerText"`
to get the actual rendered text. The static source is useful for finding
element IDs and hidden URLs, but not for reading user-visible content.

**PITFALL:** `osascript` result size is limited (~32KB). For long pages, chunk:
```javascript
document.body.innerText.substring(0, 8000)   // first chunk
document.body.innerText.substring(8000, 16000) // second chunk
```
