# Feishu Gateway Adapter Architecture — Extension Patterns

Internal reference for extending `gateway/platforms/feishu.py` (class `FeishuAdapter`, ~5400 LOC).

## Settings Pipeline

New config options follow a 3-step pattern:

```
1. FeishuAdapterSettings (frozen dataclass, line ~562)
   → Add field with default: my_option: bool = False

2. _load_settings() (line ~1673)
   → Parse from extra dict or env var:
     my_option=_to_boolean(extra.get("my_option", os.getenv("FEISHU_MY_OPTION", "false")))

3. _apply_settings() (line ~1772)
   → Store on instance: self._my_option = settings.my_option
```

Config yaml path: `feishu.my_option: true`
Env var pattern: `FEISHU_MY_OPTION=true`

## Card Action Routing

Three-way dispatch in `_on_card_action_trigger()` (line ~2721):

```
action_value = getattr(action, "value", {}) or {}

if action_value.get("hermes_action"):
    → _handle_approval_card_action()  # exec approval buttons
elif action_value.get("hermes_update_prompt_action"):
    → _handle_update_prompt_card_action()  # update prompt buttons
else:
    → _handle_card_action_event()  # generic (card click → synthetic event)
```

The generic handler creates a `MessageEvent` and routes it through `_handle_message_with_guards()`.

## Interactive Card Buttons

Card structure for buttons:

```json
{
  "config": {"wide_screen_mode": true},
  "elements": [
    {"tag": "markdown", "content": "text here"},
    {"tag": "hr"},
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {"tag": "plain_text", "content": "Button Label"},
          "type": "default",  // "primary" | "danger" | "default"
          "value": {"my_custom_key": "payload"}
        }
      ],
      "layout": "bisected"  // "bisected" | "flow"
    }
  ]
}
```

Button clicks arrive at `_handle_card_action_event()` as synthetic events.
Check `action_value.get("my_custom_key")` to identify your custom buttons.

## Routing Custom Buttons as User Messages

To make a button click appear as a normal user message (not a `/card ...` command):

```python
# In _handle_card_action_event():
suggested_q = action_value.get("my_custom_key")
if suggested_q:
    synthetic_text = str(suggested_q)
    msg_type = MessageType.TEXT  # ← agent treats as user question
else:
    synthetic_text = f"/card {action_tag} {json.dumps(action_value)}"
    msg_type = MessageType.COMMAND  # ← default: treated as /card command
```

## Extending the send() Method

The `send()` method (line ~1962) processes content through:
1. `format_message(content)` — normalize
2. `truncate_message(formatted, MAX_MESSAGE_LENGTH)` — split into chunks
3. For each chunk: `_build_outbound_payload(chunk)` → `(msg_type, payload)`
4. Send with fallback chain: interactive → post → text

To inject content into the last message:
- Track `is_last = (i == len(chunks) - 1)` in the loop
- For interactive cards: modify `payload` before sending
- For text/post: send a follow-up via `asyncio.create_task()`

## Sending Follow-up Cards

```python
async def _send_followup(self, chat_id, content, reply_to):
    card = {
        "config": {"wide_screen_mode": True},
        "elements": [{"tag": "markdown", "content": content}],
    }
    await self._feishu_send_with_retry(
        chat_id=chat_id,
        msg_type="interactive",
        payload=json.dumps(card, ensure_ascii=False),
        reply_to=reply_to,
        metadata=None,
    )
```

## Dedup for Card Actions

Card action tokens are deduped via `_card_action_tokens` dict (15-min TTL).
Always check `_is_card_action_duplicate(token)` before processing.

## Key Imports from lark_oapi

```python
from lark_oapi.event.callback.model.p2_card_action_trigger import (
    CallBackCard,
    P2CardActionTriggerResponse,
)
```

`P2CardActionTriggerResponse()` — return this from `_on_card_action_trigger` to acknowledge.
`CallBackCard` — use to return an updated card inline (e.g. approval resolution).
