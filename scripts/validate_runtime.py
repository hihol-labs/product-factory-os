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


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
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
        "pfo_runner.py",
        "existing_project_analyzer.py",
        "validate_project.py",
        "voice_intent.py",
        "voice_transcribe.py",
        "pfo_metrics.py",
        "release_check.py",
        "validate_starter_compliance.py",
        "pfo_report.py",
        "generate_execution_graph.py",
        "run_benchmarks.py",
        "export_integrations.py",
    ]:
        if not (ROOT / "scripts" / script).is_file():
            fail(f"missing runtime script {script}")

    if not (ROOT / "interface" / "voice-command-contract.json").is_file():
        fail("missing voice command contract")
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
    ]:
        if not (ROOT / path).is_file():
            fail(f"missing runtime extension {path}")

    print(f"OK: {len(starters)} starters and {len(golden_paths)} golden paths validated")


if __name__ == "__main__":
    main()
