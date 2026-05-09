#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print("PFO commit completeness: no staged git diff available; skipping")
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> None:
    changed = changed_files()
    if not changed:
        print("PFO commit completeness: no staged files")
        return

    missing: list[str] = []
    changed_set = set(changed)
    skill_changes = [path for path in changed if path.startswith("skills/") and path.endswith("/SKILL.md")]
    if skill_changes:
        for required in ["docs/SKILL_CONTRACTS.md", "docs/TRIGGERS.md", "tests/snapshots/route-snapshots.json"]:
            if required not in changed_set:
                missing.append(required)

    runtime_changes = [
        path for path in changed
        if path.startswith(("routing/", "templates/", "execution/", "pipelines/", "memory/", "deployment/", "scripts/"))
    ]
    if runtime_changes:
        for required in ["docs/PFO_ARCHITECTURE.md", "docs/ROADMAP.md", "CHANGELOG.md"]:
            if required not in changed_set:
                missing.append(required)

    hook_changes = [path for path in changed if path.startswith("hooks/")]
    if hook_changes:
        for required in ["hooks/hooks.json", "hooks/README.md", "scripts/validate_hooks.py"]:
            if required not in changed_set:
                missing.append(required)

    if missing:
        print("PFO commit completeness: staged change is missing supporting artifacts:")
        for item in sorted(set(missing)):
            print(f"- {item}")
        raise SystemExit(1)

    print("PFO commit completeness: staged scope has supporting methodology artifacts")


if __name__ == "__main__":
    main()
