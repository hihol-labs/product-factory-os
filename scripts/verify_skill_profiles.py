#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
DANGEROUS_EFFECTS = {"production-impact", "data-migration", "infrastructure-write", "external-write"}
EFFORTS = {"low", "medium", "high"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    block = text[4:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.strip().split(":", 1)
        data[key.strip()] = value.strip()
    return data


def main() -> None:
    errors: list[str] = []
    for path in sorted(SKILLS.glob("*/SKILL.md")):
        skill = "/" + path.parent.name
        text = path.read_text(encoding="utf-8")
        data = frontmatter(text)
        effort = data.get("effort")
        side_effect = data.get("side_effect")
        explicit = data.get("explicit_invocation")
        if effort not in EFFORTS:
            errors.append(f"{skill}: effort must be one of {sorted(EFFORTS)}")
        if not side_effect:
            errors.append(f"{skill}: side_effect is required")
        if explicit not in {"true", "false"}:
            errors.append(f"{skill}: explicit_invocation must be true or false")
        if side_effect in DANGEROUS_EFFECTS and explicit != "true":
            errors.append(f"{skill}: dangerous side_effect {side_effect!r} requires explicit_invocation: true")
        if "## Self-validation" not in text:
            errors.append(f"{skill}: missing ## Self-validation")
        if "## Rules" not in text:
            errors.append(f"{skill}: missing ## Rules")

    route_reminder = (ROOT / "hooks" / "route-reminder.py").read_text(encoding="utf-8")
    if "DANGEROUS_ROUTES" not in route_reminder or "PFO risk guard" not in route_reminder:
        errors.append("hooks/route-reminder.py must include dangerous route risk guard")
    for name in ["deploy", "migrate", "infra", "github-workflow", "tool-sync"]:
        if f'"/{name}"' not in route_reminder:
            errors.append(f"hooks/route-reminder.py DANGEROUS_ROUTES missing /{name}")

    contracts = (ROOT / "docs" / "SKILL_CONTRACTS.md").read_text(encoding="utf-8")
    if "Side Effects" not in contracts:
        errors.append("docs/SKILL_CONTRACTS.md must keep Side Effects column")
    if not re.search(r"/deploy.*Production impact", contracts, flags=re.S):
        errors.append("docs/SKILL_CONTRACTS.md must document /deploy production impact")

    if errors:
        print("Skill profile drift found:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("OK: skill effort, side-effect, explicit-invocation, and self-validation profiles are complete")


if __name__ == "__main__":
    main()
