#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
TRIGGERS = ROOT / "docs" / "TRIGGERS.md"
REMINDER = ROOT / "hooks" / "route-reminder.py"

NOISE = {
    "pr",
    "ci",
    "cve",
    "readme",
    "roadmap",
    "pivot",
    "market",
    "sync",
    "validate",
    "issue",
    "handoff",
    "obsidian",
    "owasp",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def split_phrases(cell: str) -> list[str]:
    phrases: list[str] = []
    for raw in re.split(r",|;", cell):
        phrase = raw.strip().strip("`")
        phrase = re.sub(r"\s+", " ", phrase)
        if not phrase:
            continue
        if phrase.lower() in NOISE:
            continue
        if len(phrase) < 4:
            continue
        phrases.append(phrase)
    return phrases


def trigger_rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    text = TRIGGERS.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("| `/"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        skill_match = re.match(r"`(/[^`]+)`", cells[0])
        if not skill_match:
            continue
        skill = skill_match.group(1)
        for cell in cells[1:3]:
            for phrase in split_phrases(cell):
                rows.append((skill, phrase))
    return rows


def route_for(phrase: str) -> str:
    result = subprocess.run(
        [sys.executable, str(REMINDER), phrase],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(result.stdout + result.stderr)
    return result.stdout.strip()


def main() -> None:
    if not TRIGGERS.is_file():
        fail("docs/TRIGGERS.md is missing")
    if not REMINDER.is_file():
        fail("hooks/route-reminder.py is missing")

    rows = trigger_rows()
    if not rows:
        fail("no trigger phrases found")

    errors: list[str] = []
    for skill, phrase in rows:
        route = route_for(phrase)
        if skill not in route:
            errors.append(f"{phrase!r} expected {skill}, got {route!r}")

    if errors:
        print("Trigger drift found:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"OK: {len(rows)} trigger phrase(s) route to the expected skill")


if __name__ == "__main__":
    main()
