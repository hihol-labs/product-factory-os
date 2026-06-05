#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime
import json


ROOT = Path(__file__).resolve().parents[1]
SUCCESS_STATUSES = {"PASS", "PASSED", "PASS_WITH_WARNINGS", "PASSED_WITH_WARNINGS", "READY", "RECORDED", "CANDIDATE_RULE"}
FAILURE_STATUSES = {"BLOCKED", "FAILED", "ERROR", "RECOVERY_REQUIRED"}
ROUTE_PROFILE_IDS = {"minimal", "standard", "full"}


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


def load_route_profiles() -> dict:
    path = ROOT / "routing" / "route-profiles.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"defaultProfile": "standard", "profiles": {}}


def select_route_profile(state: dict) -> tuple[str, str]:
    active = state.get("activeRouteProfile", {}) if isinstance(state.get("activeRouteProfile"), dict) else {}
    active_id = str(active.get("id", ""))
    if active_id in ROUTE_PROFILE_IDS:
        return active_id, "active state route profile"

    manifest = state.get("unitContextManifest", {}) if isinstance(state.get("unitContextManifest"), dict) else {}
    manifest_profile = manifest.get("routeProfile", {}) if isinstance(manifest.get("routeProfile"), dict) else {}
    manifest_id = str(manifest_profile.get("id", ""))
    if manifest_id in ROUTE_PROFILE_IDS:
        return manifest_id, "manifest route profile"

    existing = state.get("existingProject", {}) if isinstance(state.get("existingProject"), dict) else {}
    current_unit = state.get("currentUnit", {}) if isinstance(state.get("currentUnit"), dict) else {}
    text = " ".join(
        [
            str(state.get("currentTaskRoute", "")),
            str(existing.get("currentTaskRoute", "")),
            str(current_unit.get("goal", "")),
            str(state.get("intent", "")),
        ]
    ).lower()
    if any(term in text for term in ["/project", "/kickstart", "/blueprint", "/deploy", "/migrate", "/security-audit", "/harden", "production", "release", "security"]):
        return "full", "high-risk or broad route hint"
    if any(term in text for term in ["/doc", "/explain", "/review", "small task", "tiny change", "typo", "readme", "docs-only", "no behavior change", "маленьк", "мелк"]):
        return "minimal", "small-task route hint"
    return "standard", "default route profile"


def is_concrete_artifact(value: str) -> bool:
    value = str(value)
    if not value or " " in value or "<" in value or ">" in value:
        return False
    return any(value.endswith(suffix) for suffix in [".md", ".json", ".jsonl", ".tsv", ".csv", ".html"])


def artifact_debt_metrics(project_states: list[tuple[Path, dict]]) -> dict:
    profiles = load_route_profiles().get("profiles", {})
    by_project = {}
    total_missing = 0
    total_extra = 0
    for project, state in project_states:
        profile_id, reason = select_route_profile(state)
        profile = profiles.get(profile_id, {})
        required = [item for item in profile.get("requiredArtifacts", []) if is_concrete_artifact(item)]
        optional = [item for item in profile.get("optionalArtifacts", []) if is_concrete_artifact(item)]
        allowed = set(required) | set(optional)
        tracked = set(state.get("artifacts", [])) if isinstance(state.get("artifacts"), list) else set()
        present_required = sorted(item for item in required if (project / item).is_file() or item in tracked)
        missing_required = sorted(item for item in required if item not in present_required)
        extra_tracked = sorted(item for item in tracked if is_concrete_artifact(item) and item not in allowed)
        total_missing += len(missing_required)
        total_extra += len(extra_tracked)
        by_project[project.name] = {
            "routeProfile": profile_id,
            "selectionReason": reason,
            "requiredForCurrentRoute": required,
            "presentRequired": present_required,
            "missingRequired": missing_required,
            "trackedOutsideCurrentRoute": extra_tracked,
            "debtCount": len(missing_required) + len(extra_tracked),
        }
    return {
        "projectCount": len(project_states),
        "missingRequiredCount": total_missing,
        "trackedOutsideCurrentRouteCount": total_extra,
        "totalDebtCount": total_missing + total_extra,
        "byProject": by_project,
    }


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


def context_runtime_metrics(project_states: list[tuple[Path, dict]]) -> dict:
    indexed_projects = 0
    snapshot_projects = 0
    indexed_documents = 0
    for project, _ in project_states:
        index_path = project / ".codex-memory" / "context-index.json"
        snapshot_path = project / ".codex-memory" / "resume-snapshot.md"
        if index_path.is_file():
            indexed_projects += 1
            try:
                indexed_documents += int(json.loads(index_path.read_text(encoding="utf-8")).get("documentCount") or 0)
            except (json.JSONDecodeError, ValueError):
                pass
        if snapshot_path.is_file():
            snapshot_projects += 1
    return {
        "indexedProjectCount": indexed_projects,
        "snapshotProjectCount": snapshot_projects,
        "indexedEventDocuments": indexed_documents,
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
        "contextRuntime": context_runtime_metrics(project_states),
        "artifactDebt": artifact_debt_metrics(project_states),
    }
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
