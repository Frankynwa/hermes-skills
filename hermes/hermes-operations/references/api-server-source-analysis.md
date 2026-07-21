# API Server Source Analysis

Source: `gateway/platforms/api_server.py` (3524 lines, ~154KB as of 2026-05)

## Content Normalization Pipeline

Two normalizers handle incoming message content:

1. **`_normalize_chat_content()`** — legacy text-only normalizer. Flattens `[{type:"text", text:"..."}, ...]` arrays into a single string. Silently skips non-text parts (image_url etc.).

2. **`_normalize_multimodal_content()`** — new multimodal normalizer. Preserves image_url parts as OpenAI vision format dicts. Raises `ValueError` on unsupported types.

Key constants:
- `MAX_NORMALIZED_TEXT_LENGTH` = 64KB per text part
- `MAX_CONTENT_LIST_SIZE` = 1000 items max
- `MAX_REQUEST_BYTES` = 10MB request body limit

## Supported Content Part Types

| Type | Status |
|------|--------|
| `text`, `input_text`, `output_text` | Supported (normalized to `text`) |
| `image_url`, `input_image` | Supported (preserved as OpenAI vision format) |
| `file`, `input_file` | **Rejected** with 400 error |
| Anything else | **Rejected** with explicit error message |

## Image Handling Details

- http/https URLs: passed through directly
- `data:image/...` base64 URLs: passed through
- Non-image data URLs (data:text/..., data:application/...): **rejected**
- Missing URL or unsupported scheme: **rejected**
- `detail` parameter (low/high/auto) supported and forwarded

## Streaming Implementation

Chat Completions streaming uses `_write_sse_stream()`:
- SSE `text/event-stream` response
- Keepalive: 30s (`CHAT_COMPLETIONS_SSE_KEEPALIVE_SECONDS`)
- Agent stream_delta_callback feeds an `asyncio.Queue`
- `None` sentinel = end of stream
- Client disconnect triggers `agent.interrupt()`

Tool progress events during streaming:
```python
# On tool start:
{"type": "__tool_progress__", "status": "running", "toolCallId": ..., "function": ..., "args": ...}
# On tool complete:
{"type": "__tool_progress__", "status": "completed", "toolCallId": ..., "function": ..., "result": ...}
```
These are filtered from the SSE writer — only text deltas and standard tool_calls go to the client.

## Session Continuity

`_derive_chat_session_id()` generates deterministic session IDs from the conversation's first user message hash. This lets stateless requests reuse the same Hermes session without explicit session headers.

When `X-Hermes-Session-Id` header is provided, it overrides the derived ID.

## Model Name Resolution

`_model_name` is derived from config (not hardcoded). The `/v1/models` endpoint returns this name. Frontends must use the exact name returned.

## Auth

- Optional Bearer token via `API_SERVER_KEY` env var
- `_check_auth(request)` validates on every request
- No rate limiting built in
- No user/role model — single shared identity

## Idempotency

Non-streaming requests support `Idempotency-Key` header to deduplicate retries. The fingerprint is based on `["model", "messages", "tools", "tool_choice", "stream"]` keys.

## Run Submission Flow (v0.5.0+)

The `/v1/runs` endpoint provides async execution:
1. POST creates a run → returns 202 + `run_id`
2. GET `/v1/runs/{run_id}` → current status
3. GET `/v1/runs/{run_id}/events` → SSE lifecycle stream
4. POST `/v1/runs/{run_id}/approval` → resolve approval gates
5. POST `/v1/runs/{run_id}/stop` → interrupt

Run streams stored in `_run_streams` dict with TTL-based cleanup.
