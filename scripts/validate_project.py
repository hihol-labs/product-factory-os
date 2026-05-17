#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["AGENTS.md", "CODEX.md", ".codex-memory/MEMORY.md", ".codex-memory/STATE.json"]
REQUIRED_PFO = [
    ".pfo/PROJECT_CONTRACT.md",
    ".pfo/DATA_POLICY.md",
    ".pfo/GOLDEN_FLOWS.md",
    ".pfo/FORBIDDEN_CHANGES.md",
    ".pfo/FALLBACK_POLICY.md",
    ".pfo/SCOPE_LOCK.md",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        fail(result.stdout + result.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Product Factory OS project.")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    for rel in REQUIRED:
        if not (project / rel).is_file():
            fail(f"{project} is missing {rel}")

    run([sys.executable, "scripts/validate_state.py", str(project / ".codex-memory" / "STATE.json")])
    for rel in REQUIRED_PFO:
        if not (project / rel).is_file():
            fail(f"{project} is missing {rel}")
    run([sys.executable, "scripts/pfo_contract_gate.py", str(project)])
    if (project / ".pfo-starter.json").is_file():
        run([sys.executable, "scripts/validate_starter_compliance.py", str(project)])
    graph = project / "EXECUTION_GRAPH.md"
    if graph.is_file():
        run([sys.executable, "scripts/validate_execution_graph.py", str(graph)])
    run([sys.executable, "scripts/validate_plan_quality.py", str(project)])

    state = json.loads((project / ".codex-memory" / "STATE.json").read_text(encoding="utf-8"))
    planned_or_later = {
        "PLAN_READY",
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
            "PRODUCT_BLUEPRINT.md",
            "PROJECT_ARCHITECTURE.md",
            "BUILD_PLAN.md",
            "EXECUTION_GRAPH.md",
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
