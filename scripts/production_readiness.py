#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    [sys.executable, "scripts/validate_structure.py"],
    [sys.executable, "scripts/validate_plan_quality.py", "--self-check"],
    [sys.executable, "scripts/run_fixtures.py"],
    [sys.executable, "scripts/verify_triggers.py"],
    [sys.executable, "scripts/verify_fixture_contracts.py"],
    [sys.executable, "scripts/run_headless_fixtures.py", "--mode", "mock"],
    [sys.executable, "scripts/verify_skill_profiles.py"],
    [sys.executable, "scripts/validate_execution_graph.py"],
    [sys.executable, "scripts/validate_runtime.py"],
    [sys.executable, "scripts/validate_hooks.py"],
    [sys.executable, "scripts/verify_manifest_drift.py"],
    [sys.executable, "scripts/verify_install_sync.py"],
    [sys.executable, "scripts/run_benchmarks.py"],
    [sys.executable, "scripts/meta_review.py"],
]


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="")
        print("PFO production readiness: blocked by " + " ".join(command))
        raise SystemExit(result.returncode)


def main() -> None:
    for command in CHECKS:
        run(command)
    print("OK: Product Factory OS production-readiness gate passed")


if __name__ == "__main__":
    main()
