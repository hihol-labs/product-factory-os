#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys


PFO_CONTRACTS = [
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


def load_workspace_policy(cwd: Path) -> tuple[Path, dict] | None:
    for path in [cwd, *cwd.parents]:
        policy = path / "PFO_WORKSPACE.json"
        if policy.is_file():
            try:
                return path, json.loads(policy.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None
    return None


def first_level_project(cwd: Path, workspace: Path) -> Path | None:
    try:
        rel = cwd.resolve().relative_to(workspace.resolve())
    except ValueError:
        return None
    if not rel.parts:
        return None
    return workspace / rel.parts[0]


def needs_adoption(project: Path) -> bool:
    required = [
        project / "AGENTS.md",
        project / "CODEX.md",
        project / ".codex-memory" / "MEMORY.md",
        project / ".codex-memory" / "STATE.json",
        project / ".codex-memory" / "events.jsonl",
    ]
    required.extend(project / rel for rel in PFO_CONTRACTS)
    return any(not path.is_file() for path in required)


def auto_adopt(cwd: Path) -> Path:
    loaded = load_workspace_policy(cwd)
    if not loaded:
        return cwd
    workspace, policy = loaded
    project = first_level_project(cwd, workspace)
    if not project or not project.is_dir():
        return cwd
    methodology = Path(policy.get("methodologyPath", ""))
    if methodology and (project == methodology or methodology in project.parents):
        return project
    if project.name in {"product-factory-os", "idea-to-deploy"} or project.name.startswith("."):
        return project
    if not policy.get("autoAdoptExistingProjects", True):
        return project
    if not needs_adoption(project):
        return project
    script = methodology / "scripts" / "adoption_check.py"
    if not script.is_file():
        return project
    result = subprocess.run(
        [sys.executable, str(script), "--project", str(project), "--write"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode in (0, 2):
        print(f"Product Factory OS auto-adopted: {project}")
    else:
        print("Product Factory OS auto-adopt failed:")
        print(result.stdout + result.stderr)
    return project


def main() -> None:
    cwd = auto_adopt(Path.cwd())
    docs = [
        "DISCOVERY.md",
        "MARKET_BRIEF.md",
        "ICP.md",
        "PRD.md",
        "PRODUCT_BLUEPRINT.md",
        "PROJECT_ARCHITECTURE.md",
        "BUILD_PLAN.md",
        "EXECUTION_GRAPH.md",
        "TEST_PLAN.md",
        "QUALITY_GATES.md",
        "HANDOFF.md",
        "IMPLEMENTATION_PLAN.md",
        "AGENTS.md",
        "CODEX.md",
    ]
    found = [name for name in docs if (cwd / name).exists()]
    memory = cwd / ".codex-memory" / "MEMORY.md"
    state = cwd / ".codex-memory" / "STATE.json"
    events = cwd / ".codex-memory" / "events.jsonl"
    contracts_found = [name for name in PFO_CONTRACTS if (cwd / name).exists()]

    if found:
        print("Product Factory OS docs found: " + ", ".join(found))
    else:
        print("Product Factory OS docs found: none")

    if memory.exists():
        print("Memory index: .codex-memory/MEMORY.md")
    else:
        print("Memory index: none")
    if state.exists():
        print("State file: .codex-memory/STATE.json")
    else:
        print("State file: none")
    if events.exists():
        print("Event log: .codex-memory/events.jsonl")
    else:
        print("Event log: none")
    if contracts_found:
        print("PFO contracts found: " + ", ".join(contracts_found))
    else:
        print("PFO contracts found: none")


if __name__ == "__main__":
    main()
