#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent

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


def status_for(path: Path) -> dict[str, object]:
    return {
        "project": path.name,
        "path": str(path),
        "hasCodex": is_file(path / "CODEX.md"),
        "hasMemory": is_file(path / ".codex-memory" / "MEMORY.md"),
        "hasState": is_file(path / ".codex-memory" / "STATE.json"),
        "hasPrd": is_file(path / "PRD.md"),
        "hasArchitecture": is_file(path / "PROJECT_ARCHITECTURE.md"),
        "hasImplementationPlan": is_file(path / "IMPLEMENTATION_PLAN.md"),
        "hasProductBlueprint": is_file(path / "PRODUCT_BLUEPRINT.md"),
        "hasBuildPlan": is_file(path / "BUILD_PLAN.md"),
        "hasExecutionGraph": is_file(path / "EXECUTION_GRAPH.md"),
        "hasGit": is_dir(path / ".git"),
    }


def write_adoption_files(path: Path) -> None:
    codex = path / "CODEX.md"
    memory_dir = path / ".codex-memory"
    memory = memory_dir / "MEMORY.md"
    state = memory_dir / "STATE.json"

    if not codex.exists():
        codex.write_text(
            "# CODEX\n\n"
            "This project is adopted into the Product Factory OS workspace methodology.\n\n"
            "## Rules\n\n"
            "- Follow `/home/hihol/projects/CODEX.md` unless project-local rules override it.\n"
            "- Save significant session context in `.codex-memory/`.\n"
            "- Run review and tests before deploy or broad changes.\n",
            encoding="utf-8",
        )

    memory_dir.mkdir(exist_ok=True)
    if not memory.exists():
        memory.write_text("# Memory\n\n", encoding="utf-8")
    if not state.exists():
        state.write_text(
            json.dumps(
                {
                    "sessionState": "ADOPTED",
                    "currentStage": "IDLE",
                    "intent": "Existing project adopted into Product Factory OS Product Factory OS.",
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
                        "lastAnalysisSummary": "Adopted with minimal Product Factory OS state. Run /task to classify work and inspect the repository before changes.",
                    },
                    "currentNode": "",
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
                    "decisionLog": [],
                    "artifactHashes": {},
                    "lastSuccessfulState": "ADOPTED",
                    "artifacts": ["CODEX.md", ".codex-memory/MEMORY.md"],
                    "completedModules": [],
                    "failedValidations": [],
                    "blockers": [],
                    "nextAction": "Classify product and create missing PFO planning artifacts before major work.",
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
    parser.add_argument("--write", action="store_true", help="Create CODEX.md and .codex-memory/MEMORY.md where missing.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a table.")
    args = parser.parse_args()

    projects = project_dirs(args.workspace)
    if args.write:
        for project in projects:
            write_adoption_files(project)

    statuses = [status_for(project) for project in projects]

    if args.json:
        print(json.dumps(statuses, indent=2, ensure_ascii=False))
        return

    print("Project adoption status")
    print("-----------------------")
    for item in statuses:
        flags = []
        flags.append("CODEX" if item["hasCodex"] else "no-CODEX")
        flags.append("memory" if item["hasMemory"] else "no-memory")
        flags.append("state" if item["hasState"] else "no-state")
        flags.append("pfo-docs" if item["hasPrd"] and item["hasArchitecture"] and item["hasImplementationPlan"] and item["hasProductBlueprint"] and item["hasBuildPlan"] and item["hasExecutionGraph"] else "pfo-docs-partial")
        print(f"{item['project']}: {', '.join(flags)}")

    missing = [item for item in statuses if not item["hasCodex"] or not item["hasMemory"] or not item["hasState"]]
    if missing:
        print("\nRun with --write to create minimal adoption files for projects missing CODEX, memory, or state.")
        sys.exit(2)


if __name__ == "__main__":
    main()
