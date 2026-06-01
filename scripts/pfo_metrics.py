#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime
import json


SUCCESS_STATUSES = {"PASS", "PASSED", "PASS_WITH_WARNINGS", "PASSED_WITH_WARNINGS", "READY", "RECORDED", "CANDIDATE_RULE"}
FAILURE_STATUSES = {"BLOCKED", "FAILED", "ERROR", "RECOVERY_REQUIRED"}


def parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_events(project: Path) -> list[dict]:
    path = project / ".codex-memory" / "events.jsonl"
    if not path.is_file():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def efficiency_metrics(project_states: list[tuple[Path, dict]]) -> dict:
    verification_events = 0
    passed_verifications = 0
    gate_events = 0
    passed_gates = 0
    repair_loop_count = 0
    first_valid_unit_seconds = []

    for project, state in project_states:
        events = load_events(project)
        manifest_times: dict[str, datetime] = {}
        verified_units: set[str] = set()
        for event in events:
            status = str(event.get("status", "")).upper()
            if status in FAILURE_STATUSES:
                repair_loop_count += 1

            event_type = event.get("eventType")
            if event_type == "gate":
                gate_events += 1
                if status in SUCCESS_STATUSES:
                    passed_gates += 1
            if event_type == "verification":
                verification_events += 1
                if status in SUCCESS_STATUSES:
                    passed_verifications += 1

            payload = event.get("payload", {})
            payload = payload if isinstance(payload, dict) else {}
            timestamp = parse_timestamp(str(event.get("timestamp", "")))
            if not timestamp:
                continue
            if event_type == "state-change" and payload.get("command") == "manifest":
                unit_id = str(payload.get("unitId", ""))
                if unit_id and unit_id not in manifest_times:
                    manifest_times[unit_id] = timestamp
            if event_type == "verification" and status in SUCCESS_STATUSES:
                unit_id = str(payload.get("node", ""))
                if unit_id and unit_id in manifest_times and unit_id not in verified_units:
                    delta = (timestamp - manifest_times[unit_id]).total_seconds()
                    if delta >= 0:
                        first_valid_unit_seconds.append(delta)
                        verified_units.add(unit_id)

        failed_validations = state.get("failedValidations", [])
        if isinstance(failed_validations, list):
            repair_loop_count += len(failed_validations)
        blockers = state.get("blockers", [])
        if isinstance(blockers, list) and blockers:
            repair_loop_count += 1

    avg_time = None
    if first_valid_unit_seconds:
        avg_time = round(sum(first_valid_unit_seconds) / len(first_valid_unit_seconds), 2)
    repair_per_verified = None
    if passed_verifications:
        repair_per_verified = round(repair_loop_count / passed_verifications, 4)
    verification_pass_rate = None
    if verification_events:
        verification_pass_rate = round(passed_verifications / verification_events, 4)
    gate_pass_rate = None
    if gate_events:
        gate_pass_rate = round(passed_gates / gate_events, 4)

    return {
        "verifiedUnitCount": passed_verifications,
        "repairLoopCount": repair_loop_count,
        "repairLoopsPerVerifiedUnit": repair_per_verified,
        "verificationPassRate": verification_pass_rate,
        "gatePassRate": gate_pass_rate,
        "timeToFirstValidUnitSeconds": {
            "sampleCount": len(first_valid_unit_seconds),
            "average": avg_time,
            "values": [round(value, 2) for value in first_valid_unit_seconds],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Product Factory OS workspace metrics.")
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()

    project_states = []
    for state_path in args.workspace.glob("*/.codex-memory/STATE.json"):
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        project_states.append((state_path.parents[1], state))
    projects = [state for _, state in project_states]

    metrics = {
        "projectCount": len(projects),
        "deployReadyCount": sum(1 for item in projects if item.get("currentStage") == "READY_FOR_DEPLOY"),
        "deployedCount": sum(1 for item in projects if item.get("currentStage") == "DEPLOYED"),
        "blockedCount": sum(1 for item in projects if item.get("blockers")),
        "failedGateCount": sum(len(item.get("failedValidations", [])) for item in projects),
        "verificationEvents": sum(len(item.get("verificationHistory", [])) for item in projects),
        "harnessEfficiency": efficiency_metrics(project_states),
    }
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
