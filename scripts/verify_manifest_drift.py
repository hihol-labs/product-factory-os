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


def count_skills() -> int:
    return len(list((ROOT / "skills").glob("*/SKILL.md")))


def count_agents() -> int:
    return len(list((ROOT / "agents").glob("*.md")))


def count_hooks() -> int:
    data = json.loads(read("hooks/hooks.json"))
    return len(data.get("hooks", []))


def scan_count_drift(path: Path, skills: int, agents: int, hooks: int) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.startswith("|") or "CHANGELOG" in str(path):
            continue
        for match in re.finditer(r"(?<![-\w])(\d+)\s+(skills?|скилл\w*)", line, flags=re.I):
            value = int(match.group(1))
            if value != skills:
                errors.append(f"{path.relative_to(ROOT)}:{lineno}: skill count {value} != {skills}")
        for match in re.finditer(r"(?<![-\w])(\d+)\s+(agents?|агент\w*)", line, flags=re.I):
            value = int(match.group(1))
            if value != agents:
                errors.append(f"{path.relative_to(ROOT)}:{lineno}: agent count {value} != {agents}")
        for match in re.finditer(r"(?<![-\w])(\d+)\s+(hooks?|хук\w*)", line, flags=re.I):
            value = int(match.group(1))
            if value != hooks:
                errors.append(f"{path.relative_to(ROOT)}:{lineno}: hook count {value} != {hooks}")
    return errors


def main() -> None:
    skills = count_skills()
    agents = count_agents()
    hooks = count_hooks()
    manifest = json.loads(read(".codex-plugin/plugin.json"))
    marketplace = json.loads(read("marketplace/marketplace-entry.json"))
    errors: list[str] = []

    if manifest.get("version") != marketplace.get("version"):
        errors.append("marketplace/marketplace-entry.json version differs from .codex-plugin/plugin.json")
    if not marketplace.get("images"):
        errors.append("marketplace/marketplace-entry.json must include images for catalog polish")
    if "## [" + manifest.get("version", "") + "]" not in read("CHANGELOG.md"):
        errors.append("CHANGELOG.md is missing manifest version entry")

    docs_to_scan = [
        ROOT / "README.md",
        ROOT / "README.ru.md",
        ROOT / "docs" / "INSTALL.md",
        ROOT / "docs" / "WORKSPACE_DEFAULTS.md",
    ]
    for path in docs_to_scan:
        if path.is_file():
            errors.extend(scan_count_drift(path, skills, agents, hooks))

    if errors:
        print("Manifest/documentation drift found:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"OK: manifest, marketplace, and public counts match {skills} skills, {agents} agents, {hooks} hooks")


if __name__ == "__main__":
    main()
