#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import time

ROOT = Path(__file__).resolve().parents[1]


def load_state(cwd: Path) -> dict:
    path = cwd / ".codex-memory" / "STATE.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_error": "STATE.json is not valid JSON"}


def load_context_runtime():
    runtime_path = ROOT / "scripts" / "pfo_context_runtime.py"
    if not runtime_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("pfo_context_runtime", runtime_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def int_value(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def main() -> None:
    cwd = Path.cwd()
    state = load_state(cwd)
    if not state:
        print("PFO session diagnostics: no state file")
        return
    if state.get("_error"):
        print(f"PFO session diagnostics: {state['_error']}")
        return

    stage = state.get("currentStage") or state.get("stage") or state.get("currentState") or "unknown"
    node = state.get("currentNode") or state.get("activeNode") or "unknown"
    telemetry = state.get("telemetry", {})
    recovery = state.get("recovery", {})
    cost_notes = telemetry.get("costNotes") or state.get("costNotes") or "none"
    runtime = load_context_runtime()
    context_policy = runtime.load_policy(cwd) if runtime else {}

    warnings: list[str] = []
    if recovery.get("required") or stage == "RECOVERY_REQUIRED":
        warnings.append("recovery is required before new build work")
    if not (cwd / "HANDOFF.md").is_file() and node != "unknown":
        warnings.append("HANDOFF.md is missing for active node context")
    state_path = cwd / ".codex-memory" / "STATE.json"
    age_minutes = int((time.time() - state_path.stat().st_mtime) / 60)
    if age_minutes > 240:
        warnings.append(f"state file is stale ({age_minutes} min)")
    if runtime:
        kind = str(telemetry.get("lastOutputKind") or "tool")
        byte_count = int_value(telemetry.get("lastOutputBytes"))
        line_count = int_value(telemetry.get("lastOutputLines"))
        if byte_count or line_count:
            status, reason = runtime.budget_decision(context_policy, kind, byte_count, line_count, "", False, False)
            if status == "BLOCKED":
                warnings.append("context budget BLOCKED: " + reason)
            elif status == "PASSED_WITH_WARNINGS":
                warnings.append("context budget warning: " + reason)
        index_path = cwd / context_policy.get("index", {}).get("path", ".codex-memory/context-index.json")
        snapshot_path = cwd / context_policy.get("snapshot", {}).get("path", ".codex-memory/resume-snapshot.md")
        if not index_path.is_file():
            warnings.append("context search index is missing; run `pfo context-index <project>`")
        if not snapshot_path.is_file():
            warnings.append("resume snapshot is missing; run `pfo context-snapshot <project>`")

    print(f"PFO session diagnostics: stage={stage}; node={node}; cost={cost_notes}")
    if runtime:
        limits = context_policy.get("limits", {})
        print(
            "PFO context budget: "
            f"mode={context_policy.get('mode', 'budgeted-summary')}; "
            f"tool warn/block={limits.get('toolOutputWarnBytes')}/{limits.get('toolOutputBlockBytes')} bytes; "
            f"read warn/block={limits.get('readOutputWarnBytes')}/{limits.get('readOutputBlockBytes')} bytes"
        )
    if warnings:
        print("PFO session diagnostics warnings: " + "; ".join(warnings))


if __name__ == "__main__":
    main()
