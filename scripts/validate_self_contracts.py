#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import re
import sys

from pfo_contract_gate import REQUIRED_CONTRACTS, is_self_adopted_pfo_repo, missing_contracts


ROOT = Path(__file__).resolve().parents[1]
TOKEN_PATTERNS = [
    re.compile(r"replace this line", re.I),
    re.compile(r"\bTBD\b", re.I),
    re.compile(r"\bTODO\b", re.I),
    re.compile(r"\bplace\s*holder\b", re.I),
]


def fail(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}")
    raise SystemExit(1)


def contract_token_errors(project: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_CONTRACTS:
        path = project / rel
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if any(pattern.search(line) for pattern in TOKEN_PATTERNS):
                errors.append(f"{rel}:{number} contains a template token")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate self-adopted Product Factory OS contracts.")
    parser.add_argument("project", nargs="?", type=Path, default=ROOT)
    args = parser.parse_args()

    project = args.project.resolve()
    if not is_self_adopted_pfo_repo(project):
        print(f"OK: {project} is not a self-adopted PFO runtime repo")
        return

    errors = [f"missing self contract: {item}" for item in missing_contracts(project)]
    errors.extend(contract_token_errors(project))
    if errors:
        fail(errors)
    print(f"OK: self-adopted PFO contracts are concrete: {project}")


if __name__ == "__main__":
    main()
