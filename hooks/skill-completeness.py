#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def fixture_routes() -> dict[str, str]:
    path = ROOT / "tests" / "snapshots" / "route-snapshots.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["skill"].lstrip("/"): item["fixture"] for item in data.get("snapshots", [])}


def check_skill(skill: str, routes: dict[str, str]) -> list[str]:
    errors = []
    skill_file = ROOT / "skills" / skill / "SKILL.md"
    if not skill_file.is_file():
        return [f"missing skills/{skill}/SKILL.md"]
    text = skill_file.read_text(encoding="utf-8")
    if f"name: {skill}" not in text:
        errors.append(f"/{skill}: frontmatter name mismatch")
    for doc in ["docs/SKILL_CONTRACTS.md", "docs/TRIGGERS.md"]:
        body = (ROOT / doc).read_text(encoding="utf-8")
        if f"`/{skill}`" not in body:
            errors.append(f"/{skill}: missing from {doc}")
    fixture = routes.get(skill)
    if not fixture:
        errors.append(f"/{skill}: missing route snapshot")
    else:
        fixture_dir = ROOT / "tests" / "fixtures" / fixture
        if not fixture_dir.is_dir():
            errors.append(f"/{skill}: snapshot references missing fixture {fixture}")
        for name in ["idea.md", "expected-files.txt", "notes.md"]:
            if not (fixture_dir / name).is_file():
                errors.append(f"/{skill}: fixture {fixture} missing {name}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Product Factory OS skill contract completeness.")
    parser.add_argument("--skill", action="append", help="Check one skill. Can be passed multiple times.")
    args = parser.parse_args()

    routes = fixture_routes()
    skills = args.skill or sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))
    errors: list[str] = []
    for skill in skills:
        errors.extend(check_skill(skill, routes))
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"OK: {len(skills)} skill contract(s) have docs, triggers, and route snapshots")


if __name__ == "__main__":
    main()
