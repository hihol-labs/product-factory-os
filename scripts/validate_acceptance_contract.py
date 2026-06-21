#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PASS_STATUSES = {"PASSED"}
ALL_STATUSES = {"PENDING", "PASSED", "FAILED", "WAIVED"}
EVIDENCE_KINDS = {
    "command",
    "test",
    "review",
    "security",
    "manual",
    "artifact",
    "production_readiness",
    "contract_gate",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path} must contain a JSON object")
    return data


def changed_files(project: Path) -> set[str]:
    result: set[str] = set()
    for args in (["diff", "--name-only", "HEAD"], ["diff", "--cached", "--name-only"]):
        completed = subprocess.run(
            ["git", *args],
            cwd=project,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            result.update(line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip())
    return result


def text_mentions_changed_validator(text: str, changed: set[str]) -> str:
    normalized = text.replace("\\", "/")
    for rel in sorted(changed):
        path = Path(rel)
        if len(path.parts) >= 2 and path.parts[0] == "scripts":
            name = path.name
            if name.startswith("validate") and name.endswith(".py") and (rel in normalized or name in normalized):
                return rel
    return ""


def require_text(item: dict, field: str, label: str) -> str:
    value = item.get(field, "")
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} missing non-empty {field}")
    return value.strip()


def validate_criterion(item: dict, index: int, changed: set[str], allow_waived: bool) -> None:
    if not isinstance(item, dict):
        fail(f"criteria[{index}] must be an object")
    criterion_id = require_text(item, "id", f"criteria[{index}]")
    label = f"criterion {criterion_id}"
    requirement = require_text(item, "requirement", label)
    source = require_text(item, "source", label)
    source_quote = require_text(item, "sourceQuote", label)
    verification = require_text(item, "verification", label)
    status = require_text(item, "status", label).upper()
    if status not in ALL_STATUSES:
        fail(f"{label} status must be one of {', '.join(sorted(ALL_STATUSES))}")
    if not requirement or not source_quote or not verification or source.lower() not in {"user_request", "user", "product_owner"}:
        fail(f"{label} must trace to an explicit user requirement and verification method")
    if status == "WAIVED":
        if not allow_waived:
            fail(f"{label} is WAIVED; strict acceptance gate requires PASSED")
        require_text(item, "approvedBy", label)
        require_text(item, "approvedAt", label)
        return
    if status not in PASS_STATUSES:
        fail(f"{label} is {status}; all acceptance criteria must be PASSED")
    evidence = require_text(item, "evidence", label)
    evidence_kind = require_text(item, "evidenceKind", label)
    if evidence_kind not in EVIDENCE_KINDS:
        fail(f"{label} evidenceKind must be one of {', '.join(sorted(EVIDENCE_KINDS))}")
    weak_validator = text_mentions_changed_validator(" ".join([verification, evidence]), changed)
    if weak_validator:
        independent = item.get("independentEvidence")
        if not isinstance(independent, str) or not independent.strip():
            fail(
                f"{label} relies on changed validator {weak_validator}; "
                "add independentEvidence from a command, review, or external artifact"
            )


def validate_contract(project: Path, allow_waived: bool = False) -> None:
    path = project / ".pfo" / "ACCEPTANCE_CONTRACT.json"
    if not path.is_file():
        fail(f"missing acceptance contract: {path}")
    data = load_json(path)
    if data.get("version") != 1:
        fail("ACCEPTANCE_CONTRACT.json version must be 1")
    require_text(data, "originalRequest", "acceptance contract")
    if data.get("createdBeforeImplementation") is not True:
        fail("acceptance contract must set createdBeforeImplementation=true")
    criteria = data.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        fail("acceptance contract must define non-empty criteria")
    ids: set[str] = set()
    changed = changed_files(project)
    for index, item in enumerate(criteria):
        validate_criterion(item, index, changed, allow_waived)
        criterion_id = item["id"]
        if criterion_id in ids:
            fail(f"duplicate acceptance criterion id: {criterion_id}")
        ids.add(criterion_id)


def self_check() -> None:
    required = [
        "scripts/validate_acceptance_contract.py",
        "docs/templates/pfo/ACCEPTANCE_CONTRACT.json",
        "docs/gates/acceptance-contract-gate.md",
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            fail(f"missing acceptance enforcement artifact: {rel}")
    pfo_text = (ROOT / "scripts" / "pfo.py").read_text(encoding="utf-8")
    for token in [
        "cmd_acceptance",
        "validate_acceptance_contract.py",
        "ACCEPTANCE_CONTRACT.json",
        "acceptanceContract",
    ]:
        if token not in pfo_text:
            fail(f"scripts/pfo.py missing acceptance runtime token {token}")
    control_text = (ROOT / "docs" / "CONTROL_HARNESS.md").read_text(encoding="utf-8")
    if "acceptance-contract" not in control_text:
        fail("docs/CONTROL_HARNESS.md missing acceptance-contract control")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate PFO acceptance contracts.")
    parser.add_argument("project", nargs="?", type=Path, default=ROOT)
    parser.add_argument("--allow-waived", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        self_check()
        print("OK: acceptance contract runtime wiring validated")
        return
    validate_contract(args.project.resolve(), allow_waived=args.allow_waived)
    print("OK: acceptance contract passed")


if __name__ == "__main__":
    main()
