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


def route_evidence_text(fixture: str, contract: dict) -> str:
    snapshot = contracts.route_snapshot(fixture, contract.get("skill"))
    expected_route = snapshot.get("expectedRoute", contract.get("skill", ""))
    return (
        f"Expected route: {expected_route}\n"
        f"Skill: {contract.get('skill', '')}\n"
        "Quality evidence: route correctness, artifact quality, tool safety, and state save are recorded when required.\n"
        "Approval mode: read-only or explicit confirmation before live external, migration, infrastructure, or production writes.\n"
        "Session save: verification, blockers, and next action are documented.\n"
    )


def mock_file_body(fixture: str, contract: dict, rel: str, tokens: list[str]) -> str:
    route_text = route_evidence_text(fixture, contract)
    if rel.endswith(".json"):
        return json.dumps(
            {
                "fixture": fixture,
                "status": "ADOPTED",
                "route": contracts.route_snapshot(fixture, contract.get("skill")).get("expectedRoute", contract.get("skill")),
                "state": "saved",
                "verification": "mock headless quality proof",
                "blockers": [],
                "nextAction": "inspect live proof before release",
                "tokens": tokens + ["Product Factory OS"],
            },
            indent=2,
        ) + "\n"
    return (
        "# PFO headless mock artifact\n\n"
        + route_text
        + "\n"
        + "\n".join(tokens)
        + "\n\nVerification: mock output satisfies the behavioural contract and quality graders.\n"
        + "Blockers: none for mock validation.\n"
        + "Next action: run live command-mode proof before release when this fixture is critical.\n"
    )


def write_mock_output(output_dir: Path, fixture: str, contract: dict) -> str:
    output = contract.get("output_contract", {})
    stdout_parts = [route_evidence_text(fixture, contract), *output.get("stdout_must_contain", [])]
    base_tokens = output.get("any_file_must_contain", [])
    for item in output.get("required_files", []):
        target = output_dir / item
        if item.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(mock_file_body(fixture, contract, item, base_tokens), encoding="utf-8")
    for rel, tokens in output.get("files_must_contain", {}).items():
        target = output_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        target.write_text(existing + "\n" + mock_file_body(fixture, contract, rel, tokens), encoding="utf-8")
    if output.get("any_file_must_contain") and not output.get("required_files"):
        target = output_dir / "PFO_HEADLESS_REPORT.md"
        target.write_text(mock_file_body(fixture, contract, "PFO_HEADLESS_REPORT.md", output["any_file_must_contain"]), encoding="utf-8")
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


def output_file_names(output_dir: Path) -> list[str]:
    if not output_dir.exists():
        return []
    return sorted(str(path.relative_to(output_dir)) for path in output_dir.rglob("*") if path.is_file())


def read_output_file(output_dir: Path, rel: str) -> str:
    target = output_dir / rel
    if not target.is_file():
        return ""
    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def all_output_text(output_dir: Path) -> str:
    return "\n".join(read_output_file(output_dir, rel) for rel in output_file_names(output_dir))


def add_check(checks: list[dict], kind: str, expected: str, actual: str, passed: bool) -> None:
    checks.append(
        {
            "kind": kind,
            "expected": expected,
            "actual": actual,
            "status": "PASSED" if passed else "FAILED",
        }
    )


def build_comparison(
    fixture: str,
    contract: dict,
    output_dir: Path,
    stdout_text: str,
    exit_code: int,
    mode: str,
    errors: list[str],
) -> dict:
    output = contract.get("output_contract", {})
    files = output_file_names(output_dir)
    checks: list[dict] = []

    if mode == "command":
        add_check(checks, "command_exit", "exit code 0", str(exit_code), exit_code == 0)

    for item in output.get("required_files", []):
        target = output_dir / item
        if item.endswith("/"):
            passed = target.is_dir()
            actual = "directory present" if passed else "directory missing"
        else:
            passed = target.is_file()
            actual = "file present" if passed else "file missing"
        add_check(checks, "required_file", item, actual, passed)

    for pattern in output.get("forbidden_files", []):
        matches = sorted(str(path.relative_to(output_dir)) for path in output_dir.glob(pattern))
        add_check(checks, "forbidden_file", pattern, ", ".join(matches) if matches else "no matches", not matches)

    stdout_lower = stdout_text.lower()
    for token in output.get("stdout_must_contain", []):
        add_check(checks, "stdout_contains", token, "present" if token.lower() in stdout_lower else "missing", token.lower() in stdout_lower)

    for rel, tokens in output.get("files_must_contain", {}).items():
        text = read_output_file(output_dir, rel).lower()
        for token in tokens:
            add_check(checks, "file_contains", f"{rel}: {token}", "present" if token.lower() in text else "missing", token.lower() in text)

    for rel, tokens in output.get("files_must_not_contain", {}).items():
        text = read_output_file(output_dir, rel).lower()
        for token in tokens:
            add_check(checks, "file_not_contains", f"{rel}: {token}", "absent" if token.lower() not in text else "present", token.lower() not in text)

    combined_text = all_output_text(output_dir).lower()
    for token in output.get("any_file_must_contain", []):
        add_check(checks, "any_file_contains", token, "present" if token.lower() in combined_text else "missing", token.lower() in combined_text)

    quality_errors = contracts.validate_quality_graders(fixture, contract, output_dir, stdout_text)
    for grader in contract.get("quality_graders", []):
        grader_errors = [item for item in quality_errors if f"{grader} grader" in item or f"unknown quality grader {grader!r}" in item]
        add_check(
            checks,
            "quality_grader",
            grader,
            "; ".join(grader_errors) if grader_errors else "passed",
            not grader_errors,
        )

    return {
        "fixture": fixture,
        "mode": mode,
        "status": "PASSED" if not errors else "FAILED",
        "expected": output,
        "actual": {
            "exitCode": exit_code,
            "stdoutPreview": stdout_text[:4000],
            "files": files,
        },
        "checks": checks,
        "errors": errors,
    }


def comparison_markdown(comparison: dict) -> str:
    lines = [
        f"# Headless Comparison: {comparison['fixture']}",
        "",
        f"- Mode: `{comparison['mode']}`",
        f"- Status: `{comparison['status']}`",
        f"- Exit code: `{comparison['actual']['exitCode']}`",
        "",
        "## Expected",
        "",
        "```json",
        json.dumps(comparison["expected"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Actual",
        "",
        "Files:",
    ]
    files = comparison["actual"].get("files", [])
    lines.extend(f"- `{item}`" for item in files)
    if not files:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Kind | Expected | Actual | Status |",
            "|---|---|---|---|",
        ]
    )
    for check in comparison["checks"]:
        lines.append(
            f"| {check['kind']} | {check['expected']} | {check['actual']} | {check['status']} |"
        )
    if comparison["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in comparison["errors"])
    return "\n".join(lines) + "\n"


def write_comparison(log_dir: Path, comparison: dict) -> tuple[str, str]:
    json_path = log_dir / "comparison.json"
    md_path = log_dir / "comparison.md"
    json_path.write_text(json.dumps(comparison, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(comparison_markdown(comparison), encoding="utf-8")
    return str(json_path), str(md_path)


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
        stdout = write_mock_output(output_dir, fixture, contract)
        errors = contracts.validate_output(fixture, contract, output_dir, stdout)
        errors.extend(contracts.validate_quality_graders(fixture, contract, output_dir, stdout))
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
        errors.extend(contracts.validate_quality_graders(fixture, contract, output_dir, stdout))
    else:
        fail(f"unknown mode: {mode}")

    comparison = build_comparison(fixture, contract, output_dir, stdout, code, mode, errors)
    comparison_json, comparison_md = write_comparison(log_dir, comparison)
    return {
        "fixture": fixture,
        "mode": mode,
        "status": "PASSED" if not errors else "FAILED",
        "errors": errors,
        "durationSeconds": round(time.time() - started, 3),
        "outputDir": str(output_dir),
        "comparisonJson": comparison_json,
        "comparisonMarkdown": comparison_md,
        "_comparison": comparison,
    }


def write_aggregate_comparison(run_root: Path, payload: dict, comparisons: list[dict]) -> tuple[str, str]:
    report = {
        "mode": payload["mode"],
        "status": "PASSED" if payload["failed"] == 0 else "FAILED",
        "total": payload["total"],
        "passed": payload["passed"],
        "failed": payload["failed"],
        "comparisons": comparisons,
    }
    json_path = run_root / "PFO_HEADLESS_COMPARISON.json"
    md_path = run_root / "PFO_HEADLESS_COMPARISON.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# PFO Headless Expected/Actual Comparison",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Status: `{report['status']}`",
        f"- Fixtures: `{report['passed']}/{report['total']} passed`",
        "",
        "| Fixture | Status | Failed Checks | Comparison |",
        "|---|---|---:|---|",
    ]
    for comparison in comparisons:
        failed_checks = sum(1 for check in comparison["checks"] if check["status"] != "PASSED")
        fixture = comparison["fixture"]
        lines.append(f"| {fixture} | {comparison['status']} | {failed_checks} | `{fixture}/logs/comparison.md` |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(json_path), str(md_path)


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
    comparisons = [item.pop("_comparison") for item in results]
    payload = {
        "mode": args.mode,
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "runRoot": str(run_root),
        "results": results,
    }
    comparison_json, comparison_md = write_aggregate_comparison(run_root, payload, comparisons)
    payload["comparisonJson"] = comparison_json
    payload["comparisonMarkdown"] = comparison_md

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"PFO headless fixtures: {payload['passed']}/{payload['total']} passed ({args.mode})")
        if args.output_root or args.keep_output or failed:
            print(f"Comparison report: {comparison_md}")
        else:
            print("Comparison report: pass --output-root or --keep-output to preserve expected/actual artifacts")
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
