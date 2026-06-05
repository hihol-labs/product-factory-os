#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PRODUCT_TYPES = {
    "saas",
    "messaging_bot",
    "api_service",
    "landing_page",
    "cli_tool",
    "data_scraper",
    "ecommerce",
    "mini_app",
    "internal_automation",
}
HARNESS_REGULATION_CATEGORIES = {"maintainability", "architecture_fitness", "behaviour"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    product_templates_path = ROOT / "templates" / "product-templates.json"
    product_templates = json.loads(product_templates_path.read_text(encoding="utf-8"))
    templates = product_templates.get("templates", {})
    if not isinstance(templates, dict) or not templates:
        fail("templates/product-templates.json must define templates")
    for name, template in templates.items():
        if not isinstance(template, dict):
            fail(f"template {name} must be an object")
        harness = template.get("harnessTemplate")
        if not isinstance(harness, dict):
            fail(f"template {name} missing harnessTemplate")
        for field in ["topology", "regulates", "guides", "fastSensors", "pipelineSensors", "continuousSensors"]:
            if field not in harness:
                fail(f"template {name} harnessTemplate missing {field}")
        regulates = set(harness.get("regulates", []))
        if not HARNESS_REGULATION_CATEGORIES.issubset(regulates):
            fail(f"template {name} harnessTemplate must regulate maintainability, architecture_fitness, and behaviour")
        for field in ["guides", "fastSensors", "pipelineSensors", "continuousSensors"]:
            value = harness.get(field)
            if not isinstance(value, list) or not value:
                fail(f"template {name} harnessTemplate.{field} must be a non-empty list")

    starters = {}
    for path in (ROOT / "starters").glob("*/STARTER.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for field in ["id", "productType", "stack", "folders", "commands", "requiredArtifacts"]:
            if field not in data:
                fail(f"{path} missing {field}")
        starters[data["id"]] = data

    starter_types = {item["productType"] for item in starters.values()}
    missing_starters = PRODUCT_TYPES - starter_types
    if missing_starters:
        fail("missing starter product types: " + ", ".join(sorted(missing_starters)))

    golden_paths = list((ROOT / "golden-paths").glob("*.json"))
    if len(golden_paths) < len(PRODUCT_TYPES):
        fail("not enough golden paths")
    seen_types = set()
    for path in golden_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        for field in ["id", "prompt", "productType", "starter", "route", "requiredArtifacts", "minimumGates"]:
            if field not in data:
                fail(f"{path} missing {field}")
        if data["starter"] not in starters:
            fail(f"{path} references unknown starter {data['starter']}")
        seen_types.add(data["productType"])
    missing_golden = PRODUCT_TYPES - seen_types
    if missing_golden:
        fail("missing golden paths for product types: " + ", ".join(sorted(missing_golden)))

    for script in [
        "pfo.py",
        "check.py",
        "pfo_runner.py",
        "existing_project_analyzer.py",
        "validate_project.py",
        "validate_plan_quality.py",
        "validate_control_harness.py",
        "validate_defensive_layers.py",
        "validate_self_contracts.py",
        "pfo_contract_gate.py",
        "pfo_permission_gate.py",
        "pfo_event_log.py",
        "pfo_context_runtime.py",
        "pfo_skill_scaffold.py",
        "validate_context_runtime.py",
        "validate_tool_registry.py",
        "voice_intent.py",
        "voice_transcribe.py",
        "pfo_metrics.py",
        "release_check.py",
        "validate_release_live_headless.py",
        "validate_eval_layer.py",
        "validate_starter_compliance.py",
        "pfo_report.py",
        "generate_execution_graph.py",
        "run_benchmarks.py",
        "validate_hooks.py",
        "export_integrations.py",
        "install_workspace.py",
    ]:
        if not (ROOT / "scripts" / script).is_file():
            fail(f"missing runtime script {script}")

    if not (ROOT / "interface" / "voice-command-contract.json").is_file():
        fail("missing voice command contract")
    events_schema = ROOT / "memory" / "events.schema.json"
    if not events_schema.is_file():
        fail("missing event log schema")
    json.loads(events_schema.read_text(encoding="utf-8"))
    for registry in [
        ROOT / "docs" / "templates" / "pfo" / "TOOL_CAPABILITY_REGISTRY.json",
        ROOT / "integrations" / "tool-capability-registry.json",
    ]:
        result = json.loads(registry.read_text(encoding="utf-8"))
        if not result.get("tools"):
            fail(f"{registry} must define tools")
    for path in ["templates/generated-ci/validate.yml", "templates/generated-ci/justfile"]:
        if not (ROOT / path).is_file():
            fail(f"missing generated-project CI template {path}")
    for path in [
        "dashboard/index.html",
        "benchmarks/prompts.json",
        "packaging/install.sh",
        "marketplace/marketplace-entry.json",
        "integrations/github-issues.json",
        "integrations/linear.json",
        "integrations/notion.json",
        "integrations/tool-capability-registry.json",
    ]:
        if not (ROOT / path).is_file():
            fail(f"missing runtime extension {path}")

    print(f"OK: {len(starters)} starters and {len(golden_paths)} golden paths validated")


if __name__ == "__main__":
    main()
