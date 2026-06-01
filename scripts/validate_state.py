#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "memory" / "session-state.schema.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def validate_state(path: Path) -> None:
    schema = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    state = json.loads(path.read_text(encoding="utf-8"))
    required = schema.get("requiredFields", [])

    for field in required:
        if field not in state:
            fail(f"{path}: missing required state field {field}")

    if not isinstance(state.get("classification"), dict):
        fail(f"{path}: classification must be an object")
    if not isinstance(state.get("architecture"), dict):
        fail(f"{path}: architecture must be an object")
    if not isinstance(state.get("existingProject"), dict):
        fail(f"{path}: existingProject must be an object")
    if not isinstance(state.get("gateResults"), dict):
        fail(f"{path}: gateResults must be an object")
    if not isinstance(state.get("verificationHistory"), list):
        fail(f"{path}: verificationHistory must be a list")
    if not isinstance(state.get("decisionLog"), list):
        fail(f"{path}: decisionLog must be a list")
    if not isinstance(state.get("artifacts"), list):
        fail(f"{path}: artifacts must be a list")
    if not isinstance(state.get("humanSteering"), dict):
        fail(f"{path}: humanSteering must be an object")
    steering = state.get("humanSteering", {})
    if not steering.get("approvalStatus"):
        fail(f"{path}: humanSteering.approvalStatus must not be empty")
    if not steering.get("recommendedNextStep"):
        fail(f"{path}: humanSteering.recommendedNextStep must not be empty")
    gates = state.get("gateResults", {})
    if "nextStepApproval" not in gates:
        fail(f"{path}: gateResults.nextStepApproval must be present")
    if not state.get("nextAction"):
        fail(f"{path}: nextAction must not be empty")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Product Factory OS .codex-memory/STATE.json files.")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    for path in args.paths:
        if not path.is_file():
            fail(f"missing state file: {path}")
        validate_state(path)

    print(f"OK: validated {len(args.paths)} state file(s)")


if __name__ == "__main__":
    main()
