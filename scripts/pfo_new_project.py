#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import re
import sys
import shutil

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent


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
            "gateResults": {
                "strategy": "",
                "architecture": "",
                "tests": "",
                "review": "",
                "security": "",
                "dependencies": "",
                "hardening": "",
                "deploymentReadiness": "",
            },
            "verificationHistory": [],
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
                ".codex-memory/MEMORY.md",
                ".codex-memory/STATE.json",
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
            "briefArtifacts": [],
            "worktreeIsolation": {
                "enabled": False,
                "strategy": "",
                "activeBranch": "",
                "activeWorktree": "",
                "mergeStatus": "",
            },
            "blockers": [],
            "nextAction": "Route the voice/text idea through /project -> /kickstart and create Product Factory OS compiler artifacts.",
            "project": project_name,
            "methodology": str(methodology),
            "starter": starter["id"],
            "productTypeHint": starter["productType"],
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
        for source in pfo_templates.glob("*.md"):
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
DISCOVERY.md
PRD.md
PRODUCT_BLUEPRINT.md
PROJECT_ARCHITECTURE.md
PHASE_CONTEXT.md
BUILD_PLAN.md
EXECUTION_GRAPH.md
IMPLEMENTATION_PLAN.md
.pfo/UNIT_CONTEXT_MANIFEST.json
.codex-memory/STATE.json
.codex-memory/LEARNINGS.md
```

## Operating Contract

- Voice or natural-language commands are accepted as the primary interface.
- Codex performs routing automatically.
- Capture implementation decisions in `PHASE_CONTEXT.md` before detailed execution planning.
- Build `.pfo/UNIT_CONTEXT_MANIFEST.json` before autonomous or delegated execution.
- Implementation follows `EXECUTION_GRAPH.md` node by node.
- Every task must respect `.pfo/SCOPE_LOCK.md`.
- Real production data must follow `.pfo/DATA_POLICY.md`.
- Fallbacks must follow `.pfo/FALLBACK_POLICY.md` and must not silently replace real output.
- Tests, review, security, dependency, and hardening gates block deployment when they fail.
- Golden flows in `.pfo/GOLDEN_FLOWS.md` block deployment when touched and unverified.
- Verification fails closed when evidence is missing or ambiguous.
- Extract durable decisions, lessons, patterns, and surprises into `.codex-memory/LEARNINGS.md`.
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

Use `/project -> /kickstart` for new product work and `/task` routes for ongoing changes. Respect `.pfo/` contracts, update `.codex-memory/STATE.json`, and run the smallest relevant verification before finishing.
"""


def memory_md(project_name: str, idea: str) -> str:
    summary = idea or "Product Factory OS project bootstrapped."
    return f"""# Memory

- bootstrap: {project_name} initialized for Product Factory OS -> STATE.json

## Initial Intent

{summary}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap a new project under Product Factory OS.")
    parser.add_argument("name", help="Project directory name or product name.")
    parser.add_argument("--idea", default="", help="Voice transcript or natural-language product idea.")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE, help="Workspace directory.")
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
    write_once(memory_dir / "STATE.json", state_json(project_name, args.idea, methodology))
    scaffold(project, starter)

    print(f"OK: bootstrapped {project}")
    print(f"Starter: {starter['id']}")
    print("Route: /project -> /kickstart")
    print(f"Next: python3 {ROOT / 'scripts' / 'pfo.py'} plan {project}")


if __name__ == "__main__":
    main()
