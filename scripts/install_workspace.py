#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import os
import shutil
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
MANAGED_START = "<!-- PFO_WORKSPACE_RUNTIME_START -->"
MANAGED_END = "<!-- PFO_WORKSPACE_RUNTIME_END -->"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def managed_block(workspace: Path, codex_home: Path) -> str:
    return f"""{MANAGED_START}
## Product Factory OS Runtime

Product Factory OS is the default Codex runtime for this workspace.

- Workspace: `{workspace}`
- Methodology: `{ROOT}`
- Codex home: `{codex_home}`
- Command wrapper: `pfo`

For new project requests, Codex must create the project through PFO automatically. The user should not need to run setup commands manually:

```bash
pfo new <project-name> --idea "<product idea>"
```

For existing projects, PFO is automatic and full after install. Before any project work, Codex must ensure the project has:

```text
AGENTS.md
CODEX.md
.codex-memory/STATE.json
.pfo/
PFO_EXISTING_PROJECT_ANALYSIS.json
PFO_CONTRACT_GATE.json
PFO_REPORT.md
```

If any of these are missing, Codex must run `pfo adopt <project>` before implementation. Project-local instructions may add constraints, but they do not replace the PFO lifecycle, gates, memory, or `.pfo/` contracts.
{MANAGED_END}
"""


def upsert_managed_block(path: Path, title: str, block: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def write_workspace_policy(workspace: Path, codex_home: Path) -> None:
    block = managed_block(workspace, codex_home)
    upsert_managed_block(workspace / "CODEX.md", "Workspace Rules", block)
    upsert_managed_block(workspace / "AGENTS.md", "Workspace Agents", block)
    policy = {
        "methodology": "product-factory-os",
        "methodologyPath": str(ROOT),
        "scope": str(workspace),
        "codexHome": str(codex_home),
        "enforcement": "mandatory",
        "defaultForNewProjects": True,
        "automaticForNewProjects": True,
        "manualUserCommandsRequired": False,
        "codexAutoBootstrapNewProjects": True,
        "mandatoryForExistingProjects": True,
        "autoAdoptExistingProjects": True,
        "autoAnalyzeExistingProjects": True,
        "fullAdoptionForExistingProjects": True,
        "autoReportProjects": True,
        "defaultNewProjectRoute": "/project -> /kickstart",
        "existingProjectRoute": "/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save",
        "requiredProjectFiles": [
            "AGENTS.md",
            "CODEX.md",
            ".codex-memory/MEMORY.md",
            ".codex-memory/STATE.json",
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
            "PFO_EXISTING_PROJECT_ANALYSIS.json",
            "PFO_CONTRACT_GATE.json",
            "PFO_REPORT.md",
        ],
        "pfoCommand": "pfo",
        "nonBypassRule": "New and existing project work in this workspace must use full Product Factory OS automatically.",
    }
    (workspace / "PFO_WORKSPACE.json").write_text(
        json.dumps(policy, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_global_policy(workspace: Path, codex_home: Path) -> None:
    policy = {
        "methodology": "product-factory-os",
        "methodologyPath": str(ROOT),
        "defaultWorkspace": str(workspace),
        "codexHome": str(codex_home),
        "enforcement": "global",
        "autoAdoptAnyProject": True,
        "autoAnalyzeExistingProjects": True,
        "autoReportProjects": True,
        "defaultNewProjectRoute": "/project -> /kickstart",
        "existingProjectRoute": "/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save",
        "nonBypassRule": "Any local project opened in Codex should auto-connect to Product Factory OS, even outside the default workspace.",
    }
    for target in [codex_home / "PFO_GLOBAL.json", Path.home() / ".pfo" / "PFO_GLOBAL.json"]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def install_hooks(codex_home: Path) -> Path:
    target = codex_home / "hooks" / "product-factory-os"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted((ROOT / "hooks").glob("*.py")):
        shutil.copyfile(source, target / source.name)
        mode = (target / source.name).stat().st_mode
        (target / source.name).chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    shutil.copyfile(ROOT / "hooks" / "hooks.json", target / "hooks.json")
    return target


def install_bin() -> Path | None:
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    target = bin_dir / "pfo"
    wrapper = f"""#!/usr/bin/env bash
# Product Factory OS managed wrapper
exec python3 "{ROOT / 'scripts' / 'pfo.py'}" "$@"
"""
    if target.exists():
        current = target.read_text(encoding="utf-8", errors="ignore")
        if "Product Factory OS managed wrapper" not in current:
            print(f"WARNING: {target} already exists and is not managed by PFO; leaving it unchanged.")
            return None
    target.write_text(wrapper, encoding="utf-8")
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return target


def adopt_workspace(workspace: Path) -> None:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "adoption_check.py"),
        "--workspace",
        str(workspace),
        "--write",
        "--analyze",
        "--report",
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode not in (0, 2):
        fail(result.stdout + result.stderr)
    output = result.stdout.strip()
    if output:
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Product Factory OS into a Codex workspace.")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    parser.add_argument("--no-hooks", action="store_true")
    parser.add_argument("--no-adopt", action="store_true")
    parser.add_argument("--no-bin", action="store_true")
    parser.add_argument("--no-workspace-policy", action="store_true")
    parser.add_argument("--no-global-policy", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.expanduser().resolve()
    codex_home = args.codex_home.expanduser().resolve()
    if not workspace.is_dir():
        fail(f"workspace does not exist: {workspace}")
    if not inside(ROOT, workspace):
        print(f"WARNING: methodology repo {ROOT} is outside workspace {workspace}; install will still work.")

    if not args.no_workspace_policy:
        write_workspace_policy(workspace, codex_home)
    if not args.no_global_policy:
        write_global_policy(workspace, codex_home)
    hook_target = None if args.no_hooks else install_hooks(codex_home)
    bin_target = None if args.no_bin else install_bin()
    if not args.no_adopt:
        adopt_workspace(workspace)

    print("\nProduct Factory OS installed.")
    print(f"Workspace: {workspace}")
    print(f"Methodology: {ROOT}")
    if bin_target:
        print(f"Command: {bin_target}")
    if hook_target:
        print(f"Hooks: {hook_target}")
    print("Daily use: open any project in the workspace; PFO instructions and state are already present.")
    print("Global use: open any local project; the preflight hook will auto-connect PFO from PFO_GLOBAL.json.")


if __name__ == "__main__":
    main()
