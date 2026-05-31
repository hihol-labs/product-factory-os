#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import re
import sys
import shutil
import subprocess

from pfo_alias_targets import ALIAS_DOCUMENT_NAMES, missing_targets_for_text

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent


def load_alias_documents() -> dict[str, str]:
    return {
        name: (ROOT / "docs" / "templates" / name).read_text(encoding="utf-8")
        for name in ALIAS_DOCUMENT_NAMES
    }


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "new-product"


def write_once(path: Path, text: str) -> None:
    if path.exists():
        return
    path.write_text(text, encoding="utf-8")


def write_alias_documents_if_valid(project: Path) -> None:
    for name, text in load_alias_documents().items():
        if missing_targets_for_text(project, name, text):
            continue
        write_once(project / name, text)


def state_json(project_name: str, idea: str, methodology: Path) -> str:
    starter = select_starter(idea)
    return json.dumps(
        {
            "sessionState": "BOOTSTRAPPED",
            "currentStage": "IDLE",
            "intent": idea,
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
                "isExistingProject": False,
                "detectedStack": [],
                "availableCommands": [],
                "currentTaskRoute": "",
                "lastAnalysisSummary": "",
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
                "nextStepApproval": "PENDING",
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
            "humanSteering": {
                "approvalRequired": True,
                "approvalStatus": "PENDING",
                "approvedBy": "",
                "approvedAt": "",
                "lastPrompt": "Ask the user to confirm, change, or stop before implementation.",
                "lastIterationSummary": "Project runtime is bootstrapped. Planning and first implementation step need user steering.",
                "recommendedNextStep": "Review the generated roadmap and approve the first implementation slice.",
                "alternatives": [
                    "Approve the recommended first implementation slice.",
                    "Change MVP scope before implementation.",
                    "Pause and review planning artifacts."
                ],
                "pendingQuestions": [
                    "Do you approve the recommended next step?",
                    "Should scope or priority change before implementation?"
                ],
                "visibleRoadmap": [],
                "completedIterations": [],
            },
            "dispatchJournal": [],
            "decisionLog": [],
            "capturedNotes": [],
            "artifactHashes": {},
            "lastSuccessfulState": "BOOTSTRAPPED",
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
            "nextAction": "Ask product steering questions, show the visible roadmap, then request approval before the first implementation slice.",
            "project": project_name,
            "methodology": str(methodology),
            "starter": starter["id"],
            "productTypeHint": starter["productType"],
            "pfoRuntime": {
                "status": "FULLY_BOOTSTRAPPED",
                "methodologyPath": str(methodology),
                "mode": "automatic-workspace-runtime",
            },
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def select_starter(idea: str) -> dict:
    lowered = idea.lower()
    if re.search(r"mini app|мини|embedded", lowered):
        starter_id = "mini-app-vue"
    elif re.search(r"api|backend|webhook|вебхук|эндпо", lowered):
        starter_id = "api-fastapi"
    elif re.search(r"telegram bot|discord bot|\bbot\b|бот", lowered):
        starter_id = "bot-aiogram"
    elif re.search(r"saas|подпис", lowered):
        starter_id = "saas-fastapi-vue"
    elif re.search(r"landing|лендинг|сайт", lowered):
        starter_id = "landing-vite"
    elif re.search(r"cli|терминал|command", lowered):
        starter_id = "cli-typer"
    elif re.search(r"парсер|scraper|crawl|мониторинг цен", lowered):
        starter_id = "scraper-python"
    elif re.search(r"shop|store|магазин|e-?commerce", lowered):
        starter_id = "ecommerce-fastapi-vue"
    elif re.search(r"automation|автоматизац|internal", lowered):
        starter_id = "internal-automation"
    else:
        starter_id = "saas-fastapi-vue"
    starter_path = ROOT / "starters" / starter_id / "STARTER.json"
    return json.loads(starter_path.read_text(encoding="utf-8"))


def scaffold(project: Path, starter: dict) -> None:
    for folder in starter.get("folders", []):
        (project / folder).mkdir(parents=True, exist_ok=True)
    pfo_dir = project / ".pfo"
    pfo_dir.mkdir(exist_ok=True)
    pfo_templates = ROOT / "docs" / "templates" / "pfo"
    if pfo_templates.is_dir():
        for source in pfo_templates.iterdir():
            if not source.is_file() or source.suffix not in {".md", ".json"}:
                continue
            target = pfo_dir / source.name
            if not target.exists():
                shutil.copyfile(source, target)
    write_once(project / ".pfo-starter.json", json.dumps(starter, indent=2, ensure_ascii=False) + "\n")
    write_once(project / ".env.example", "# Product Factory OS environment variables\n")
    workflow_dir = project / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    ci_source = ROOT / "templates" / "generated-ci" / "validate.yml"
    if ci_source.is_file() and not (workflow_dir / "validate.yml").exists():
        shutil.copyfile(ci_source, workflow_dir / "validate.yml")
    just_source = ROOT / "templates" / "generated-ci" / "justfile"
    if just_source.is_file() and not (project / "justfile").exists():
        shutil.copyfile(just_source, project / "justfile")
    starter_files = ROOT / "starters" / starter["id"] / "files"
    if starter_files.is_dir():
        for source in starter_files.rglob("*"):
            if source.is_file():
                target = project / source.relative_to(starter_files)
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copyfile(source, target)
    write_once(
        project / "PFO_REPORT.md",
        "# Product Factory OS Report\n\nCURRENT STATE: BOOTSTRAPPED\n\nNEXT ACTION: Run `/project -> /kickstart`.\n",
    )
    next_step_template = ROOT / "docs" / "templates" / "NEXT_STEP.md"
    if next_step_template.is_file():
        write_once(project / "NEXT_STEP.md", next_step_template.read_text(encoding="utf-8"))


def run_auto_plan(project: Path) -> int:
    plan = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "pfo.py"), "plan", str(project)],
        cwd=ROOT,
        text=True,
        check=False,
    )
    if plan.returncode != 0:
        return plan.returncode
    report = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "pfo_report.py"), str(project)],
        cwd=ROOT,
        text=True,
        check=False,
    )
    return report.returncode


def codex_md(project_name: str, idea: str, methodology: Path) -> str:
    return f"""# CODEX

This project is automatically governed by Product Factory OS from:

```text
{methodology}
```

## Project

- Name: {project_name}
- Initial idea: {idea or "not captured yet"}

## Mandatory Route

New product work starts from:

```text
/project -> /kickstart
```

Product Factory OS must create and maintain:

```text
.pfo/PROJECT_CONTRACT.md
.pfo/DATA_POLICY.md
.pfo/GOLDEN_FLOWS.md
.pfo/FORBIDDEN_CHANGES.md
.pfo/FALLBACK_POLICY.md
.pfo/SCOPE_LOCK.md
.pfo/EXECUTION_POLICY.json
.pfo/PERMISSION_MATRIX.md
.pfo/PERMISSION_MATRIX.json
.pfo/VERIFICATION_CONTRACT.json
.pfo/LEARNING_PROMOTION_GATE.md
.pfo/TOOL_CAPABILITY_REGISTRY.json
MASTER_CONTEXT.md
ARCHITECTURE.md
TASKS.md
PROGRESS.md
TESTING.md
DISCOVERY.md
IDEA_SCORECARD.md
VALIDATION_PLAN.md
FEEDBACK_LOG.md
ITERATION_REVIEW.md
FUNNEL_MODEL.md
ASSET_REGISTER.md
CONTENT_BACKLOG.md
PRD.md
PRODUCT_BLUEPRINT.md
PROJECT_ARCHITECTURE.md
PHASE_CONTEXT.md
BUILD_PLAN.md
EXECUTION_GRAPH.md
NEXT_STEP.md
IMPLEMENTATION_PLAN.md
.pfo/UNIT_CONTEXT_MANIFEST.json
HANDOFF.md when transfer is in scope
.codex-memory/STATE.json
.codex-memory/LEARNINGS.md
```

## Operating Contract

- Voice or natural-language commands are accepted as the primary interface.
- Codex performs routing automatically.
- Score ideas before broad build scope in `IDEA_SCORECARD.md`.
- Validate risky assumptions in `VALIDATION_PLAN.md`.
- Broad market-facing scope requires evidence quality: real conversations, past behavior evidence, contradicting evidence, and BUILD truth conditions.
- Use `MARKET_BRIEF.md` for adversarial discovery when market or competitor risk matters.
- Define activation, retention, PMF signals, and false-positive traction in `FUNNEL_MODEL.md` or `GO_TO_MARKET.md` before MVP launch.
- Use `LAUNCH_MATURITY_GATE.md` and `SCALE_MOAT_REGISTER.md` only when launch, scale, enterprise, or defensibility is in scope.
- Capture implementation decisions in `PHASE_CONTEXT.md` before detailed execution planning.
- Update `NEXT_STEP.md` and record `gateResults.nextStepApproval=PASSED` before major implementation starts.
- Build `.pfo/UNIT_CONTEXT_MANIFEST.json` before autonomous or delegated execution.
- Respect `.pfo/EXECUTION_POLICY.json` and `.pfo/PERMISSION_MATRIX.md` before commands, writes, external APIs, push, deploy, or secret access.
- Validate `.pfo/PERMISSION_MATRIX.json` with `pfo permission-check .`.
- Validate `.pfo/TOOL_CAPABILITY_REGISTRY.json` with `pfo tool-registry .`.
- Keep `.pfo/VERIFICATION_CONTRACT.json` current for every active execution unit.
- Write `HANDOFF.md` before switching sessions, roles, delegated agents, AFK execution, compaction, or recovery.
- Behavior changes require TDD red/green evidence unless explicitly waived by project owner.
- Bugfixes require root-cause evidence before implementation.
- Reviews run in two stages: spec compliance first, code quality second.
- Implementation follows `EXECUTION_GRAPH.md` node by node.
- Every task must respect `.pfo/SCOPE_LOCK.md`.
- Real production data must follow `.pfo/DATA_POLICY.md`.
- Fallbacks must follow `.pfo/FALLBACK_POLICY.md` and must not silently replace real output.
- Tests, review, security, dependency, and hardening gates block deployment when they fail.
- Golden flows in `.pfo/GOLDEN_FLOWS.md` block deployment when touched and unverified.
- Verification fails closed when evidence is missing or ambiguous.
- Product iterations must reference feedback, metrics, validation evidence, or a recorded strategy decision.
- Reusable solutions should be promoted into `ASSET_REGISTER.md`; publishable lessons go into `CONTENT_BACKLOG.md`.
- Branch finish must record a PR, merge, keep, or discard decision with verification evidence.
- Extract durable decisions, lessons, patterns, and surprises into `.codex-memory/LEARNINGS.md`.
- Promote repeated errors only through `.pfo/LEARNING_PROMOTION_GATE.md`.
- Record significant commands, gates, approvals, verification, errors, and learning events in `.codex-memory/events.jsonl`.
- Use `pfo export . --target obsidian` when a local Obsidian knowledge graph is needed; keep `.pfo-integrations/obsidian/` generated.
- Session state is saved after significant milestones.

## Memory

Update `.codex-memory/STATE.json` and `.codex-memory/MEMORY.md` after significant work.
"""


def agents_md(project_name: str, idea: str, methodology: Path) -> str:
    return f"""# AGENTS

This project is automatically governed by Product Factory OS.

- Project: {project_name}
- Initial idea: {idea or "not captured yet"}
- Methodology: {methodology}

Use `/project -> /kickstart` for new product work and `/task` routes for ongoing changes. Require `NEXT_STEP.md` plus next-step approval before major implementation. Write `HANDOFF.md` before session or role transfer. Respect `.pfo/` contracts, update `.codex-memory/STATE.json`, and run the smallest relevant verification before finishing.
"""


def memory_md(project_name: str, idea: str) -> str:
    summary = idea or "Product Factory OS project bootstrapped."
    return f"""---
title: "Memory"
project: "{project_name}"
tags:
  - pfo/memory
  - pfo/project
aliases:
  - "Project Memory"
---

# Memory

- bootstrap: {project_name} initialized for Product Factory OS -> STATE.json

## Initial Intent

{summary}

## Obsidian Links

- [[STATE]]
- [[LEARNINGS]]
- [[HANDOFF]]
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap a new project under Product Factory OS.")
    parser.add_argument("name", help="Project directory name or product name.")
    parser.add_argument("--idea", default="", help="Voice transcript or natural-language product idea.")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE, help="Workspace directory.")
    parser.add_argument("--no-plan", action="store_true", help="Only bootstrap runtime files; skip automatic planning.")
    args = parser.parse_args()

    project_name = slugify(args.name)
    workspace = args.workspace.resolve()
    methodology = workspace / "product-factory-os"
    if not methodology.exists():
        methodology = ROOT

    project = workspace / project_name
    project.mkdir(parents=True, exist_ok=True)
    memory_dir = project / ".codex-memory"
    memory_dir.mkdir(exist_ok=True)
    starter = select_starter(args.idea)

    write_once(project / "CODEX.md", codex_md(project_name, args.idea, methodology))
    write_once(project / "AGENTS.md", agents_md(project_name, args.idea, methodology))
    write_once(memory_dir / "MEMORY.md", memory_md(project_name, args.idea))
    write_once(memory_dir / "events.jsonl", "")
    write_once(memory_dir / "STATE.json", state_json(project_name, args.idea, methodology))
    scaffold(project, starter)
    if not args.no_plan:
        code = run_auto_plan(project)
        if code != 0:
            sys.exit(code)

    print(f"OK: bootstrapped {project}")
    print(f"Starter: {starter['id']}")
    print("Route: /project -> /kickstart")
    if args.no_plan:
        write_alias_documents_if_valid(project)
        print(f"Next: python3 {ROOT / 'scripts' / 'pfo.py'} plan {project}")
    else:
        print("Plan: generated automatically")
        print("Report: PFO_REPORT.md")


if __name__ == "__main__":
    main()
