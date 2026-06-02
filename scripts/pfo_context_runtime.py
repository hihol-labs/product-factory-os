#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
import re
from typing import Any


DEFAULT_POLICY = {
    "version": 1,
    "mode": "budgeted-summary",
    "limits": {
        "toolOutputWarnBytes": 12000,
        "toolOutputBlockBytes": 48000,
        "toolOutputWarnLines": 240,
        "toolOutputBlockLines": 960,
        "readOutputWarnBytes": 16000,
        "readOutputBlockBytes": 64000,
        "readOutputWarnLines": 300,
        "readOutputBlockLines": 1200,
        "logOutputWarnBytes": 24000,
        "logOutputBlockBytes": 96000,
        "logOutputWarnLines": 500,
        "logOutputBlockLines": 2000,
        "webOutputWarnBytes": 12000,
        "webOutputBlockBytes": 40000,
        "webOutputWarnLines": 200,
        "webOutputBlockLines": 800,
        "httpOutputWarnBytes": 8000,
        "httpOutputBlockBytes": 24000,
        "httpOutputWarnLines": 160,
        "httpOutputBlockLines": 600,
    },
    "routing": {
        "rawHttp": "block-unless-approved-or-summarized",
        "largeOutputWorkflow": "sandbox-summary",
        "summaryRequired": True,
        "summaryArtifact": ".codex-memory/context-summary.md",
    },
    "index": {
        "path": ".codex-memory/context-index.json",
        "source": ".codex-memory/events.jsonl",
    },
    "snapshot": {
        "path": ".codex-memory/resume-snapshot.md",
        "maxItems": 8,
    },
    "evidence": [
        ".codex-memory/events.jsonl",
        ".codex-memory/context-index.json",
        ".codex-memory/resume-snapshot.md",
    ],
}

TOKEN_RE = re.compile(r"[A-Za-z0-9_./:-]+")
RAW_HTTP_RE = re.compile(r"\b(curl|wget|http|httpie|Invoke-WebRequest|Invoke-RestMethod)\b|https?://", re.I)
SUMMARY_HINT_RE = re.compile(r"\b(-I|--head|HEAD|summary|summarize|digest|jq|select|head|tail)\b", re.I)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.is_file():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_policy(project: Path) -> dict[str, Any]:
    matrix = read_json(project / ".pfo" / "PERMISSION_MATRIX.json")
    return deep_merge(DEFAULT_POLICY, matrix.get("contextRuntimePolicy", {}))


def normalize_kind(kind: str, command: str = "") -> str:
    lowered = (kind or "").lower()
    if lowered in {"grep", "rg", "cat", "file"}:
        return "read"
    if lowered in {"http", "curl", "wget"}:
        return "http"
    if lowered in {"tool", "read", "log", "web"}:
        return lowered
    if command:
        c = command.lower()
        if any(token in c for token in ["curl", "wget", "invoke-webrequest", "invoke-restmethod"]):
            return "http"
        if any(token in c for token in ["rg ", "grep ", "cat ", "get-content", "sed "]):
            return "read"
    return "tool"


def command_is_raw_http(command: str) -> bool:
    if not command:
        return False
    if not RAW_HTTP_RE.search(command):
        return False
    return not SUMMARY_HINT_RE.search(command)


def limits_for(policy: dict[str, Any], kind: str) -> dict[str, int]:
    limits = policy.get("limits", {})
    fallback = {
        "warn_bytes": int(limits.get("toolOutputWarnBytes", DEFAULT_POLICY["limits"]["toolOutputWarnBytes"])),
        "block_bytes": int(limits.get("toolOutputBlockBytes", DEFAULT_POLICY["limits"]["toolOutputBlockBytes"])),
        "warn_lines": int(limits.get("toolOutputWarnLines", DEFAULT_POLICY["limits"]["toolOutputWarnLines"])),
        "block_lines": int(limits.get("toolOutputBlockLines", DEFAULT_POLICY["limits"]["toolOutputBlockLines"])),
    }
    prefix = kind.lower()
    return {
        "warn_bytes": int(limits.get(f"{prefix}OutputWarnBytes", fallback["warn_bytes"])),
        "block_bytes": int(limits.get(f"{prefix}OutputBlockBytes", fallback["block_bytes"])),
        "warn_lines": int(limits.get(f"{prefix}OutputWarnLines", fallback["warn_lines"])),
        "block_lines": int(limits.get(f"{prefix}OutputBlockLines", fallback["block_lines"])),
    }


def budget_decision(
    policy: dict[str, Any],
    kind: str,
    byte_count: int,
    line_count: int,
    command: str,
    raw_http: bool,
    approved: bool,
) -> tuple[str, str]:
    kind = normalize_kind(kind, command)
    raw_http = raw_http or command_is_raw_http(command)
    routing = policy.get("routing", {})
    if raw_http and routing.get("rawHttp") == "block-unless-approved-or-summarized" and not approved:
        return (
            "BLOCKED",
            "raw HTTP output must be approved or routed through sandbox-summary with a bounded digest",
        )
    limit = limits_for(policy, kind)
    if byte_count >= limit["block_bytes"] or line_count >= limit["block_lines"]:
        return (
            "BLOCKED",
            f"{kind} output {byte_count} bytes/{line_count} lines exceeds block limit "
            f"{limit['block_bytes']} bytes/{limit['block_lines']} lines; use sandbox-summary",
        )
    if byte_count >= limit["warn_bytes"] or line_count >= limit["warn_lines"]:
        return (
            "PASSED_WITH_WARNINGS",
            f"{kind} output {byte_count} bytes/{line_count} lines exceeds warning limit "
            f"{limit['warn_bytes']} bytes/{limit['warn_lines']} lines; summarize before adding to context",
        )
    return "PASSED", f"{kind} output is within context budget"


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if len(token) > 1]


def flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {flatten(item)}" for key, item in value.items())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return str(value)


def event_log_path(project: Path, policy: dict[str, Any]) -> Path:
    return project / policy.get("index", {}).get("source", ".codex-memory/events.jsonl")


def index_path(project: Path, policy: dict[str, Any]) -> Path:
    return project / policy.get("index", {}).get("path", ".codex-memory/context-index.json")


def event_documents(project: Path, policy: dict[str, Any]) -> list[dict[str, Any]]:
    path = event_log_path(project, policy)
    documents: list[dict[str, Any]] = []
    if not path.is_file():
        return documents
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = flatten(event)
        terms = Counter(tokenize(text))
        documents.append(
            {
                "id": event.get("id", f"line-{line_number}"),
                "timestamp": event.get("timestamp", ""),
                "eventType": event.get("eventType", ""),
                "status": event.get("status", ""),
                "source": event.get("source", ""),
                "line": line_number,
                "length": sum(terms.values()) or 1,
                "terms": dict(terms),
                "excerpt": text[:280],
            }
        )
    return documents


def build_index(project: Path, policy: dict[str, Any]) -> dict[str, Any]:
    documents = event_documents(project, policy)
    avg_len = sum(item["length"] for item in documents) / len(documents) if documents else 1.0
    data = {
        "version": 1,
        "builtAt": now_iso(),
        "source": str(event_log_path(project, policy).relative_to(project)),
        "documentCount": len(documents),
        "avgDocumentLength": avg_len,
        "documents": documents,
    }
    path = index_path(project, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def load_or_build_index(project: Path, policy: dict[str, Any], reindex: bool) -> dict[str, Any]:
    path = index_path(project, policy)
    source = event_log_path(project, policy)
    if reindex or not path.is_file() or (source.is_file() and source.stat().st_mtime > path.stat().st_mtime):
        return build_index(project, policy)
    return read_json(path)


def bm25_search(index: dict[str, Any], query: str, limit: int) -> list[dict[str, Any]]:
    query_terms = tokenize(query)
    if not query_terms:
        return []
    documents = index.get("documents", [])
    doc_count = max(int(index.get("documentCount") or len(documents) or 1), 1)
    avg_len = float(index.get("avgDocumentLength") or 1.0)
    df: Counter[str] = Counter()
    for doc in documents:
        for term in set(doc.get("terms", {})):
            df[term] += 1
    results: list[dict[str, Any]] = []
    for doc in documents:
        score = 0.0
        length = float(doc.get("length") or 1)
        terms = doc.get("terms", {})
        for term in query_terms:
            tf = float(terms.get(term, 0))
            if tf <= 0:
                continue
            idf = math.log(1 + (doc_count - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * ((tf * 2.5) / (tf + 1.5 * (0.25 + 0.75 * length / avg_len)))
        if score > 0:
            item = dict(doc)
            item["score"] = round(score, 4)
            item.pop("terms", None)
            results.append(item)
    return sorted(results, key=lambda item: item["score"], reverse=True)[:limit]


def markdown_list(items: list[str], empty: str) -> str:
    clean = [str(item).strip() for item in items if str(item).strip()]
    if not clean:
        return f"- {empty}"
    return "\n".join(f"- {item}" for item in clean)


def recent_events(project: Path, policy: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    path = event_log_path(project, policy)
    if not path.is_file():
        return []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events[-limit:]


def create_snapshot(project: Path, policy: dict[str, Any], reason: str, quiet: bool) -> Path:
    state_path = project / ".codex-memory" / "STATE.json"
    state = read_json(state_path)
    max_items = int(policy.get("snapshot", {}).get("maxItems", 8))
    events = recent_events(project, policy, max_items)
    steering = state.get("humanSteering", {}) if isinstance(state.get("humanSteering"), dict) else {}
    current_unit = state.get("currentUnit", {}) if isinstance(state.get("currentUnit"), dict) else {}
    last_request = steering.get("lastPrompt") or state.get("intent") or ""
    tasks = [
        f"stage={state.get('currentStage', '')}",
        f"node={state.get('currentNode', '')}",
        f"unit={current_unit.get('id', '')}",
        f"goal={current_unit.get('goal', '')}",
        f"next={state.get('nextAction', '')}",
    ]
    decisions = []
    for item in state.get("decisionLog", [])[-max_items:]:
        decisions.append(flatten(item)[:240])
    files = list(state.get("artifacts", [])[-max_items:]) if isinstance(state.get("artifacts"), list) else []
    errors = []
    for event in events:
        if event.get("eventType") == "error" or event.get("status") in {"BLOCKED", "FAILED"}:
            errors.append(flatten(event)[:240])
    for item in state.get("failedValidations", [])[-max_items:]:
        errors.append(flatten(item)[:240])
    blockers = [flatten(item)[:240] for item in state.get("blockers", [])[-max_items:]]
    recent = [
        f"{event.get('timestamp', '')} {event.get('eventType', '')} {event.get('status', '')} {event.get('source', '')}".strip()
        for event in events
    ]
    created = now_iso()
    body = f"""---
title: "Resume Snapshot"
project: "{project.name}"
reason: "{reason}"
created: "{created}"
tags:
  - pfo/context
  - pfo/resume
---

# Resume Snapshot

Created: {created}
Reason: {reason}

## Last Request

{last_request or "TBD"}

## Active Task

{markdown_list(tasks, "No active task recorded.")}

## Files

{markdown_list(files, "No files recorded.")}

## Decisions

{markdown_list(decisions, "No decisions recorded.")}

## Errors

{markdown_list(errors, "No recent errors.")}

## Blockers

{markdown_list(blockers, "No blockers recorded.")}

## Recent Events

{markdown_list(recent, "No events recorded.")}
"""
    path = project / policy.get("snapshot", {}).get("path", ".codex-memory/resume-snapshot.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    if state:
        rel = str(path.relative_to(project))
        artifacts = set(state.get("artifacts", []))
        artifacts.add(rel)
        state["artifacts"] = sorted(artifacts)
        state["resumeSnapshot"] = {"path": rel, "reason": reason, "createdAt": created}
        events_path = event_log_path(project, policy)
        events_path.parent.mkdir(parents=True, exist_ok=True)
        event_id = f"event-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-snapshot"
        event = {
            "id": event_id,
            "timestamp": created,
            "eventType": "state-change",
            "status": "RECORDED",
            "project": project.name,
            "source": "context-snapshot",
            "payload": {"reason": reason, "snapshot": rel},
        }
        with events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        state["eventLog"] = {"path": str(events_path.relative_to(project)), "lastEventId": event_id, "lastEventAt": created}
        artifacts.add(str(events_path.relative_to(project)))
        state["artifacts"] = sorted(artifacts)
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not quiet:
        print(f"OK: wrote {path.relative_to(project)}")
    return path


def cmd_budget(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    policy = load_policy(project)
    status, reason = budget_decision(
        policy,
        args.kind,
        args.bytes,
        args.lines,
        args.command_text,
        args.raw_http,
        args.approved,
    )
    payload = {"status": status, "reason": reason, "kind": normalize_kind(args.kind, args.command_text)}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{status}: {reason}")
    return 1 if status == "BLOCKED" else 0


def cmd_index(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    policy = load_policy(project)
    index = build_index(project, policy)
    print(f"OK: indexed {index['documentCount']} context events into {policy['index']['path']}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    policy = load_policy(project)
    query = " ".join(args.query)
    index = load_or_build_index(project, policy, args.reindex)
    results = bm25_search(index, query, args.limit)
    if args.json:
        print(json.dumps({"query": query, "results": results}, indent=2, ensure_ascii=False))
    else:
        print(f"Context search: {len(results)} result(s) for {query!r}")
        for item in results:
            print(
                f"- {item['score']:.4f} {item.get('timestamp', '')} "
                f"{item.get('eventType', '')}/{item.get('status', '')} {item.get('id', '')}: "
                f"{item.get('excerpt', '')[:160]}"
            )
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    policy = load_policy(project)
    create_snapshot(project, policy, args.reason, args.quiet)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    policy = load_policy(project)
    required = ["limits", "routing", "index", "snapshot", "evidence"]
    missing = [key for key in required if key not in policy]
    if missing:
        print("ERROR: context runtime policy missing " + ", ".join(missing))
        return 1
    warn_status, _ = budget_decision(policy, "read", policy["limits"]["readOutputWarnBytes"], 1, "", False, False)
    block_status, _ = budget_decision(policy, "http", 0, 0, "curl https://example.com", False, False)
    if warn_status != "PASSED_WITH_WARNINGS":
        print("ERROR: read warning budget did not warn")
        return 1
    if block_status != "BLOCKED":
        print("ERROR: raw HTTP budget did not block")
        return 1
    state_path = project / ".codex-memory" / "STATE.json"
    state = read_json(state_path)
    if state:
        state.setdefault("gateResults", {})["contextBudget"] = "PASSED"
        state["contextBudget"] = {
            "gate": "pfo context-budget",
            "indexPath": policy.get("index", {}).get("path", ".codex-memory/context-index.json"),
            "snapshotPath": policy.get("snapshot", {}).get("path", ".codex-memory/resume-snapshot.md"),
            "status": "READY",
        }
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OK: context runtime policy, budget gate, and raw HTTP routing validated")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Product Factory OS context budget, search, and resume runtime.")
    sub = parser.add_subparsers(dest="command", required=True)

    budget = sub.add_parser("budget")
    budget.add_argument("project", type=Path)
    budget.add_argument("--kind", choices=["tool", "read", "log", "web", "http", "grep", "rg"], default="tool")
    budget.add_argument("--bytes", type=int, default=0)
    budget.add_argument("--lines", type=int, default=0)
    budget.add_argument("--command-text", default="")
    budget.add_argument("--raw-http", action="store_true")
    budget.add_argument("--approved", action="store_true")
    budget.add_argument("--json", action="store_true")
    budget.set_defaults(func=cmd_budget)

    index = sub.add_parser("index")
    index.add_argument("project", type=Path)
    index.set_defaults(func=cmd_index)

    search = sub.add_parser("search")
    search.add_argument("project", type=Path)
    search.add_argument("query", nargs="+")
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--reindex", action="store_true")
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=cmd_search)

    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("project", type=Path)
    snapshot.add_argument("--reason", default="manual")
    snapshot.add_argument("--quiet", action="store_true")
    snapshot.set_defaults(func=cmd_snapshot)

    validate = sub.add_parser("validate")
    validate.add_argument("project", type=Path)
    validate.set_defaults(func=cmd_validate)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
