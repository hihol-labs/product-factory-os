#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "memory" / "events.schema.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def event_path(project: Path) -> Path:
    return project / ".codex-memory" / "events.jsonl"


def validate_event(event: dict[str, Any], schema: dict[str, Any], line_number: int) -> list[str]:
    errors: list[str] = []
    for field in schema.get("requiredFields", []):
        if field not in event:
            errors.append(f"line {line_number}: missing {field}")
    if event.get("eventType") not in schema.get("eventTypes", []):
        errors.append(f"line {line_number}: invalid eventType {event.get('eventType')!r}")
    payload = event.get("payload", {})
    if not isinstance(payload, dict):
        errors.append(f"line {line_number}: payload must be an object")
        return errors
    event_payload_schema = schema.get("payloadSchemas", {}).get(event.get("eventType"), {})
    for field in event_payload_schema.get("recommendedFields", []):
        payload.setdefault(field, None)
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    path = event_path(project)
    schema = load_schema()
    if not path.is_file():
        fail(f"missing event log: {path}")
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc}")
            continue
        errors.extend(validate_event(event, schema, line_number))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: validated event log {path}")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    path = event_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = now_iso()
    event = {
        "id": args.event_id or f"event-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "timestamp": timestamp,
        "eventType": args.event_type,
        "status": args.status,
        "project": project.name,
        "source": args.source,
        "payload": {
            "command": args.command,
            "exitCode": args.exit_code,
            "durationSeconds": args.duration_seconds,
            "costNotes": args.cost_notes,
            "tokenNotes": args.token_notes,
            "reason": args.reason,
        },
    }
    schema = load_schema()
    errors = validate_event(event, schema, 1)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    state_path = project / ".codex-memory" / "STATE.json"
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["eventLog"] = {"path": ".codex-memory/events.jsonl", "lastEventId": event["id"], "lastEventAt": timestamp}
        artifacts = set(state.get("artifacts", []))
        artifacts.add(".codex-memory/events.jsonl")
        state["artifacts"] = sorted(artifacts)
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: recorded event {event['id']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and validate Product Factory OS structured event logs.")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record")
    record.add_argument("project", type=Path)
    record.add_argument("--event-type", choices=load_schema().get("eventTypes", []), required=True)
    record.add_argument("--status", required=True)
    record.add_argument("--source", default="manual")
    record.add_argument("--event-id", default="")
    record.add_argument("--command", default="")
    record.add_argument("--exit-code", type=int, default=None)
    record.add_argument("--duration-seconds", type=float, default=None)
    record.add_argument("--cost-notes", default="")
    record.add_argument("--token-notes", default="")
    record.add_argument("--reason", default="")
    record.set_defaults(func=cmd_record)

    validate = sub.add_parser("validate")
    validate.add_argument("project", type=Path)
    validate.set_defaults(func=cmd_validate)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
