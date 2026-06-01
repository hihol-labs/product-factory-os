#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import shlex
import sys
from typing import Any


TEMPLATE_ENV_SUFFIXES = (
    ".example",
    ".sample",
    ".template",
    ".templates",
    ".dist",
    ".defaults",
)

FILE_TOOL_NAMES = {
    "Read",
    "Edit",
    "Write",
    "MultiEdit",
    "NotebookEdit",
    "Glob",
    "Grep",
}

DELETE_DENY_PATTERNS = [
    re.compile(r"(^|\s)rm\s+[^;\n]*-(?:[^\s-]*r[^\s-]*f|[^\s-]*f[^\s-]*r|r|R|recursive)\b", re.I),
    re.compile(r"(^|\s)rm\s+[^;\n]*--recursive\b", re.I),
    re.compile(r"(^|\s)rmdir\b", re.I),
    re.compile(r"(^|\s)find\s+[^;\n]*\s-delete\b", re.I),
    re.compile(r"(^|\s)find\s+[^;\n]*\s-exec\s+rm\b", re.I),
    re.compile(r"(^|\s)git\s+clean\b[^;\n]*\s-d\b", re.I),
]


def is_env_template(path: str) -> bool:
    name = Path(path.replace("\\", "/")).name.lower()
    return name.startswith(".env.") and name.endswith(TEMPLATE_ENV_SUFFIXES)


def is_real_env_path(path: str) -> bool:
    normalized = path.replace("\\", "/").strip().strip("'\"")
    if not normalized:
        return False
    name = Path(normalized).name.lower()
    if name == ".env":
        return True
    if name.startswith(".env.") and not is_env_template(normalized):
        return True
    return False


def command_mentions_real_env(command: str) -> bool:
    lowered = command.lower()
    if re.search(r"(^|[\s/\\'\"])\.e\*($|[\s/\\'\"])", lowered):
        return True
    if re.search(r"(^|[\s/\\'\"])\.\?\?v($|[\s/\\'\"])", lowered):
        return True
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = command.split()
    return any(is_real_env_path(token) for token in tokens)


def command_has_recursive_delete(command: str) -> bool:
    return any(pattern.search(command) for pattern in DELETE_DENY_PATTERNS)


def extract_tool_name(payload: dict[str, Any]) -> str:
    for key in ["tool_name", "toolName", "name"]:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def extract_tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ["tool_input", "toolInput", "input", "arguments"]:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def paths_from_tool_input(tool_input: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ["file_path", "filePath", "path", "notebook_path", "notebookPath"]:
        value = tool_input.get(key)
        if isinstance(value, str):
            paths.append(value)
    for key in ["pattern", "glob", "include"]:
        value = tool_input.get(key)
        if isinstance(value, str):
            paths.append(value)
    return paths


def deny_reason(payload: dict[str, Any]) -> str | None:
    tool_name = extract_tool_name(payload)
    tool_input = extract_tool_input(payload)

    if tool_name in FILE_TOOL_NAMES:
        for path in paths_from_tool_input(tool_input):
            if is_real_env_path(path):
                return "Blocked real .env access; use .env.example/.sample/.template/.dist/.defaults instead."

    command = ""
    if tool_name in {"Bash", "Shell", "shell_command"}:
        command = str(tool_input.get("command") or tool_input.get("cmd") or "")
    elif "command" in payload:
        command = str(payload.get("command") or "")

    if command:
        if command_mentions_real_env(command):
            return "Blocked command that targets a real .env file; use template env files only."
        if command_has_recursive_delete(command):
            return "Blocked recursive directory deletion; use an explicit scoped deletion plan and approval."

    return None


def decision_payload(reason: str | None) -> dict[str, str]:
    if reason:
        return {"permissionDecision": "deny", "permissionDecisionReason": reason}
    return {"permissionDecision": "allow"}


def run_self_test() -> None:
    samples = [
        ({"tool_name": "Read", "tool_input": {"file_path": ".env"}}, True),
        ({"tool_name": "Read", "tool_input": {"file_path": ".env.example"}}, False),
        ({"tool_name": "Bash", "tool_input": {"command": "cat .env.local"}}, True),
        ({"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}}, True),
        ({"tool_name": "Bash", "tool_input": {"command": "python3 scripts/validate_project.py ."}}, False),
    ]
    for payload, should_deny in samples:
        denied = deny_reason(payload) is not None
        if denied != should_deny:
            raise SystemExit(f"ERROR: security guard self-test failed for {payload}")
    print("OK: security guard blocks real .env access and recursive deletes")


def main() -> None:
    parser = argparse.ArgumentParser(description="PFO PreToolUse security guard.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps(decision_payload(None)))
        return
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps(decision_payload(None)))
        return
    reason = deny_reason(payload if isinstance(payload, dict) else {})
    print(json.dumps(decision_payload(reason), ensure_ascii=False))


if __name__ == "__main__":
    main()
