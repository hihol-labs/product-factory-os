#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PLAN_PATTERNS = [
    (re.compile(r"\bTBD\b", re.I), "TBD"),
    (re.compile(r"\bTODO\b", re.I), "TODO"),
    (re.compile(r"similar to previous task", re.I), "similar to previous task"),
    (re.compile(r"handle errors", re.I), "handle errors"),
    (re.compile(r"\badd tests\b", re.I), "add tests"),
]

ALLOWED_RULE_CONTEXT = [
    "do not leave",
    "forbidden",
    "placeholder",
    "plan failures",
]

EXECUTABLE_TASK_REQUIREMENTS = [
    "Exact files",
    "Exact verification command",
    "Expected output",
    "User-facing next-step approval",
    "TDD red and green evidence",
    "Root-cause evidence",
    "Spec compliance review",
    "Branch finish decision",
]

TDD_ENFORCEMENT_STAGES = {
    "TDD_EVIDENCE",
    "BUILDING",
    "VERIFYING_WORK",
    "TESTING",
    "TWO_STAGE_REVIEW",
    "REVIEWING",
    "SECURITY_REVIEW",
    "DEPENDENCY_REVIEW",
    "HARDENING",
    "READY_FOR_DEPLOY",
    "BRANCH_FINISH",
    "DEPLOYED",
    "SESSION_SAVED",
}

TDD_RED_ENFORCEMENT_STAGES = {"UNIT_DISPATCHED"} | TDD_ENFORCEMENT_STAGES

REVIEW_ENFORCEMENT_STAGES = {
    "TWO_STAGE_REVIEW",
    "REVIEWING",
    "SECURITY_REVIEW",
    "DEPENDENCY_REVIEW",
    "HARDENING",
    "READY_FOR_DEPLOY",
    "BRANCH_FINISH",
    "DEPLOYED",
    "SESSION_SAVED",
}

NEXT_STEP_APPROVAL_STAGES = {
    "UNIT_DISPATCHED",
    "TDD_EVIDENCE",
    "BUILDING",
}

ROOT_CAUSE_ENFORCEMENT_STAGES = {"ROOT_CAUSE_ANALYSIS"} | TDD_ENFORCEMENT_STAGES

EXPERIMENT_ENFORCEMENT_STAGES = {"EXPERIMENT_READY", "EXPERIMENT_RUNNING", "EXPERIMENT_EVALUATED"}

VERIFICATION_CONTRACT_STAGES = {
    "UNIT_CONTEXT_READY",
    "UNIT_DISPATCHED",
    "ROOT_CAUSE_ANALYSIS",
    "TDD_EVIDENCE",
    "BUILDING",
    "VERIFYING_WORK",
    "TESTING",
    "TWO_STAGE_REVIEW",
    "REVIEWING",
    "SECURITY_REVIEW",
    "DEPENDENCY_REVIEW",
    "HARDENING",
    "READY_FOR_DEPLOY",
    "BRANCH_FINISH",
    "DEPLOYED",
}

PASS_STATUSES = {"PASSED", "PASSED_WITH_WARNINGS"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def line_is_rule(line: str) -> bool:
    lower = line.lower()
    return any(token in lower for token in ALLOWED_RULE_CONTEXT)


def validate_build_plan(project: Path) -> list[str]:
    errors: list[str] = []
    path = project / "BUILD_PLAN.md"
    if not path.is_file():
        return errors

    text = path.read_text(encoding="utf-8")
    lower_text = text.lower()
    for token in EXECUTABLE_TASK_REQUIREMENTS:
        if token.lower() not in lower_text:
            errors.append(f"BUILD_PLAN.md missing executable-task requirement: {token}")

    for number, line in enumerate(text.splitlines(), start=1):
        if line_is_rule(line):
            continue
        for pattern, label in FORBIDDEN_PLAN_PATTERNS:
            if pattern.search(line):
                errors.append(f"BUILD_PLAN.md:{number} contains forbidden placeholder: {label}")

    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or not cells[0].isdigit():
            continue
        if len(cells) < 6:
            errors.append(f"BUILD_PLAN.md:{number} module row must include step, module, dependencies, files, verification, exit criteria")
            continue
        if any(not cell for cell in cells[:6]):
            errors.append(f"BUILD_PLAN.md:{number} module row has an empty executable field")

    return errors


def route_text(state: dict) -> str:
    parts = [
        str(state.get("currentTaskRoute", "")),
        str(state.get("taskRoute", "")),
        str(state.get("nextAction", "")),
        str(state.get("currentNode", "")),
    ]
    existing = state.get("existingProject", {})
    if isinstance(existing, dict):
        parts.append(str(existing.get("currentTaskRoute", "")))
    current_unit = state.get("currentUnit", {})
    if isinstance(current_unit, dict):
        parts.append(str(current_unit.get("goal", "")))
    return " ".join(parts).lower()


def manifest_discipline(manifest: dict) -> dict:
    discipline = manifest.get("engineeringDiscipline", {})
    return discipline if isinstance(discipline, dict) else {}


def requires_tdd(state: dict, manifest: dict) -> bool:
    discipline = manifest_discipline(manifest)
    route = route_text(state)
    state_discipline = state.get("engineeringDiscipline", {})
    if discipline.get("behaviorChange") is True or discipline.get("requiresTdd") is True:
        return True
    if isinstance(state_discipline, dict) and state_discipline.get("behaviorChange") is True:
        return True
    if state.get("currentStage") == "TDD_EVIDENCE":
        return True
    if "/bugfix" in route or "/kickstart" in route:
        return True
    evidence = state.get("tddEvidence", {})
    if isinstance(evidence, dict) and any(evidence.get(key) for key in ["red", "green", "refactor"]):
        return True
    return False


def requires_root_cause(state: dict, manifest: dict) -> bool:
    discipline = manifest_discipline(manifest)
    route = route_text(state)
    if discipline.get("bugfix") is True or discipline.get("requiresRootCause") is True:
        return True
    if state.get("currentStage") == "ROOT_CAUSE_ANALYSIS":
        return True
    return "/bugfix" in route or "bugfix" in route


def passed(status: str) -> bool:
    return status in PASS_STATUSES


def validate_state_gates(project: Path) -> list[str]:
    errors: list[str] = []
    state = read_json(project / ".codex-memory" / "STATE.json")
    if not state:
        return errors
    manifest = read_json(project / ".pfo" / "UNIT_CONTEXT_MANIFEST.json")
    stage = state.get("currentStage", "")
    gates = state.get("gateResults", {})
    experiment = state.get("experimentLoop", {}) if isinstance(state.get("experimentLoop", {}), dict) else {}

    if stage in VERIFICATION_CONTRACT_STAGES:
        contract = read_json(project / ".pfo" / "VERIFICATION_CONTRACT.json")
        if not contract:
            errors.append("unit execution is missing .pfo/VERIFICATION_CONTRACT.json")
        else:
            commands = contract.get("commands", [])
            if not isinstance(commands, list) or not commands:
                errors.append("verification contract has no commands")
            for index, command in enumerate(commands, start=1):
                if not isinstance(command, dict):
                    errors.append(f"verification contract command {index} must be an object")
                    continue
                for field in ["id", "command", "timeoutSeconds", "expectedOutput", "passFailParser"]:
                    if not command.get(field):
                        errors.append(f"verification contract command {index} missing {field}")
            artifacts = contract.get("requiredArtifacts", [])
            if not isinstance(artifacts, list) or not artifacts:
                errors.append("verification contract has no requiredArtifacts")

    if requires_tdd(state, manifest) and stage in TDD_RED_ENFORCEMENT_STAGES:
        evidence = state.get("tddEvidence", {})
        if not isinstance(evidence, dict) or not evidence.get("red"):
            errors.append("behavior change is missing TDD red evidence")
        if not passed(str(gates.get("tddRed", ""))):
            errors.append("behavior change has no passing tddRed gate")
    if requires_tdd(state, manifest) and stage in TDD_ENFORCEMENT_STAGES:
        evidence = state.get("tddEvidence", {})
        if not isinstance(evidence, dict) or not evidence.get("green"):
            errors.append("behavior change is missing TDD green evidence")
        if stage in REVIEW_ENFORCEMENT_STAGES and (not isinstance(evidence, dict) or not evidence.get("refactor")):
            errors.append("behavior change is missing TDD refactor evidence or explicit no-refactor note")
        if not passed(str(gates.get("tddGreen", ""))):
            errors.append("behavior change has no passing tddGreen gate")

    if requires_root_cause(state, manifest) and stage in ROOT_CAUSE_ENFORCEMENT_STAGES:
        root_cause = state.get("rootCause", {})
        if not (project / "ROOT_CAUSE.md").is_file():
            errors.append("bugfix is missing ROOT_CAUSE.md")
        if not isinstance(root_cause, dict) or not root_cause.get("summary") or not root_cause.get("evidence"):
            errors.append("bugfix is missing root-cause summary/evidence in state")
        if not passed(str(gates.get("rootCause", ""))):
            errors.append("bugfix has no passing rootCause gate")

    review = state.get("reviewStages", {})
    spec = review.get("specCompliance", {}) if isinstance(review, dict) else {}
    quality = review.get("codeQuality", {}) if isinstance(review, dict) else {}
    spec_status = str(spec.get("status", "")) if isinstance(spec, dict) else ""
    quality_status = str(quality.get("status", "")) if isinstance(quality, dict) else ""
    if quality_status and quality_status != "BLOCKED" and not passed(spec_status):
        errors.append("code quality review is recorded before passing spec compliance review")
    if stage in REVIEW_ENFORCEMENT_STAGES:
        if not passed(spec_status):
            errors.append("review stage is missing passing spec compliance review")
        if not passed(quality_status):
            errors.append("review stage is missing passing code quality review")

    branch_finish = state.get("branchFinish", {})
    if stage in {"BRANCH_FINISH", "SESSION_SAVED", "DEPLOYED"}:
        if not isinstance(branch_finish, dict) or not branch_finish.get("mode"):
            errors.append("branch finish stage is missing PR/merge/keep/discard mode")
        if not isinstance(branch_finish, dict) or not branch_finish.get("verification"):
            errors.append("branch finish stage is missing fresh verification evidence")

    if stage in EXPERIMENT_ENFORCEMENT_STAGES:
        metric = experiment.get("metric", {}) if isinstance(experiment.get("metric", {}), dict) else {}
        program_path = experiment.get("programPath") or ".pfo/EXPERIMENT_PROGRAM.md"
        results_path = experiment.get("resultsPath") or ".pfo/EXPERIMENTS.tsv"
        if not (project / program_path).is_file():
            errors.append("experiment loop is missing .pfo/EXPERIMENT_PROGRAM.md")
        if not (project / results_path).is_file():
            errors.append("experiment loop is missing .pfo/EXPERIMENTS.tsv")
        if not metric.get("name") or metric.get("direction") not in {"lower", "higher"}:
            errors.append("experiment loop is missing primary metric name/direction")
        if not experiment.get("budgetSeconds"):
            errors.append("experiment loop is missing fixed budget seconds")
        if stage == "EXPERIMENT_EVALUATED":
            last_run = experiment.get("lastRun", {}) if isinstance(experiment.get("lastRun", {}), dict) else {}
            if last_run.get("status") not in {"keep", "discard", "crash"}:
                errors.append("experiment loop is missing keep/discard/crash decision")
            if str(gates.get("experimentDecision", "")) not in PASS_STATUSES:
                errors.append("experiment loop has no passing experimentDecision gate")

    if stage in NEXT_STEP_APPROVAL_STAGES:
        steering = state.get("humanSteering", {}) if isinstance(state.get("humanSteering", {}), dict) else {}
        if not (project / "NEXT_STEP.md").is_file():
            errors.append("implementation started without NEXT_STEP.md")
        if not passed(str(gates.get("nextStepApproval", ""))):
            errors.append("implementation started without passing nextStepApproval gate")
        if steering.get("approvalStatus") not in {"APPROVED", "CONSUMED"}:
            errors.append("implementation started without recorded human steering approval")

    return errors


def self_check() -> None:
    checks = {
        "docs/templates/BUILD_PLAN.md": EXECUTABLE_TASK_REQUIREMENTS,
        "docs/templates/NEXT_STEP.md": ["Decision Needed", "Visible Roadmap", "Recommended Next Step"],
        "docs/SUPERPOWERS_INTEGRATION.md": ["Engineering Discipline v2", "source of truth"],
        "scripts/pfo.py": ["tdd-evidence", "root-cause", "review-stage", "finish-branch"],
        "docs/templates/pfo/VERIFICATION_CONTRACT.json": ["passFailParser", "requiredArtifacts"],
        "docs/AUTORESEARCH_INTEGRATION.md": ["fixed budget", "keep/discard"],
        "hooks/review-before-commit.py": ["validate_plan_quality.py"],
    }
    for rel, tokens in checks.items():
        path = ROOT / rel
        if not path.is_file():
            fail(f"missing self-check file: {rel}")
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing Engineering Discipline v2 token: {token}")
    print("OK: Engineering Discipline v2 self-check passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Engineering Discipline v2 plan and gate quality.")
    parser.add_argument("project", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--self-check", action="store_true", help="Validate PFO's built-in Engineering Discipline v2 wiring.")
    args = parser.parse_args()

    if args.self_check:
        self_check()
        return

    project = args.project.resolve()
    errors = []
    errors.extend(validate_build_plan(project))
    errors.extend(validate_state_gates(project))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: Engineering Discipline v2 gates passed for {project}")


if __name__ == "__main__":
    main()
