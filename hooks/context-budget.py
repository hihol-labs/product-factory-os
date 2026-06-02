#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import importlib.util
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "scripts" / "pfo_context_runtime.py"


def load_runtime():
    spec = importlib.util.spec_from_file_location("pfo_context_runtime", RUNTIME)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing pfo_context_runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description="Route large tool outputs through the PFO context budget gate.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--phase", choices=["pre", "post"], default="post")
    parser.add_argument("--kind", choices=["tool", "read", "log", "web", "http", "grep", "rg"], default="tool")
    parser.add_argument("--bytes", type=int, default=0)
    parser.add_argument("--lines", type=int, default=0)
    parser.add_argument("--command-text", default="")
    parser.add_argument("--raw-http", action="store_true")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    runtime = load_runtime()
    project = args.project.resolve()
    policy = runtime.load_policy(project)
    if args.self_test:
        status, _ = runtime.budget_decision(
            policy,
            "http",
            0,
            0,
            "curl https://example.com",
            False,
            False,
        )
        if status != "BLOCKED":
            print("ERROR: context budget hook did not block raw HTTP")
            raise SystemExit(1)
        print("OK: context budget hook blocks raw HTTP and can evaluate output budgets")
        return

    byte_count = args.bytes
    line_count = args.lines
    if args.phase == "pre" and args.command_text:
        byte_count = 0
        line_count = 0
    status, reason = runtime.budget_decision(
        policy,
        args.kind,
        byte_count,
        line_count,
        args.command_text,
        args.raw_http,
        args.approved,
    )
    payload = {"status": status, "reason": reason, "phase": args.phase}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"PFO context budget {args.phase}: {status}: {reason}")
    if status == "BLOCKED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
