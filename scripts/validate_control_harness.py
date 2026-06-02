#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

CONTROL_DOC = ROOT / "docs" / "CONTROL_HARNESS.md"

RUNTIME_ONLY_ARTIFACTS = {
    ".codex-memory/STATE.json",
}

CONTROL_REGISTRY = [
    {
        "id": "intent-routing",
        "timing": "Feedforward",
        "evaluator": "Computational",
        "artifacts": [
            "hooks/route-reminder.py",
            "docs/TRIGGERS.md",
            "tests/snapshots/route-snapshots.json",
        ],
    },
    {
        "id": "product-classification",
        "timing": "Feedforward",
        "evaluator": "Computational",
        "artifacts": [
            "routing/product-classifier.json",
            "templates/product-templates.json",
            "core/product-compiler.md",
        ],
    },
    {
        "id": "planning-documents",
        "timing": "Feedforward",
        "evaluator": "Inferential",
        "artifacts": [
            "docs/templates/PRODUCT_BLUEPRINT.md",
            "docs/templates/PROJECT_ARCHITECTURE.md",
            "docs/templates/BUILD_PLAN.md",
            "skills/blueprint/SKILL.md",
        ],
    },
    {
        "id": "adversarial-planning",
        "timing": "Feedforward",
        "evaluator": "Inferential",
        "artifacts": [
            "skills/grill-me/SKILL.md",
            "skills/advisor/SKILL.md",
            "agents/architect.md",
        ],
    },
    {
        "id": "unit-context",
        "timing": "Feedforward",
        "evaluator": "Computational",
        "artifacts": [
            "docs/templates/pfo/EXECUTION_POLICY.json",
            "docs/templates/pfo/PERMISSION_MATRIX.json",
            "docs/templates/UNIT_CONTEXT_MANIFEST.json",
        ],
    },
    {
        "id": "verification-contract",
        "timing": "Feedforward",
        "evaluator": "Computational",
        "artifacts": [
            "docs/templates/pfo/VERIFICATION_CONTRACT.json",
            "docs/templates/TEST_PLAN.md",
            "docs/templates/QUALITY_GATES.md",
        ],
    },
    {
        "id": "session-security-guard",
        "timing": "Feedforward",
        "evaluator": "Computational",
        "artifacts": [
            "hooks/security-guard.py",
            "hooks/hooks.json",
            "docs/templates/pfo/EXECUTION_POLICY.json",
        ],
    },
    {
        "id": "context-economy",
        "timing": "Feedforward",
        "evaluator": "Computational",
        "artifacts": [
            "docs/AGENT_HARNESS_ENGINEERING.md",
            "skills/handoff/SKILL.md",
            "docs/templates/HANDOFF.md",
        ],
    },
    {
        "id": "tool-surface-discipline",
        "timing": "Feedforward",
        "evaluator": "Computational",
        "artifacts": [
            "docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json",
            "integrations/tool-capability-registry.json",
            "docs/AGENT_HARNESS_ENGINEERING.md",
        ],
    },
    {
        "id": "harness-templates",
        "timing": "Feedforward",
        "evaluator": "Computational",
        "artifacts": [
            "templates/product-templates.json",
            "starters/README.md",
            "golden-paths/README.md",
        ],
    },
    {
        "id": "market-validation",
        "timing": "Feedforward",
        "evaluator": "Inferential",
        "artifacts": [
            "skills/discover/SKILL.md",
            "skills/market-scan/SKILL.md",
            "docs/templates/IDEA_SCORECARD.md",
            "docs/templates/VALIDATION_PLAN.md",
            "docs/templates/MARKET_BRIEF.md",
            "docs/templates/FUNNEL_MODEL.md",
            "docs/templates/GO_TO_MARKET.md",
        ],
    },
    {
        "id": "seo-growth",
        "timing": "Feedforward",
        "evaluator": "Inferential",
        "artifacts": [
            "skills/seo/SKILL.md",
            "docs/templates/CONTENT_BACKLOG.md",
            "docs/templates/GO_TO_MARKET.md",
            "docs/templates/VALIDATION_PLAN.md",
        ],
    },
    {
        "id": "maturity-stage-gates",
        "timing": "Feedforward",
        "evaluator": "Inferential",
        "artifacts": [
            "skills/strategy/SKILL.md",
            "docs/templates/LAUNCH_MATURITY_GATE.md",
            "docs/templates/SCALE_MOAT_REGISTER.md",
        ],
    },
    {
        "id": "harnessability-assessment",
        "timing": "Feedforward",
        "evaluator": "Inferential",
        "artifacts": [
            "docs/DESIGN_SPACE.md",
            "docs/PFO_ARCHITECTURE.md",
            "docs/AGENT_HARNESS_ENGINEERING.md",
        ],
    },
    {
        "id": "route-regression",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            "scripts/run_fixtures.py",
            "scripts/verify_triggers.py",
            "scripts/verify_fixture_contracts.py",
        ],
    },
    {
        "id": "alias-integrity",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            "scripts/pfo_alias_targets.py",
            "scripts/pfo_contract_gate.py",
            "docs/templates/existing/MASTER_CONTEXT.md",
        ],
    },
    {
        "id": "methodology-ci",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            ".github/workflows/validate.yml",
            "scripts/validate_structure.py",
            "scripts/validate_runtime.py",
            "scripts/meta_review.py",
        ],
    },
    {
        "id": "quality-left-scheduling",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            "hooks/review-before-commit.py",
            ".github/workflows/validate.yml",
            "scripts/production_readiness.py",
        ],
    },
    {
        "id": "continuous-health-sensors",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            "scripts/production_readiness.py",
            "scripts/pfo_metrics.py",
            "scripts/validate_runtime.py",
        ],
    },
    {
        "id": "project-ci",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            "templates/generated-ci/validate.yml",
            "scripts/validate_project.py",
            "scripts/pfo_contract_gate.py",
        ],
    },
    {
        "id": "engineering-discipline",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            "scripts/validate_plan_quality.py",
            "docs/templates/ROOT_CAUSE.md",
            "docs/templates/BRANCH_FINISH.md",
        ],
    },
    {
        "id": "browser-smoke",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            "skills/browser-check/SKILL.md",
            "skills/browser-check/playwright/run.js",
            "docs/templates/TEST_PLAN.md",
        ],
    },
    {
        "id": "review-agent",
        "timing": "Feedback",
        "evaluator": "Inferential",
        "artifacts": [
            "skills/review/SKILL.md",
            "agents/reviewer.md",
            "docs/rubrics/review.md",
        ],
    },
    {
        "id": "security-review-agent",
        "timing": "Feedback",
        "evaluator": "Inferential",
        "artifacts": [
            "skills/security-audit/SKILL.md",
            "agents/security-reviewer.md",
            "docs/rubrics/security.md",
        ],
    },
    {
        "id": "ux-review-agent",
        "timing": "Feedback",
        "evaluator": "Inferential",
        "artifacts": [
            "agents/ux-reviewer.md",
            "skills/browser-check/SKILL.md",
            "docs/templates/QUALITY_GATES.md",
        ],
    },
    {
        "id": "human-approval",
        "timing": "Feedback",
        "evaluator": "Inferential",
        "artifacts": [
            "docs/METHODOLOGY.md",
            "docs/templates/pfo/PERMISSION_MATRIX.md",
            "skills/deploy/SKILL.md",
        ],
    },
    {
        "id": "human-steering",
        "timing": "Feedback",
        "evaluator": "Inferential",
        "artifacts": [
            "docs/METHODOLOGY.md",
            ".codex-memory/STATE.json",
            "NEXT_STEP.md",
        ],
    },
    {
        "id": "learning-promotion",
        "timing": "Feedback",
        "evaluator": "Computational",
        "artifacts": [
            "docs/templates/pfo/LEARNING_PROMOTION_GATE.md",
            "scripts/pfo_learn.py",
            "memory/LEARNING_REGISTRY.json",
        ],
    },
]


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
        "# Control Harness",
        "## Quadrant Matrix",
        "## Control Inventory",
        "## Precedence",
        "## Operating Rules",
        "## Lifecycle Mapping",
        "## Addition Checklist",
    ]:
        assert_contains(text, heading, "docs/CONTROL_HARNESS.md")

    for token in [
        "Feedforward",
        "Feedback",
        "Computational",
        "Inferential",
        "Computational feedforward",
        "Computational feedback",
        "Inferential feedforward",
        "Inferential feedback",
        "guides",
        "sensors",
    ]:
        assert_contains(text, token, "docs/CONTROL_HARNESS.md")


def validate_inventory(text: str) -> None:
    seen_quadrants: set[tuple[str, str]] = set()
    for item in CONTROL_REGISTRY:
        control_id = item["id"]
        assert_contains(text, f"| {control_id} |", "docs/CONTROL_HARNESS.md")
        seen_quadrants.add((item["timing"], item["evaluator"]))
        for artifact in item["artifacts"]:
            if artifact not in RUNTIME_ONLY_ARTIFACTS and not (ROOT / artifact).is_file():
                fail(f"{control_id} references missing artifact: {artifact}")
            assert_contains(text, f"`{artifact}`", "docs/CONTROL_HARNESS.md")

    required_quadrants = {
        ("Feedforward", "Computational"),
        ("Feedback", "Computational"),
        ("Feedforward", "Inferential"),
        ("Feedback", "Inferential"),
    }
    missing = required_quadrants - seen_quadrants
    if missing:
        labels = [f"{timing}/{evaluator}" for timing, evaluator in sorted(missing)]
        fail("control inventory misses quadrants: " + ", ".join(labels))


def validate_cross_docs() -> None:
    methodology = read("docs/METHODOLOGY.md")
    architecture = read("docs/PFO_ARCHITECTURE.md")
    design_space = read("docs/DESIGN_SPACE.md")
    agent_harness = read("docs/AGENT_HARNESS_ENGINEERING.md")
    install = read("docs/INSTALL.md")
    workflow = read(".github/workflows/validate.yml")

    for token in [
        "## Control Harness Model",
        "Feedforward controls",
        "Feedback controls",
        "Computational controls",
        "Inferential controls",
        "guides",
        "sensors",
        "docs/CONTROL_HARNESS.md",
    ]:
        assert_contains(methodology, token, "docs/METHODOLOGY.md")

    for token in [
        "### 5a. Control Harness Layer",
        "## Control Ownership",
        "maintainability, architecture fitness, and behaviour",
        "scripts/validate_control_harness.py",
    ]:
        assert_contains(architecture, token, "docs/PFO_ARCHITECTURE.md")

    assert_contains(design_space, "Control harness taxonomy", "docs/DESIGN_SPACE.md")
    assert_contains(design_space, "Harnessability", "docs/DESIGN_SPACE.md")
    assert_contains(design_space, "quality-left sensor scheduling", "docs/DESIGN_SPACE.md")
    for token in [
        "## Outer Harness Goals",
        "## Guides And Sensors",
        "## Ratchet",
        "## Quality Left",
        "## Regulation Categories",
        "## Context Economy",
        "## Tool Surface Discipline",
        "## Harnessability",
        "## Harness Templates",
        "## Evaluator Split",
        "## Human Steering",
    ]:
        assert_contains(agent_harness, token, "docs/AGENT_HARNESS_ENGINEERING.md")
    assert_contains(install, "python3 scripts/validate_control_harness.py", "docs/INSTALL.md")
    assert_contains(workflow, "python3 scripts/validate_control_harness.py", ".github/workflows/validate.yml")


def validate_quadrant_counts() -> None:
    counts: dict[tuple[str, str], int] = {}
    for item in CONTROL_REGISTRY:
        key = (item["timing"], item["evaluator"])
        counts[key] = counts.get(key, 0) + 1
    for key, minimum in {
        ("Feedforward", "Computational"): 3,
        ("Feedback", "Computational"): 5,
        ("Feedforward", "Inferential"): 3,
        ("Feedback", "Inferential"): 4,
    }.items():
        if counts.get(key, 0) < minimum:
            fail(f"quadrant {key[0]}/{key[1]} has only {counts.get(key, 0)} controls")


def validate_markdown_table(text: str) -> None:
    inventory_rows = [
        line for line in text.splitlines()
        if re.match(r"^\| [a-z0-9-]+ \|", line)
    ]
    if len(inventory_rows) != len(CONTROL_REGISTRY):
        fail(
            "control inventory row count does not match registry: "
            f"{len(inventory_rows)} != {len(CONTROL_REGISTRY)}"
        )


def main() -> None:
    if not CONTROL_DOC.is_file():
        fail("missing docs/CONTROL_HARNESS.md")
    text = CONTROL_DOC.read_text(encoding="utf-8")
    validate_doc_shape(text)
    validate_inventory(text)
    validate_quadrant_counts()
    validate_markdown_table(text)
    validate_cross_docs()
    print(f"OK: {len(CONTROL_REGISTRY)} control harness entries validated across all four quadrants")


if __name__ == "__main__":
    main()
