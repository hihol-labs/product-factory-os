#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

from pfo_alias_targets import ALIAS_DOCUMENT_NAMES, missing_alias_targets, missing_targets_for_text

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PFO_TEMPLATE_DIR = ROOT / "docs" / "templates" / "pfo"
EXISTING_ALIAS_TEMPLATE_DIR = ROOT / "docs" / "templates" / "existing"
MANAGED_START = "<!-- PFO_PROJECT_RUNTIME_START -->"
MANAGED_END = "<!-- PFO_PROJECT_RUNTIME_END -->"
OPTIONAL_EXISTING_ALIAS_REFERENCES = {
    "MASTER_CONTEXT.md": [
        ("Active project plan", "CURRENT_PLAN.md"),
        ("Historical launch context", "LAUNCH_PLAN.md"),
        ("Existing project analysis", "PFO_EXISTING_PROJECT_ANALYSIS.json"),
        ("PFO report", "PFO_REPORT.md"),
    ],
    "ARCHITECTURE.md": [
        ("Existing project analysis", "PFO_EXISTING_PROJECT_ANALYSIS.json"),
        ("Project architecture notes", "docs/PROJECT_ARCHITECTURE.md"),
        ("Implementation plan", "docs/IMPLEMENTATION_PLAN.md"),
    ],
    "TASKS.md": [
        ("Active project plan", "CURRENT_PLAN.md"),
        ("Implementation plan", "docs/IMPLEMENTATION_PLAN.md"),
        ("Contract gate status", "PFO_CONTRACT_GATE.json"),
    ],
    "PROGRESS.md": [
        ("Active project plan", "CURRENT_PLAN.md"),
        ("PFO report", "PFO_REPORT.md"),
        ("Contract gate status", "PFO_CONTRACT_GATE.json"),
    ],
    "TESTING.md": [
        ("Active gate checklist", "CURRENT_PLAN.md"),
        ("PFO report", "PFO_REPORT.md"),
        ("Contract gate status", "PFO_CONTRACT_GATE.json"),
    ],
}


def load_alias_documents() -> dict[str, str]:
    return {
        name: (ROOT / "docs" / "templates" / name).read_text(encoding="utf-8")
        for name in ALIAS_DOCUMENT_NAMES
    }


def load_existing_alias_documents(project: Path) -> dict[str, str]:
    documents = {
        name: (EXISTING_ALIAS_TEMPLATE_DIR / name).read_text(encoding="utf-8")
        for name in ALIAS_DOCUMENT_NAMES
    }
    for name, references in OPTIONAL_EXISTING_ALIAS_REFERENCES.items():
        lines = [f"- {label}: `{rel}`" for label, rel in references if (project / rel).exists()]
        if not lines:
            continue
        block = "\n## Existing Project Sources\n\n" + "\n".join(lines) + "\n"
        documents[name] = documents[name].replace("\n## Rule\n", block + "\n## Rule\n")
    return documents


GENERATED_PLAN_FILES = [
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
    "NEXT_STEP.md",
    "TEST_PLAN.md",
    "QUALITY_GATES.md",
]

IGNORED = {
    ".agents",
    ".claude",
    ".codex",
    "product-factory-os",
    "idea-to-deploy",
}


def project_dirs(workspace: Path) -> list[Path]:
    result = []
    for path in sorted(workspace.iterdir()):
        try:
            is_dir = path.is_dir()
        except PermissionError:
            continue
        if not is_dir or path.name in IGNORED or path.name.startswith("."):
            continue
        result.append(path)
    return result


def is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except PermissionError:
        return False


def is_dir(path: Path) -> bool:
    try:
        return path.is_dir()
    except PermissionError:
        return False


def default_human_steering() -> dict:
    return {
        "approvalRequired": True,
        "approvalStatus": "PENDING",
        "approvedBy": "",
        "approvedAt": "",
        "lastPrompt": "Ask the user to confirm, change, or stop before implementation.",
        "lastIterationSummary": "Project is adopted into Product Factory OS.",
        "recommendedNextStep": "Choose and approve the next task-specific implementation step.",
        "alternatives": [
            "Approve the recommended next task.",
            "Change scope or priority.",
            "Pause and review project state."
        ],
        "pendingQuestions": [
            "Do you approve the recommended next step?",
            "Should scope or priority change before implementation?"
        ],
        "visibleRoadmap": [],
        "completedIterations": [],
    }


def backfill_human_steering(path: Path) -> None:
    state_path = path / ".codex-memory" / "STATE.json"
    if not state_path.is_file():
        return
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    gate_results = state.setdefault("gateResults", {})
    gate_results.setdefault("nextStepApproval", "PENDING")
    if not gate_results.get("nextStepApproval"):
        gate_results["nextStepApproval"] = "PENDING"
    steering = state.setdefault("humanSteering", default_human_steering())
    if not isinstance(steering, dict):
        steering = default_human_steering()
        state["humanSteering"] = steering
    for key, value in default_human_steering().items():
        steering.setdefault(key, value)
    if not steering.get("approvalStatus"):
        steering["approvalStatus"] = "PENDING"
    if steering.get("approvalStatus") == "PENDING":
        steering["approvalRequired"] = True
    if not steering.get("recommendedNextStep"):
        steering["recommendedNextStep"] = default_human_steering()["recommendedNextStep"]
    artifacts = set(state.get("artifacts", []))
    artifacts.add("NEXT_STEP.md")
    state["artifacts"] = sorted(artifacts)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def has_pfo_contracts(path: Path) -> bool:
    for name in [
        "PROJECT_CONTRACT.md",
        "DATA_POLICY.md",
        "GOLDEN_FLOWS.md",
        "FORBIDDEN_CHANGES.md",
        "FALLBACK_POLICY.md",
        "SCOPE_LOCK.md",
        "PERMISSION_MATRIX.md",
        "PERMISSION_MATRIX.json",
        "LEARNING_PROMOTION_GATE.md",
        "EXECUTION_POLICY.json",
        "UNIT_CONTEXT_MANIFEST.json",
        "VERIFICATION_CONTRACT.json",
        "TOOL_CAPABILITY_REGISTRY.json",
    ]:
        if not (path / ".pfo" / name).is_file():
            return False
    return True


def is_generated_pfo_project(path: Path) -> bool:
    return (path / ".pfo-starter.json").is_file()


def has_full_pfo_runtime(path: Path) -> bool:
    required = [
        path / "AGENTS.md",
        path / "CODEX.md",
        path / ".codex-memory" / "MEMORY.md",
        path / ".codex-memory" / "STATE.json",
        path / ".codex-memory" / "events.jsonl",
        path / "PFO_REPORT.md",
        path / "NEXT_STEP.md",
    ]
    if is_generated_pfo_project(path):
        required.extend(path / name for name in GENERATED_PLAN_FILES)
    else:
        required.extend(
            [
                path / "PFO_EXISTING_PROJECT_ANALYSIS.json",
                path / "PFO_CONTRACT_GATE.json",
            ]
        )
    return all(item.is_file() for item in required) and has_pfo_contracts(path) and not missing_alias_targets(path)


def status_for(path: Path) -> dict[str, object]:
    return {
        "project": path.name,
        "path": str(path),
        "hasAgents": is_file(path / "AGENTS.md"),
        "hasCodex": is_file(path / "CODEX.md"),
        "hasMemory": is_file(path / ".codex-memory" / "MEMORY.md"),
        "hasState": is_file(path / ".codex-memory" / "STATE.json"),
        "hasPfoContracts": has_pfo_contracts(path),
        "hasFullPfoRuntime": has_full_pfo_runtime(path),
        "hasPrd": is_file(path / "PRD.md"),
        "hasArchitecture": is_file(path / "PROJECT_ARCHITECTURE.md"),
        "hasImplementationPlan": is_file(path / "IMPLEMENTATION_PLAN.md"),
        "hasProductBlueprint": is_file(path / "PRODUCT_BLUEPRINT.md"),
        "hasBuildPlan": is_file(path / "BUILD_PLAN.md"),
        "hasExecutionGraph": is_file(path / "EXECUTION_GRAPH.md"),
        "hasAliasDocs": all(is_file(path / name) for name in ALIAS_DOCUMENT_NAMES),
        "hasValidAliasTargets": not missing_alias_targets(path),
        "hasGit": is_dir(path / ".git"),
    }


def infer_existing_project_summary(path: Path) -> str:
    stack = []
    if (path / "package.json").is_file():
        stack.append("Node.js")
    if (path / "pnpm-lock.yaml").is_file():
        stack.append("pnpm")
    if (path / "turbo.json").is_file():
        stack.append("Turborepo")
    if (path / "apps").is_dir() and (path / "packages").is_dir():
        stack.append("monorepo")
    if (path / "pyproject.toml").is_file():
        stack.append("Python")
    suffix = f" Detected stack hints: {', '.join(stack)}." if stack else ""
    return "Adopted with minimal Product Factory OS state. Run `pfo analyze <project> --run-gates` before major work, and `pfo handoff <project>` before session transfer." + suffix


def project_runtime_block(path: Path, workspace: Path) -> str:
    return f"""{MANAGED_START}
## Product Factory OS Runtime

This existing project is adopted into Product Factory OS.

- Workspace: `{workspace}`
- Methodology: `{ROOT}`
- Project: `{path}`

Before implementation, Codex must enforce full PFO adoption automatically:

```bash
pfo adopt {path}
```

Then route work through `/task`, write `HANDOFF.md` before session or role transfer, update `.codex-memory/STATE.json`, and respect `.pfo/` contracts. Codex `/goal` mode is default-on for non-trivial work: create or continue the goal before implementation, and keep it active through gates, verification, and state-save. Project-local rules may add constraints, but they do not replace PFO gates, memory, or scope/data/degraded-mode contracts. Keep local rules short and earned: add them only for observed failures or hard external constraints.
{MANAGED_END}
"""


def upsert_managed_block(path: Path, title: str, block: str) -> None:
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if MANAGED_START in text and MANAGED_END in text:
            before = text.split(MANAGED_START, 1)[0].rstrip()
            after = text.split(MANAGED_END, 1)[1].lstrip()
            new_text = before + "\n\n" + block.rstrip() + "\n"
            if after:
                new_text += "\n" + after
        else:
            new_text = text.rstrip() + "\n\n" + block.rstrip() + "\n"
    else:
        new_text = f"# {title}\n\n" + block.rstrip() + "\n"
    path.write_text(new_text, encoding="utf-8")


def ensure_pfo_contracts(path: Path) -> None:
    pfo_dir = path / ".pfo"
    pfo_dir.mkdir(exist_ok=True)
    if not PFO_TEMPLATE_DIR.is_dir():
        return
    for source in PFO_TEMPLATE_DIR.iterdir():
        if not source.is_file() or source.suffix not in {".md", ".json"}:
            continue
        target = pfo_dir / source.name
        if not target.exists():
            shutil.copyfile(source, target)
        elif source.suffix == ".json":
            upgrade_json_contract(target, source)


def merge_missing(current: object, default: object) -> tuple[object, bool]:
    if not isinstance(current, dict) or not isinstance(default, dict):
        return current, False
    changed = False
    result = dict(current)
    for key, value in default.items():
        if key not in result:
            result[key] = value
            changed = True
            continue
        merged, child_changed = merge_missing(result[key], value)
        if child_changed:
            result[key] = merged
            changed = True
    return result, changed


def upgrade_json_contract(target: Path, source: Path) -> None:
    try:
        current = json.loads(target.read_text(encoding="utf-8"))
        default = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    merged, changed = merge_missing(current, default)
    if changed:
        target.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_alias_documents(path: Path) -> None:
    generated = is_generated_pfo_project(path)
    documents = load_alias_documents() if generated else load_existing_alias_documents(path)
    for name, text in documents.items():
        errors = missing_targets_for_text(path, name, text)
        if errors:
            if generated:
                continue
            fail("refusing to create alias document with missing target(s):\n" + "\n".join(f"- {item}" for item in errors))
        target = path / name
        if not target.exists():
            target.write_text(text, encoding="utf-8")
            continue
        current_errors = missing_targets_for_text(path, name, target.read_text(encoding="utf-8"))
        if current_errors:
            target.write_text(text, encoding="utf-8")


def methodology_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def mark_runtime_synced(path: Path, workspace: Path) -> None:
    state_path = path / ".codex-memory" / "STATE.json"
    if not state_path.is_file():
        return
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    generated = is_generated_pfo_project(path)
    alias_errors = missing_alias_targets(path)
    state["pfoRuntime"] = {
        "status": "ALIAS_TARGETS_BROKEN" if alias_errors else ("FULLY_BOOTSTRAPPED" if generated else "FULLY_ADOPTED"),
        "methodologyPath": str(ROOT),
        "workspace": str(workspace),
        "methodologyRevision": methodology_revision(),
        "mode": "automatic-workspace-runtime",
        "codexGoalMode": {
            "enabled": True,
            "defaultOn": True,
            "route": "/project -> /kickstart" if generated else "/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save",
        },
        "aliasTargetStatus": "BROKEN" if alias_errors else "PASS",
        "aliasTargetErrors": alias_errors,
    }
    existing = state.setdefault("existingProject", {})
    if isinstance(existing, dict) and not generated:
        existing["isExistingProject"] = True
        existing["currentTaskRoute"] = (
            "/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save"
        )
    artifacts = set(state.get("artifacts", []))
    artifacts.update(
        [
            "AGENTS.md",
            "CODEX.md",
            ".codex-memory/MEMORY.md",
            ".codex-memory/STATE.json",
            ".codex-memory/events.jsonl",
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
            ".pfo/UNIT_CONTEXT_MANIFEST.json",
            ".pfo/VERIFICATION_CONTRACT.json",
            ".pfo/TOOL_CAPABILITY_REGISTRY.json",
            *ALIAS_DOCUMENT_NAMES,
        ]
    )
    state["artifacts"] = sorted(artifacts)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_adoption_files(path: Path, workspace: Path) -> None:
    codex = path / "CODEX.md"
    agents = path / "AGENTS.md"
    memory_dir = path / ".codex-memory"
    memory = memory_dir / "MEMORY.md"
    events = memory_dir / "events.jsonl"
    state = memory_dir / "STATE.json"
    block = project_runtime_block(path, workspace)

    upsert_managed_block(codex, "CODEX", block)
    upsert_managed_block(agents, "AGENTS", block)
    ensure_pfo_contracts(path)

    memory_dir.mkdir(exist_ok=True)
    if not memory.exists():
        memory.write_text(
            f"""---
title: "Memory"
project: "{path.name}"
tags:
  - pfo/memory
  - pfo/project
aliases:
  - "Project Memory"
---

# Memory

- adopted: {path.name} connected to Product Factory OS -> STATE.json

## Obsidian Links

- [[STATE]]
- [[LEARNINGS]]
- [[HANDOFF]]
""",
            encoding="utf-8",
        )
    if not events.exists():
        events.write_text("", encoding="utf-8")
    if not state.exists():
        state.write_text(
            json.dumps(
                {
                    "sessionState": "ADOPTED",
                    "currentStage": "IDLE",
                    "intent": "Existing project adopted into Product Factory OS.",
                    "classification": {
                        "productType": "",
                        "domain": "",
                        "complexity": "",
                        "requiredModules": [],
                        "infrastructure": [],
                    },
                    "architecture": {
                        "pattern": "",
                        "backend": "",
                        "frontend": "",
                        "database": "",
                        "auth": "",
                        "deployment": "",
                    },
                    "existingProject": {
                        "isExistingProject": True,
                        "detectedStack": [],
                        "availableCommands": [],
                        "currentTaskRoute": "",
                        "lastAnalysisSummary": infer_existing_project_summary(path),
                    },
                    "currentPhase": "",
                    "currentNode": "",
                    "currentUnit": {
                        "id": "",
                        "goal": "",
                        "status": "",
                        "owner": "",
                        "startedAt": "",
                        "completedAt": "",
                    },
                    "unitContextManifest": {
                        "path": ".pfo/UNIT_CONTEXT_MANIFEST.json",
                        "version": 1,
                        "unitId": "",
                        "requiredInputs": [],
                        "allowedWriteAreas": [],
                        "forbiddenChanges": [],
                        "dependencies": [],
                        "verificationCommands": [],
                        "gates": [],
                        "recovery": "",
                    },
                    "handoff": {
                        "path": "HANDOFF.md",
                        "status": "",
                        "fromRole": "",
                        "toRole": "",
                        "reason": "",
                        "createdAt": "",
                        "nextAction": "",
                    },
                    "gateResults": {
                        "ideaGate": "",
                        "marketValidation": "",
                        "strategy": "",
                        "feedbackLoop": "",
                        "funnel": "",
                        "architecture": "",
                        "tests": "",
                        "review": "",
                        "tddRed": "",
                        "tddGreen": "",
                        "tddRefactor": "",
                        "rootCause": "",
                        "specComplianceReview": "",
                        "codeQualityReview": "",
                        "branchFinish": "",
                        "nextStepApproval": "",
                        "handoff": "",
                        "security": "",
                        "dependencies": "",
                        "hardening": "",
                        "assetExtraction": "",
                        "contentPipeline": "",
                        "experimentSetup": "",
                        "experimentMetric": "",
                        "experimentDecision": "",
                        "executionPolicy": "",
                        "permissionMatrix": "",
                        "verificationContract": "",
                        "learningPromotion": "",
                        "toolCapabilityRegistry": "",
                        "deploymentReadiness": "",
                    },
                    "verificationHistory": [],
                    "tddEvidence": {
                        "red": "",
                        "green": "",
                        "refactor": "",
                        "lastRecordedAt": "",
                    },
                    "rootCause": {
                        "status": "",
                        "summary": "",
                        "evidence": "",
                        "hypothesis": "",
                        "recordedAt": "",
                    },
                    "reviewStages": {
                        "specCompliance": {"status": "", "evidence": "", "recordedAt": ""},
                        "codeQuality": {"status": "", "evidence": "", "recordedAt": ""},
                    },
                    "branchFinish": {
                        "status": "",
                        "mode": "",
                        "verification": "",
                        "remoteBranch": "",
                        "prUrl": "",
                        "cleanupDecision": "",
                        "recordedAt": "",
                    },
                    "humanSteering": default_human_steering(),
                    "dispatchJournal": [],
                    "decisionLog": [],
                    "capturedNotes": [],
                    "artifactHashes": {},
                    "lastSuccessfulState": "ADOPTED",
                    "artifacts": [
                        "AGENTS.md",
                        "CODEX.md",
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
                        ".pfo/UNIT_CONTEXT_MANIFEST.json",
                        ".pfo/VERIFICATION_CONTRACT.json",
                        ".pfo/TOOL_CAPABILITY_REGISTRY.json",
                        ".codex-memory/MEMORY.md",
                        ".codex-memory/STATE.json",
                        ".codex-memory/events.jsonl",
                        "MASTER_CONTEXT.md",
                        "ARCHITECTURE.md",
                        "TASKS.md",
                        "PROGRESS.md",
                        "TESTING.md",
                        "NEXT_STEP.md",
                    ],
                    "completedModules": [],
                    "failedValidations": [],
                    "driftChecks": [],
                    "recoveryState": {
                        "status": "",
                        "reason": "",
                        "retryCount": 0,
                        "nextRepairAction": "",
                    },
                    "telemetry": {
                        "unitCount": 0,
                        "verificationCount": 0,
                        "lastCommand": "",
                        "lastDurationSeconds": None,
                        "tokenNotes": "",
                        "costNotes": "",
                    },
                    "knowledgeLog": [],
                    "learningProposals": [],
                    "eventLog": {
                        "path": ".codex-memory/events.jsonl",
                        "lastEventId": "",
                        "lastEventAt": "",
                    },
                    "executionPolicy": {
                        "path": ".pfo/EXECUTION_POLICY.json",
                        "status": "",
                    },
                    "permissionMatrix": {
                        "path": ".pfo/PERMISSION_MATRIX.json",
                        "humanPath": ".pfo/PERMISSION_MATRIX.md",
                        "status": "",
                    },
                    "verificationContract": {
                        "path": ".pfo/VERIFICATION_CONTRACT.json",
                        "status": "",
                    },
                    "learningPromotionGate": {
                        "path": ".pfo/LEARNING_PROMOTION_GATE.md",
                        "status": "",
                    },
                    "toolCapabilityRegistry": {
                        "path": ".pfo/TOOL_CAPABILITY_REGISTRY.json",
                        "status": "",
                    },
                    "experimentLoop": {
                        "status": "",
                        "tag": "",
                        "programPath": ".pfo/EXPERIMENT_PROGRAM.md",
                        "resultsPath": ".pfo/EXPERIMENTS.tsv",
                        "metric": {"name": "", "direction": "lower", "bestValue": None, "bestRunId": ""},
                        "budgetSeconds": None,
                        "runCommand": "",
                        "baselineCommand": "",
                        "allowedWriteAreas": [],
                        "protectedFiles": [],
                        "baselineRecorded": False,
                        "lastRun": {},
                    },
                    "briefArtifacts": [],
                    "worktreeIsolation": {
                        "enabled": False,
                        "strategy": "",
                        "activeBranch": "",
                        "activeWorktree": "",
                        "mergeStatus": "",
                    },
                    "blockers": [],
                    "nextAction": "PFO is active. Review NEXT_STEP.md and approve the next major implementation step before build work.",
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    next_step_template = ROOT / "docs" / "templates" / "NEXT_STEP.md"
    if next_step_template.is_file() and not (path / "NEXT_STEP.md").exists():
        (path / "NEXT_STEP.md").write_text(next_step_template.read_text(encoding="utf-8"), encoding="utf-8")
    backfill_human_steering(path)
    ensure_alias_documents(path)
    mark_runtime_synced(path, workspace)


def run_child(command: list[str], quiet: bool) -> int:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=quiet,
        check=False,
    )
    if result.returncode != 0 and quiet:
        sys.stderr.write(result.stdout + result.stderr)
    return result.returncode


def analyze_project(project: Path, run_gates: bool, timeout: int, report: bool, quiet: bool) -> int:
    analyze_args = [
        sys.executable,
        str(ROOT / "scripts" / "existing_project_analyzer.py"),
        str(project),
        "--timeout",
        str(timeout),
    ]
    if run_gates:
        analyze_args.append("--run-gates")
    code = run_child(analyze_args, quiet)
    if code != 0:
        return code
    if report:
        return run_child([sys.executable, str(ROOT / "scripts" / "pfo_report.py"), str(project)], quiet)
    return 0


def plan_generated_project(project: Path, report: bool, quiet: bool) -> int:
    code = run_child([sys.executable, str(ROOT / "scripts" / "pfo.py"), "plan", str(project)], quiet)
    if code != 0:
        return code
    if report:
        return run_child([sys.executable, str(ROOT / "scripts" / "pfo_report.py"), str(project)], quiet)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Check or bootstrap Product Factory OS adoption for workspace projects.")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    parser.add_argument("--project", type=Path, help="Check or adopt a single existing project root.")
    parser.add_argument("--write", action="store_true", help="Create AGENTS.md, CODEX.md, .pfo/, and .codex-memory/ where missing.")
    parser.add_argument("--analyze", action="store_true", help="Run existing-project analysis after adoption.")
    parser.add_argument("--report", action="store_true", help="Write PFO_REPORT.md after analysis.")
    parser.add_argument("--run-gates", action="store_true", help="Run detected project gates during analysis.")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a table.")
    args = parser.parse_args()

    projects = [args.project.resolve()] if args.project else project_dirs(args.workspace)
    if args.write:
        for project in projects:
            write_adoption_files(project, args.workspace.resolve())
    if args.analyze:
        for project in projects:
            if is_generated_pfo_project(project):
                code = plan_generated_project(project, args.report, args.json)
            else:
                code = analyze_project(project, args.run_gates, args.timeout, args.report, args.json)
            if code != 0:
                fail(f"full PFO adoption failed for {project}")

    statuses = [status_for(project) for project in projects]

    if args.json:
        print(json.dumps(statuses, indent=2, ensure_ascii=False))
        return

    print("Project adoption status")
    print("-----------------------")
    for item in statuses:
        flags = []
        flags.append("AGENTS" if item["hasAgents"] else "no-AGENTS")
        flags.append("CODEX" if item["hasCodex"] else "no-CODEX")
        flags.append("memory" if item["hasMemory"] else "no-memory")
        flags.append("state" if item["hasState"] else "no-state")
        flags.append("contracts" if item["hasPfoContracts"] else "no-contracts")
        flags.append("aliases" if item["hasAliasDocs"] else "no-aliases")
        flags.append("alias-targets" if item["hasValidAliasTargets"] else "broken-alias-targets")
        flags.append("full-runtime" if item["hasFullPfoRuntime"] else "partial-runtime")
        flags.append("pfo-docs" if item["hasPrd"] and item["hasArchitecture"] and item["hasImplementationPlan"] and item["hasProductBlueprint"] and item["hasBuildPlan"] and item["hasExecutionGraph"] else "pfo-docs-partial")
        print(f"{item['project']}: {', '.join(flags)}")

    missing = [
        item for item in statuses
        if not item["hasAgents"]
        or not item["hasCodex"]
        or not item["hasMemory"]
        or not item["hasState"]
        or not item["hasPfoContracts"]
        or not item["hasAliasDocs"]
        or not item["hasValidAliasTargets"]
        or not item["hasFullPfoRuntime"]
    ]
    if missing:
        print("\nRun with --write --analyze --report to enforce full PFO runtime files for incomplete projects.")
        sys.exit(2)


if __name__ == "__main__":
    main()
