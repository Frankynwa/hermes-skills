#!/usr/bin/env python3
"""
Hermes Tool Progress Proxy
把 Hermes API 的 hermes.tool.progress SSE 事件翻译成 Open WebUI 能显示的格式

用法: python3 hermes-proxy.py
默认监听 :8643，转发到 :8642

原理:
  Hermes 发出:  event: hermes.tool.progress
                data: {"tool":"search_files","status":"running"}

  代理翻译为:    data: {"choices":[{"delta":{"content":"🔍 search_files..."}}]}

  这样 Open WebUI 就能在聊天界面实时显示工具调用过程

心跳: 每 5 秒发送 SSE 注释行 (: heartbeat)，防止浏览器切后台时断连
"""

import asyncio
import json
import sys
import time
import aiohttp
from aiohttp import web

HERMES_API = "http://127.0.0.1:8642"
API_KEY="hermes...2026"
PROXY_PORT = 8643

TOOL_EMOJI = {
    "search_files": "🔍",
    "read_file": "📖",
    "write_file": "✏️",
    "patch": "🩹",
    "terminal": "💻",
    "execute_code": "🐍",
    "browser_navigate": "🌐",
    "browser_snapshot": "📸",
    "browser_click": "👆",
    "browser_type": "⌨️",
    "vision_analyze": "👁️",
    "memory": "🧠",
    "web_search": "🔎",
    "session_search": "📜",
    "skill_view": "📚",
    "skill_manage": "🛠️",
    "delegate_task": "🤖",
    "process": "⚙️",
    "todo": "📋",
}


def make_content_chunk(text: str) -> str:
    """生成 OpenAI 兼容的 content chunk"""
    return json.dumps(
        {
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": text},
                    "finish_reason": None,
                }
            ]
        }
    )


def escape_unicode(text: str) -> str:
    """把中文等字符保持为 Unicode 转义，与上游保持一致"""
    return text


async def handle_request(request):
    """转发所有请求到 Hermes API"""
    path = request.match_info.get("path", "")
    target_url = f"{HERMES_API}/{path}"

    headers = dict(request.headers)
    headers.pop("Host", None)
    headers["Authorization"] = f"Bearer {API_KEY}"

    if path == "v1/chat/completions":
        return await handle_chat(request, target_url, headers)
    else:
        # 其他请求直接转发
        async with aiohttp.ClientSession() as session:
            body = await request.read()
            async with session.request(
                request.method, target_url, headers=headers, data=body
            ) as resp:
                response = web.StreamResponse(status=resp.status, headers=resp.headers)
                await response.prepare(request)
                async for chunk in resp.content.iter_any():
                    await response.write(chunk)
                await response.write_eof()
                return response


async def handle_chat(request, target_url, headers):
    """处理 chat completions，如果是流式则转换 tool progress 事件"""
    body = await request.read()

    # 判断是否流式请求
    is_stream = False
    try:
        payload = json.loads(body)
        is_stream = payload.get("stream", False)
    except json.JSONDecodeError:
        pass

    async with aiohttp.ClientSession() as session:
        async with session.request(
            "POST", target_url, headers=headers, data=body
        ) as upstream:
            if not is_stream or "event-stream" not in upstream.headers.get(
                "Content-Type", ""
            ):
                # 非流式：直接转发
                response = web.StreamResponse(
                    status=upstream.status, headers=upstream.headers
                )
                await response.prepare(request)
                data = await upstream.read()
                await response.write(data)
                await response.write_eof()
                return response

            # 流式处理：转换 hermes.tool.progress 事件
            response = web.StreamResponse(
                status=200,
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )
            await response.prepare(request)

            HEARTBEAT_SEC = 5
            write_lock = asyncio.Lock()
            heartbeat_running = True

            async def heartbeat():
                """每隔 HEARTBEAT_SEC 秒发送 SSE 注释行，防止浏览器切后台时断连"""
                while heartbeat_running:
                    await asyncio.sleep(HEARTBEAT_SEC)
                    if heartbeat_running:
                        try:
                            async with write_lock:
                                await response.write(b": heartbeat\n\n")
                        except Exception:
                            break

            heartbeat_task = asyncio.create_task(heartbeat())

            try:
                line_buffer = ""
                current_event = ""

                async for chunk in upstream.content.iter_any():
                    text = chunk.decode("utf-8", errors="replace")
                    # 按行处理
                    for ch in text:
                        line_buffer += ch
                        if ch != "\n":
                            continue

                        line = line_buffer.strip()
                        line_buffer = ""

                        if line.startswith("event:"):
                            current_event = line[6:].strip()
                            continue

                        if line.startswith("data:"):
                            data_str = line[5:].strip()

                            if current_event == "hermes.tool.progress":
                                try:
                                    tp = json.loads(data_str)
                                    tool_name = tp.get("tool", "?")
                                    status = tp.get("status", "?")
                                    emoji = TOOL_EMOJI.get(tool_name, "⚡")

                                    if status == "running":
                                        label = tp.get("label", tool_name)
                                        # 截断过长的 label
                                        if len(label) > 80:
                                            label = label[:77] + "..."
                                        content = f"\n{emoji} 调用 {tool_name}\n"
                                        async with write_lock:
                                            await response.write(
                                                (
                                                    "data: "
                                                    + make_content_chunk(content)
                                                    + "\n\n"
                                                ).encode()
                                            )
                                    elif status == "completed":
                                        async with write_lock:
                                            await response.write(
                                                (
                                                    "data: "
                                                    + make_content_chunk(
                                                        f"{emoji} {tool_name} 完成\n"
                                                    )
                                                    + "\n\n"
                                                ).encode()
                                            )
                                except Exception:
                                    pass
                                current_event = ""
                                continue

                            elif current_event == "hermes.reasoning":
                                try:
                                    r = json.loads(data_str)
                                    content = r.get("delta", {}).get("text", "")
                                    if content:
                                        async with write_lock:
                                            await response.write(
                                                (
                                                    "data: "
                                                    + make_content_chunk(
                                                        f"💭 {content}"
                                                    )
                                                    + "\n\n"
                                                ).encode()
                                            )
                                except Exception:
                                    pass
                                current_event = ""
                                continue

                            # 标准 content chunk，直接转发
                            async with write_lock:
                                await response.write(
                                    (f"data: {data_str}\n\n").encode()
                                )
                            current_event = ""

                async with write_lock:
                    await response.write("data: [DONE]\n\n".encode())
            finally:
                heartbeat_running = False
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

            await response.write_eof()
            return response


def main():
    print(f"🚀 Hermes Tool Progress Proxy started on :{PROXY_PORT}")
    print(f"   Forwarding to {HERMES_API}")
    print(f"   Translating hermes.tool.progress → visible content")
    print(f"   Heartbeat: every 5s to prevent background-tab disconnection")
    app = web.Application()
    app.router.add_route("*", "/{path:.*}", handle_request)
    web.run_app(app, host="127.0.0.1", port=PROXY_PORT)


if __name__ == "__main__":
    main()
