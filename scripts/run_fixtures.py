#!/usr/bin/env python3
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
SNAPSHOTS = ROOT / "tests" / "snapshots" / "route-snapshots.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def extract_expected_route(text: str) -> str:
    match = re.search(r"Expected route:\s*```text\s*(.*?)\s*```", text, re.S)
    if not match:
        fail("fixture is missing an Expected route fenced block")
    return " ".join(match.group(1).split())


def main() -> None:
    snapshots = json.loads(SNAPSHOTS.read_text(encoding="utf-8")).get("snapshots", [])
    checked = 0
    for item in snapshots:
        name = item["fixture"]
        expected = item["expectedRoute"]
        idea_path = FIXTURES / name / "idea.md"
        if not idea_path.is_file():
            fail(f"missing fixture idea file: {idea_path.relative_to(ROOT)}")
        actual = extract_expected_route(idea_path.read_text())
        normalized_expected = " ".join(expected.split())
        if actual != normalized_expected:
            fail(f"fixture {name} route mismatch: expected {expected!r}, got {actual!r}")
        checked += 1

    reminder = subprocess.run(
        [sys.executable, "hooks/route-reminder.py", "Deploy web service to production"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if "/deploy" not in reminder.stdout:
        fail("route-reminder hook did not suggest /deploy for deploy prompt")

    pfo_reminder = subprocess.run(
        [sys.executable, "hooks/route-reminder.py", "Сделай Telegram бот для продаж с CRM"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if "/project" not in pfo_reminder.stdout:
        fail("route-reminder hook did not suggest /project for PFO bot prompt")

    for item in snapshots:
        if item.get("reminderPrompt"):
            reminder = subprocess.run(
                [sys.executable, "hooks/route-reminder.py", item["reminderPrompt"]],
                cwd=ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            expected_skill = item["skill"]
            if expected_skill not in reminder.stdout:
                fail(f"route-reminder hook did not suggest {expected_skill} for fixture {item['fixture']}")

    print(f"OK: {checked} fixture routes and hook reminder match expectations")


if __name__ == "__main__":
    main()
