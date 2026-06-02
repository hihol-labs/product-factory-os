#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import subprocess
import sys

from pfo_alias_targets import missing_alias_targets

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AGENTS.md",
    "CODEX.md",
    "NEXT_STEP.md",
    ".codex-memory/MEMORY.md",
    ".codex-memory/STATE.json",
    ".codex-memory/events.jsonl",
]
REQUIRED_PFO = [
    ".pfo/PROJECT_CONTRACT.md",
    ".pfo/DATA_POLICY.md",
    ".pfo/GOLDEN_FLOWS.md",
    ".pfo/FORBIDDEN_CHANGES.md",
    ".pfo/FALLBACK_POLICY.md",
    ".pfo/SCOPE_LOCK.md",
    ".pfo/PERMISSION_MATRIX.md",
    ".pfo/PERMISSION_MATRIX.json",
    ".pfo/LEARNING_PROMOTION_GATE.md",
    ".pfo/EXECUTION_POLICY.json",
    ".pfo/VERIFICATION_CONTRACT.json",
    ".pfo/TOOL_CAPABILITY_REGISTRY.json",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        fail(result.stdout + result.stderr)


def require_json_contract(project: Path, rel: str, fields: list[str]) -> dict:
    path = project / rel
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{project} has invalid {rel}: {exc}")
    for field in fields:
        if field not in data:
            fail(f"{project} {rel} is missing {field}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Product Factory OS project.")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    for rel in REQUIRED:
        if not (project / rel).is_file():
            fail(f"{project} is missing {rel}")
    alias_errors = missing_alias_targets(project)
    if alias_errors:
        fail(f"{project} has broken alias target(s):\n" + "\n".join(alias_errors))

    run([sys.executable, "scripts/validate_state.py", str(project / ".codex-memory" / "STATE.json")])
    for rel in REQUIRED_PFO:
        if not (project / rel).is_file():
            fail(f"{project} is missing {rel}")
    require_json_contract(
        project,
        ".pfo/EXECUTION_POLICY.json",
        ["commandPolicy", "writePolicy", "networkPolicy", "approvalPolicy"],
    )
    require_json_contract(
        project,
        ".pfo/PERMISSION_MATRIX.json",
        ["actors", "capabilities", "rules"],
    )
    require_json_contract(
        project,
        ".pfo/VERIFICATION_CONTRACT.json",
        ["commands", "requiredArtifacts", "passCriteria", "failureMode"],
    )
    require_json_contract(
        project,
        ".pfo/TOOL_CAPABILITY_REGISTRY.json",
        ["tools"],
    )
    permission_text = (project / ".pfo/PERMISSION_MATRIX.md").read_text(encoding="utf-8")
    for token in ["Run local verification", "External API write", "Context budget", "Deploy or migrate production"]:
        if token not in permission_text:
            fail(f"{project} .pfo/PERMISSION_MATRIX.md is missing {token!r}")
    run([sys.executable, "scripts/pfo_permission_gate.py", str(project)])
    run([sys.executable, "scripts/pfo_event_log.py", "validate", str(project)])
    run([sys.executable, "scripts/validate_tool_registry.py", str(project / ".pfo" / "TOOL_CAPABILITY_REGISTRY.json")])
    run([sys.executable, "scripts/pfo_contract_gate.py", str(project)])
    if (project / ".pfo-starter.json").is_file():
        run([sys.executable, "scripts/validate_starter_compliance.py", str(project)])
    graph = project / "EXECUTION_GRAPH.md"
    if graph.is_file():
        run([sys.executable, "scripts/validate_execution_graph.py", str(graph)])
    run([sys.executable, "scripts/validate_plan_quality.py", str(project)])

    state = json.loads((project / ".codex-memory" / "STATE.json").read_text(encoding="utf-8"))
    steering = state.get("humanSteering", {})
    if not isinstance(steering, dict):
        fail(f"{project} state is missing humanSteering object")
    next_step_gate = state.get("gateResults", {}).get("nextStepApproval")
    if next_step_gate not in {"PENDING", "PASSED", "PASSED_WITH_WARNINGS", "BLOCKED"}:
        fail(f"{project} state gateResults.nextStepApproval must be PENDING, PASSED, PASSED_WITH_WARNINGS, or BLOCKED")
    if steering.get("approvalStatus") not in {"PENDING", "APPROVED", "CONSUMED", "CHANGED", "BLOCKED"}:
        fail(f"{project} state humanSteering.approvalStatus must be PENDING, APPROVED, CONSUMED, CHANGED, or BLOCKED")
    if not steering.get("recommendedNextStep"):
        fail(f"{project} state humanSteering.recommendedNextStep must not be empty")
    planned_or_later = {
        "PLAN_READY",
        "NEXT_STEP_REVIEW",
        "UNIT_CONTEXT_READY",
        "UNIT_DISPATCHED",
        "ROOT_CAUSE_ANALYSIS",
        "TDD_EVIDENCE",
        "BUILDING",
        "VERIFYING_WORK",
        "TESTING",
        "TWO_STAGE_REVIEW",
        "REVIEWING",
        "RECOVERY_REQUIRED",
        "SECURITY_REVIEW",
        "DEPENDENCY_REVIEW",
        "HARDENING",
        "READY_FOR_DEPLOY",
        "BRANCH_FINISH",
        "DEPLOYED",
    }
    if state.get("currentStage") in planned_or_later:
        for rel in [
            "IDEA_SCORECARD.md",
            "VALIDATION_PLAN.md",
            "FEEDBACK_LOG.md",
            "ITERATION_REVIEW.md",
            "FUNNEL_MODEL.md",
            "ASSET_REGISTER.md",
            "CONTENT_BACKLOG.md",
            "SEO_GROWTH_GUARANTEE_GATE.md",
            "PRODUCT_BLUEPRINT.md",
            "PROJECT_ARCHITECTURE.md",
            "BUILD_PLAN.md",
            "EXECUTION_GRAPH.md",
            "NEXT_STEP.md",
            "TEST_PLAN.md",
            "QUALITY_GATES.md",
        ]:
            if not (project / rel).is_file():
                fail(f"planned project is missing {rel}")
    if state.get("currentStage") in {
        "UNIT_CONTEXT_READY",
        "UNIT_DISPATCHED",
        "ROOT_CAUSE_ANALYSIS",
        "TDD_EVIDENCE",
        "BUILDING",
        "VERIFYING_WORK",
        "TWO_STAGE_REVIEW",
    }:
        rel = ".pfo/UNIT_CONTEXT_MANIFEST.json"
        if not (project / rel).is_file():
            fail(f"unit execution project is missing {rel}")
    if state.get("currentStage") == "HANDOFF_READY":
        rel = "HANDOFF.md"
        if not (project / rel).is_file():
            fail(f"handoff project is missing {rel}")
    if state.get("currentStage") in ["READY_FOR_DEPLOY", "DEPLOYED"]:
        for rel in ["QUALITY_GATES.md", "TEST_PLAN.md"]:
            if not (project / rel).is_file():
                fail(f"deploy-ready project is missing {rel}")

    print(f"OK: validated PFO project {project}")


if __name__ == "__main__":
    main()
