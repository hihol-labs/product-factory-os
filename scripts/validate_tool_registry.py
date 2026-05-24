#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys
from typing import Any

REQUIRED_TOOL_FIELDS = [
    "id",
    "type",
    "usedBy",
    "capabilities",
    "sideEffects",
    "authNeeded",
    "externalDataRisk",
    "fallbackMode",
    "approvalRequiredFor",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def validate_registry(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")
    tools = data.get("tools")
    if not isinstance(tools, list) or not tools:
        fail(f"{path}: tools must be a non-empty list")
    seen: set[str] = set()
    for index, tool in enumerate(tools, start=1):
        if not isinstance(tool, dict):
            fail(f"{path}: tool {index} must be an object")
        for field in REQUIRED_TOOL_FIELDS:
            if field not in tool:
                fail(f"{path}: tool {index} missing {field}")
        tool_id = str(tool["id"])
        if tool_id in seen:
            fail(f"{path}: duplicate tool id {tool_id}")
        seen.add(tool_id)
        capabilities = tool.get("capabilities")
        if not isinstance(capabilities, dict):
            fail(f"{path}: {tool_id}.capabilities must be an object")
        for capability in ["read", "write", "execute"]:
            if capability not in capabilities or not isinstance(capabilities[capability], bool):
                fail(f"{path}: {tool_id}.capabilities.{capability} must be boolean")
        for field in ["usedBy", "approvalRequiredFor"]:
            if not isinstance(tool.get(field), list):
                fail(f"{path}: {tool_id}.{field} must be a list")
        if not isinstance(tool.get("authNeeded"), bool):
            fail(f"{path}: {tool_id}.authNeeded must be boolean")
        if tool["capabilities"].get("write") and not tool.get("approvalRequiredFor"):
            fail(f"{path}: {tool_id} writes but has no approvalRequiredFor")
    print(f"OK: validated {len(tools)} tool capabilities in {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Product Factory OS tool capability registry.")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.paths:
        if not path.is_file():
            fail(f"missing registry: {path}")
        validate_registry(path)


if __name__ == "__main__":
    main()
