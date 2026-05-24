#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import sys
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "memory" / "LEARNING_REGISTRY.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def learning_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"learning-{stamp}"


def candidate_id(learning: dict) -> str:
    source = learning.get("id", learning_id()).replace("learning-", "")
    return f"candidate-{source}"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def read_json(path: Path, fallback: dict) -> dict:
    if not path.is_file():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    if path.exists() and path.is_dir():
        fail(f"refusing to write JSON over directory: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_state(project: Path) -> dict:
    state_path = project / ".codex-memory" / "STATE.json"
    if not state_path.is_file():
        fail(f"missing state file: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(project: Path, state: dict) -> None:
    write_json(project / ".codex-memory" / "STATE.json", state)


def add_artifact(state: dict, artifact: str) -> None:
    artifacts = set(state.get("artifacts", []))
    artifacts.add(artifact)
    state["artifacts"] = sorted(artifacts)


def append_event(project: Path, state: dict, event_type: str, status: str, payload: dict) -> None:
    timestamp = now_iso()
    event_id = f"event-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{len(state.get('knowledgeLog', [])) + 1}"
    event = {
        "id": event_id,
        "timestamp": timestamp,
        "eventType": event_type,
        "status": status,
        "project": project.name,
        "source": "pfo-learn",
        "payload": payload,
    }
    path = project / ".codex-memory" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    state["eventLog"] = {
        "path": ".codex-memory/events.jsonl",
        "lastEventId": event_id,
        "lastEventAt": timestamp,
    }
    add_artifact(state, ".codex-memory/events.jsonl")


def infer_scope(project: Path, state: dict) -> str:
    starter = state.get("starter")
    product_type = state.get("productTypeHint") or state.get("classification", {}).get("productType")
    if starter:
        return f"starter:{starter}"
    if product_type:
        return f"product-type:{product_type}"
    return f"project:{project.name}"


def normalize_confidence(value: Optional[float]) -> float:
    if value is None:
        return 0.5
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        fail("confidence must be numeric")
    if confidence < 0 or confidence > 1:
        fail("--confidence must be between 0 and 1")
    return confidence


def require_learning_content(args: argparse.Namespace) -> None:
    fields = [
        args.decision,
        args.lesson,
        args.pattern,
        args.surprise,
        args.problem,
        args.rule,
        *(args.evidence or []),
    ]
    if not any(str(field).strip() for field in fields):
        fail("record at least one learning field")


def append_markdown(path: Path, entry: dict) -> None:
    if not path.exists():
        path.write_text("# Learnings\n", encoding="utf-8")

    evidence = entry.get("evidence", [])
    evidence_lines = "\n".join(f"  - {item}" for item in evidence) if evidence else "  - TBD"
    block = [
        "",
        f"## {entry['recordedAt']}",
        "",
        f"- Scope: {entry['scope']}",
        f"- Decision: {entry.get('decision') or 'TBD'}",
        f"- Lesson: {entry.get('lesson') or 'TBD'}",
        f"- Pattern: {entry.get('pattern') or 'TBD'}",
        f"- Surprise: {entry.get('surprise') or 'TBD'}",
        f"- Problem: {entry.get('problem') or 'TBD'}",
        f"- Proposed rule: {entry.get('proposedRule') or 'TBD'}",
        f"- Confidence: {entry.get('confidence', 0)}",
        "- Evidence:",
        evidence_lines,
        "",
    ]
    path.write_text(path.read_text(encoding="utf-8") + "\n".join(block), encoding="utf-8")


def append_jsonl(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    entries = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as exc:
            fail(f"{path}:{line_number}: invalid JSONL entry: {exc}")
    return entries


def cmd_record(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    require_learning_content(args)
    state = load_state(project)
    recorded_at = now_iso()
    entry = {
        "id": learning_id(),
        "recordedAt": recorded_at,
        "project": project.name,
        "scope": args.scope or infer_scope(project, state),
        "decision": args.decision,
        "lesson": args.lesson,
        "pattern": args.pattern,
        "surprise": args.surprise,
        "problem": args.problem,
        "proposedRule": args.rule,
        "evidence": args.evidence or [],
        "confidence": normalize_confidence(args.confidence),
        "status": "CANDIDATE_RULE" if args.rule else "RECORDED",
    }

    memory_dir = project / ".codex-memory"
    memory_dir.mkdir(exist_ok=True)
    append_markdown(memory_dir / "LEARNINGS.md", entry)
    append_jsonl(memory_dir / "LEARNINGS.jsonl", entry)

    state.setdefault("knowledgeLog", []).append(entry)
    add_artifact(state, ".codex-memory/LEARNINGS.md")
    add_artifact(state, ".codex-memory/LEARNINGS.jsonl")
    state["nextAction"] = "Run `pfo improve <project> --from-learnings --propose` to turn candidate rules into reviewed improvements."
    append_event(project, state, "learning", entry["status"], {"id": entry["id"], "rule": entry.get("proposedRule", "")})
    save_state(project, state)
    print("OK: recorded structured learning")
    return 0


def candidate_from_learning(learning: dict) -> Optional[dict]:
    rule = learning.get("proposedRule") or learning.get("rule")
    if not rule:
        return None
    problem = learning.get("problem") or learning.get("lesson") or learning.get("surprise")
    if not problem:
        return None
    created_at = now_iso()
    return {
        "id": candidate_id(learning),
        "sourceLearningId": learning.get("id", ""),
        "sourceProject": learning.get("project", ""),
        "scope": learning.get("scope", ""),
        "problem": problem,
        "rule": rule,
        "evidence": learning.get("evidence", []),
        "confidence": normalize_confidence(learning.get("confidence")),
        "status": "PROPOSED",
        "promotion": {
            "target": "review-required",
            "artifacts": [],
            "checks": [],
            "reviewStatus": "PENDING",
        },
        "promotionGates": [
            "python3 scripts/validate_structure.py",
            "python3 scripts/validate_runtime.py",
            "python3 scripts/run_fixtures.py",
            "python3 scripts/validate_execution_graph.py <project>/EXECUTION_GRAPH.md",
        ],
        "createdAt": created_at,
        "updatedAt": created_at,
    }


def merge_candidates(existing: list[dict], incoming: list[dict]) -> list[dict]:
    by_id = {item.get("id"): item for item in existing if item.get("id")}
    for item in incoming:
        current = by_id.get(item["id"])
        if current and current.get("status") not in {"PROPOSED", "RECORDED"}:
            continue
        by_id[item["id"]] = {**current, **item} if current else item
    return sorted(by_id.values(), key=lambda item: item.get("createdAt", ""))


def cmd_propose(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    jsonl_entries = load_jsonl(project / ".codex-memory" / "LEARNINGS.jsonl")
    state_entries = state.get("knowledgeLog", [])
    entries = [*jsonl_entries, *state_entries]

    seen = set()
    unique_entries = []
    for entry in entries:
        key = entry.get("id") or json.dumps(entry, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        unique_entries.append(entry)

    candidates = []
    for entry in unique_entries:
        candidate = candidate_from_learning(entry)
        if not candidate:
            continue
        if candidate["confidence"] < args.min_confidence:
            continue
        if args.promotion_target:
            candidate["promotion"] = {
                "target": args.promotion_target,
                "artifacts": args.promotion_artifact or [],
                "checks": args.promotion_check or [],
                "reviewStatus": args.review_status,
            }
        candidates.append(candidate)

    if not candidates:
        fail("no candidate rules found in structured learnings")

    proposal = {
        "version": 1,
        "project": project.name,
        "generatedAt": now_iso(),
        "candidateRules": candidates,
    }
    proposal_path = project / ".codex-memory" / "LEARNING_PROPOSALS.json"
    write_json(proposal_path, proposal)

    registry = read_json(
        args.registry,
        {
            "version": 1,
            "updatedAt": "",
            "candidateRules": [],
            "appliedRules": [],
            "rejectedRules": [],
        },
    )
    registry["version"] = max(1, int(registry.get("version", 1)))
    registry["updatedAt"] = now_iso()
    registry["candidateRules"] = merge_candidates(registry.get("candidateRules", []), candidates)
    registry.setdefault("appliedRules", [])
    registry.setdefault("rejectedRules", [])
    write_json(args.registry, registry)

    state["learningProposals"] = candidates
    add_artifact(state, ".codex-memory/LEARNING_PROPOSALS.json")
    state["nextAction"] = "Review proposed learning rules, run promotion gates, then apply approved changes to PFO templates, routing, gates, or skills."
    append_event(project, state, "learning", "PROPOSED", {"candidateCount": len(candidates)})
    save_state(project, state)
    print(f"OK: proposed {len(candidates)} learning rule(s)")
    return 0


def candidate_gate_errors(candidate: dict, require_approved: bool) -> list[str]:
    errors: list[str] = []
    allowed_targets = {"test", "hook", "doc", "rule", "linter", "validator", "template", "skill", "route"}
    promotion = candidate.get("promotion", {}) if isinstance(candidate.get("promotion", {}), dict) else {}
    target = promotion.get("target") or candidate.get("promotionTarget", "")
    artifacts = promotion.get("artifacts") or candidate.get("promotionArtifacts", [])
    checks = promotion.get("checks") or candidate.get("promotionChecks", [])
    review_status = promotion.get("reviewStatus") or candidate.get("reviewStatus", "")

    if not candidate.get("evidence"):
        errors.append(f"{candidate.get('id', '<unknown>')}: missing evidence")
    if target not in allowed_targets:
        errors.append(f"{candidate.get('id', '<unknown>')}: promotion target must be one of {sorted(allowed_targets)}")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append(f"{candidate.get('id', '<unknown>')}: missing promotion artifacts")
    if not isinstance(checks, list) or not checks:
        errors.append(f"{candidate.get('id', '<unknown>')}: missing promotion checks")
    if require_approved and review_status != "APPROVED":
        errors.append(f"{candidate.get('id', '<unknown>')}: reviewStatus must be APPROVED")
    return errors


def cmd_gate(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    proposal_path = project / ".codex-memory" / "LEARNING_PROPOSALS.json"
    if not proposal_path.is_file():
        fail("missing .codex-memory/LEARNING_PROPOSALS.json; run propose first")
    proposal = read_json(proposal_path, {})
    candidates = proposal.get("candidateRules", [])
    if not isinstance(candidates, list) or not candidates:
        fail("learning proposal has no candidateRules")

    errors: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("candidateRules contains a non-object item")
            continue
        if candidate.get("status") == "REJECTED":
            continue
        errors.extend(candidate_gate_errors(candidate, args.require_approved))

    gate_status = "PASSED" if not errors else "BLOCKED"
    state.setdefault("gateResults", {})["learningPromotion"] = gate_status
    state["learningPromotionGate"] = {
        "path": ".pfo/LEARNING_PROMOTION_GATE.md",
        "status": gate_status,
        "checkedAt": now_iso(),
    }
    if errors:
        state.setdefault("blockers", []).extend(errors)
        state["nextAction"] = "Fill learning proposal target, artifacts, checks, and review status before changing PFO runtime."
    else:
        state["nextAction"] = "Apply the approved learning promotion and rerun the declared checks."
    append_event(project, state, "gate", gate_status, {"command": "learning-gate", "errors": errors})
    save_state(project, state)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: learning promotion gate passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and promote structured Product Factory OS learnings.")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record", help="Record a structured project learning.")
    record.add_argument("project", type=Path)
    record.add_argument("--scope", default="")
    record.add_argument("--decision", default="")
    record.add_argument("--lesson", default="")
    record.add_argument("--pattern", default="")
    record.add_argument("--surprise", default="")
    record.add_argument("--problem", default="")
    record.add_argument("--rule", default="")
    record.add_argument("--evidence", action="append", default=[])
    record.add_argument("--confidence", type=float, default=None)
    record.set_defaults(func=cmd_record)

    propose = sub.add_parser("propose", help="Turn structured learnings into candidate PFO rules.")
    propose.add_argument("project", type=Path)
    propose.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    propose.add_argument("--min-confidence", type=float, default=0.0)
    propose.add_argument("--promotion-target", choices=["test", "hook", "doc", "rule", "linter", "validator", "template", "skill", "route"], default="")
    propose.add_argument("--promotion-artifact", action="append", default=[])
    propose.add_argument("--promotion-check", action="append", default=[])
    propose.add_argument("--review-status", choices=["PENDING", "APPROVED", "REJECTED"], default="PENDING")
    propose.set_defaults(func=cmd_propose)

    gate = sub.add_parser("gate", help="Validate learning proposals before promoting them into runtime changes.")
    gate.add_argument("project", type=Path)
    gate.add_argument("--require-approved", action="store_true")
    gate.set_defaults(func=cmd_gate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
