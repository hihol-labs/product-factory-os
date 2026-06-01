#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ".codex-plugin/plugin.json",
    ".github/workflows/validate.yml",
    "install.sh",
    "README.md",
    "README.ru.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "GOVERNANCE.md",
    "MASTER_CONTEXT.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "PROGRESS.md",
    "TESTING.md",
    "docs/PFO_ARCHITECTURE.md",
    "docs/DESIGN_SPACE.md",
    "docs/CONTROL_HARNESS.md",
    "docs/AGENT_HARNESS_ENGINEERING.md",
    "docs/demo.svg",
    "docs/MASTER_PROMPT.ru.md",
    "docs/INSTALL.md",
    "docs/HEADLESS_EXECUTION.md",
    "docs/PRODUCTION_READINESS.md",
    "docs/METHODOLOGY.md",
    "docs/SKILL_CONTRACTS.md",
    "docs/CALL_GRAPH.md",
    "docs/TRIGGERS.md",
    "docs/ROADMAP.md",
    "docs/GSD_INTEGRATION.md",
    "docs/SUPERPOWERS_INTEGRATION.md",
    "docs/WORKSPACE_DEFAULTS.md",
    "docs/OPEN_CORE.md",
    "docs/COMMERCIAL.md",
    "docs/PRICING.md",
    "docs/PACKS.md",
    "docs/CLOUD.md",
    "docs/GO_TO_MARKET_OPEN_CORE.md",
    "docs/OPENAI_MCP_INTEGRATIONS.md",
    "docs/AUTORESEARCH_INTEGRATION.md",
    "docs/RELEASE_NOTES_v0.6.1.md",
    "docs/RELEASE_NOTES_v1.0.0.md",
    "docs/RELEASE_NOTES_v0.6.0.md",
    "docs/gates/README.md",
    "docs/gates/scope-lock.md",
    "docs/gates/data-authenticity-gate.md",
    "docs/gates/golden-flow-tests.md",
    "docs/gates/regression-contract-gate.md",
    "docs/gates/fallback-policy-gate.md",
    "docs/gates/diff-risk-classifier.md",
    "docs/gates/no-silent-substitution-rule.md",
    "docs/rubrics/review.md",
    "docs/rubrics/pfo.md",
    "docs/rubrics/strategy.md",
    "docs/rubrics/testing.md",
    "docs/rubrics/security.md",
    "docs/rubrics/deps.md",
    "docs/rubrics/production.md",
    "docs/templates/DISCOVERY.md",
    "docs/templates/IDEA_SCORECARD.md",
    "docs/templates/VALIDATION_PLAN.md",
    "docs/templates/FEEDBACK_LOG.md",
    "docs/templates/ITERATION_REVIEW.md",
    "docs/templates/FUNNEL_MODEL.md",
    "docs/templates/LAUNCH_MATURITY_GATE.md",
    "docs/templates/SCALE_MOAT_REGISTER.md",
    "docs/templates/ASSET_REGISTER.md",
    "docs/templates/CONTENT_BACKLOG.md",
    "docs/templates/MARKET_BRIEF.md",
    "docs/templates/ICP.md",
    "docs/templates/GO_TO_MARKET.md",
    "docs/templates/BUSINESS_MODEL.md",
    "docs/templates/PRD.md",
    "docs/templates/PROJECT_ARCHITECTURE.md",
    "docs/templates/PRODUCT_BLUEPRINT.md",
    "docs/templates/BUILD_PLAN.md",
    "docs/templates/EXECUTION_GRAPH.md",
    "docs/templates/THREAT_MODEL.md",
    "docs/templates/DATA_CLASSIFICATION.md",
    "docs/templates/TEST_PLAN.md",
    "docs/templates/QUALITY_GATES.md",
    "docs/templates/NEXT_STEP.md",
    "docs/templates/PHASE_CONTEXT.md",
    "docs/templates/HANDOFF.md",
    "docs/templates/UNIT_CONTEXT_MANIFEST.json",
    "docs/templates/EXPERIMENT_LOOP.md",
    "docs/templates/PFO_RECOVERY.md",
    "docs/templates/LEARNINGS.md",
    "docs/templates/ROOT_CAUSE.md",
    "docs/templates/BRANCH_FINISH.md",
    "docs/templates/pfo/PROJECT_CONTRACT.md",
    "docs/templates/pfo/DATA_POLICY.md",
    "docs/templates/pfo/GOLDEN_FLOWS.md",
    "docs/templates/pfo/FORBIDDEN_CHANGES.md",
    "docs/templates/pfo/FALLBACK_POLICY.md",
    "docs/templates/pfo/SCOPE_LOCK.md",
    "docs/templates/pfo/EXECUTION_POLICY.json",
    "docs/templates/pfo/PERMISSION_MATRIX.md",
    "docs/templates/pfo/PERMISSION_MATRIX.json",
    "docs/templates/pfo/VERIFICATION_CONTRACT.json",
    "docs/templates/pfo/LEARNING_PROMOTION_GATE.md",
    "docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json",
    "templates/generated-ci/validate.yml",
    "templates/generated-ci/justfile",
    "docs/templates/IMPLEMENTATION_PLAN.md",
    "docs/templates/AGENTS.md",
    "docs/templates/CODEX.md",
    "docs/templates/MASTER_CONTEXT.md",
    "docs/templates/ARCHITECTURE.md",
    "docs/templates/TASKS.md",
    "docs/templates/PROGRESS.md",
    "docs/templates/TESTING.md",
    "docs/templates/existing/MASTER_CONTEXT.md",
    "docs/templates/existing/ARCHITECTURE.md",
    "docs/templates/existing/TASKS.md",
    "docs/templates/existing/PROGRESS.md",
    "docs/templates/existing/TESTING.md",
    "docs/examples/golden-path-booking-app/README.md",
    "docs/examples/golden-path-booking-app/DISCOVERY.md",
    "docs/examples/golden-path-booking-app/PRD.md",
    "docs/examples/golden-path-booking-app/PRODUCT_BLUEPRINT.md",
    "docs/examples/golden-path-booking-app/PROJECT_ARCHITECTURE.md",
    "docs/examples/golden-path-booking-app/BUILD_PLAN.md",
    "docs/examples/golden-path-booking-app/EXECUTION_GRAPH.md",
    "docs/examples/golden-path-booking-app/IMPLEMENTATION_PLAN.md",
    "docs/examples/golden-path-booking-app/CODEX.md",
    "docs/examples/golden-path-booking-app/CODEX_GUIDE.md",
    "hooks/hooks.json",
    "hooks/README.md",
    "hooks/route-reminder.py",
    "hooks/preflight-context.py",
    "hooks/security-guard.py",
    "hooks/session-diagnostics.py",
    "hooks/skill-completeness.py",
    "hooks/commit-completeness.py",
    "hooks/review-before-commit.py",
    "core/README.md",
    "core/product-compiler.md",
    "routing/product-classifier.json",
    "templates/product-templates.json",
    "pipelines/execution-pipeline.json",
    "execution/state-machine.json",
    "memory/session-state.schema.json",
    "memory/LEARNING_REGISTRY.json",
    "memory/events.schema.json",
    "deployment/deployment-targets.json",
    "interface/voice-first.md",
    "interface/voice-command-contract.json",
    "interface/voice-to-text.md",
    "dashboard/index.html",
    "dashboard/README.md",
    "benchmarks/prompts.json",
    "packaging/install.sh",
    "packaging/README.md",
    "marketplace/marketplace-entry.json",
    "commercial/README.md",
    "commercial/premium-packs.md",
    "commercial/cloud-roadmap.md",
    "commercial/enterprise.md",
    "integrations/README.md",
    "integrations/github-issues.json",
    "integrations/linear.json",
    "integrations/notion.json",
    "integrations/google-drive.json",
    "integrations/obsidian.json",
    "integrations/mcp-capabilities.json",
    "integrations/tool-capability-registry.json",
    "starters/README.md",
    "golden-paths/README.md",
    "tests/README.md",
    "tests/fixture-contracts.json",
    "tests/snapshots/route-snapshots.json",
    "scripts/run_fixtures.py",
    "scripts/run_headless_fixtures.py",
    "scripts/pfo_headless_adapter.py",
    "scripts/verify_triggers.py",
    "scripts/verify_fixture_contracts.py",
    "scripts/verify_skill_profiles.py",
    "scripts/verify_manifest_drift.py",
    "scripts/verify_install_sync.py",
    "scripts/production_readiness.py",
    "scripts/meta_review.py",
    "scripts/validate_hooks.py",
    "scripts/install_workspace.py",
    "scripts/adoption_check.py",
    "scripts/existing_project_analyzer.py",
    "scripts/validate_execution_graph.py",
    "scripts/validate_state.py",
    "scripts/validate_runtime.py",
    "scripts/validate_project.py",
    "scripts/pfo_alias_targets.py",
    "scripts/validate_plan_quality.py",
    "scripts/validate_control_harness.py",
    "scripts/pfo_contract_gate.py",
    "scripts/pfo_permission_gate.py",
    "scripts/pfo_event_log.py",
    "scripts/validate_tool_registry.py",
    "scripts/validate_starter_compliance.py",
    "scripts/pfo.py",
    "scripts/pfo_learn.py",
    "scripts/pfo_runner.py",
    "scripts/pfo_report.py",
    "scripts/voice_intent.py",
    "scripts/voice_transcribe.py",
    "scripts/pfo_metrics.py",
    "scripts/pfo_report.py",
    "scripts/generate_execution_graph.py",
    "scripts/run_benchmarks.py",
    "scripts/export_integrations.py",
    "scripts/release_check.py",
    "scripts/pfo_new_project.py",
]

REQUIRED_SKILLS = [
    "project",
    "task",
    "discover",
    "market-scan",
    "blueprint",
    "guide",
    "kickstart",
    "review",
    "test",
    "bugfix",
    "refactor",
    "doc",
    "explain",
    "security-audit",
    "deps-audit",
    "mcp-docs",
    "skill-create",
    "perf",
    "browser-check",
    "harden",
    "infra",
    "deploy",
    "migrate",
    "github-workflow",
    "tool-sync",
    "obsidian-export",
    "handoff",
    "session-save",
    "advisor",
    "grill-me",
    "strategy",
    "adopt",
]

REQUIRED_AGENTS = [
    "architect",
    "reviewer",
    "tester",
    "business-analyst",
    "security-reviewer",
    "operator",
    "orchestrator",
    "backend-builder",
    "frontend-builder",
    "memory-agent",
    "researcher",
    "ux-reviewer",
    "release-manager",
    "integration-engineer",
    "data-reviewer",
]

REQUIRED_FIXTURES = [
    "new-project",
    "existing-bug",
    "planning-only",
    "discover",
    "market-scan",
    "guide-existing-docs",
    "review-quality",
    "test-existing-feature",
    "refactor-module",
    "doc-readme",
    "explain-code",
    "perf-bottleneck",
    "deploy-production",
    "security-audit",
    "deps-audit",
    "harden-service",
    "infra-generate",
    "browser-check",
    "mcp-docs",
    "skill-create",
    "github-workflow",
    "tool-sync",
    "obsidian-export",
    "handoff",
    "strategy-replan",
    "advisor-decision",
    "grill-me",
    "session-save",
    "adopt-existing",
    "migration",
    "pfo-bot",
]

PFO_PRODUCT_TYPES = [
    "saas",
    "messaging_bot",
    "api_service",
    "web_app",
    "landing_page",
    "cli_tool",
    "mini_app",
    "ecommerce",
    "data_scraper",
    "internal_automation",
]

REFERENCE_CHECKS = {
    "review": "docs/rubrics/review.md",
    "security-audit": "docs/rubrics/security.md",
    "deps-audit": "docs/rubrics/deps.md",
    "harden": "docs/rubrics/production.md",
    "deploy": "docs/rubrics/production.md",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")

    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
    if manifest.get("name") != "product-factory-os":
        fail("plugin manifest name must be product-factory-os")
    if manifest.get("skills") != "./skills/":
        fail("plugin manifest must point skills to ./skills/")
    if manifest.get("hooks") != "./hooks/hooks.json":
        fail("plugin manifest must point hooks to ./hooks/hooks.json")

    classifier = json.loads((ROOT / "routing/product-classifier.json").read_text())
    if classifier.get("version", 0) < 2:
        fail("product classifier must be version 2 or newer")
    stack_policy = classifier.get("defaultStackPolicy", {})
    if stack_policy.get("id") != "pfo-default-stack-v1":
        fail("product classifier must define PFO Default Stack v1")
    if "deviationPolicy" not in stack_policy:
        fail("product classifier default stack policy must define deviationPolicy")
    classifier_types = {item.get("id") for item in classifier.get("productTypes", [])}
    for product_type in PFO_PRODUCT_TYPES:
        if product_type not in classifier_types:
            fail(f"product classifier is missing {product_type}")
    for item in classifier.get("productTypes", []):
        for field in [
            "defaultMonetization",
            "defaultDataSensitivity",
            "recommendedStack",
            "stackPreset",
            "stackDeviationPolicy",
            "requiredStrategyArtifacts",
            "requiredSecurityArtifacts",
        ]:
            if field not in item:
                fail(f"product classifier item {item.get('id')} is missing {field}")

    templates = json.loads((ROOT / "templates/product-templates.json").read_text())
    if templates.get("version", 0) < 2:
        fail("template library must be version 2 or newer")
    template_names = set(templates.get("templates", {}).keys())
    for product_type in PFO_PRODUCT_TYPES:
        if product_type not in template_names:
            fail(f"template library is missing {product_type}")
        template = templates.get("templates", {}).get(product_type, {})
        for field in ["modules", "defaultFolders", "testMinimums", "securityMinimums", "deployMinimums"]:
            if field not in template:
                fail(f"template {product_type} is missing {field}")

    state_machine = json.loads((ROOT / "execution/state-machine.json").read_text())
    states = set(state_machine.get("states", []))
    for state in [
        "IDLE",
        "EXISTING_PROJECT_DETECTED",
        "ADOPTION_REQUIRED",
        "ADOPTED",
        "EXISTING_PROJECT_ANALYZED",
        "TASK_CLASSIFIED",
        "CLASSIFIED",
        "PHASE_DISCUSSION",
        "PLAN_READY",
        "NEXT_STEP_REVIEW",
        "UNIT_CONTEXT_READY",
        "EXPERIMENT_READY",
        "EXPERIMENT_RUNNING",
        "EXPERIMENT_EVALUATED",
        "HANDOFF_READY",
        "UNIT_DISPATCHED",
        "ROOT_CAUSE_ANALYSIS",
        "TDD_EVIDENCE",
        "BUILDING",
        "VERIFYING_WORK",
        "TWO_STAGE_REVIEW",
        "SECURITY_REVIEW",
        "DEPENDENCY_REVIEW",
        "HARDENING",
        "RECOVERY_REQUIRED",
        "REPAIRING",
        "ROLLBACK_READY",
        "BRANCH_FINISH",
        "READY_FOR_DEPLOY",
        "DEPLOY_BLOCKED",
        "SESSION_SAVED",
    ]:
        if state not in states:
            fail(f"state machine is missing state {state}")

    memory_schema = json.loads((ROOT / "memory/session-state.schema.json").read_text())
    for field in [
        "sessionState",
        "currentStage",
        "classification",
        "architecture",
        "existingProject",
        "currentNode",
        "gateResults",
        "verificationHistory",
        "decisionLog",
        "lastSuccessfulState",
        "humanSteering",
        "nextAction",
    ]:
        if field not in memory_schema.get("requiredFields", []):
            fail(f"memory schema is missing required field {field}")

    pipeline = json.loads((ROOT / "pipelines/execution-pipeline.json").read_text())
    for stage in [
        "PRODUCT_CLASSIFICATION",
        "PHASE_DISCUSSION",
        "NEXT_STEP_REVIEW",
        "UNIT_CONTEXT_MANIFEST",
        "HANDOFF",
        "EXPERIMENT_PROGRAM",
        "EXPERIMENT_EVALUATION",
        "EXECUTION_PLAN_GENERATION",
        "ROOT_CAUSE_ANALYSIS",
        "EXECUTION_POLICY",
        "VERIFICATION_CONTRACT",
        "TDD_EVIDENCE",
        "UNIT_VERIFICATION",
        "TWO_STAGE_REVIEW",
        "VALIDATION_GATES",
        "BRANCH_FINISH",
        "LEARNING_PROMOTION",
        "SESSION_PERSISTENCE",
    ]:
        if stage not in pipeline.get("pipeline", []):
            fail(f"execution pipeline is missing stage {stage}")

    deployment_targets = json.loads((ROOT / "deployment/deployment-targets.json").read_text())
    for target in ["docker", "vps", "vercel", "netlify", "aws", "gcp", "azure"]:
        if target not in deployment_targets.get("targets", {}):
            fail(f"deployment targets are missing {target}")

    hooks = json.loads((ROOT / "hooks/hooks.json").read_text())
    hook_names = {hook.get("name") for hook in hooks.get("hooks", [])}
    for expected_hook in ["route-reminder", "preflight-context", "security-guard", "session-diagnostics", "skill-completeness", "commit-completeness", "review-before-commit"]:
        if expected_hook not in hook_names:
            fail(f"hooks/hooks.json is missing hook {expected_hook}")

    contracts = (ROOT / "docs/SKILL_CONTRACTS.md").read_text()
    triggers = (ROOT / "docs/TRIGGERS.md").read_text()
    call_graph = (ROOT / "docs/CALL_GRAPH.md").read_text()

    for skill in REQUIRED_SKILLS:
        path = ROOT / "skills" / skill / "SKILL.md"
        if not path.is_file():
            fail(f"missing skill file: skills/{skill}/SKILL.md")
        text = path.read_text()
        if f"name: {skill}" not in text:
            fail(f"skill {skill} has missing or mismatched frontmatter name")
        if f"`/{skill}`" not in contracts:
            fail(f"skill {skill} is missing from docs/SKILL_CONTRACTS.md")
        if f"`/{skill}`" not in triggers:
            fail(f"skill {skill} is missing from docs/TRIGGERS.md")
        if skill in REFERENCE_CHECKS and REFERENCE_CHECKS[skill] not in text:
            fail(f"skill {skill} does not reference {REFERENCE_CHECKS[skill]}")

    for skill in ["blueprint", "kickstart", "session-save"]:
        text = (ROOT / "skills" / skill / "SKILL.md").read_text()
        for token in ["PRODUCT_BLUEPRINT.md", "BUILD_PLAN.md", "EXECUTION_GRAPH.md"]:
            if token not in text:
                fail(f"skill {skill} does not reference {token}")

    for skill, tokens in {
        "strategy": ["docs/rubrics/strategy.md", "MARKET_BRIEF.md", "ICP.md"],
        "test": ["docs/rubrics/testing.md", "TEST_PLAN.md"],
        "security-audit": ["THREAT_MODEL.md", "DATA_CLASSIFICATION.md"],
        "review": ["docs/rubrics/pfo.md", "scripts/validate_execution_graph.py"],
    }.items():
        text = (ROOT / "skills" / skill / "SKILL.md").read_text()
        for token in tokens:
            if token not in text:
                fail(f"skill {skill} does not reference {token}")

    task = (ROOT / "skills" / "task" / "SKILL.md").read_text()
    for token in ["EXISTING_PROJECT_DETECTED", "TASK_CLASSIFIED", ".codex-memory/STATE.json"]:
        if token not in task:
            fail(f"skill task does not reference existing-project PFO token {token}")

    adopt = (ROOT / "skills" / "adopt" / "SKILL.md").read_text()
    for token in ["ADOPTION_REQUIRED", "ADOPTED", ".codex-memory/STATE.json"]:
        if token not in adopt:
            fail(f"skill adopt does not reference existing-project PFO token {token}")

    for routed in [
        "project",
        "task",
        "kickstart",
        "blueprint",
        "guide",
        "review",
        "test",
        "security-audit",
        "deps-audit",
        "mcp-docs",
        "skill-create",
        "browser-check",
        "harden",
        "deploy",
        "github-workflow",
        "tool-sync",
        "obsidian-export",
        "handoff",
        "session-save",
    ]:
        if f"/{routed}" not in call_graph:
            fail(f"/{routed} is missing from docs/CALL_GRAPH.md")

    for agent in REQUIRED_AGENTS:
        path = ROOT / "agents" / f"{agent}.md"
        if not path.is_file():
            fail(f"missing agent role file: agents/{agent}.md")
        text = path.read_text()
        if f"name: {agent}" not in text:
            fail(f"agent {agent} has missing or mismatched frontmatter name")

    for fixture in REQUIRED_FIXTURES:
        fixture_dir = ROOT / "tests" / "fixtures" / fixture
        if not fixture_dir.is_dir():
            fail(f"missing fixture directory: tests/fixtures/{fixture}")
        for name in ["idea.md", "expected-files.txt", "notes.md"]:
            if not (fixture_dir / name).is_file():
                fail(f"fixture {fixture} is missing {name}")

    fixture_contracts = json.loads((ROOT / "tests" / "fixture-contracts.json").read_text())
    contract_names = set(fixture_contracts.get("fixtures", {}))
    for fixture in REQUIRED_FIXTURES:
        if fixture not in contract_names:
            fail(f"fixture {fixture} is missing behavioural contract")

    snapshots = json.loads((ROOT / "tests" / "snapshots" / "route-snapshots.json").read_text())
    snapshot_fixtures = {item.get("fixture") for item in snapshots.get("snapshots", [])}
    for fixture in REQUIRED_FIXTURES:
        if fixture not in snapshot_fixtures:
            fail(f"route snapshots are missing fixture {fixture}")

    print(
        f"OK: {len(REQUIRED_SKILLS)} skills, {len(REQUIRED_AGENTS)} agents, "
        f"{len(REQUIRED_FIXTURES)} fixtures, PFO runtime contracts, and core methodology files are present"
    )


if __name__ == "__main__":
    main()
