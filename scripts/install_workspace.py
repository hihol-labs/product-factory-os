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
GLOBAL_MANAGED_START = "<!-- PFO_GLOBAL_RUNTIME_START -->"
GLOBAL_MANAGED_END = "<!-- PFO_GLOBAL_RUNTIME_END -->"


def codex_goal_mode_policy() -> dict:
    return {
        "enabled": True,
        "defaultOn": True,
        "scope": "new-and-existing-local-projects",
        "startRule": "At the start of any non-trivial PFO project request, Codex must create or continue a /goal objective that names the user outcome and active PFO route.",
        "completionRule": "Keep the goal active through implementation, gates, verification, and state-save. Mark complete only when the requested outcome and PFO exit gates are satisfied.",
        "blockedRule": "Mark blocked only when PFO cannot continue without user input or an external state change.",
    }


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

Codex `/goal` mode is part of the PFO runtime. At the start of any non-trivial local project request, Codex must create or continue a goal whose objective names the user outcome and the active PFO route. Keep that goal active until implementation, gates, verification, and state-save are complete.
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
        "codexGoalMode": codex_goal_mode_policy(),
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
        "scope": "all-local-projects-on-this-computer",
        "automaticForNewProjectsAnywhere": True,
        "mandatoryForExistingProjectsAnywhere": True,
        "autoAdoptAnyProject": True,
        "autoAnalyzeExistingProjects": True,
        "autoReportProjects": True,
        "codexGoalMode": codex_goal_mode_policy(),
        "defaultNewProjectRoute": "/project -> /kickstart",
        "existingProjectRoute": "/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save",
        "nonBypassRule": "Any new or existing local project opened in Codex must auto-connect to Product Factory OS, including projects outside the default workspace.",
    }
    for target in [codex_home / "PFO_GLOBAL.json", Path.home() / ".pfo" / "PFO_GLOBAL.json"]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def global_runtime_block(methodology: str, workspace: str) -> str:
    return f"""{GLOBAL_MANAGED_START}
## Product Factory OS Global Runtime

Product Factory OS is the default methodology for Codex work on this computer.

- Methodology: `{methodology}`
- Default workspace: `{workspace}`
- New projects route: `/project -> /kickstart`
- Existing projects route: `/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save`
- Codex `/goal` mode: default-on for every non-trivial PFO project task

For any local project, including projects outside the default workspace, Codex must auto-connect Product Factory OS from `PFO_GLOBAL.json` and ensure adoption before implementation. The user should not need to run setup commands manually.

This applies to both existing projects and newly created projects anywhere on this computer, not only under the default `projects` workspace.

At the start of any non-trivial local project request, Codex must create or continue a `/goal` objective that names the user outcome and active PFO route. Keep it active through implementation, gates, verification, and state-save; complete it only after the requested outcome and PFO exit gates are satisfied.
{GLOBAL_MANAGED_END}
"""


def write_global_agents_rule(codex_home: Path, methodology: str, workspace: str) -> None:
    upsert_managed_block(
        codex_home / "AGENTS.md",
        "Global Codex Rules",
        global_runtime_block(methodology, workspace),
    )


def install_hooks(codex_home: Path, use_wsl_commands: bool = False) -> Path:
    target = codex_home / "hooks" / "product-factory-os"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted((ROOT / "hooks").glob("*.py")):
        shutil.copyfile(source, target / source.name)
        mode = (target / source.name).stat().st_mode
        (target / source.name).chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if use_wsl_commands:
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        for hook in hooks.get("hooks", []):
            script_name = Path(str(hook.get("command", "")).split()[-1]).name
            hook["command"] = f"wsl python3 {(target / script_name).as_posix()}"
        (target / "hooks.json").write_text(
            json.dumps(hooks, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    else:
        shutil.copyfile(ROOT / "hooks" / "hooks.json", target / "hooks.json")
    return target


def wsl_distro_name() -> str:
    return os.environ.get("WSL_DISTRO_NAME") or "Ubuntu-24.04"


def wsl_unc(path: Path) -> str:
    rel = str(path.resolve()).lstrip("/").replace("/", "\\")
    return f"\\\\wsl.localhost\\{wsl_distro_name()}\\{rel}"


def windows_path_from_mnt(path: Path) -> str:
    resolved = path.resolve()
    parts = resolved.parts
    if len(parts) >= 4 and parts[1] == "mnt" and len(parts[2]) == 1:
        drive = parts[2].upper()
        return drive + ":\\" + "\\".join(parts[3:])
    return str(resolved)


def write_windows_global_policy(workspace: Path, codex_home: Path) -> None:
    policy = {
        "methodology": "product-factory-os",
        "methodologyPath": wsl_unc(ROOT),
        "defaultWorkspace": wsl_unc(workspace),
        "codexHome": windows_path_from_mnt(codex_home),
        "enforcement": "global",
        "scope": "all-local-projects-on-this-computer",
        "automaticForNewProjectsAnywhere": True,
        "mandatoryForExistingProjectsAnywhere": True,
        "autoAdoptAnyProject": True,
        "autoAnalyzeExistingProjects": True,
        "autoReportProjects": True,
        "codexGoalMode": codex_goal_mode_policy(),
        "defaultNewProjectRoute": "/project -> /kickstart",
        "existingProjectRoute": "/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save",
        "nonBypassRule": "Any new or existing local project opened in Codex must auto-connect to Product Factory OS, including projects outside the default workspace.",
    }
    for target in [codex_home / "PFO_GLOBAL.json", codex_home.parent / ".pfo" / "PFO_GLOBAL.json"]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_global_agents_rule(codex_home, policy["methodologyPath"], policy["defaultWorkspace"])


def detect_windows_codex_homes() -> list[Path]:
    users = Path("/mnt/c/Users")
    if not users.is_dir():
        return []
    return sorted(path for path in users.glob("*/.codex") if path.is_dir())


def managed_wrapper() -> str:
    return f"""#!/usr/bin/env bash
# Product Factory OS managed wrapper
exec python3 "{ROOT / 'scripts' / 'pfo.py'}" "$@"
"""


def write_managed_wrapper(target: Path) -> bool:
    wrapper = managed_wrapper()
    if target.exists():
        current = target.read_text(encoding="utf-8", errors="ignore")
        if "Product Factory OS managed wrapper" not in current:
            print(f"WARNING: {target} already exists and is not managed by PFO; leaving it unchanged.")
            return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(wrapper, encoding="utf-8")
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return True


def install_bin() -> list[Path]:
    bin_dir = Path.home() / ".local" / "bin"
    target = bin_dir / "pfo"
    installed: list[Path] = []
    if write_managed_wrapper(target):
        installed.append(target)

    system_target = Path("/usr/local/bin/pfo")
    can_write_system = os.access(system_target.parent, os.W_OK) or (
        system_target.exists() and os.access(system_target, os.W_OK)
    )
    if can_write_system and write_managed_wrapper(system_target):
        installed.append(system_target)
    elif system_target.exists():
        current = system_target.read_text(encoding="utf-8", errors="ignore")
        if "Product Factory OS managed wrapper" in current:
            installed.append(system_target)
        else:
            print(f"WARNING: {system_target} exists and is not managed by PFO; leaving it unchanged.")
    else:
        print(f"WARNING: {system_target} is not writable; direct 'wsl pfo ...' may need a system wrapper.")
    return installed


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
        write_global_agents_rule(codex_home, str(ROOT), str(workspace))
    hook_target = None if args.no_hooks else install_hooks(codex_home)
    bin_targets = [] if args.no_bin else install_bin()
    windows_hook_targets: list[Path] = []
    if not args.no_hooks or not args.no_global_policy:
        for windows_codex_home in detect_windows_codex_homes():
            if not args.no_global_policy:
                write_windows_global_policy(workspace, windows_codex_home)
            if not args.no_hooks:
                windows_hook_targets.append(install_hooks(windows_codex_home, use_wsl_commands=True))
    if not args.no_adopt:
        adopt_workspace(workspace)

    print("\nProduct Factory OS installed.")
    print(f"Workspace: {workspace}")
    print(f"Methodology: {ROOT}")
    for bin_target in bin_targets:
        print(f"Command: {bin_target}")
    if hook_target:
        print(f"Hooks: {hook_target}")
    for target in windows_hook_targets:
        print(f"Windows hooks: {target}")
    print("Daily use: open any project in the workspace; PFO instructions and state are already present.")
    print("Global use: open any new or existing local project anywhere on this computer; the preflight hook will auto-connect PFO from PFO_GLOBAL.json.")


if __name__ == "__main__":
    main()
