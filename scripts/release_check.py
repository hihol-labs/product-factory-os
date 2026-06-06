#!/usr/bin/env python3
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        fail(result.stdout + result.stderr)


def main() -> None:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = manifest.get("version")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if not version or f"## [{version}]" not in changelog:
        fail("manifest version must exist in CHANGELOG.md")
    run([sys.executable, "scripts/validate_structure.py"])
    run([sys.executable, "scripts/validate_plan_quality.py", "--self-check"])
    run([sys.executable, "scripts/validate_control_harness.py"])
    run([sys.executable, "scripts/validate_defensive_layers.py"])
    run([sys.executable, "scripts/validate_self_contracts.py"])
    run([sys.executable, "scripts/pfo_contract_gate.py", str(ROOT)])
    run([sys.executable, "scripts/run_fixtures.py"])
    run([sys.executable, "scripts/verify_triggers.py"])
    run([sys.executable, "scripts/verify_fixture_contracts.py"])
    run([sys.executable, "scripts/run_headless_fixtures.py", "--mode", "mock"])
    live_proof = os.environ.get("PFO_RELEASE_LIVE_PROOF")
    live_command = [sys.executable, "scripts/validate_release_live_headless.py"]
    if live_proof:
        live_command.extend(["--proof-root", live_proof])
    run(live_command)
    run([sys.executable, "scripts/validate_eval_layer.py"])
    run([sys.executable, "scripts/validate_workspace_targets.py"])
    run([sys.executable, "scripts/verify_skill_profiles.py"])
    run([sys.executable, "scripts/validate_execution_graph.py"])
    run([sys.executable, "scripts/validate_runtime.py"])
    run([sys.executable, "scripts/validate_tool_registry.py", "docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json", "integrations/tool-capability-registry.json"])
    run([sys.executable, "scripts/validate_hooks.py"])
    run([sys.executable, "scripts/verify_manifest_drift.py"])
    run([sys.executable, "scripts/verify_install_sync.py"])
    run([sys.executable, "scripts/run_benchmarks.py"])
    run([sys.executable, "scripts/meta_review.py"])
    print(f"OK: release checks passed for {version}")


if __name__ == "__main__":
    main()
