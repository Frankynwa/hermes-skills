# Feishu Gateway Message Rendering

## Source Code

`gateway/platforms/feishu.py`

## Key Regex Patterns

### `_MARKDOWN_HINT_RE` (line ~161)
```python
_MARKDOWN_HINT_RE = re.compile(
    r"(^#{1,6}\s)|(^\s*[-*]\s)|(^\s*\d+\.\s)|(^\s*---+\s*$)|(```)|(`[^`\n]+`)|(\*\*[^*\n].+?\*\*)|(~~[^~\n].+?~~)|(<u>.+?</u>)|(\*[^*\n]+\*)|(\[[^\]]+\]\([^)]+\))|(^>\s)",
    re.MULTILINE,
)
```

### `_MARKDOWN_TABLE_RE` (line ~158)
```python
_MARKDOWN_TABLE_RE = re.compile(r"^\|.*\|\n\|[-|: ]+\|", re.MULTILINE)
```

### `_POST_CONTENT_INVALID_RE` (line ~164)
```python
_POST_CONTENT_INVALID_RE = re.compile(r"content format of the post type is incorrect", re.IGNORECASE)
```

## Rendering Decision Logic (line ~4225-4234)

```python
def _build_outbound_payload(self, chunk: str):
    content = chunk  # simplified
    if _MARKDOWN_TABLE_RE.search(content):
        # Tables → text mode (forced, because Feishu post doesn't render tables)
        return "text", json.dumps({"text": content})
    if _MARKDOWN_HINT_RE.search(content):
        # Markdown present → post mode (rich rendering)
        return "post", _build_markdown_post_payload(content)
    # No markdown → text mode (plain)
    return "text", json.dumps({"text": content})
```

## Post-Failure Fallback to Text

The send logic has automatic fallback: if post mode fails with `content format of the post type is incorrect` (Feishu error code), it retries as text mode. This happens silently.

## `_build_markdown_post_rows` (line ~561)

Converts markdown content into Feishu post rows. Splits content by fenced code blocks to avoid Feishu's post renderer swallowing content after code fences. Each code block gets its own post element.

## `final_response_markdown` Config

The `display.final_response_markdown` config (values: `strip`/`render`/`raw`) is ONLY used in `cli.py`. It has zero effect on gateway platforms. Do not waste time changing this when debugging Feishu rendering issues.
