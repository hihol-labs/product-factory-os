#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

import verify_fixture_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]
CRITICAL_RELEASE_FIXTURES = [
    "deploy-production",
    "migration",
    "infra-generate",
    "github-workflow",
    "tool-sync",
    "security-audit",
    "session-save",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def validate_config(fixtures: list[str]) -> None:
    loaded = contracts.all_contracts()
    if not 5 <= len(fixtures) <= 7:
        fail("release live headless proof must cover 5 to 7 critical fixtures")
    missing = [name for name in fixtures if name not in loaded]
    if missing:
        fail("release live headless proof references unknown fixture(s): " + ", ".join(missing))
    for name in fixtures:
        contract = loaded[name]
        if contract.get("status") != "active":
            fail(f"{name}: release fixture contract must be active")
        if not contract.get("release_headless_required"):
            fail(f"{name}: release fixture must set release_headless_required")
        if not contract.get("output_contract"):
            fail(f"{name}: release fixture needs an output_contract")
        if not contract.get("quality_graders"):
            fail(f"{name}: release fixture needs quality_graders")


def validate_proof(proof_root: Path, fixtures: list[str], max_age_hours: float) -> None:
    payload_path = proof_root / "PFO_HEADLESS_COMPARISON.json"
    if not payload_path.is_file():
        fail(f"missing live proof comparison: {payload_path}")
    age_hours = (time.time() - payload_path.stat().st_mtime) / 3600
    if age_hours > max_age_hours:
        fail(f"live proof is stale: {age_hours:.1f}h old, max {max_age_hours:.1f}h")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    if payload.get("mode") != "command":
        fail("release proof must be command-mode live headless output")
    if payload.get("status") != "PASSED":
        fail("release proof status must be PASSED")
    comparisons = {item.get("fixture"): item for item in payload.get("comparisons", [])}
    missing = [name for name in fixtures if name not in comparisons]
    if missing:
        fail("release proof missing critical fixture(s): " + ", ".join(missing))
    for name in fixtures:
        comparison = comparisons[name]
        if comparison.get("status") != "PASSED":
            fail(f"{name}: release proof comparison did not pass")
        failed_checks = [item for item in comparison.get("checks", []) if item.get("status") != "PASSED"]
        if failed_checks:
            fail(f"{name}: release proof has failed checks")
    print(f"OK: release live headless proof artifact is current and passed for {len(fixtures)} critical fixtures")


def default_command_template() -> str:
    return os.environ.get("PFO_HEADLESS_COMMAND") or f"{sys.executable} {{root}}/scripts/pfo_headless_adapter.py"


def run_live(fixtures: list[str], command_template: str, output_root: Path, timeout: int) -> None:
    command = [
        sys.executable,
        "scripts/run_headless_fixtures.py",
        "--mode",
        "command",
        "--command-template",
        command_template,
        "--output-root",
        str(output_root),
        "--timeout",
        str(timeout),
    ]
    for fixture in fixtures:
        command.extend(["--fixture", fixture])
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        fail("release live headless proof failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Require live command-mode headless proof before release.")
    parser.add_argument("--check-config", action="store_true", help="Validate release proof wiring without running Codex.")
    parser.add_argument("--proof-root", type=Path, default=os.environ.get("PFO_RELEASE_LIVE_PROOF"), help="Validate an existing live proof root instead of running Codex.")
    parser.add_argument("--fixture", action="append", help="Override fixture set. Must still contain 5 to 7 fixtures.")
    parser.add_argument("--command-template", default=default_command_template())
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--max-age-hours", type=float, default=24)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    fixtures = args.fixture or CRITICAL_RELEASE_FIXTURES
    validate_config(fixtures)
    if args.check_config:
        print(f"OK: release live headless proof requires {len(fixtures)} critical fixtures")
        return
    if args.proof_root:
        validate_proof(args.proof_root, fixtures, args.max_age_hours)
        return

    output_root = args.output_root or ROOT / ".pfo-headless-runs" / f"release-{int(time.time())}"
    run_live(fixtures, args.command_template, output_root, args.timeout)
    print(f"OK: release live headless proof passed for {len(fixtures)} critical fixtures")


if __name__ == "__main__":
    main()
