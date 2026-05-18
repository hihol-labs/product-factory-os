#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import time


def load_state(cwd: Path) -> dict:
    path = cwd / ".codex-memory" / "STATE.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_error": "STATE.json is not valid JSON"}


def main() -> None:
    cwd = Path.cwd()
    state = load_state(cwd)
    if not state:
        print("PFO session diagnostics: no state file")
        return
    if state.get("_error"):
        print(f"PFO session diagnostics: {state['_error']}")
        return

    stage = state.get("stage") or state.get("currentState") or "unknown"
    node = state.get("currentNode") or state.get("activeNode") or "unknown"
    telemetry = state.get("telemetry", {})
    recovery = state.get("recovery", {})
    cost_notes = telemetry.get("costNotes") or state.get("costNotes") or "none"

    warnings: list[str] = []
    if recovery.get("required") or stage == "RECOVERY_REQUIRED":
        warnings.append("recovery is required before new build work")
    if not (cwd / "HANDOFF.md").is_file() and node != "unknown":
        warnings.append("HANDOFF.md is missing for active node context")
    state_path = cwd / ".codex-memory" / "STATE.json"
    age_minutes = int((time.time() - state_path.stat().st_mtime) / 60)
    if age_minutes > 240:
        warnings.append(f"state file is stale ({age_minutes} min)")

    print(f"PFO session diagnostics: stage={stage}; node={node}; cost={cost_notes}")
    if warnings:
        print("PFO session diagnostics warnings: " + "; ".join(warnings))


if __name__ == "__main__":
    main()
