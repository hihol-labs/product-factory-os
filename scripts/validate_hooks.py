#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def command_path(command: str) -> Path:
    parts = command.split()
    if len(parts) < 2:
        fail(f"hook command is too short: {command}")
    return ROOT / parts[1]


def run(command: list[str], expected: str) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        fail("hook command failed: " + " ".join(command) + "\n" + result.stdout + result.stderr)
    if expected not in result.stdout:
        fail(f"expected {expected!r} in output from {' '.join(command)}, got {result.stdout!r}")


def main() -> None:
    hooks_path = ROOT / "hooks" / "hooks.json"
    data = json.loads(hooks_path.read_text(encoding="utf-8"))
    hooks = data.get("hooks", [])
    names = {hook.get("name") for hook in hooks}
    for expected in [
        "route-reminder",
        "preflight-context",
        "security-guard",
        "context-budget-pre",
        "context-budget-post",
        "session-diagnostics",
        "skill-completeness",
        "commit-completeness",
        "review-before-commit",
    ]:
        if expected not in names:
            fail(f"hooks/hooks.json is missing {expected}")

    for hook in hooks:
        path = command_path(hook.get("command", ""))
        if not path.is_file():
            fail(f"hook command references missing file: {path.relative_to(ROOT)}")

    preflight = (ROOT / "hooks" / "preflight-context.py").read_text(encoding="utf-8")
    for token in ["EXECUTION_POLICY.json", "PERMISSION_MATRIX.json", "PERMISSION_MATRIX.md", "VERIFICATION_CONTRACT.json", "TOOL_CAPABILITY_REGISTRY.json", "events.jsonl", "PFO_EXISTING_PROJECT_ANALYSIS.json", "PFO_REPORT.md"]:
        if token not in preflight:
            fail(f"preflight-context.py missing policy/event token {token}")

    run([sys.executable, "hooks/route-reminder.py", "plan only, architecture first"], "/blueprint")
    run([sys.executable, "hooks/route-reminder.py", "latest SDK docs"], "/mcp-docs")
    run([sys.executable, "hooks/security-guard.py", "--self-test"], "OK:")
    run([sys.executable, "hooks/context-budget.py", "--self-test"], "OK:")
    run([sys.executable, "hooks/skill-completeness.py", "--skill", "project"], "OK:")
    print(f"OK: {len(hooks)} hook contracts validated")


if __name__ == "__main__":
    main()
