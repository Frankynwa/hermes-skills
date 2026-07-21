# Safari do JavaScript Patterns (Fallback Mode)

These snippets assume "Allow JavaScript from Apple Events" is enabled
(Safari → Develop menu). They are invoked via `osascript -e`.

## The Correct AppleScript Syntax

CRITICAL: `do JavaScript` does NOT capture a `return` statement.
The last expression value in the JS code block becomes the AppleScript
result. Do NOT write `return JSON.stringify(...)` — just write
`JSON.stringify(...)` as the final expression.

CORRECT:
```applescript
tell application "Safari"
    set js to "(function() { var links = document.querySelectorAll('a'); for (var i = 0; i < links.length; i++) { if (links[i].textContent.includes('foo')) { return JSON.stringify({href: links[i].href}); } } return 'not found'; })()"
    try
        set resultText to do JavaScript js in current tab of front window
        return resultText
    on error errMsg
        return "JS Error: " & errMsg
    end try
end tell
```

The `(function() { ... })()` wrapper is essential — it lets you use `return`
inside the function, whose value becomes the expression result passed back
to AppleScript.

## Finding Dynamically Rendered Elements

LAMS and many modern LMS pages use Svelte/React/Vue. Links and buttons are
rendered client-side — nowhere in `document.source`. Use `querySelectorAll`:

```javascript
// Find all buttons and links (works on any JS framework)
var buttons = document.querySelectorAll('button, a, [role="button"], input[type="submit"]');
for (var i = 0; i < buttons.length; i++) {
    if (buttons[i].textContent.includes('Next Activity')) {
        buttons[i].click();
        break;
    }
}
```

## Clicking by ID (Most Reliable)

When `querySelectorAll` reveals an element has an `id`, use `getElementById`:

```javascript
document.getElementById('finishButton').click();
```

This is immune to text-matching issues, framework re-renders, and element
ordering changes.

## Page Content Extraction

```javascript
// Full text content (all visible text)
document.body.innerText

// Substring to avoid truncation in AppleScript
document.body.innerText.substring(0, 8000)

// Second chunk
document.body.innerText.substring(8000, 16000)
```

The `substring` approach is needed because AppleScript has a ~32KB result
limit for `do JavaScript`.

## Moodle + LAMS Interaction Patterns

### LAMS SSO URL Discovery (Extract from Page Source)

LAMS "Open Lesson" buttons use `href="#"` but the real URL is embedded
in a `<script>` tag in the page source. Search static source for the
element ID found in the button (e.g. `action_link6a13de6e9a9f320`) to
find the associated `window.open()` call:

```
pattern: "url":"https://lams.must.edu.mo/lams/LoginRequest?uid=..."
params: uid, firstName, lastName, email, method=learnerStrictAuth,
        ts (timestamp), sid, hash, country, lang
```

The SSO URL can be extracted from source and opened directly with curl or
a new Safari tab — skip the click entirely. This is faster and avoids
popup-blocker issues.

### LAMS Lesson Activity Structure

Each DL_LectN contains exactly 4 activities in fixed order:
1. **Noticeboard** — course announcements / overview
2. **Self-study** — learning materials + comprehension quiz (≥70% to pass)
3. **Assessment** — formal graded assessment
4. **Gate** — permission gate (must wait for lecturer to open)

The side panel (hamburger menu → offcanvas) lists all activities with
status: completed ✓, current ▶, not-reached-yet ⬜.

Self-study follows a flipped-classroom 5-stage model:
- Pre-class materials → Quiz → Self-assessment → Group learning → Teaching

### Gate Activity Behavior

The Gate activity blocks progress even when all prior activities are
complete. The page shows:
```
"You have stopped at a gate. You cannot continue until the lecturer
allows you to continue."
```
A "Next" button is present but clicking it has no effect until the
lecturer opens the gate. The page auto-refreshes every 60 seconds.

1. **Course page** — LAMS lessons are listed as `<a>` links with text like
   "DL_Lect3 LAMS Lesson". Find by `textContent.includes('DL_LectN')`.

2. **Lesson page** — The "Open Lesson" button is an `<a>` with
   `href="...#"` and `textContent.includes('Open Lesson')`. Clicking it
   opens a NEW Safari window (not a new tab).

3. **LAMS popup window** — After clicking "Open Lesson", a new Safari window
   appears (often Window 2 or Window 1 if it was already open). Its tab has
   URL like `https://lams.must.edu.mo/lams/tool/lanb11/learning/learner.do?toolSessionID=...`

4. **Advancing activities** — The "Next Activity" button is a `<button>` with
   `id="finishButton"` and class `btn btn-primary na`. Always click by id.

5. **Quiz submission** — Quiz questions are in the page text. The "Submit Quiz"
   button appears after all questions. Click by id or by searching for button
   text.

## Error Recovery

If `do JavaScript` fails with permissions error:
- Check Safari → Develop → "Allow JavaScript from Apple Events" is checked
- If Develop menu is missing: Safari → Settings → Advanced → "Show features for web developers"

If `document.getElementById('finishButton')` returns null:
- The page hasn't navigated yet. Re-extract content and check the current activity.
- The element may be inside an iframe. Check with `document.querySelectorAll('iframe')`.
