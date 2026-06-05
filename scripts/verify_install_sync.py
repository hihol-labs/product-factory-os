#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    hooks = json.loads(read("hooks/hooks.json")).get("hooks", [])
    installer = read("scripts/install_workspace.py")
    install_docs = read("docs/INSTALL.md")
    workflow = read(".github/workflows/validate.yml")
    packaging = read("packaging/install.sh")
    errors: list[str] = []

    for hook in hooks:
        command = hook.get("command", "")
        parts = command.split()
        if len(parts) < 2:
            errors.append(f"{hook.get('name')}: invalid command {command!r}")
            continue
        path = ROOT / parts[1]
        if not path.is_file():
            errors.append(f"{hook.get('name')}: command references missing {parts[1]}")

    required_snippets = [
        'glob("*.py")',
        '"hooks.json"',
        "validate_hooks.py",
    ]
    for snippet in required_snippets:
        if snippet not in installer and snippet not in packaging and snippet not in install_docs:
            errors.append(f"install sync missing snippet {snippet!r}")

    for command in [
        "python3 scripts/verify_triggers.py",
        "python3 scripts/verify_fixture_contracts.py",
        "python3 scripts/run_headless_fixtures.py --mode mock",
        "python3 scripts/validate_eval_layer.py",
        "python3 scripts/verify_skill_profiles.py",
        "python3 scripts/validate_control_harness.py",
        "python3 scripts/validate_defensive_layers.py",
        "python3 scripts/validate_self_contracts.py",
        "python3 scripts/validate_context_runtime.py",
        "python3 scripts/validate_tool_registry.py docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json integrations/tool-capability-registry.json",
        "python3 scripts/verify_manifest_drift.py",
        "python3 scripts/verify_install_sync.py",
        "python3 scripts/production_readiness.py",
    ]:
        if command not in workflow:
            errors.append(f".github/workflows/validate.yml must run {command}")
        if command not in install_docs:
            errors.append(f"docs/INSTALL.md must document {command}")

    hook_names = {hook.get("name") for hook in hooks}
    if "session-diagnostics" not in hook_names:
        errors.append("hooks/hooks.json must register session-diagnostics")

    if not re.search(r"install_hooks\(codex_home\)", installer):
        errors.append("scripts/install_workspace.py must install hooks by default")

    if errors:
        print("Install/hook sync drift found:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"OK: {len(hooks)} hooks are present in manifest, installer, docs, and CI sync checks")


if __name__ == "__main__":
    main()
