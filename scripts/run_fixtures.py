#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"

EXPECTED_ROUTES = {
    "new-project": "/project -> /kickstart",
    "existing-bug": "/project redirects to /task -> /bugfix",
    "planning-only": "/project -> /blueprint",
    "deploy-production": "/task -> /deploy",
    "security-audit": "/task -> /security-audit",
    "adopt-existing": "/task -> /adopt",
    "migration": "/task -> /migrate",
    "pfo-bot": "/project -> /kickstart",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def extract_expected_route(text: str) -> str:
    match = re.search(r"Expected route:\s*```text\s*(.*?)\s*```", text, re.S)
    if not match:
        fail("fixture is missing an Expected route fenced block")
    return " ".join(match.group(1).split())


def main() -> None:
    checked = 0
    for name, expected in EXPECTED_ROUTES.items():
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

    print(f"OK: {checked} fixture routes and hook reminder match expectations")


if __name__ == "__main__":
    main()
