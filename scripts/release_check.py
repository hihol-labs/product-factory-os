#!/usr/bin/env python3
from pathlib import Path
import json
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
    run([sys.executable, "scripts/run_fixtures.py"])
    run([sys.executable, "scripts/verify_triggers.py"])
    run([sys.executable, "scripts/verify_fixture_contracts.py"])
    run([sys.executable, "scripts/run_headless_fixtures.py", "--mode", "mock"])
    run([sys.executable, "scripts/verify_skill_profiles.py"])
    run([sys.executable, "scripts/validate_execution_graph.py"])
    run([sys.executable, "scripts/validate_runtime.py"])
    run([sys.executable, "scripts/validate_hooks.py"])
    run([sys.executable, "scripts/verify_manifest_drift.py"])
    run([sys.executable, "scripts/verify_install_sync.py"])
    run([sys.executable, "scripts/run_benchmarks.py"])
    run([sys.executable, "scripts/meta_review.py"])
    print(f"OK: release checks passed for {version}")


if __name__ == "__main__":
    main()
