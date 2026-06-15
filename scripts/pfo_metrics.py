#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import re


ROOT = Path(__file__).resolve().parents[1]
SUCCESS_STATUSES = {"PASS", "PASSED", "PASS_WITH_WARNINGS", "PASSED_WITH_WARNINGS", "READY", "RECORDED", "CANDIDATE_RULE"}
FAILURE_STATUSES = {"BLOCKED", "FAILED", "ERROR", "RECOVERY_REQUIRED"}
ROUTE_PROFILE_IDS = {"minimal", "standard", "full"}
TARGET_CONTEXT_COVERAGE = 0.9
TARGET_BLOCKED_RATIO = 0.2
TARGET_VERIFICATION_PASS_RATE = 0.95
TARGET_REPAIR_LOOPS_PER_VERIFIED_UNIT = 0.25
STALE_STATE_DAYS = 7
MISSING_GATE_STATUSES = {"", "NOT_RUN", "NOT_CONFIGURED", "PENDING", "RECOVERY_REQUIRED"}
BLOCKING_GATE_STATUSES = {"BLOCKED", "FAILED", "ERROR", "RECOVERY_REQUIRED"}
INACTIVE_STAGES = {"", "IDLE", "ADOPTED", "EXISTING_PROJECT_ANALYZED", "REVIEWING"}
NON_BLOCKING_BLOCKER_PATTERNS = [
    re.compile(r"no root test/typecheck script was detected", re.I),
    re.compile(r"no root test/typecheck/check script was detected", re.I),
    re.compile(r"no automated test/typecheck/check command was detected", re.I),
]


def parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def ratio(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0


def percent(count: int, total: int) -> float:
    return round(ratio(count, total) * 100, 2)


def status_text(value: object) -> str:
    return str(value or "").upper()


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


def classify_blocker(text: str) -> str:
    lowered = text.lower()
    if ".pfo/" in lowered or "contract" in lowered or "selectionpolicy" in lowered or "alias" in lowered:
        return "contract"
    if "security" in lowered or "secret" in lowered or ".env" in lowered or "tls" in lowered:
        return "security"
    if "test" in lowered or "typecheck" in lowered or "lint" in lowered or "build" in lowered or "command" in lowered:
        return "verification"
    if "missing" in lowered or "not_configured" in lowered or "not configured" in lowered:
        return "missing_gates"
    if "stale" in lowered or "old" in lowered:
        return "stale_state"
    return "other"


def is_non_blocking_blocker(text: str) -> bool:
    return any(pattern.search(text) for pattern in NON_BLOCKING_BLOCKER_PATTERNS)


def has_active_gate_scope(state: dict) -> bool:
    current_unit = state.get("currentUnit", {}) if isinstance(state.get("currentUnit"), dict) else {}
    if current_unit.get("id") or current_unit.get("goal"):
        return True
    return status_text(state.get("currentStage")) not in INACTIVE_STAGES


def adoption_gate_status(project: Path) -> str:
    required = [
        "AGENTS.md",
        "CODEX.md",
        ".codex-memory/STATE.json",
        ".pfo/PROJECT_CONTRACT.md",
        ".pfo/VERIFICATION_CONTRACT.json",
    ]
    return "PASS" if all((project / rel).is_file() for rel in required) else ""


def live_blockers_for_project(project: Path, state: dict) -> list[dict]:
    blockers: list[dict] = []
    raw_blockers = state.get("blockers", []) if isinstance(state.get("blockers"), list) else []
    for item in raw_blockers:
        text = str(item).strip()
        if not text or is_non_blocking_blocker(text):
            continue
        blockers.append({"type": classify_blocker(text), "source": "state.blockers", "message": text})

    failed_validations = state.get("failedValidations", []) if isinstance(state.get("failedValidations"), list) else []
    for item in failed_validations:
        text = json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item)
        blockers.append({"type": "verification", "source": "failedValidations", "message": text})

    gates = state.get("gateResults", {}) if isinstance(state.get("gateResults"), dict) else {}
    for gate, value in gates.items():
        status = status_text(value)
        if status not in BLOCKING_GATE_STATUSES:
            continue
        if gate == "deploymentReadiness" and not blockers:
            continue
        if gate == "tests" and status == "NOT_CONFIGURED":
            continue
        message = f"{gate}: {status}"
        if not any(item["message"] == message for item in blockers):
            blockers.append({"type": "gate", "source": "gateResults", "message": message})
    return blockers


def blocker_metrics(project_states: list[tuple[Path, dict]]) -> dict:
    by_type: dict[str, int] = {}
    by_project: dict[str, dict] = {}
    legacy_count = 0
    live_count = 0
    for project, state in project_states:
        raw_blockers = state.get("blockers", []) if isinstance(state.get("blockers"), list) else []
        if raw_blockers:
            legacy_count += 1
        live = live_blockers_for_project(project, state)
        if live:
            live_count += 1
        for item in live:
            by_type[item["type"]] = by_type.get(item["type"], 0) + 1
        by_project[project.name] = {
            "legacyBlockerCount": len(raw_blockers),
            "liveBlockerCount": len(live),
            "liveBlockers": live,
        }
    project_count = len(project_states)
    live_ratio = ratio(live_count, project_count)
    return {
        "targetRatio": TARGET_BLOCKED_RATIO,
        "legacyBlockedProjectCount": legacy_count,
        "liveBlockedProjectCount": live_count,
        "liveBlockedProjectRatio": live_ratio,
        "liveBlockedProjectPercent": percent(live_count, project_count),
        "status": "PASS" if live_ratio < TARGET_BLOCKED_RATIO else "BLOCKED",
        "byType": dict(sorted(by_type.items())),
        "byProject": by_project,
    }


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
    complete_projects = 0
    indexed_documents = 0
    missing_index = []
    missing_snapshot = []
    for project, _ in project_states:
        index_path = project / ".codex-memory" / "context-index.json"
        snapshot_path = project / ".codex-memory" / "resume-snapshot.md"
        has_index = index_path.is_file()
        has_snapshot = snapshot_path.is_file()
        if has_index:
            indexed_projects += 1
            try:
                indexed_documents += int(json.loads(index_path.read_text(encoding="utf-8")).get("documentCount") or 0)
            except (json.JSONDecodeError, ValueError):
                pass
        else:
            missing_index.append(project.name)
        if has_snapshot:
            snapshot_projects += 1
        else:
            missing_snapshot.append(project.name)
        if has_index and has_snapshot:
            complete_projects += 1
    project_count = len(project_states)
    complete_ratio = ratio(complete_projects, project_count)
    return {
        "indexedProjectCount": indexed_projects,
        "snapshotProjectCount": snapshot_projects,
        "completeProjectCount": complete_projects,
        "indexCoverageRatio": ratio(indexed_projects, project_count),
        "snapshotCoverageRatio": ratio(snapshot_projects, project_count),
        "completeCoverageRatio": complete_ratio,
        "indexCoveragePercent": percent(indexed_projects, project_count),
        "snapshotCoveragePercent": percent(snapshot_projects, project_count),
        "completeCoveragePercent": percent(complete_projects, project_count),
        "targetCoverageRatio": TARGET_CONTEXT_COVERAGE,
        "status": "PASS" if complete_ratio >= TARGET_CONTEXT_COVERAGE else "BLOCKED",
        "missingIndexProjects": missing_index,
        "missingSnapshotProjects": missing_snapshot,
        "indexedEventDocuments": indexed_documents,
    }


def stale_state_metrics(project_states: list[tuple[Path, dict]]) -> dict:
    stale = {}
    current = now_utc()
    for project, state in project_states:
        event_log = state.get("eventLog", {}) if isinstance(state.get("eventLog"), dict) else {}
        timestamp = parse_timestamp(str(event_log.get("lastEventAt", "")))
        source = "eventLog.lastEventAt"
        if timestamp is None:
            state_path = project / ".codex-memory" / "STATE.json"
            timestamp = datetime.fromtimestamp(state_path.stat().st_mtime, tz=timezone.utc)
            source = "STATE.json mtime"
        age_days = (current - aware(timestamp)).total_seconds() / 86400
        if age_days > STALE_STATE_DAYS:
            stale[project.name] = {
                "ageDays": round(age_days, 2),
                "lastUpdatedAt": aware(timestamp).isoformat(),
                "source": source,
            }
    return {
        "thresholdDays": STALE_STATE_DAYS,
        "staleProjectCount": len(stale),
        "byProject": stale,
        "status": "PASS" if not stale else "STALE",
    }


def missing_gate_metrics(project_states: list[tuple[Path, dict]], artifact_debt: dict) -> dict:
    profiles = load_route_profiles().get("profiles", {})
    by_project = {}
    total_missing_gates = 0
    total_missing_artifacts = 0
    artifact_by_project = artifact_debt.get("byProject", {}) if isinstance(artifact_debt.get("byProject"), dict) else {}
    for project, state in project_states:
        profile_id, reason = select_route_profile(state)
        profile = profiles.get(profile_id, {})
        required_gates = profile.get("gates", []) if has_active_gate_scope(state) and isinstance(profile.get("gates"), list) else []
        gate_results = state.get("gateResults", {}) if isinstance(state.get("gateResults"), dict) else {}
        missing_gates = [
            {
                "gate": gate,
                "status": adoption_gate_status(project) if gate == "adoption" else status_text(gate_results.get(gate)),
            }
            for gate in required_gates
            if (adoption_gate_status(project) if gate == "adoption" else status_text(gate_results.get(gate))) in MISSING_GATE_STATUSES
        ]
        missing_artifacts = artifact_by_project.get(project.name, {}).get("missingRequired", [])
        total_missing_gates += len(missing_gates)
        total_missing_artifacts += len(missing_artifacts)
        by_project[project.name] = {
            "routeProfile": profile_id,
            "selectionReason": reason,
            "missingGateStatuses": missing_gates,
            "missingRequiredArtifacts": missing_artifacts,
            "missingCount": len(missing_gates) + len(missing_artifacts),
        }
    return {
        "missingGateStatusCount": total_missing_gates,
        "missingRequiredArtifactCount": total_missing_artifacts,
        "totalMissingCount": total_missing_gates + total_missing_artifacts,
        "byProject": by_project,
        "status": "PASS" if total_missing_gates + total_missing_artifacts == 0 else "ATTENTION",
    }


def live_eval_status(
    project_states: list[tuple[Path, dict]],
    efficiency: dict,
    context: dict,
    blockers: dict,
    stale: dict,
) -> dict:
    latest_verification: datetime | None = None
    project_status = {}
    for project, state in project_states:
        history = state.get("verificationHistory", []) if isinstance(state.get("verificationHistory"), list) else []
        latest = history[-1] if history and isinstance(history[-1], dict) else {}
        project_status[project.name] = {
            "latestStatus": latest.get("status") or latest.get("stage") or "UNKNOWN",
            "latestMode": latest.get("mode", ""),
            "verificationCount": len(history),
        }
        for event in load_events(project):
            if event.get("eventType") != "verification":
                continue
            timestamp = parse_timestamp(str(event.get("timestamp", "")))
            if timestamp and (latest_verification is None or aware(timestamp) > aware(latest_verification)):
                latest_verification = timestamp

    verification_rate = efficiency.get("verificationPassRate")
    gate_rate = efficiency.get("gatePassRate")
    repair_loops_per_verified_unit = efficiency.get("repairLoopsPerVerifiedUnit")
    status = "PASS"
    reasons = []
    if context.get("completeCoverageRatio", 0) <= TARGET_CONTEXT_COVERAGE:
        status = "BLOCKED"
        reasons.append("context index/snapshot coverage must be above 90%")
    if blockers.get("liveBlockedProjectRatio", 0) >= TARGET_BLOCKED_RATIO:
        status = "BLOCKED"
        reasons.append("live blocked workspace project ratio above target")
    if verification_rate is not None and verification_rate <= TARGET_VERIFICATION_PASS_RATE:
        status = "BLOCKED"
        reasons.append("verification pass rate must be above 95%")
    if (
        repair_loops_per_verified_unit is not None
        and repair_loops_per_verified_unit >= TARGET_REPAIR_LOOPS_PER_VERIFIED_UNIT
    ):
        status = "BLOCKED"
        reasons.append("repair loops per verified unit must stay below 0.25")
    if gate_rate is not None and gate_rate < 0.9:
        status = "DEGRADED" if status == "PASS" else status
        reasons.append("gate pass rate below 90%")
    if stale.get("staleProjectCount", 0):
        status = "DEGRADED" if status == "PASS" else status
        reasons.append("stale project state detected")

    return {
        "status": status,
        "reasons": reasons,
        "lastVerificationAt": aware(latest_verification).isoformat() if latest_verification else "",
        "verificationPassRate": verification_rate,
        "targetVerificationPassRate": TARGET_VERIFICATION_PASS_RATE,
        "repairLoopsPerVerifiedUnit": repair_loops_per_verified_unit,
        "targetRepairLoopsPerVerifiedUnit": TARGET_REPAIR_LOOPS_PER_VERIFIED_UNIT,
        "gatePassRate": gate_rate,
        "byProject": project_status,
    }


def platform_surface_metrics(project_states: list[tuple[Path, dict]]) -> dict:
    surfaces = {
        "readiness": "PFO_READINESS_REPORT.md",
        "mission": ".pfo/mission.json",
        "policy": ".pfo/PERMISSION_MATRIX.json",
        "wiki": ".pfo/wiki/index.md",
        "qa": ".pfo/qa/PFO_QA_REPORT.md",
        "telemetry": ".pfo/telemetry/pfo-telemetry.jsonl",
    }
    by_project = {}
    totals = {key: 0 for key in surfaces}
    for project, state in project_states:
        project_surfaces = {}
        for key, rel in surfaces.items():
            present = (project / rel).is_file() or rel in set(state.get("artifacts", []))
            project_surfaces[key] = {"path": rel, "status": "READY" if present else "MISSING"}
            if present:
                totals[key] += 1
        by_project[project.name] = project_surfaces
    project_count = len(project_states)
    coverage = {
        key: {
            "readyProjectCount": value,
            "coverageRatio": ratio(value, project_count),
            "coveragePercent": percent(value, project_count),
        }
        for key, value in totals.items()
    }
    return {
        "surfaces": coverage,
        "byProject": by_project,
        "status": "PASS" if all(item["readyProjectCount"] == project_count for item in coverage.values()) else "ATTENTION",
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

    harness = efficiency_metrics(project_states)
    context = context_runtime_metrics(project_states)
    artifact_debt = artifact_debt_metrics(project_states)
    blockers = blocker_metrics(project_states)
    stale = stale_state_metrics(project_states)
    missing_gates = missing_gate_metrics(project_states, artifact_debt)
    live_eval = live_eval_status(project_states, harness, context, blockers, stale)
    platform_surfaces = platform_surface_metrics(project_states)

    metrics = {
        "projectCount": len(projects),
        "deployReadyCount": sum(1 for item in projects if item.get("currentStage") == "READY_FOR_DEPLOY"),
        "deployedCount": sum(1 for item in projects if item.get("currentStage") == "DEPLOYED"),
        "blockedCount": blockers["liveBlockedProjectCount"],
        "legacyBlockedCount": blockers["legacyBlockedProjectCount"],
        "blockedProjectPercent": blockers["liveBlockedProjectPercent"],
        "failedGateCount": sum(len(item.get("failedValidations", [])) for item in projects),
        "verificationEvents": sum(len(item.get("verificationHistory", [])) for item in projects),
        "harnessEfficiency": harness,
        "contextRuntime": context,
        "artifactDebt": artifact_debt,
        "blockers": blockers,
        "staleState": stale,
        "missingGates": missing_gates,
        "liveEvalStatus": live_eval,
        "platformSurfaces": platform_surfaces,
    }
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
