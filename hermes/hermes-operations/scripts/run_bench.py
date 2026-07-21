#!/usr/bin/env python3
"""
Hermes Model Benchmark Runner

Usage:
    python run_bench.py --profile deepseek --task simple-tools
    python run_bench.py --profile deepseek   # all tasks
    python run_bench.py                      # all profiles × all tasks

Results saved to: ../results/<profile>-<task>-<timestamp>.json
"""

import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
TASKS_DIR = SCRIPT_DIR.parent / "tasks"
RESULTS_DIR = SCRIPT_DIR.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

PROFILES = {
    "deepseek": "bench-deepseek",
    "mimo": "bench-mimo",
    "qwen": "bench-qwen",
}

TASK_FILES = {
    "simple-tools": TASKS_DIR / "tool-calling" / "simple-tools.md",
    "chained-tools": TASKS_DIR / "tool-calling" / "chained-tools.md",
    "error-recovery": TASKS_DIR / "tool-calling" / "error-recovery.md",
    "coding": TASKS_DIR / "coding" / "code-tasks.md",
    "instruction": TASKS_DIR / "instruction-following" / "instruction-tasks.md",
    "skill-usage": TASKS_DIR / "skill-usage" / "complex-workflow.md",
}


def run_task(profile_name: str, profile_label: str, task_key: str,
             task_file: Path, timeout: int = 300) -> dict:
    """Run a single task on a profile, return result dict."""
    prompt = task_file.read_text(encoding="utf-8")
    start = time.time()

    result = {
        "profile": profile_label,
        "task_name": task_key,
        "task_file": str(task_file),
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "elapsed_seconds": 0,
        "stdout": "",
        "stderr": "",
        "exit_code": None,
    }

    try:
        proc = subprocess.run(
            ["hermes", "chat", "-q", "--profile", profile_name, prompt],
            capture_output=True, text=True, timeout=timeout
        )
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
        result["exit_code"] = proc.returncode
        result["success"] = proc.returncode == 0 and len(proc.stdout.strip()) > 0
    except subprocess.TimeoutExpired as e:
        result["stderr"] = f"TIMEOUT after {timeout}s"
        result["exit_code"] = -1
        result["stdout"] = e.stdout or ""
    except Exception as e:
        result["stderr"] = str(e)
        result["exit_code"] = -2

    result["elapsed_seconds"] = time.time() - start

    # Save result
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    fname = f"{profile_label}-{task_key}-{ts}.json"
    (RESULTS_DIR / fname).write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description="Hermes Model Benchmark")
    parser.add_argument("-p", "--profile", choices=list(PROFILES.keys()),
                        help="Run on specific profile only")
    parser.add_argument("-t", "--task", choices=list(TASK_FILES.keys()),
                        help="Run specific task only")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Timeout per task in seconds")
    args = parser.parse_args()

    profiles = {args.profile: PROFILES[args.profile]} if args.profile else PROFILES
    tasks = {args.task: TASK_FILES[args.task]} if args.task else TASK_FILES
    total = len(profiles) * len(tasks)
    done = 0

    print(f"\n{'='*60}")
    print(f"Hermes Benchmark: {len(profiles)} profiles × {len(tasks)} tasks = {total} runs")
    print(f"{'='*60}\n")

    all_results = {}

    for pkey, pname in profiles.items():
        all_results[pkey] = {}
        for tkey, tfile in tasks.items():
            done += 1
            print(f"[{done}/{total}] {pkey:>8}  ×  {tkey:<25} ", end="", flush=True)

            result = run_task(pname, pkey, tkey, tfile, timeout=args.timeout)
            status = "OK" if result["success"] else "FAIL"
            print(f"→ {status} ({result['elapsed_seconds']:.1f}s)")
            all_results[pkey][tkey] = result

    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "profiles": list(profiles.keys()),
        "tasks": list(tasks.keys()),
        "results": {
            p: {
                t: {
                    "success": r["success"],
                    "elapsed": r["elapsed_seconds"],
                    "output_chars": len(r.get("stdout", "")),
                }
                for t, r in tasks_results.items()
            }
            for p, tasks_results in all_results.items()
        },
        "stats": {
            p: {
                "passed": sum(1 for r in tasks_results.values() if r["success"]),
                "total": len(tasks_results),
                "avg_time": sum(r["elapsed_seconds"] for r in tasks_results.values()) / len(tasks_results) if tasks_results else 0,
            }
            for p, tasks_results in all_results.items()
        },
    }
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    (RESULTS_DIR / f"summary-{ts}.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Print summary table
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for pkey, stats in summary["stats"].items():
        print(f"  {pkey:>8}: {stats['passed']}/{stats['total']} passed, avg {stats['avg_time']:.1f}s")
    print(f"\nResults: {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
