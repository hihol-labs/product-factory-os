#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import verify_fixture_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def selected_fixtures(names: list[str] | None) -> list[str]:
    available = sorted(contracts.all_contracts())
    if not names:
        return available
    missing = sorted(set(names) - set(available))
    if missing:
        fail("unknown fixture(s): " + ", ".join(missing))
    return names


def write_mock_output(output_dir: Path, contract: dict) -> str:
    output = contract.get("output_contract", {})
    stdout_parts = output.get("stdout_must_contain", [])
    for item in output.get("required_files", []):
        target = output_dir / item
        if item.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# PFO headless mock artifact\n\n"
            + "\n".join(output.get("any_file_must_contain", []))
            + "\n",
            encoding="utf-8",
        )
    for rel, tokens in output.get("files_must_contain", {}).items():
        target = output_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        target.write_text(existing + "\n" + "\n".join(tokens) + "\n", encoding="utf-8")
    if output.get("any_file_must_contain") and not output.get("required_files"):
        target = output_dir / "PFO_HEADLESS_REPORT.md"
        target.write_text("\n".join(output["any_file_must_contain"]) + "\n", encoding="utf-8")
    return "\n".join(stdout_parts)


def run_command(template: str, fixture: str, output_dir: Path, timeout: int) -> tuple[int, str, str]:
    fixture_dir = FIXTURES / fixture
    prompt_file = fixture_dir / "idea.md"
    command = template.format(
        fixture=fixture,
        fixture_dir=str(fixture_dir),
        prompt_file=str(prompt_file),
        output_dir=str(output_dir),
        root=str(ROOT),
    )
    env = os.environ.copy()
    env.update(
        {
            "PFO_FIXTURE": fixture,
            "PFO_FIXTURE_DIR": str(fixture_dir),
            "PFO_PROMPT_FILE": str(prompt_file),
            "PFO_OUTPUT_DIR": str(output_dir),
            "PFO_ROOT": str(ROOT),
        }
    )
    result = subprocess.run(
        command,
        cwd=output_dir,
        env=env,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def run_one(fixture: str, contract: dict, mode: str, command_template: str | None, run_root: Path, timeout: int) -> dict:
    output_dir = run_root / fixture / "output"
    log_dir = run_root / fixture / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    stdout = ""
    stderr = ""
    code = 0

    if mode == "contract-only":
        errors = contracts.check_output_contract(FIXTURES / fixture, contract)
    elif mode == "mock":
        stdout = write_mock_output(output_dir, contract)
        errors = contracts.validate_output(fixture, contract, output_dir, stdout)
    elif mode == "command":
        if not command_template:
            fail("--command-template or PFO_HEADLESS_COMMAND is required for command mode")
        code, stdout, stderr = run_command(command_template, fixture, output_dir, timeout)
        (log_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
        (log_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
        errors = []
        if code != 0:
            errors.append(f"{fixture}: command exited with {code}")
        errors.extend(contracts.validate_output(fixture, contract, output_dir, stdout))
    else:
        fail(f"unknown mode: {mode}")

    return {
        "fixture": fixture,
        "mode": mode,
        "status": "PASSED" if not errors else "FAILED",
        "errors": errors,
        "durationSeconds": round(time.time() - started, 3),
        "outputDir": str(output_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or validate PFO behavioural fixtures in headless mode.")
    parser.add_argument("--fixture", action="append", help="Fixture name. Can be passed multiple times.")
    parser.add_argument("--mode", choices=["contract-only", "mock", "command"], default="contract-only")
    parser.add_argument("--command-template", default=os.environ.get("PFO_HEADLESS_COMMAND"))
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--keep-output", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    loaded = contracts.all_contracts()
    names = selected_fixtures(args.fixture)
    temp_dir = None
    if args.output_root:
        run_root = args.output_root
        run_root.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="pfo-headless-")
        run_root = Path(temp_dir.name)

    results = [
        run_one(name, loaded[name], args.mode, args.command_template, run_root, args.timeout)
        for name in names
    ]
    failed = [item for item in results if item["status"] != "PASSED"]
    payload = {
        "mode": args.mode,
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "runRoot": str(run_root),
        "results": results,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"PFO headless fixtures: {payload['passed']}/{payload['total']} passed ({args.mode})")
        for item in failed:
            print(f"- {item['fixture']}: " + "; ".join(item["errors"]))

    if temp_dir and (args.keep_output or failed):
        preserved = ROOT / ".pfo-headless-runs" / str(int(time.time()))
        preserved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(run_root, preserved)
        print(f"Preserved output: {preserved}")
    if temp_dir:
        temp_dir.cleanup()
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
