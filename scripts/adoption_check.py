#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PFO_TEMPLATE_DIR = ROOT / "docs" / "templates" / "pfo"
MANAGED_START = "<!-- PFO_PROJECT_RUNTIME_START -->"
MANAGED_END = "<!-- PFO_PROJECT_RUNTIME_END -->"

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


def has_pfo_contracts(path: Path) -> bool:
    for name in [
        "PROJECT_CONTRACT.md",
        "DATA_POLICY.md",
        "GOLDEN_FLOWS.md",
        "FORBIDDEN_CHANGES.md",
        "FALLBACK_POLICY.md",
        "SCOPE_LOCK.md",
    ]:
        if not (path / ".pfo" / name).is_file():
            return False
    return True


def status_for(path: Path) -> dict[str, object]:
    return {
        "project": path.name,
        "path": str(path),
        "hasAgents": is_file(path / "AGENTS.md"),
        "hasCodex": is_file(path / "CODEX.md"),
        "hasMemory": is_file(path / ".codex-memory" / "MEMORY.md"),
        "hasState": is_file(path / ".codex-memory" / "STATE.json"),
        "hasPfoContracts": has_pfo_contracts(path),
        "hasPrd": is_file(path / "PRD.md"),
        "hasArchitecture": is_file(path / "PROJECT_ARCHITECTURE.md"),
        "hasImplementationPlan": is_file(path / "IMPLEMENTATION_PLAN.md"),
        "hasProductBlueprint": is_file(path / "PRODUCT_BLUEPRINT.md"),
        "hasBuildPlan": is_file(path / "BUILD_PLAN.md"),
        "hasExecutionGraph": is_file(path / "EXECUTION_GRAPH.md"),
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
    return "Adopted with minimal Product Factory OS state. Run `pfo analyze <project> --run-gates` before major work." + suffix


def project_runtime_block(path: Path, workspace: Path) -> str:
    return f"""{MANAGED_START}
## Product Factory OS Runtime

This existing project is adopted into Product Factory OS.

- Workspace: `{workspace}`
- Methodology: `{ROOT}`
- Project: `{path}`

Before substantial implementation, Codex must use:

```bash
pfo adopt {path} --analyze
```

Then route work through `/task`, update `.codex-memory/STATE.json`, and respect `.pfo/` contracts. Project-local rules may add constraints, but they do not replace PFO gates, memory, or scope/data/fallback contracts.
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
    for source in PFO_TEMPLATE_DIR.glob("*.md"):
        target = pfo_dir / source.name
        if not target.exists():
            shutil.copyfile(source, target)


def write_adoption_files(path: Path, workspace: Path) -> None:
    codex = path / "CODEX.md"
    agents = path / "AGENTS.md"
    memory_dir = path / ".codex-memory"
    memory = memory_dir / "MEMORY.md"
    state = memory_dir / "STATE.json"
    block = project_runtime_block(path, workspace)

    upsert_managed_block(codex, "CODEX", block)
    upsert_managed_block(agents, "AGENTS", block)
    ensure_pfo_contracts(path)

    memory_dir.mkdir(exist_ok=True)
    if not memory.exists():
        memory.write_text("# Memory\n\n", encoding="utf-8")
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
                    "gateResults": {
                        "strategy": "",
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
                        "security": "",
                        "dependencies": "",
                        "hardening": "",
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
                    "learningProposals": [],
                    "briefArtifacts": [],
                    "worktreeIsolation": {
                        "enabled": False,
                        "strategy": "",
                        "activeBranch": "",
                        "activeWorktree": "",
                        "mergeStatus": "",
                    },
                    "blockers": [],
                    "nextAction": "PFO is active. Run `pfo adopt <project> --analyze` before major work.",
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Check or bootstrap Product Factory OS adoption for workspace projects.")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    parser.add_argument("--project", type=Path, help="Check or adopt a single existing project root.")
    parser.add_argument("--write", action="store_true", help="Create AGENTS.md, CODEX.md, .pfo/, and .codex-memory/ where missing.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a table.")
    args = parser.parse_args()

    projects = [args.project.resolve()] if args.project else project_dirs(args.workspace)
    if args.write:
        for project in projects:
            write_adoption_files(project, args.workspace.resolve())

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
        flags.append("pfo-docs" if item["hasPrd"] and item["hasArchitecture"] and item["hasImplementationPlan"] and item["hasProductBlueprint"] and item["hasBuildPlan"] and item["hasExecutionGraph"] else "pfo-docs-partial")
        print(f"{item['project']}: {', '.join(flags)}")

    missing = [
        item for item in statuses
        if not item["hasAgents"]
        or not item["hasCodex"]
        or not item["hasMemory"]
        or not item["hasState"]
        or not item["hasPfoContracts"]
    ]
    if missing:
        print("\nRun with --write to create PFO runtime files for projects missing AGENTS, CODEX, memory, state, or contracts.")
        sys.exit(2)


if __name__ == "__main__":
    main()
