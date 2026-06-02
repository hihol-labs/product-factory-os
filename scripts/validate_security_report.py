#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SECTIONS = [
    "## Scope",
    "## Threat Model",
    "## Discovery",
    "## Validation",
    "## Attack Path",
    "## Findings",
    "## Coverage Artifacts",
    "## Final Decision",
]

REQUIRED_FINDING_FIELDS = [
    "Severity",
    "Confidence",
    "CWE",
    "Affected lines",
]

REQUIRED_FINDING_SUBSECTIONS = [
    "#### Summary",
    "#### Validation",
    "#### Dataflow",
    "#### Reachability",
    "#### Remediation",
]

REQUIRED_ARTIFACTS = [
    "deep_review_input.csv",
    "work_ledger.jsonl",
    "repository_coverage_ledger.md",
]

FINDING_RE = re.compile(r"^### \[(\d+)\]\s+(.+?)\s*$", re.MULTILINE)
FIELD_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$", re.MULTILINE)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"missing security report: {path}")
    return path.read_text(encoding="utf-8")


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def finding_body(text: str, finding: re.Match[str], next_finding: re.Match[str] | None) -> str:
    start = finding.end()
    end = next_finding.start() if next_finding else len(text)
    return text[start:end]


def metadata_fields(body: str) -> set[str]:
    first_subsection = body.find("\n#### ")
    region = body[: first_subsection if first_subsection != -1 else len(body)]
    return {match.group(1).strip().rstrip(":") for match in FIELD_ROW_RE.finditer(region)}


def validate_report_text(text: str) -> list[str]:
    errors: list[str] = []
    if not text.startswith("# Security Review:"):
        errors.append("line 1: report must start with '# Security Review: <target>'")

    positions: list[int] = []
    for section in REQUIRED_SECTIONS:
        match = re.search(rf"^{re.escape(section)}\s*$", text, flags=re.MULTILINE)
        if not match:
            errors.append(f"missing required section: {section}")
        else:
            positions.append(match.start())
    if len(positions) == len(REQUIRED_SECTIONS) and positions != sorted(positions):
        errors.append("required sections are not in the expected order")

    for artifact in REQUIRED_ARTIFACTS + ["candidate_ledger.jsonl"]:
        if artifact not in text:
            errors.append(f"report must reference coverage artifact: {artifact}")

    findings = list(FINDING_RE.finditer(text))
    no_findings = re.search(r"^### No findings\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if not findings and not no_findings:
        errors.append("Findings must contain numbered finding entries or '### No findings'")

    for index, finding in enumerate(findings):
        expected_number = index + 1
        actual_number = int(finding.group(1))
        line = line_number(text, finding.start())
        if actual_number != expected_number:
            errors.append(f"line {line}: finding number should be {expected_number}, got {actual_number}")
        body = finding_body(text, finding, findings[index + 1] if index + 1 < len(findings) else None)
        fields = metadata_fields(body)
        for field in REQUIRED_FINDING_FIELDS:
            if field not in fields:
                errors.append(f"line {line}: finding metadata missing {field}")
        for subsection in REQUIRED_FINDING_SUBSECTIONS:
            if not re.search(rf"^{re.escape(subsection)}\s*$", body, flags=re.MULTILINE):
                errors.append(f"line {line}: finding missing subsection {subsection}")
    return errors


def validate_artifacts(artifacts_dir: Path, require_candidate_ledger: bool) -> list[str]:
    errors: list[str] = []
    if not artifacts_dir.is_dir():
        return [f"missing artifacts directory: {artifacts_dir}"]

    for name in REQUIRED_ARTIFACTS:
        matches = list(artifacts_dir.rglob(name))
        if not matches:
            errors.append(f"missing coverage artifact: {name}")
        elif not matches[0].read_text(encoding="utf-8").strip():
            errors.append(f"coverage artifact is empty: {matches[0]}")

    candidate_ledgers = list(artifacts_dir.rglob("candidate_ledger.jsonl"))
    if require_candidate_ledger and not candidate_ledgers:
        errors.append("missing candidate_ledger.jsonl for numbered findings")
    for ledger in candidate_ledgers:
        text = ledger.read_text(encoding="utf-8").lower()
        for token in ["discovery", "validation", "attack_path"]:
            if token not in text:
                errors.append(f"{ledger}: missing {token} receipt")
    return errors


def check_template() -> None:
    template = ROOT / "docs" / "templates" / "SECURITY_AUDIT_REPORT.md"
    text = read(template)
    errors = validate_report_text(text)
    for token in [
        "threat model -> discovery -> validation -> attack path -> final report",
        "deep_review_input.csv",
        "work_ledger.jsonl",
        "repository_coverage_ledger.md",
        "candidate_ledger.jsonl",
        "PASSED_WITH_WARNINGS",
        "BLOCKED",
    ]:
        if token not in text:
            errors.append(f"template missing token: {token}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("OK: security audit report template contains required v2 sections and artifacts")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Product Factory OS security-audit v2 reports.")
    parser.add_argument("report", nargs="?", type=Path, help="Security report markdown file.")
    parser.add_argument("--file", type=Path, help="Explicit security report markdown file.")
    parser.add_argument("--artifacts-dir", type=Path, help="Directory containing coverage artifacts.")
    parser.add_argument("--self-check", action="store_true", help="Validate the PFO report template.")
    parser.add_argument("--require-artifacts", action="store_true", help="Require coverage artifacts to exist.")
    args = parser.parse_args()

    if args.self_check:
        check_template()
        return

    report = args.file or args.report
    if report is None:
        fail("provide a report path or --self-check")
    report = report.resolve()
    text = read(report)
    errors = validate_report_text(text)
    findings_present = bool(list(FINDING_RE.finditer(text)))

    if args.require_artifacts:
        artifacts_dir = args.artifacts_dir or report.parent / "artifacts"
        errors.extend(validate_artifacts(artifacts_dir.resolve(), require_candidate_ledger=findings_present))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: security report validated: {report}")


if __name__ == "__main__":
    main()
