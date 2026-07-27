#!/usr/bin/env python3
"""
本地 MoA（Mixture of Agents）脚本
方案：3 模型最优组合提案 + DeepSeek 聚合
实证最优：deepseek-v4-pro + MiniMax-M3 + qwen3.8-max-preview（15题互补性测试验证）
参考论文：ModelSwitch (2025), MoA (Together AI 2024), CORE (2026)

用法：
  python3 moa.py "你的问题"
  echo "你的问题" | python3 moa.py
  python3 moa.py --model single "你的问题"   # 单模型基线对比
"""

import os
import sys
import json
import time
import argparse
from concurrent.futures import ThreadPoolExecutor

# --- 配置 ---

PROPOSERS = [
    {
        "name": "DeepSeek V4 Pro",
        "api_base": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-v4-pro",
        "temperature": 0.6,
    },
    {
        "name": "MiniMax-M3",
        "api_base": "https://api.minimax.chat/v1",
        "api_key_env": "MINIMAX_API_KEY",
        "model": "MiniMax-M3",
        "temperature": 0.7,
    },
    {
        "name": "Qwen3.8-Max",
        "api_base": "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "QWEN_API_KEY",
        "model": "qwen3.8-max-preview",
        "temperature": 0.7,
    },
]

AGGREGATOR = {
    "name": "DeepSeek (聚合器)",
    "api_base": "https://api.deepseek.com",
    "api_key_env": "DEEPSEEK_API_KEY",
    "model": "deepseek-v4-pro",
    "temperature": 0.3,
}

AGGREGATOR_PROMPT = """你是一个 AI 委员会的聚合器。下面是 {n} 个独立 AI 对同一个问题的回答。

你的任务：
1. 找出所有回答中一致的结论
2. 找出各回答之间互补的部分——A 提到但 B 没提的关键点
3. 找出矛盾之处，判断哪个更可能正确（给出理由）
4. 高置信度的情况直接给出结论，不确定时诚实说明
5. 综合以上，给出一个最完整、最准确的最终答案

原始问题：
{question}

各模型回答：
{proposals}

最终综合答案："""


def _call_api(api_base: str, api_key: str, model: str, messages: list,
              temperature: float, max_tokens: int = 4096) -> str:
    import urllib.request
    import urllib.error

    url = f"{api_base.rstrip('/')}/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return f"[错误: HTTP {e.code}] {body[:500]}"
    except Exception as e:
        return f"[错误: {type(e).__name__}] {str(e)[:500]}"


def call_proposer(config: dict, question: str) -> tuple:
    api_key = os.environ.get(config["api_key_env"], "")
    if not api_key:
        return config["name"], f"[错误: 环境变量 {config['api_key_env']} 未设置]", 0

    messages = [{"role": "user", "content": question}]
    start = time.time()
    result = _call_api(
        config["api_base"], api_key, config["model"],
        messages, config["temperature"]
    )
    elapsed = time.time() - start
    return config["name"], result, elapsed


def run_moa(question: str, verbose: bool = False) -> str:
    t0 = time.time()

    if verbose:
        print(f"  → 并行调用 {len(PROPOSERS)} 个提案模型...")

    proposals = []
    with ThreadPoolExecutor(max_workers=len(PROPOSERS)) as pool:
        futures = [pool.submit(call_proposer, cfg, question) for cfg in PROPOSERS]
        for f in futures:
            name, result, elapsed = f.result()
            proposals.append((name, result))
            if verbose:
                ok = not result.startswith("[错误")
                print(f"    {'✓' if ok else '✗'} {name} ({elapsed:.1f}s)")

    t1 = time.time()

    if verbose:
        ok_count = sum(1 for _, r in proposals if not r.startswith("[错误"))
        print(f"  → 聚合器综合 {ok_count}/{len(proposals)} 个有效回答...")

    proposals_text = ""
    for i, (name, text) in enumerate(proposals):
        proposals_text += f"\n\n========== 回答 {i+1}：{name} ==========\n{text}"

    agg_messages = [{
        "role": "user",
        "content": AGGREGATOR_PROMPT.format(
            n=len(proposals), question=question, proposals=proposals_text,
        )
    }]

    api_key = os.environ.get(AGGREGATOR["api_key_env"], "")
    final = _call_api(
        AGGREGATOR["api_base"], api_key, AGGREGATOR["model"],
        agg_messages, AGGREGATOR["temperature"], max_tokens=8192,
    )

    t2 = time.time()
    if verbose:
        print(f"  → 完成 (提案 {t1-t0:.1f}s + 聚合 {t2-t1:.1f}s = {t2-t0:.1f}s)")

    return final


def run_single(question: str, verbose: bool = False) -> str:
    cfg = PROPOSERS[0]
    if verbose:
        print(f"  → 单模型 {cfg['name']} ...")
    name, result, elapsed = call_proposer(cfg, question)
    if verbose:
        print(f"    ✓ ({elapsed:.1f}s)")
    return result


def main():
    parser = argparse.ArgumentParser(description="本地 MoA — 多模型委员会")
    parser.add_argument("question", nargs="?", help="问题")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--model", choices=["moa", "single"], default="moa")
    parser.add_argument("--file", "-f")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            question = f.read().strip()
    elif args.question:
        question = args.question
    elif not sys.stdin.isatty():
        question = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    if not question:
        print("错误：问题不能为空"); sys.exit(1)

    keys_ok = True
    for cfg in PROPOSERS + [AGGREGATOR]:
        if not os.environ.get(cfg["api_key_env"]):
            print(f"错误：环境变量 {cfg['api_key_env']} 未设置"); keys_ok = False
    if not keys_ok:
        sys.exit(1)

    result = run_single(question, verbose=args.verbose) if args.model == "single" else run_moa(question, verbose=args.verbose)
    print(result)


if __name__ == "__main__":
    main()
