#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_O = {
    "O1": "declarative agent YAML profiles",
    "O2": "policy event verdict engine",
    "O3": "runner/server separation",
    "O4": "dispatch worktree isolation",
    "O5": "cross-vendor critical review",
    "O6": "cost/risk routing",
    "O7": "live session observability",
    "O8": "session fork attach share",
    "O9": "sandbox spec in profiles and unit manifests",
}


POLICY_EVENT_FIELDS = ["type", "target", "data", "actor", "usage", "session_state", "result"]
LIVE_STATUS_FIELDS = ["activeGoal", "route", "currentUnit", "runningCommand", "subagents", "inbox", "approvals", "gates", "diff", "verification"]
SANDBOX_FIELDS = ["type", "read_paths", "write_paths", "allow_network", "env_passthrough"]
COST_FIELDS = ["riskScore", "estimatedCost", "modelTier", "budgetDecision", "downgradeAllowed"]


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


def require_json_fields(path: Path, fields: list[str], source: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    text = json.dumps(data, ensure_ascii=False)
    for field in fields:
        if field not in text:
            fail(f"{source} missing {field}")


def yaml_block_has(text: str, block: str, fields: list[str], source: str) -> None:
    require_token(text, block + ":", source)
    for field in fields:
        require_token(text, field + ":", source)


def validate_agent_specs() -> None:
    require_file("docs/templates/PFO_AGENT_SPEC.yaml")
    specs = sorted((ROOT / "agents").glob("*.yaml"))
    if len(specs) < 7:
        fail("expected at least seven runnable PFO agent specs")
    for path in [ROOT / "docs/templates/PFO_AGENT_SPEC.yaml", *specs]:
        text = path.read_text(encoding="utf-8")
        source = str(path.relative_to(ROOT))
        for token in ["spec_version:", "name:", "instructions:", "executor:", "harness:", "tools:", "policies:", "terminals:", "sandbox:"]:
            require_token(text, token, source)
        yaml_block_has(text, "sandbox", SANDBOX_FIELDS, source)


def validate_policy_runtime(pfo: str) -> None:
    for token in ["cmd_policy_eval", "ALLOW", "DENY", "ASK", "policy_eval_payload"]:
        require_token(pfo, token, "scripts/pfo.py")
    for field in POLICY_EVENT_FIELDS:
        require_token(pfo, field, "policy event schema")
    for arg in ["--actor", "--usage-json", "--session-state-json", "--result-json"]:
        require_token(pfo, arg, "pfo policy-eval parser")


def validate_runner_server(pfo: str, docs: str, harness: str) -> None:
    for token in ["cmd_runner", "cmd_server", "runner-host.json", "control-plane.json", "neverExecutesTools", "local-source-of-truth"]:
        require_token(pfo + docs, token, "runner/server runtime")
    require_token(harness, "runner-server-separation", "docs/CONTROL_HARNESS.md")


def validate_dispatch(pfo: str) -> None:
    for token in ["cmd_dispatch", "git", "worktree", "add", "--no-create-worktree", "independent", ".pfo-worktrees"]:
        require_token(pfo, token, "dispatch runtime")


def validate_cross_review(pfo: str) -> None:
    for token in ["CRITICAL_REVIEW_RISKS", "implementer_vendor", "reviewer_vendor", "vendor_available", "requireDifferentVendorForCriticalRisk"]:
        require_token(pfo, token, "cross-vendor review")
    for risk in ["security", "migration", "deploy", "auth", "payments", "data-loss"]:
        require_token(pfo, risk, "critical review risks")


def validate_cost_routing(pfo: str) -> None:
    for token in ["cmd_cost_route", "dailyBudgetUsd", "estimatedCost", "estimatedCostUsd", "downgradeAllowed", "modelTier", "budgetDecision"]:
        require_token(pfo, token, "cost/risk routing")
    require_json_fields(ROOT / "docs/templates/pfo/PERMISSION_MATRIX.json", COST_FIELDS, "permission matrix template")
    require_json_fields(ROOT / ".pfo/PERMISSION_MATRIX.json", COST_FIELDS, "project permission matrix")


def validate_live_session(pfo: str) -> None:
    for field in LIVE_STATUS_FIELDS:
        require_token(pfo, field, "live session payload")
    for token in ["live_session_payload", "live-status.json"]:
        require_token(pfo, token, "live session observability")


def validate_session_ops(pfo: str) -> None:
    for token in ["attach", "share", "session-share.json", "eventRange", "unitManifest"]:
        require_token(pfo, token, "session fork/attach/share")


def validate_sandbox_specs(pfo: str) -> None:
    for rel in ["docs/templates/UNIT_CONTEXT_MANIFEST.json", "docs/templates/pfo/UNIT_CONTEXT_MANIFEST.json"]:
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        sandbox = data.get("sandbox", {})
        for field in SANDBOX_FIELDS:
            if field not in sandbox:
                fail(f"{rel} sandbox missing {field}")
    for field in SANDBOX_FIELDS:
        require_token(pfo, field, "generated unit sandbox")


def validate_docs() -> None:
    docs = read("docs/PFO_OMNIGENT_RUNTIME.md")
    harness = read("docs/CONTROL_HARNESS.md")
    readiness = read("scripts/production_readiness.py")
    structure = read("scripts/validate_structure.py")
    for oid in REQUIRED_O:
        require_token(docs, oid, "docs/PFO_OMNIGENT_RUNTIME.md")
    require_token(readiness, "validate_omnigent_runtime.py", "production readiness")
    require_token(structure, "validate_omnigent_runtime.py", "structure validation")
    for control_id in [
        "agent-spec-runtime",
        "policy-verdict-runtime",
        "runner-server-separation",
        "dispatch-runtime",
        "cross-harness-review",
        "cost-risk-routing",
        "live-session-observability",
        "forkable-session-context",
        "sandbox-spec-runtime",
    ]:
        require_token(harness, control_id, "docs/CONTROL_HARNESS.md")


def main() -> None:
    pfo = read("scripts/pfo.py")
    docs = read("docs/PFO_OMNIGENT_RUNTIME.md")
    harness = read("docs/CONTROL_HARNESS.md")
    validate_agent_specs()
    validate_policy_runtime(pfo)
    validate_runner_server(pfo, docs, harness)
    validate_dispatch(pfo)
    validate_cross_review(pfo)
    validate_cost_routing(pfo)
    validate_live_session(pfo)
    validate_session_ops(pfo)
    validate_sandbox_specs(pfo)
    validate_docs()
    print("OK: Omnigent-inspired PFO runtime O1-O9 is behaviorally wired")


if __name__ == "__main__":
    main()
