#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
import shutil
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python <3.11 fallback.
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMEOUT = 90
PFO_TEMPLATE_DIR = ROOT / "docs" / "templates" / "pfo"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def upgrade_json_contract(target: Path, source: Path) -> bool:
    try:
        current = json.loads(target.read_text(encoding="utf-8"))
        default = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    merged, changed = merge_missing(current, default)
    if changed:
        write_json(target, merged)
    return changed


def default_human_steering() -> dict[str, Any]:
    return {
        "approvalRequired": True,
        "approvalStatus": "PENDING",
        "approvedBy": "",
        "approvedAt": "",
        "lastPrompt": "Ask the user to confirm, change, or stop before implementation.",
        "lastIterationSummary": "Existing project is adopted into Product Factory OS.",
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


def backfill_human_steering(state: dict[str, Any]) -> dict[str, Any]:
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
    return state


def ensure_next_step_template(project: Path) -> None:
    source = ROOT / "docs" / "templates" / "NEXT_STEP.md"
    target = project / "NEXT_STEP.md"
    if source.is_file() and not target.exists():
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def write_next_step(project: Path, state: dict[str, Any]) -> None:
    steering = state.get("humanSteering", {}) if isinstance(state.get("humanSteering"), dict) else {}
    target = project / "NEXT_STEP.md"
    target.write_text(
        "# Next Step\n\n"
        "This is the user-facing steering checkpoint.\n\n"
        "## Where We Are\n\n"
        f"- Product: {project.name}\n"
        f"- Current outcome: {steering.get('lastIterationSummary', 'Existing project is adopted into PFO.')}\n"
        f"- Recommended next step: {steering.get('recommendedNextStep', 'Choose the next task.')}\n"
        f"- Approval status: {steering.get('approvalStatus', 'PENDING')}\n\n"
        "## Visible Roadmap\n\n"
        "| Step | Outcome | Status |\n|---|---|---|\n"
        "| 1 | Analyze existing project | done |\n"
        "| 2 | Choose a narrow task | pending |\n"
        "| 3 | Approve next implementation step | pending |\n\n"
        "## Decision Needed\n\n"
        "Confirm, change, or stop before another major implementation iteration starts.\n",
        encoding="utf-8",
    )


def ensure_pfo_contracts(project: Path) -> list[str]:
    created: list[str] = []
    pfo_dir = project / ".pfo"
    pfo_dir.mkdir(exist_ok=True)
    if not PFO_TEMPLATE_DIR.is_dir():
        return created
    for source in PFO_TEMPLATE_DIR.iterdir():
        if not source.is_file() or source.suffix not in {".md", ".json"}:
            continue
        target = pfo_dir / source.name
        if not target.exists():
            shutil.copyfile(source, target)
            created.append(str(target.relative_to(project)))
        elif source.suffix == ".json" and upgrade_json_contract(target, source):
            created.append(str(target.relative_to(project)))
    return created


def ensure_state(project: Path) -> tuple[Path, dict[str, Any]]:
    ensure_pfo_contracts(project)
    state_path = project / ".codex-memory" / "STATE.json"
    memory = project / ".codex-memory" / "MEMORY.md"
    events = project / ".codex-memory" / "events.jsonl"
    memory.parent.mkdir(parents=True, exist_ok=True)
    if not events.is_file():
        events.write_text("", encoding="utf-8")
    if state_path.is_file():
        state = backfill_human_steering(read_json(state_path))
        ensure_next_step_template(project)
        write_next_step(project, state)
        write_json(state_path, state)
        return state_path, state

    codex = project / "CODEX.md"
    agents = project / "AGENTS.md"
    if not memory.is_file():
        memory.write_text("# Memory\n\n", encoding="utf-8")
    if not codex.is_file():
        codex.write_text(
            "# CODEX\n\n"
            "This project is fully adopted into the Product Factory OS workspace methodology.\n\n"
            "## Rules\n\n"
            "- Follow Product Factory OS gates for significant work.\n"
            "- Save significant session context in `.codex-memory/`.\n",
            encoding="utf-8",
        )
    if not agents.is_file():
        agents.write_text(
            "# AGENTS\n\n"
            "This project is fully adopted into Product Factory OS.\n\n"
            "Before implementation, ensure `pfo adopt .` or `pfo analyze . --report` has refreshed analysis, report, memory, and `.pfo/` contracts.\n",
            encoding="utf-8",
        )

    state = json.loads((ROOT / "memory" / "session-state.schema.json").read_text(encoding="utf-8"))[
        "stateTemplate"
    ]
    state["sessionState"] = "ADOPTED"
    state["currentStage"] = "ADOPTED"
    state["intent"] = "Existing project adopted into Product Factory OS."
    state["existingProject"]["isExistingProject"] = True
    state["lastSuccessfulState"] = "ADOPTED"
    state["artifacts"] = [
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
    ]
    state = backfill_human_steering(state)
    state["nextAction"] = "Run existing-project analyzer, then review NEXT_STEP.md before major implementation work."
    ensure_next_step_template(project)
    write_next_step(project, state)
    write_json(state_path, state)
    return state_path, state


def package_manager(project: Path, root_package: dict[str, Any]) -> str:
    declared = str(root_package.get("packageManager", ""))
    if declared.startswith("pnpm"):
        return "pnpm"
    if declared.startswith("yarn"):
        return "yarn"
    if declared.startswith("npm"):
        return "npm"
    if (project / "pnpm-lock.yaml").is_file():
        return "pnpm"
    if (project / "yarn.lock").is_file():
        return "yarn"
    if (project / "package-lock.json").is_file():
        return "npm"
    return ""


def command_text(command: list[str]) -> str:
    return " ".join(command)


def list_package_files(project: Path) -> list[Path]:
    ignored = {"node_modules", ".git", ".next", "dist", "build", ".turbo"}
    result: list[Path] = []
    for path in project.rglob("package.json"):
        if any(part in ignored for part in path.relative_to(project).parts):
            continue
        result.append(path)
    return sorted(result)


def read_pyproject(project: Path) -> dict[str, Any]:
    path = project / "pyproject.toml"
    if not path.is_file() or tomllib is None:
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def python_dependency_names(project: Path) -> set[str]:
    names: set[str] = set()
    pyproject = read_pyproject(project)
    project_data = pyproject.get("project", {}) if isinstance(pyproject.get("project"), dict) else {}
    for item in project_data.get("dependencies", []) if isinstance(project_data.get("dependencies"), list) else []:
        names.add(re.split(r"[<>=~!;\[]", str(item), maxsplit=1)[0].strip().lower())
    for section in ["dependency-groups", "tool"]:
        value = pyproject.get(section, {})
        if isinstance(value, dict):
            names.update(token.lower() for token in json.dumps(value).split('"') if token.isidentifier())
    for rel in ["requirements.txt", "requirements-dev.txt"]:
        path = project / rel
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            names.add(re.split(r"[<>=~!;\[]", line, maxsplit=1)[0].strip().lower())
    return names


def detect_stack(project: Path, packages: list[dict[str, Any]]) -> list[str]:
    stack: set[str] = set()
    starter = read_json(project / ".pfo-starter.json")
    for item in starter.get("stack", []):
        stack.add(str(item))
    files = {path.name for path in project.iterdir() if path.is_file()}
    dirs = {path.name for path in project.iterdir() if path.is_dir()}
    deps: dict[str, str] = {}
    for package in packages:
        for key in ["dependencies", "devDependencies", "optionalDependencies"]:
            deps.update(package.get(key, {}))

    if "package.json" in files:
        stack.add("Node.js")
    if len(packages) > 1:
        stack.add("monorepo")
    if "pnpm-lock.yaml" in files:
        stack.add("pnpm")
    if "yarn.lock" in files:
        stack.add("Yarn")
    if "package-lock.json" in files:
        stack.add("npm")
    if "turbo.json" in files:
        stack.add("Turborepo")
    if "apps" in dirs and "packages" in dirs:
        stack.add("monorepo")
    if "next" in deps:
        stack.add("Next.js")
    if "react" in deps:
        stack.add("React")
    if "vue" in deps:
        stack.add("Vue")
    if "vite" in deps:
        stack.add("Vite")
    if "svelte" in deps or "@sveltejs/kit" in deps:
        stack.add("Svelte")
    if "nuxt" in deps:
        stack.add("Nuxt")
    if "express" in deps:
        stack.add("Express")
    if "@nestjs/core" in deps:
        stack.add("NestJS")
    if "tailwindcss" in deps:
        stack.add("TailwindCSS")
    if "grammy" in deps:
        stack.add("Telegram bot")
    if "@supabase/supabase-js" in deps or "@supabase/ssr" in deps or (project / "packages" / "supabase").exists():
        stack.add("Supabase")
        stack.add("PostgreSQL")
    if "typescript" in deps or any((project / name).is_file() for name in ["tsconfig.json"]):
        stack.add("TypeScript")
    if "openai" in deps:
        stack.add("OpenAI")
    if "@anthropic-ai/sdk" in deps:
        stack.add("Anthropic")
    compose_names = {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
    if any(path.name.lower() in compose_names for path in project.iterdir() if path.is_file()) or (
        (project / "docker").is_dir()
        and any(path.name.lower() in compose_names or path.name.startswith("docker-compose") for path in (project / "docker").glob("*.y*ml"))
    ):
        stack.add("Docker Compose")
    if (project / "Dockerfile").is_file() or list(project.glob("**/Dockerfile")):
        stack.add("Docker")
    python_deps = python_dependency_names(project)
    has_python = (
        "pyproject.toml" in files
        or "requirements.txt" in files
        or "setup.py" in files
        or "tox.ini" in files
        or "pytest.ini" in files
        or (project / "tests").is_dir()
        or (project / "scripts").is_dir()
        and any(path.suffix == ".py" for path in (project / "scripts").glob("*.py"))
    )
    if has_python:
        stack.add("Python")
    if "fastapi" in python_deps:
        stack.add("FastAPI")
    if "django" in python_deps:
        stack.add("Django")
    if "flask" in python_deps:
        stack.add("Flask")
    if "pytest" in python_deps or (project / "pytest.ini").is_file() or (project / "tests").is_dir():
        stack.add("pytest")
    if (project / "go.mod").is_file():
        stack.add("Go")
    if (project / "Cargo.toml").is_file():
        stack.add("Rust")
    if (project / "composer.json").is_file():
        stack.add("PHP")
    if (project / "Gemfile").is_file():
        stack.add("Ruby")
    if (project / "scripts" / "pfo.py").is_file() and (project / ".codex-plugin" / "plugin.json").is_file():
        stack.add("Product Factory OS runtime")
    return sorted(stack)


def classify(stack: list[str], project: Path) -> dict[str, Any]:
    starter = read_json(project / ".pfo-starter.json")
    if starter.get("productType"):
        return {
            "productType": str(starter.get("productType")),
            "domain": "PFO-generated project",
            "complexity": "medium",
            "requiredModules": starter.get("requiredArtifacts", []),
            "infrastructure": starter.get("stack", []),
        }

    has_web = "Next.js" in stack or "React" in stack
    has_bot = "Telegram bot" in stack or (project / "apps" / "bot").is_dir()
    has_worker = (project / "apps" / "worker").is_dir()
    has_api = has_web or (project / "apps" / "api").is_dir()
    product_parts = []
    modules = []
    if has_web:
        product_parts.append("SaaS Application")
        modules.extend(["web frontend", "API routes"])
    if has_bot:
        product_parts.append("Messaging Bot")
        modules.append("bot service")
    if has_worker:
        product_parts.append("Background Worker")
        modules.append("worker service")
    if not product_parts and has_api:
        product_parts.append("REST API Service")
    if not product_parts:
        product_parts.append("Existing Software Project")
    if "Supabase" in stack:
        modules.append("database layer")
    if "OpenAI" in stack or "Anthropic" in stack:
        modules.append("LLM integration")

    return {
        "productType": " + ".join(product_parts),
        "domain": "existing project inferred from repository docs and stack",
        "complexity": "high" if len(product_parts) > 1 or "monorepo" in stack else "medium",
        "requiredModules": sorted(set(modules)),
        "infrastructure": [item for item in stack if item in {"pnpm", "Turborepo", "Docker", "Docker Compose", "Supabase", "PostgreSQL"}],
    }


def architecture(stack: list[str], project: Path) -> dict[str, str]:
    is_monorepo = "monorepo" in stack
    return {
        "pattern": "modular monorepo" if is_monorepo else "modular monolith",
        "backend": "Next.js API routes and service packages" if "Next.js" in stack else "repository-defined backend",
        "frontend": "Next.js/React" if "Next.js" in stack else ("React" if "React" in stack else ""),
        "database": "Supabase/PostgreSQL" if "Supabase" in stack else "",
        "auth": "Supabase auth or project-specific auth" if "Supabase" in stack else "project-specific auth",
        "deployment": "Docker Compose" if "Docker Compose" in stack else ("Docker" if "Docker" in stack else "project-specific deployment"),
    }


def root_command(manager: str, script: str) -> list[str]:
    if manager == "pnpm":
        return ["pnpm", script]
    if manager == "yarn":
        return ["yarn", script]
    if manager == "npm":
        return ["npm", "run", script]
    return []


def package_script_command(project: Path, package_path: Path, package: dict[str, Any], script: str) -> list[str]:
    package_dir = package_path.parent
    manager = package_manager(package_dir, package)
    if not manager and package_dir != project:
        manager = package_manager(project, read_json(project / "package.json"))
    rel = package_dir.relative_to(project).as_posix()
    if package_dir == project:
        return root_command(manager, script)
    if manager == "pnpm":
        return ["pnpm", "--dir", rel, script]
    if manager == "yarn":
        return ["yarn", "--cwd", rel, script]
    if manager == "npm":
        return ["npm", "--prefix", rel, "run", script]
    return []


def add_command(commands: list[dict[str, Any]], name: str, command: list[str], script: str = "", cwd: str = ".") -> None:
    if not command:
        return
    text = command_text(command)
    if any(item.get("command") == text for item in commands):
        return
    commands.append({"name": name, "script": script or name, "cwd": cwd, "command": text, "commandArgv": command})


def make_targets(project: Path) -> set[str]:
    path = project / "Makefile"
    if not path.is_file():
        return set()
    targets = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+):(?:\s|$)", line)
        if match and not match.group(1).startswith("."):
            targets.add(match.group(1))
    return targets


def just_targets(project: Path) -> set[str]:
    path = project / "justfile"
    if not path.is_file():
        path = project / "Justfile"
    if not path.is_file():
        return set()
    targets = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+):(?:\s|$)", line)
        if match and not match.group(1).startswith("_"):
            targets.add(match.group(1))
    return targets


def available_commands(
    project: Path,
    root_package: dict[str, Any],
    manager: str,
    package_files: list[Path],
    packages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for package_path, package in zip(package_files, packages):
        scripts = package.get("scripts", {}) if isinstance(package, dict) else {}
        if not isinstance(scripts, dict):
            continue
        rel_dir = package_path.parent.relative_to(project).as_posix()
        for script in sorted(scripts):
            command = package_script_command(project, package_path, package, script)
            name = script if rel_dir == "." else f"{rel_dir}:{script}"
            add_command(commands, name, command, script=script, cwd=rel_dir)

    if (project / "scripts" / "check.py").is_file():
        add_command(commands, "check", ["python3", "scripts/check.py"], script="check")
    has_tests = (project / "tests").is_dir() or any(project.glob("test_*.py")) or any(project.glob("**/test_*.py"))
    if has_tests:
        add_command(commands, "pytest", ["python3", "-m", "pytest"], script="test")
    for target in sorted(make_targets(project) & {"build", "check", "lint", "test", "typecheck"}):
        add_command(commands, f"make:{target}", ["make", target], script=target)
    for target in sorted(just_targets(project) & {"build", "check", "lint", "test", "typecheck"}):
        add_command(commands, f"just:{target}", ["just", target], script=target)
    if (project / "go.mod").is_file():
        add_command(commands, "go:test", ["go", "test", "./..."], script="test")
    if (project / "Cargo.toml").is_file():
        add_command(commands, "cargo:test", ["cargo", "test"], script="test")
        add_command(commands, "cargo:check", ["cargo", "check"], script="check")
    return commands


def select_gates(project: Path, commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gates = []
    for script, gate in [
        ("build", "build"),
        ("lint", "lint"),
        ("test", "tests"),
        ("typecheck", "tests"),
        ("check", "tests"),
    ]:
        for item in commands:
            if item.get("script") == script:
                command = list(item.get("commandArgv", []))
                if script == "check" and command == ["python3", "scripts/check.py"]:
                    command = [sys.executable, "scripts/check.py", "--no-smoke"]
                gates.append({"gate": gate, "script": item["name"], "command": command})
    return gates


def run_gate(project: Path, gate: dict[str, Any], timeout: int) -> dict[str, Any]:
    command = gate["command"]
    result: dict[str, Any] = {
        "gate": gate["gate"],
        "script": gate["script"],
        "command": " ".join(command),
        "status": "NOT_RUN",
        "exitCode": None,
        "summary": "",
    }
    if not command:
        result["status"] = "SKIPPED"
        result["summary"] = "No command available."
        return result
    try:
        completed = subprocess.run(
            command,
            cwd=project,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
    except FileNotFoundError:
        result["status"] = "BLOCKED"
        result["summary"] = f"Command executable not found: {command[0]}"
        return result
    except subprocess.TimeoutExpired as exc:
        result["status"] = "BLOCKED"
        result["summary"] = f"Command timed out after {timeout}s."
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        output = (stdout + "\n" + stderr).strip()
        result["outputTail"] = "\n".join(output.splitlines()[-30:])
        return result

    output = (completed.stdout + "\n" + completed.stderr).strip()
    result["exitCode"] = completed.returncode
    result["outputTail"] = "\n".join(output.splitlines()[-30:])
    if completed.returncode == 0:
        result["status"] = "PASS"
        result["summary"] = "Command completed successfully."
    else:
        result["status"] = "BLOCKED"
        result["summary"] = f"Command failed with exit code {completed.returncode}."
    if "How would you like to configure ESLint" in output:
        result["status"] = "BLOCKED"
        result["summary"] = "Command requires interactive Next.js ESLint setup."
    return result


def run_contract_gate(project: Path) -> dict[str, Any]:
    command = [sys.executable, str(ROOT / "scripts" / "pfo_contract_gate.py"), str(project), "--write", "--json"]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "BLOCKED",
            "summary": "PFO contract gate timed out.",
            "blockers": ["PFO contract gate timed out."],
            "warnings": [],
            "riskClasses": [],
            "gates": {},
        }
    if completed.stdout.strip():
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError:
            pass
    return {
        "status": "PASS" if completed.returncode == 0 else "BLOCKED",
        "summary": (completed.stdout + completed.stderr).strip()[-1000:],
        "blockers": [] if completed.returncode == 0 else [(completed.stdout + completed.stderr).strip()],
        "warnings": [],
        "riskClasses": [],
        "gates": {},
    }


def security_findings(project: Path) -> list[str]:
    findings = []
    if os.environ.get("NODE_TLS_REJECT_UNAUTHORIZED") == "0":
        findings.append("NODE_TLS_REJECT_UNAUTHORIZED=0 is set in the execution environment.")
    gitignore = (project / ".gitignore").read_text(encoding="utf-8") if (project / ".gitignore").is_file() else ""
    ignored_env_local = any(line.strip() == ".env.local" for line in gitignore.splitlines())
    if (project / ".env.local").is_file() and not ignored_env_local:
        findings.append(".env.local exists but is not explicitly ignored by .gitignore.")
    return findings


def update_state(project: Path, state: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    has_strategy_artifacts = (project / "CODEX.md").is_file() and (project / ".codex-memory" / "MEMORY.md").is_file()
    has_architecture_artifacts = (project / "PFO_AUDIT.md").is_file() or (project / "docs" / "ARCHITECTURE.md").is_file()

    state["sessionState"] = "ACTIVE"
    state["currentStage"] = "REVIEWING" if analysis["gateRuns"] else "EXISTING_PROJECT_ANALYZED"
    state["intent"] = f"Existing project `{project.name}` analyzed by Product Factory OS."
    state["classification"] = analysis["classification"]
    state["architecture"] = analysis["architecture"]
    state["existingProject"] = {
        "isExistingProject": True,
        "detectedStack": analysis["detectedStack"],
        "availableCommands": [item["command"] for item in analysis["availableCommands"]],
        "currentTaskRoute": "/task -> adoption-check -> repository-analysis -> task-classification -> gates -> state-save",
        "lastAnalysisSummary": analysis["summary"],
    }
    gate_results = state.setdefault("gateResults", {})
    gate_results["strategy"] = "PASS" if has_strategy_artifacts else "PASS_WITH_WARNINGS"
    gate_results["architecture"] = "PASS" if has_architecture_artifacts else "PASS_WITH_WARNINGS"
    gate_results["dependencies"] = "NOT_RUN"
    gate_results["hardening"] = "NOT_RUN"
    gate_results["security"] = "BLOCKED" if analysis["securityFindings"] else "PASS"
    for key, value in analysis.get("contractGate", {}).get("gates", {}).items():
        gate_results[key] = value

    ran = {item["gate"]: item for item in analysis["gateRuns"]}
    available_command_names = {
        value
        for item in analysis.get("availableCommands", [])
        for value in [item.get("name"), item.get("script")]
        if value
    }
    if "build" in ran:
        gate_results["review"] = "PASS" if ran["build"]["status"] == "PASS" else "BLOCKED"
    else:
        gate_results["review"] = "NOT_RUN"
    if "tests" in ran:
        gate_results["tests"] = "PASS" if ran["tests"]["status"] == "PASS" else "BLOCKED"
    elif {"test", "typecheck", "check"} & available_command_names:
        gate_results["tests"] = "NOT_RUN"
    else:
        gate_results["tests"] = "NOT_CONFIGURED"
    deployment_blocked = (
        any(item["status"] != "PASS" for item in analysis["gateRuns"])
        or bool(analysis["securityFindings"])
        or analysis.get("contractGate", {}).get("status") == "BLOCKED"
    )
    gate_results["deploymentReadiness"] = "BLOCKED" if deployment_blocked else "PASS"

    blockers = []
    for item in analysis["gateRuns"]:
        if item["status"] != "PASS":
            blockers.append(f"{item['command']} -> {item['summary']}")
    blockers.extend(analysis["securityFindings"])
    blockers.extend(analysis.get("contractGate", {}).get("blockers", []))
    if gate_results["tests"] == "NOT_CONFIGURED":
        warnings = state.setdefault("warnings", [])
        if isinstance(warnings, list) and "No automated test/typecheck/check command was detected." not in warnings:
            warnings.append("No automated test/typecheck/check command was detected.")
    state["blockers"] = blockers
    steering = state.setdefault("humanSteering", default_human_steering())
    steering["approvalRequired"] = True
    steering["approvalStatus"] = "PENDING"
    steering["lastIterationSummary"] = analysis["summary"]
    steering["recommendedNextStep"] = (
        "Resolve analyzer blockers before any implementation work."
        if blockers
        else "Choose and approve the next task-specific implementation step."
    )
    steering["alternatives"] = [
        "Fix analyzer blockers first.",
        "Open a narrow task plan before implementation.",
        "Pause and review PFO_EXISTING_PROJECT_ANALYSIS.json.",
    ]
    steering["pendingQuestions"] = ["Confirm the next task before implementation starts."]
    gate_results["nextStepApproval"] = "PENDING"
    ensure_next_step_template(project)
    write_next_step(project, state)
    state["nextAction"] = "Review NEXT_STEP.md and approve or change the next task before implementation."
    state.setdefault("artifacts", [])
    for artifact in [
        "PFO_EXISTING_PROJECT_ANALYSIS.json",
        "PFO_CONTRACT_GATE.json",
        "PFO_REPORT.md",
    ]:
        if artifact not in state["artifacts"]:
            state["artifacts"].append(artifact)
    state.setdefault("verificationHistory", []).append(
        {
            "mode": "existing-project-analyze",
            "stage": state["currentStage"],
            "status": "BLOCKED" if blockers else "PASS",
            "summary": analysis["summary"],
        }
    )
    state.setdefault("decisionLog", []).append(
        {"event": "existing project analyzer run", "note": f"runGates={bool(analysis['gateRuns'])}"}
    )
    if not blockers:
        state["lastSuccessfulState"] = state["currentStage"]
    return state


def analyze(project: Path, run_gates: bool, timeout: int) -> dict[str, Any]:
    created_contracts = ensure_pfo_contracts(project)
    package_files = list_package_files(project)
    packages = [read_json(path) for path in package_files]
    root_package = read_json(project / "package.json")
    manager = package_manager(project, root_package)
    stack = detect_stack(project, packages)
    commands = available_commands(project, root_package, manager, package_files, packages)
    gates = select_gates(project, commands) if run_gates else []
    gate_runs = [run_gate(project, gate, timeout) for gate in gates]
    security = security_findings(project)
    contract_gate = run_contract_gate(project)
    classification = classify(stack, project)
    arch = architecture(stack, project)
    summary = (
        f"Detected {classification['productType']} with {', '.join(stack) or 'unknown stack'}. "
        f"Ran {len(gate_runs)} gate command(s)."
    )
    return {
        "project": str(project),
        "isMonorepo": "monorepo" in stack,
        "packageManager": manager,
        "packageFiles": [str(path.relative_to(project)) for path in package_files],
        "detectedStack": stack,
        "availableCommands": commands,
        "selectedGates": [{"gate": item["gate"], "script": item["script"], "command": command_text(item["command"])} for item in gates],
        "gateRuns": gate_runs,
        "securityFindings": security,
        "contractGate": contract_gate,
        "createdContracts": created_contracts,
        "classification": classification,
        "architecture": arch,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an existing project and write Product Factory OS state.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--run-gates", action="store_true", help="Run detected build/lint/test/typecheck commands.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    if not project.is_dir():
        fail(f"project does not exist: {project}")
    state_path, state = ensure_state(project)
    analysis = analyze(project, args.run_gates, args.timeout)
    write_json(project / "PFO_EXISTING_PROJECT_ANALYSIS.json", analysis)
    state = update_state(project, state, analysis)
    write_json(state_path, state)

    if args.json:
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    else:
        print(f"OK: analyzed {project}")
        print(f"Product type: {analysis['classification']['productType']}")
        print(f"Stack: {', '.join(analysis['detectedStack']) or 'unknown'}")
        if analysis["gateRuns"]:
            for item in analysis["gateRuns"]:
                print(f"{item['status']}: {item['command']} - {item['summary']}")
        if analysis["securityFindings"]:
            for finding in analysis["securityFindings"]:
                print(f"SECURITY: {finding}")


if __name__ == "__main__":
    main()
