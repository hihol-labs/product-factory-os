#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "DEFENSIVE_LAYERS.md"

LAYERS = [
    {
        "id": "task-specification",
        "artifacts": [
            "docs/templates/PRD.md",
            "docs/templates/BUILD_PLAN.md",
            "docs/templates/EXECUTION_GRAPH.md",
            "docs/templates/pfo/SCOPE_LOCK.md",
            "docs/templates/UNIT_CONTEXT_MANIFEST.json",
        ],
    },
    {
        "id": "context-provisioning",
        "artifacts": [
            "AGENTS.md",
            "CODEX.md",
            "docs/AGENT_HARNESS_ENGINEERING.md",
            "docs/templates/HANDOFF.md",
            "docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json",
            "scripts/validate_context_runtime.py",
            "hooks/context-budget.py",
            "hooks/session-diagnostics.py",
        ],
    },
    {
        "id": "execution-environment",
        "artifacts": [
            "scripts/adoption_check.py",
            "docs/templates/pfo/EXECUTION_POLICY.json",
            "docs/templates/pfo/PERMISSION_MATRIX.json",
            "docs/templates/pfo/PROJECT_CONTRACT.md",
            "scripts/pfo_permission_gate.py",
            "scripts/pfo_contract_gate.py",
            "scripts/validate_self_contracts.py",
            "scripts/validate_runtime.py",
        ],
    },
    {
        "id": "verification-feedback",
        "artifacts": [
            "docs/templates/pfo/VERIFICATION_CONTRACT.json",
            "docs/templates/TEST_PLAN.md",
            "docs/templates/QUALITY_GATES.md",
            "docs/CONTROL_HARNESS.md",
            "scripts/production_readiness.py",
            "scripts/validate_control_harness.py",
            "scripts/pfo_contract_gate.py",
        ],
    },
    {
        "id": "state-management",
        "artifacts": [
            "memory/session-state.schema.json",
            "docs/templates/HANDOFF.md",
            "docs/templates/BRANCH_FINISH.md",
            "scripts/validate_state.py",
            "scripts/pfo_context_runtime.py",
            "hooks/session-diagnostics.py",
        ],
    },
]

COMMAND = "python3 scripts/validate_defensive_layers.py"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def assert_contains(text: str, token: str, source: str) -> None:
    if token not in text:
        fail(f"{source} is missing {token!r}")


def validate_doc_shape(text: str) -> None:
    for heading in [
        "# Defensive Layers",
        "## Five Layers",
        "## Diagnostic Triage",
        "## Evidence Matrix",
        "## Systematic Check",
        "## Current Coverage Decision",
    ]:
        assert_contains(text, heading, "docs/DEFENSIVE_LAYERS.md")

    for layer in LAYERS:
        layer_id = layer["id"]
        assert_contains(text, f"| {layer_id} |", "docs/DEFENSIVE_LAYERS.md")
        assert_contains(text, f"`{layer_id}`", "docs/DEFENSIVE_LAYERS.md")
        for artifact in layer["artifacts"]:
            assert_contains(text, f"`{artifact}`", "docs/DEFENSIVE_LAYERS.md")

    ordered = [match.group(1) for match in re.finditer(r"^\d+\. `([^`]+)`:", text, re.M)]
    expected = [layer["id"] for layer in LAYERS]
    if ordered != expected:
        fail("docs/DEFENSIVE_LAYERS.md diagnostic order must be " + ", ".join(expected))

    assert_contains(text, COMMAND, "docs/DEFENSIVE_LAYERS.md")


def validate_artifacts() -> None:
    missing: list[str] = []
    for layer in LAYERS:
        for artifact in layer["artifacts"]:
            if not (ROOT / artifact).is_file():
                missing.append(f"{layer['id']}: {artifact}")
    if missing:
        fail("missing defensive layer artifacts:\n- " + "\n- ".join(missing))

    state = ROOT / ".codex-memory" / "STATE.json"
    if state.is_file():
        data = json.loads(state.read_text(encoding="utf-8"))
        for field in ["currentStage", "currentNode", "gateResults", "nextAction"]:
            if field not in data:
                fail(f".codex-memory/STATE.json is missing {field}")


def validate_wiring() -> None:
    required_snippets = {
        "scripts/validate_structure.py": [
            '"docs/DEFENSIVE_LAYERS.md"',
            '"scripts/validate_defensive_layers.py"',
        ],
        "scripts/validate_runtime.py": ['"validate_defensive_layers.py"', '"validate_self_contracts.py"'],
        "scripts/production_readiness.py": ['"scripts/validate_defensive_layers.py"', '"scripts/validate_self_contracts.py"'],
        "scripts/release_check.py": ['"scripts/validate_defensive_layers.py"', '"scripts/validate_self_contracts.py"'],
        ".github/workflows/validate.yml": [COMMAND, "python3 scripts/validate_self_contracts.py"],
        "docs/INSTALL.md": [COMMAND, "python3 scripts/validate_self_contracts.py"],
        "docs/PRODUCTION_READINESS.md": ["defensive layer diagnostics"],
        "scripts/meta_review.py": [COMMAND],
        "scripts/verify_install_sync.py": [COMMAND],
        "docs/METHODOLOGY.md": ["## Five Defensive Layers", "docs/DEFENSIVE_LAYERS.md"],
        "docs/PFO_ARCHITECTURE.md": ["### 5b. Defensive Diagnostics Layer", "docs/DEFENSIVE_LAYERS.md"],
        "docs/AGENT_HARNESS_ENGINEERING.md": ["## Defensive Layers", "docs/DEFENSIVE_LAYERS.md"],
        "docs/DESIGN_SPACE.md": ["Five-layer defensive diagnostics"],
        "docs/rubrics/pfo.md": ["Defensive layer diagnostics"],
    }
    for rel, snippets in required_snippets.items():
        text = read(rel)
        for snippet in snippets:
            assert_contains(text, snippet, rel)

    control_harness = read("docs/CONTROL_HARNESS.md")
    for token in [
        "| defensive-layer-diagnostics |",
        "`docs/DEFENSIVE_LAYERS.md`",
        "`scripts/validate_defensive_layers.py`",
    ]:
        assert_contains(control_harness, token, "docs/CONTROL_HARNESS.md")

    control_validator = read("scripts/validate_control_harness.py")
    for token in [
        '"id": "defensive-layer-diagnostics"',
        '"docs/DEFENSIVE_LAYERS.md"',
        '"scripts/validate_defensive_layers.py"',
    ]:
        assert_contains(control_validator, token, "scripts/validate_control_harness.py")


def main() -> None:
    if not DOC.is_file():
        fail("missing docs/DEFENSIVE_LAYERS.md")
    text = DOC.read_text(encoding="utf-8")
    validate_doc_shape(text)
    validate_artifacts()
    validate_wiring()
    print(f"OK: {len(LAYERS)} defensive layers validated and wired into PFO gates")


if __name__ == "__main__":
    main()
