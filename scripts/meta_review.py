#!/usr/bin/env python3
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text()


def fail(message: str) -> None:
    print(f"CRITICAL: {message}")
    sys.exit(1)


def warn(message: str, warnings: list[str]) -> None:
    warnings.append(message)


def skill_names() -> list[str]:
    return sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))


def fenced_routes() -> dict[str, str]:
    routes = {}
    for idea in (ROOT / "tests" / "fixtures").glob("*/idea.md"):
        text = idea.read_text()
        match = re.search(r"Expected route:\s*```text\s*(.*?)\s*```", text, re.S)
        if match:
            routes[idea.parent.name] = " ".join(match.group(1).split())
    return dict(sorted(routes.items()))


def main() -> None:
    warnings: list[str] = []
    skills = skill_names()
    contracts = read("docs/SKILL_CONTRACTS.md")
    triggers = read("docs/TRIGGERS.md")
    call_graph = read("docs/CALL_GRAPH.md")
    methodology = read("docs/METHODOLOGY.md")
    install = read("docs/INSTALL.md")
    workspace_defaults = read("docs/WORKSPACE_DEFAULTS.md")
    open_core = read("docs/OPEN_CORE.md")
    commercial = read("docs/COMMERCIAL.md")
    pfo_architecture = read("docs/PFO_ARCHITECTURE.md")
    master_prompt = read("docs/MASTER_PROMPT.ru.md")
    changelog = read("CHANGELOG.md")
    manifest = json.loads(read(".codex-plugin/plugin.json"))

    for skill in skills:
        token = f"`/{skill}`"
        if token not in contracts:
            fail(f"{token} missing from docs/SKILL_CONTRACTS.md")
        if token not in triggers:
            fail(f"{token} missing from docs/TRIGGERS.md")

    for rubric in ["review", "pfo", "strategy", "testing", "security", "deps", "production"]:
        path = ROOT / "docs" / "rubrics" / f"{rubric}.md"
        if not path.is_file():
            fail(f"missing rubric: {path.relative_to(ROOT)}")
        text = path.read_text()
        if "## Critical" not in text:
            fail(f"rubric {rubric} has no Critical section")

    if "BLOCKED" not in methodology or "PASSED_WITH_WARNINGS" not in methodology:
        fail("docs/METHODOLOGY.md must document gate statuses")

    version = manifest.get("version")
    if not version:
        fail("plugin manifest has no version")
    if f"## [{version}]" not in changelog:
        fail(f"CHANGELOG.md has no entry for manifest version {version}")

    for command in [
        "python3 scripts/validate_structure.py",
        "python3 scripts/run_fixtures.py",
        "python3 scripts/validate_execution_graph.py",
        "python3 scripts/validate_runtime.py",
        "python3 scripts/meta_review.py",
    ]:
        if command not in install:
            fail(f"docs/INSTALL.md must document {command}")

    if "CODEX.md" not in workspace_defaults or "PFO_WORKSPACE.json" not in workspace_defaults:
        fail("docs/WORKSPACE_DEFAULTS.md must document workspace policy files")
    if "EXISTING_PROJECT_DETECTED" not in workspace_defaults or "TASK_CLASSIFIED" not in workspace_defaults:
        fail("docs/WORKSPACE_DEFAULTS.md must document existing-project PFO state path")
    if "Products generated with Product Factory OS belong to their authors" not in open_core:
        fail("docs/OPEN_CORE.md must document generated product ownership")
    if "Commercial Boundary" not in commercial:
        fail("docs/COMMERCIAL.md must document commercial boundary")

    workspace_policy = ROOT.parent / "PFO_WORKSPACE.json"
    workspace_codex = ROOT.parent / "CODEX.md"
    if not workspace_policy.is_file() or not workspace_codex.is_file():
        warn(
            "workspace root policy files are absent; this is expected for a standalone GitHub clone",
            warnings,
        )

    routes = fenced_routes()
    if len(routes) < 8:
        fail("expected at least 8 routing fixtures for 0.5.0")

    for fixture, route in routes.items():
        if not route.startswith("/project") and not route.startswith("/task"):
            fail(f"fixture {fixture} route must start from /project or /task")
        for token in re.findall(r"/[a-z0-9-]+", route):
            if token[1:] not in skills:
                fail(f"fixture {fixture} references unknown skill {token}")

    for skill in ["kickstart", "blueprint", "review", "deploy", "session-save"]:
        text = (ROOT / "skills" / skill / "SKILL.md").read_text()
        if len(text.splitlines()) < 55:
            warn(f"skill /{skill} may still be thin", warnings)

    for required in [
        "routing/product-classifier.json",
        "templates/product-templates.json",
        "execution/state-machine.json",
        "memory/session-state.schema.json",
        "deployment/deployment-targets.json",
    ]:
        if required not in pfo_architecture:
            fail(f"docs/PFO_ARCHITECTURE.md must reference {required}")

    for required in [
        "PRODUCT_BLUEPRINT",
        "BUILD_PLAN",
        "EXECUTION_GRAPH",
        "CURRENT STATE",
        "DEPLOY_BLOCKED",
        "SECURITY_REVIEW",
        "DEPENDENCY_REVIEW",
    ]:
        if required not in master_prompt:
            fail(f"docs/MASTER_PROMPT.ru.md must document {required}")

    state_machine = json.loads(read("execution/state-machine.json"))
    transitions = state_machine.get("transitions", [])
    if not any(item.get("from") == "PLAN_READY" and item.get("to") == "BUILDING" for item in transitions):
        fail("state machine must define PLAN_READY -> BUILDING")
    if not any(item.get("to") == "DEPLOY_BLOCKED" for item in transitions):
        fail("state machine must define a DEPLOY_BLOCKED transition")
    if not any(item.get("from") == "EXISTING_PROJECT_ANALYZED" and item.get("to") == "TASK_CLASSIFIED" for item in transitions):
        fail("state machine must define EXISTING_PROJECT_ANALYZED -> TASK_CLASSIFIED")
    for source, target in [
        ("REVIEWING", "SECURITY_REVIEW"),
        ("SECURITY_REVIEW", "DEPENDENCY_REVIEW"),
        ("DEPENDENCY_REVIEW", "HARDENING"),
        ("HARDENING", "READY_FOR_DEPLOY"),
    ]:
        if not any(item.get("from") == source and item.get("to") == target for item in transitions):
            fail(f"state machine must define {source} -> {target}")

    graph_check = subprocess.run(
        [sys.executable, "scripts/validate_execution_graph.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if graph_check.returncode != 0:
        fail("execution graph validation failed: " + graph_check.stdout + graph_check.stderr)

    runtime_check = subprocess.run(
        [sys.executable, "scripts/validate_runtime.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if runtime_check.returncode != 0:
        fail("runtime validation failed: " + runtime_check.stdout + runtime_check.stderr)

    if "/deploy" not in call_graph or "/migrate" not in call_graph:
        fail("docs/CALL_GRAPH.md must include operations routes")

    golden = ROOT / "docs" / "examples" / "golden-path-booking-app"
    for required in [
        "README.md",
        "DISCOVERY.md",
        "PRD.md",
        "PRODUCT_BLUEPRINT.md",
        "PROJECT_ARCHITECTURE.md",
        "BUILD_PLAN.md",
        "EXECUTION_GRAPH.md",
        "IMPLEMENTATION_PLAN.md",
        "CODEX.md",
        "CODEX_GUIDE.md",
    ]:
        if not (golden / required).is_file():
            fail(f"golden path is missing {required}")

    if warnings:
        print("FINAL STATUS: PASSED_WITH_WARNINGS")
        for item in warnings:
            print(f"WARNING: {item}")
    else:
        print("FINAL STATUS: PASSED")
    print(f"Checked {len(skills)} skills and {len(routes)} fixtures")


if __name__ == "__main__":
    main()
