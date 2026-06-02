#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def run(command: list[str], expected: str | None = None, allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if not allow_fail and result.returncode != 0:
        fail("command failed: " + " ".join(command) + "\n" + result.stdout + result.stderr)
    if expected and expected not in (result.stdout + result.stderr):
        fail(f"expected {expected!r} from {' '.join(command)}, got {result.stdout!r}{result.stderr!r}")
    return result


def main() -> None:
    for rel in [
        "scripts/pfo_context_runtime.py",
        "hooks/context-budget.py",
        "docs/templates/pfo/PERMISSION_MATRIX.json",
        "docs/templates/pfo/EXECUTION_POLICY.json",
    ]:
        if not (ROOT / rel).is_file():
            fail(f"missing {rel}")

    for rel in [
        "docs/templates/pfo/PERMISSION_MATRIX.json",
        ".pfo/PERMISSION_MATRIX.json",
    ]:
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        policy = data.get("contextRuntimePolicy", {})
        for field in ["limits", "routing", "index", "snapshot", "evidence"]:
            if field not in policy:
                fail(f"{rel} contextRuntimePolicy missing {field}")
        if not policy["routing"].get("summaryRequired"):
            fail(f"{rel} must require summary routing")

    run([sys.executable, "scripts/pfo_context_runtime.py", "validate", str(ROOT)], "OK:")
    run([sys.executable, "scripts/pfo_context_runtime.py", "budget", str(ROOT), "--kind", "read", "--bytes", "16000"], "PASSED_WITH_WARNINGS")
    run(
        [sys.executable, "scripts/pfo_context_runtime.py", "budget", str(ROOT), "--kind", "http", "--command-text", "curl https://example.com"],
        "BLOCKED",
        allow_fail=True,
    )
    run([sys.executable, "hooks/context-budget.py", "--self-test"], "OK:")
    run([sys.executable, "scripts/pfo_context_runtime.py", "index", str(ROOT)], "OK:")
    run([sys.executable, "scripts/pfo_context_runtime.py", "search", str(ROOT), "context", "runtime", "--limit", "2"], "Context search:")
    run([sys.executable, "scripts/pfo_context_runtime.py", "snapshot", str(ROOT), "--reason", "validator", "--quiet"])
    if not (ROOT / ".codex-memory" / "context-index.json").is_file():
        fail("context search index was not written")
    if not (ROOT / ".codex-memory" / "resume-snapshot.md").is_file():
        fail("resume snapshot was not written")
    print("OK: context runtime budget, search index, snapshot, and hook routing validated")


if __name__ == "__main__":
    main()
