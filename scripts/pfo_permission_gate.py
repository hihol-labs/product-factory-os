#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys
from typing import Any


CAPABILITIES = {"read", "write", "test", "commit", "push", "deploy", "external_api", "secrets", "context_budget"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing {path}")
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")


def validate_matrix(matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    caps = matrix.get("capabilities", {})
    if not isinstance(caps, dict):
        return ["capabilities must be an object"]
    for capability in sorted(CAPABILITIES):
        if capability not in caps:
            errors.append(f"missing capability {capability}")
            continue
        item = caps[capability]
        if not isinstance(item, dict):
            errors.append(f"{capability}: must be an object")
            continue
        if item.get("default") not in {"allow", "allow_when_declared", "scoped", "block"}:
            errors.append(f"{capability}: invalid default {item.get('default')!r}")
        if "approvalRequired" not in item:
            errors.append(f"{capability}: missing approvalRequired")
        if not isinstance(item.get("evidence", []), list) or not item.get("evidence"):
            errors.append(f"{capability}: evidence must be a non-empty list")
    return errors


def allowed_write_areas(project: Path, policy: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    areas: list[str] = []
    write_policy = policy.get("writePolicy", {}) if isinstance(policy.get("writePolicy", {}), dict) else {}
    if isinstance(write_policy.get("allowedWriteAreas"), list):
        areas.extend(str(item) for item in write_policy["allowedWriteAreas"])
    if isinstance(manifest.get("allowedWriteAreas"), list):
        areas.extend(str(item) for item in manifest["allowedWriteAreas"])
    normalized: list[str] = []
    for area in areas:
        if not area or "files listed by" in area:
            continue
        normalized.append(area.rstrip("/"))
    return normalized


def path_in_scope(path: str, areas: list[str]) -> bool:
    if not path:
        return False
    normalized = path.strip().lstrip("./").replace("\\", "/")
    for area in areas:
        area_norm = area.lstrip("./").replace("\\", "/")
        if normalized == area_norm or normalized.startswith(area_norm.rstrip("/") + "/"):
            return True
    return False


def command_allowed(command: str, policy: dict[str, Any]) -> bool:
    command_policy = policy.get("commandPolicy", {}) if isinstance(policy.get("commandPolicy", {}), dict) else {}
    lowered = command.lower()
    for dangerous in command_policy.get("dangerousCommands", []):
        if str(dangerous).lower() in lowered:
            return False
    for item in command_policy.get("allowedCommands", []):
        prefix = str(item.get("commandPrefix", "")).strip()
        if prefix and command.startswith(prefix):
            allowed_args = item.get("allowedArgs", [])
            if not allowed_args:
                return True
            if any(str(arg) in command for arg in allowed_args):
                return True
    return command_policy.get("default") != "deny-unless-declared"


def decision(project: Path, capability: str, path: str, command: str, approved: bool) -> tuple[str, str]:
    matrix = read_json(project / ".pfo" / "PERMISSION_MATRIX.json")
    policy = read_json(project / ".pfo" / "EXECUTION_POLICY.json")
    manifest_path = project / ".pfo" / "UNIT_CONTEXT_MANIFEST.json"
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    errors = validate_matrix(matrix)
    if errors:
        return "BLOCKED", "; ".join(errors)
    item = matrix["capabilities"].get(capability)
    if not item:
        return "BLOCKED", f"unknown capability {capability}"
    default = item.get("default")
    approval_required = item.get("approvalRequired")

    if command and not command_allowed(command, policy):
        if approved:
            return "PASSED_WITH_WARNINGS", "command outside execution policy explicitly approved"
        return "BLOCKED", "command is not allowed by execution policy"

    if default == "allow":
        return "PASSED", "allowed by permission matrix"
    if default == "allow_when_declared":
        if capability == "test" and (project / ".pfo" / "VERIFICATION_CONTRACT.json").is_file():
            return "PASSED", "verification contract declares test capability"
        if capability == "context_budget":
            matrix = read_json(project / ".pfo" / "PERMISSION_MATRIX.json")
            if matrix.get("contextRuntimePolicy"):
                return "PASSED", "context runtime policy declares context budget capability"
        return "BLOCKED", "capability must be declared first"
    if default == "scoped":
        if capability == "write" and path:
            if path_in_scope(path, allowed_write_areas(project, policy, manifest)):
                return "PASSED", "write path is in allowed scope"
            if approved:
                return "PASSED_WITH_WARNINGS", "approved write outside declared scope"
            return "BLOCKED", "write path is outside allowed scope"
        if capability == "commit":
            return ("PASSED_WITH_WARNINGS", "commit approved") if approved else ("BLOCKED", "commit requires request or approval")
        if capability == "external_api":
            return ("PASSED_WITH_WARNINGS", "external API action approved") if approved else ("BLOCKED", "external API write or sensitive read requires approval")
        return "PASSED_WITH_WARNINGS", "scoped capability requires caller-specific scope evidence"
    if default == "block":
        if approved:
            return "PASSED_WITH_WARNINGS", "blocked capability explicitly approved"
        return "BLOCKED", "capability is blocked without approval"

    if approval_required is True and not approved:
        return "BLOCKED", "approval required"
    return "PASSED", "permission gate passed"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Product Factory OS permission matrix and check a capability.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--capability", choices=sorted(CAPABILITIES))
    parser.add_argument("--path", default="")
    parser.add_argument("--command", default="")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    matrix = read_json(project / ".pfo" / "PERMISSION_MATRIX.json")
    errors = validate_matrix(matrix)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    if not args.capability:
        print("OK: permission matrix validated")
        return
    status, reason = decision(project, args.capability, args.path, args.command, args.approved)
    payload = {"status": status, "reason": reason, "capability": args.capability}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{status}: {reason}")
    if status == "BLOCKED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
