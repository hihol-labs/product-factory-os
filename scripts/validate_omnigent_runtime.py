#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

MECHANISMS = {
    "O1": ["PFO_AGENT_SPEC.yaml", "agent-spec", "agents/orchestrator.yaml"],
    "O2": ["policy-eval", "ALLOW", "DENY", "ASK"],
    "O3": ["pfo exec", "session export", "live-status.json"],
    "O4": ["dispatch", ".pfo/dispatch"],
    "O5": ["cross-review", "different reviewer harness"],
    "O6": ["cost-route", "riskScore", "estimatedCostUsd"],
    "O7": ["telemetry", "live observability"],
    "O8": ["session export/import/status", "forkable context"],
    "O9": ["sandbox:", "read_paths", "write_paths"],
}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def require_file(rel: str) -> None:
    if not (ROOT / rel).is_file():
        fail(f"missing {rel}")


def require_token(text: str, token: str, source: str) -> None:
    if token not in text:
        fail(f"{source} missing {token!r}")


def validate_agent_specs() -> None:
    require_file("docs/templates/PFO_AGENT_SPEC.yaml")
    specs = sorted((ROOT / "agents").glob("*.yaml"))
    if len(specs) < 7:
        fail("expected at least seven runnable PFO agent specs")
    for path in specs:
        text = path.read_text(encoding="utf-8")
        for token in ["spec_version:", "name:", "instructions:", "executor:", "tools:", "policies:", "sandbox:"]:
            require_token(text, token, str(path.relative_to(ROOT)))


def main() -> None:
    pfo = read("scripts/pfo.py")
    docs = read("docs/PFO_OMNIGENT_RUNTIME.md")
    harness = read("docs/CONTROL_HARNESS.md")
    readiness = read("scripts/production_readiness.py")
    structure = read("scripts/validate_structure.py")
    validate_agent_specs()
    for mechanism, tokens in MECHANISMS.items():
        require_token(docs, mechanism, "docs/PFO_OMNIGENT_RUNTIME.md")
        for token in tokens:
            haystack = "\n".join([pfo, docs, harness, structure, readiness])
            require_token(haystack, token, mechanism)
    for command in ["cmd_agent_spec", "cmd_policy_eval", "cmd_dispatch", "cmd_cross_review", "cmd_cost_route", "cmd_session"]:
        require_token(pfo, f"def {command}", "scripts/pfo.py")
    for control_id in [
        "agent-spec-runtime",
        "policy-verdict-runtime",
        "dispatch-runtime",
        "cross-harness-review",
        "cost-risk-routing",
        "live-session-observability",
        "forkable-session-context",
        "sandbox-spec-runtime",
    ]:
        require_token(harness, control_id, "docs/CONTROL_HARNESS.md")
    print("OK: Omnigent-inspired PFO runtime O1-O9 is fully wired")


if __name__ == "__main__":
    main()
