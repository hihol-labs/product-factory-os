#!/usr/bin/env python3
from pathlib import Path
import json
import os
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

ALIAS_DOCUMENT_NAMES = [
    "MASTER_CONTEXT.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "PROGRESS.md",
    "TESTING.md",
]

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


def discover_methodology(cwd: Path) -> Path | None:
    candidates = []
    env_path = os.environ.get("PFO_METHODOLOGY_PATH")
    if env_path:
        candidates.append(Path(env_path))
    for policy in [*find_policy_files(cwd), global_policy_file()]:
        if policy and policy.is_file():
            try:
                data = json.loads(policy.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if data.get("methodologyPath"):
                candidates.append(Path(data["methodologyPath"]))
    for parent in Path(__file__).resolve().parents:
        candidates.append(parent)
    for candidate in candidates:
        if (candidate / "scripts" / "pfo.py").is_file() and (candidate / "docs" / "METHODOLOGY.md").is_file():
            return candidate.resolve()
    return None


def global_policy_file() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return codex_home / "PFO_GLOBAL.json"


def home_policy_file() -> Path:
    return Path.home() / ".pfo" / "PFO_GLOBAL.json"


def find_policy_files(cwd: Path) -> list[Path]:
    files = []
    for path in [cwd, *cwd.parents]:
        files.append(path / "PFO_WORKSPACE.json")
    files.append(home_policy_file())
    return files


def missing_alias_targets_for(methodology: Path, project: Path) -> list[str]:
    sys.path.insert(0, str(methodology / "scripts"))
    try:
        from pfo_alias_targets import missing_alias_targets
    except ImportError:
        return []
    return missing_alias_targets(project)


def load_workspace_policy(cwd: Path) -> tuple[Path, dict] | None:
    for path in [cwd, *cwd.parents]:
        policy = path / "PFO_WORKSPACE.json"
        if policy.is_file():
            try:
                return path, json.loads(policy.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None
    return None


def load_global_policy(cwd: Path) -> dict | None:
    for path in [global_policy_file(), home_policy_file()]:
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None
    methodology = discover_methodology(cwd)
    if methodology:
        return {
            "methodologyPath": str(methodology),
            "autoAdoptAnyProject": True,
            "autoAnalyzeExistingProjects": True,
            "autoReportProjects": True,
        }
    return None


def first_level_project(cwd: Path, workspace: Path) -> Path | None:
    try:
        rel = cwd.resolve().relative_to(workspace.resolve())
    except ValueError:
        return None
    if not rel.parts:
        return None
    return workspace / rel.parts[0]


def project_root_anywhere(cwd: Path) -> Path | None:
    markers = [
        ".git",
        "package.json",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
        "pom.xml",
        "README.md",
        "AGENTS.md",
        "CODEX.md",
    ]
    home = Path.home().resolve()
    for path in [cwd, *cwd.parents]:
        if path.resolve() == home or path.parent == path:
            break
        if any((path / marker).exists() for marker in markers):
            return path
    if cwd.resolve() != home and cwd.parent != cwd and not cwd.name.startswith("."):
        return cwd
    return None


def needs_adoption(project: Path) -> bool:
    required = [
        project / "AGENTS.md",
        project / "CODEX.md",
        project / "NEXT_STEP.md",
        project / ".codex-memory" / "MEMORY.md",
        project / ".codex-memory" / "STATE.json",
        project / ".codex-memory" / "events.jsonl",
    ]
    required.extend(project / rel for rel in PFO_CONTRACTS)
    required.extend(project / rel for rel in ALIAS_DOCUMENT_NAMES)
    return any(not path.is_file() for path in required)


def is_generated_pfo_project(project: Path) -> bool:
    return (project / ".pfo-starter.json").is_file()


def needs_full_runtime(methodology: Path, project: Path) -> bool:
    if needs_adoption(project):
        return True
    if is_generated_pfo_project(project):
        required = [project / "PFO_REPORT.md"]
        required.extend(project / rel for rel in GENERATED_PLAN_FILES)
    else:
        required = [
            project / "PFO_EXISTING_PROJECT_ANALYSIS.json",
            project / "PFO_CONTRACT_GATE.json",
            project / "PFO_REPORT.md",
            project / "NEXT_STEP.md",
        ]
    return any(not path.is_file() for path in required) or bool(missing_alias_targets_for(methodology, project))


def run_auto_full_runtime(project: Path, workspace: Path, methodology: Path, generated: bool) -> None:
    if generated:
        commands = [
            [sys.executable, str(methodology / "scripts" / "adoption_check.py"), "--project", str(project), "--workspace", str(workspace), "--write"],
            [sys.executable, str(methodology / "scripts" / "pfo.py"), "plan", str(project)],
            [sys.executable, str(methodology / "scripts" / "pfo_report.py"), str(project)],
        ]
    else:
        commands = [
            [
                sys.executable,
                str(methodology / "scripts" / "adoption_check.py"),
                "--project",
                str(project),
                "--workspace",
                str(workspace),
                "--write",
                "--analyze",
                "--report",
            ]
        ]
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            print("Product Factory OS full-runtime sync failed:")
            print(result.stdout + result.stderr)
            return
    print(f"Product Factory OS full-runtime active: {project}")


def auto_adopt(cwd: Path) -> Path:
    loaded = load_workspace_policy(cwd)
    policy = loaded[1] if loaded else (load_global_policy(cwd) or {})
    methodology = Path(policy.get("methodologyPath", "")) if policy else discover_methodology(cwd)
    if not methodology or not methodology.exists():
        return cwd
    if loaded:
        workspace = loaded[0]
        project = first_level_project(cwd, workspace)
    else:
        project = project_root_anywhere(cwd)
        workspace = project.parent if project else cwd.parent
    if not project or not project.is_dir():
        return cwd
    if methodology and (project == methodology or methodology in project.parents):
        return project
    if project.name in {"product-factory-os", "idea-to-deploy"} or project.name.startswith("."):
        return project
    if loaded and not policy.get("autoAdoptExistingProjects", True):
        return project
    if not loaded and not policy.get("autoAdoptAnyProject", True):
        return project
    if not needs_full_runtime(methodology, project):
        return project
    script = methodology / "scripts" / "adoption_check.py"
    if not script.is_file():
        return project
    run_auto_full_runtime(project, workspace, methodology, is_generated_pfo_project(project))
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
