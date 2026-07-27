# Provider Billing Investigation — Evidence Extraction

When a model provider charges you for failed API calls (429s, timeouts, connection errors), you need to extract evidence from local databases to support a billing dispute. This reference covers the extraction patterns and the Kimi/Moonshot Context Caching billing trap as a case study.

## Evidence Sources

| Source | Path | What it contains |
|--------|------|-----------------|
| Open WebUI chat DB | `~/.open-webui/webui.db` → `chat` table | Full conversation JSON including model names, error mentions |
| Hermes request dumps | `~/.hermes/sessions/request_dump_*.json` | API request/response pairs, retry chains |
| Hermes session files | `~/.hermes/sessions/session_*.json` | Agent tool call logs containing model error mentions |
| Benchmark results | `~/projects/hermes-model-bench/results/` | Run summaries with model status |

## Extraction Pattern 1: Open WebUI chat DB

The `chat` table stores all conversations as JSON in the `chat` column. Search for model+error patterns:

```python
import sqlite3, json, re

conn = sqlite3.connect(os.path.expanduser("~/.open-webui/webui.db"))
c = conn.cursor()

# Find chats mentioning a specific model + error pattern
c.execute("""
    SELECT id, title, chat FROM chat 
    WHERE chat LIKE '%kimi%' OR chat LIKE '%moonshot%'
    ORDER BY updated_at DESC
""")

for chat_id, title, chat_json in c.fetchall():
    # Search for specific error patterns
    for m in re.finditer(r'kimi.{0,300}(?:429|overloaded|限流).{0,300}', 
                         chat_json, re.IGNORECASE):
        context = m.group()
        # Decode unicode escapes
        try:
            context = context.encode().decode('unicode_escape', errors='replace')
        except:
            pass
        # Clean JSON artifacts
        context = re.sub(r'[{}\[\]"\\]', '', context)
        print(f"Chat: {title}\n  {context[:200]}")
```

**Pitfall**: The chat JSON may have layers of unicode escaping (`\\u9650\\u6d41`). Always try `unicode_escape` decoding.

## Extraction Pattern 2: Hermes Session Request Dumps

Request dumps capture API call details including URL, model, and status. Named `request_dump_{session_id}_{timestamp}.json`:

```python
import os, json, re

sessions_dir = os.path.expanduser("~/.hermes/sessions/")
for f in sorted(os.listdir(sessions_dir)):
    if not f.startswith('request_dump_'):
        continue
    filepath = os.path.join(sessions_dir, f)
    with open(filepath) as fh:
        content = fh.read()
    if 'moonshot' in content.lower():
        print(f"Found in: {f}")
        # Extract model, URL, error patterns
```

**Key fields in request dumps**:
- `reason`: e.g., `"max_retries_exhausted"` — why the request was dumped
- `request.url`: the API endpoint called
- `request.body.model`: the model name requested
- Search for error patterns in the full JSON: `engine_overloaded`, `429`, `insufficient_balance`

## Extraction Pattern 3: Unstructured Chat JSON Search

When the chat table stores long JSON strings with embedded error mentions, use `strings` + grep to find patterns without full SQL parsing:

```bash
# Find kimi 429 mentions with surrounding context
python3 -c "
import sqlite3, re
conn = sqlite3.connect('$HOME/.open-webui/webui.db')
c = conn.cursor()
c.execute(\"SELECT chat FROM chat WHERE chat LIKE '%kimi%429%'\")
for (chat_json,) in c.fetchall():
    for m in re.finditer(r'kimi.{0,200}(?:429|overloaded|限流|过载).{0,300}', 
                         chat_json, re.IGNORECASE):
        text = m.group()
        try:
            text = text.encode().decode('unicode_escape', errors='replace')
        except: pass
        text = re.sub(r'[{}\[\]\"\\\\]', '', text)
        print(f'>>> {text[:300]}')
"
```

## Case Study: Kimi/Moonshot Context Caching Billing Trap

**Date**: 2026-07-21
**Model**: kimi-k3 (via `api.moonshot.cn/v1`)
**Symptom**: All requests returned `429 engine_overloaded_error`, zero successful outputs
**Charge**: 22.77 CNY (primarily Context Caching fees)
**Root cause**: Moonshot's Context Caching billing triggers at request entry, before processing. Even when the server returns 429 (server-side overload), the cache creation cost is billed.

### Evidence collected:
- Open WebUI chat logs showing 5+ separate 429 occurrences
- Moonshot's own docs: `engine_overloaded_error` is "caused by server capacity, cannot be resolved by topping up or upgrading Tier"

### Complaint template structure:
1. **Timeline**: when calls were made, what models, what errors
2. **Evidence**: chat log excerpts or request dump snippets
3. **Policy contradiction**: official docs say server fault, but billing still applied
4. **Specific ask**: refund amount + affected date range

### Lessons learned:
- Context Caching billing happens at request ENTRY, not on success — a design flaw
- Always check billing console immediately after a failed benchmark run
- Save request dumps — they're the strongest evidence for disputes
- The `chat` table is your fallback when request dumps aren't available

## Moonshot-Specific Notes

- API base: `https://api.moonshot.cn/v1`
- Billing console: `https://platform.kimi.com` (or `platform.moonshot.cn`)
- Error doc: `https://platform.kimi.com/docs/api/errors`
- `reasoning_effort` is a TOP-LEVEL param (not `extra_body`) — unique among providers
- `temperature` locked at 1.0, `top_p` locked at 0.95
