#!/usr/bin/env python3
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="")
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fast Product Factory OS gates before committing methodology changes.")
    parser.add_argument("--full", action="store_true", help="Also run meta_review.py and benchmark checks.")
    args = parser.parse_args()

    checks = [
        [sys.executable, "scripts/validate_structure.py"],
        [sys.executable, "scripts/run_fixtures.py"],
        [sys.executable, "scripts/validate_hooks.py"],
        [sys.executable, "scripts/validate_runtime.py"],
    ]
    if args.full:
        checks.extend([
            [sys.executable, "scripts/run_benchmarks.py"],
            [sys.executable, "scripts/meta_review.py"],
        ])

    for command in checks:
        code = run(command)
        if code != 0:
            print("PFO review-before-commit: blocked by " + " ".join(command))
            raise SystemExit(code)
    print("PFO review-before-commit: fast gates passed")


if __name__ == "__main__":
    main()
