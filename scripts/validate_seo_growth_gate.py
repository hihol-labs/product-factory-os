#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FIELDS = [
    "baseline metric",
    "target metric",
    "measurement source",
    "attribution window",
    "implemented changes",
    "exclusion factors",
    "result decision",
    "next iteration",
]

VALID_GATE_STATUSES = {"PENDING", "BLOCKED", "PASSED_WITH_WARNINGS", "PASSED"}
VALID_DECISIONS = {"PENDING", "KEEP", "DISCARD", "ITERATE", "BLOCKED", "STOP"}
PLACEHOLDERS = {"", "-", "tbd", "todo", "pending", "unknown"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"missing SEO growth gate: {path}")
    return path.read_text(encoding="utf-8")


def parse_table_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = normalize(cells[0])
        if key == "field":
            continue
        fields[key] = cells[1]
    return fields


def extract_gate_status(text: str, fields: dict[str, str]) -> str:
    if "gate status" in fields:
        return fields["gate status"].strip().upper()
    match = re.search(r"(?im)^\s*gate status\s*:\s*([A-Z_]+)\s*$", text)
    if match:
        return match.group(1).strip().upper()
    fenced = re.search(r"## Gate Status\s*```text\s*([A-Z_ |]+)\s*```", text, flags=re.S)
    if fenced:
        return "PENDING"
    return ""


def check_template() -> None:
    template = ROOT / "docs" / "templates" / "SEO_GROWTH_GUARANTEE_GATE.md"
    text = read(template)
    fields = parse_table_fields(text)
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if normalize(field) not in fields:
            errors.append(f"template missing field: {field}")
    for token in ["SEO Growth Guarantee Gate", "PENDING", "BLOCKED", "PASSED_WITH_WARNINGS", "PASSED"]:
        if token not in text:
            errors.append(f"template missing token: {token}")
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print("OK: SEO growth guarantee gate template contains required fields and statuses")


def validate_gate(path: Path, allow_pending: bool = False) -> None:
    text = read(path)
    fields = parse_table_fields(text)
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        key = normalize(field)
        value = fields.get(key, "").strip()
        if normalize(value) in PLACEHOLDERS:
            errors.append(f"{field}: missing concrete value")

    status = extract_gate_status(text, fields)
    if status and status not in VALID_GATE_STATUSES:
        errors.append(f"gate status must be one of {sorted(VALID_GATE_STATUSES)}")
    if status == "PENDING" and not allow_pending:
        errors.append("gate status is PENDING; pass --allow-pending for in-flight SEO measurement")

    decision = fields.get("result decision", "").strip().upper()
    if decision and decision not in VALID_DECISIONS:
        errors.append(f"result decision must be one of {sorted(VALID_DECISIONS)}")
    if decision == "PENDING" and not allow_pending:
        errors.append("result decision is PENDING; pass --allow-pending for in-flight SEO measurement")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: SEO growth guarantee gate validated: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SEO_GROWTH_GUARANTEE_GATE.md.")
    parser.add_argument("project", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--file", type=Path, help="Explicit gate file path.")
    parser.add_argument("--self-check", action="store_true", help="Validate the PFO template shape.")
    parser.add_argument("--allow-pending", action="store_true", help="Allow in-flight PENDING status or decision.")
    args = parser.parse_args()

    if args.self_check:
        check_template()
        return

    path = args.file or args.project / "SEO_GROWTH_GUARANTEE_GATE.md"
    validate_gate(path.resolve(), allow_pending=args.allow_pending)


if __name__ == "__main__":
    main()
