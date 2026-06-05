#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

import validate_release_live_headless as release_live
import verify_fixture_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "tests" / "eval-datasets"
HIGH_RISK_SKILLS = {
    "deploy",
    "migrate",
    "infra",
    "github-workflow",
    "tool-sync",
    "security-audit",
    "skill-create",
    "session-save",
    "seo",
}
ADVERSARIAL_FIXTURES = {
    "prompt-injection": "adversarial-prompt-injection",
    "mcp-tool-misuse": "adversarial-tool-misuse",
    "fake-data-substitution": "adversarial-fake-data",
}


def fail(errors: list[str]) -> None:
    print("Eval layer drift found:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.strip().split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_release_gate(errors: list[str]) -> None:
    try:
        release_live.validate_config(release_live.CRITICAL_RELEASE_FIXTURES)
    except SystemExit:
        errors.append("release live headless proof config is invalid")
    release_text = (ROOT / "scripts" / "release_check.py").read_text(encoding="utf-8")
    if "validate_release_live_headless.py" not in release_text:
        errors.append("release_check.py must run validate_release_live_headless.py")


def validate_quality_graders(errors: list[str]) -> None:
    loaded = contracts.all_contracts()
    used: set[str] = set()
    for name, contract in loaded.items():
        graders = contract.get("quality_graders", [])
        for grader in graders:
            used.add(grader)
            if grader not in contracts.QUALITY_GRADERS:
                errors.append(f"{name}: unknown quality grader {grader}")
    missing = contracts.QUALITY_GRADERS - used
    if missing:
        errors.append("quality graders are not all covered by fixtures: " + ", ".join(sorted(missing)))


def validate_high_risk_datasets(errors: list[str]) -> None:
    for skill in sorted(HIGH_RISK_SKILLS):
        path = ROOT / "skills" / skill / "SKILL.md"
        if not path.is_file():
            errors.append(f"/{skill}: missing SKILL.md")
            continue
        metadata = frontmatter(path.read_text(encoding="utf-8"))
        skill_version = metadata.get("skill_version")
        prompt_version = metadata.get("prompt_version")
        dataset_rel = metadata.get("eval_dataset")
        if not skill_version:
            errors.append(f"/{skill}: missing skill_version")
        if not prompt_version:
            errors.append(f"/{skill}: missing prompt_version")
        if not dataset_rel:
            errors.append(f"/{skill}: missing eval_dataset")
            continue
        dataset_path = ROOT / dataset_rel
        if not dataset_path.is_file():
            errors.append(f"/{skill}: missing eval dataset {dataset_rel}")
            continue
        dataset = load_json(dataset_path)
        if dataset.get("skill") != f"/{skill}":
            errors.append(f"{dataset_rel}: skill mismatch")
        if str(dataset.get("skillVersion")) != str(skill_version):
            errors.append(f"{dataset_rel}: skillVersion mismatch")
        if dataset.get("promptVersion") != prompt_version:
            errors.append(f"{dataset_rel}: promptVersion mismatch")
        cases = dataset.get("cases", [])
        if not isinstance(cases, list) or not cases:
            errors.append(f"{dataset_rel}: cases must be non-empty")
        if not any(case.get("kind") in {"critical-live", "adversarial"} for case in cases if isinstance(case, dict)):
            errors.append(f"{dataset_rel}: needs critical-live or adversarial case")


def validate_adversarial_fixtures(errors: list[str]) -> None:
    loaded = contracts.all_contracts()
    snapshots = contracts.route_fixtures()
    for kind, fixture in ADVERSARIAL_FIXTURES.items():
        fixture_dir = ROOT / "tests" / "fixtures" / fixture
        if not fixture_dir.is_dir():
            errors.append(f"{fixture}: missing adversarial fixture directory")
            continue
        if fixture not in loaded:
            errors.append(f"{fixture}: missing fixture contract")
            continue
        if fixture not in snapshots:
            errors.append(f"{fixture}: missing route snapshot")
        contract = loaded[fixture]
        if contract.get("adversarial_type") != kind:
            errors.append(f"{fixture}: adversarial_type must be {kind}")
        if "tool_safety" not in contract.get("quality_graders", []):
            errors.append(f"{fixture}: adversarial fixture must use tool_safety grader")
        text = "\n".join((fixture_dir / name).read_text(encoding="utf-8") for name in ["idea.md", "notes.md"])
        if not re.search(kind.replace("-", ".?"), text, flags=re.I):
            errors.append(f"{fixture}: prompt/notes must name {kind}")


def main() -> None:
    errors: list[str] = []
    validate_release_gate(errors)
    validate_quality_graders(errors)
    validate_high_risk_datasets(errors)
    validate_adversarial_fixtures(errors)
    if errors:
        fail(errors)
    print(
        "OK: eval layer has mandatory release live proof, quality graders, "
        "high-risk datasets, and adversarial fixtures"
    )


if __name__ == "__main__":
    main()
