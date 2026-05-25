#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
SNAPSHOTS = ROOT / "tests" / "snapshots" / "route-snapshots.json"
REGISTRY = ROOT / "tests" / "fixture-contracts.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def read_fixture_file(fixture: Path, name: str) -> str:
    path = fixture / name
    if not path.is_file():
        fail(f"{fixture.name}: missing {name}")
    return path.read_text(encoding="utf-8")


def count_scenarios(text: str) -> int:
    return len(re.findall(r"(?im)^\s*(?:##+\s*)?(?:scenario|сценарий)\b", text))


def check_text_contract(fixture: Path, file_name: str, contract: dict) -> list[str]:
    text = read_fixture_file(fixture, file_name)
    errors: list[str] = []
    for item in contract.get("must_contain", []):
        if item not in text:
            errors.append(f"{fixture.name}/{file_name}: missing {item!r}")
    for item in contract.get("must_not_contain", []):
        if item in text:
            errors.append(f"{fixture.name}/{file_name}: forbidden {item!r}")
    minimum = contract.get("min_scenario_count")
    if minimum is not None and count_scenarios(text) < int(minimum):
        errors.append(f"{fixture.name}/{file_name}: expected at least {minimum} scenarios")
    minimum_length = contract.get("min_length_chars")
    if minimum_length is not None and len(text) < int(minimum_length):
        errors.append(f"{fixture.name}/{file_name}: expected at least {minimum_length} chars")
    return errors


def deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def route_fixtures() -> dict[str, set[str]]:
    data = json.loads(SNAPSHOTS.read_text(encoding="utf-8"))
    fixtures: dict[str, set[str]] = {}
    for item in data.get("snapshots", []):
        fixtures.setdefault(item["fixture"], set()).add(item["skill"])
    return fixtures


def load_registry() -> dict[str, dict]:
    if not REGISTRY.is_file():
        return {}
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return data.get("fixtures", {})


def load_contract(fixture: Path, registry: dict[str, dict]) -> dict:
    data = dict(registry.get(fixture.name, {}))
    path = fixture / "expected-contract.json"
    if path.is_file():
        data = deep_merge(data, json.loads(path.read_text(encoding="utf-8")))
    return data


def check_output_contract(fixture: Path, data: dict) -> list[str]:
    errors: list[str] = []
    output = data.get("output_contract")
    if not isinstance(output, dict):
        return [f"{fixture.name}: missing output_contract"]
    has_assertion = any(
        output.get(key)
        for key in [
            "required_files",
            "forbidden_files",
            "stdout_must_contain",
            "files_must_contain",
            "files_must_not_contain",
            "any_file_must_contain",
        ]
    )
    if not has_assertion:
        errors.append(f"{fixture.name}: output_contract has no assertions")
    return errors


def read_output_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def output_files(output_dir: Path) -> list[Path]:
    if not output_dir.exists():
        return []
    return [path for path in output_dir.rglob("*") if path.is_file()]


def validate_output(fixture_name: str, contract: dict, output_dir: Path, stdout_text: str = "") -> list[str]:
    output = contract.get("output_contract", {})
    errors: list[str] = []
    for item in output.get("required_files", []):
        target = output_dir / item
        if item.endswith("/"):
            if not target.is_dir():
                errors.append(f"{fixture_name}: missing required directory {item}")
        elif not target.is_file():
            errors.append(f"{fixture_name}: missing required file {item}")

    for pattern in output.get("forbidden_files", []):
        matches = list(output_dir.glob(pattern))
        if matches:
            rendered = ", ".join(str(path.relative_to(output_dir)) for path in matches[:5])
            errors.append(f"{fixture_name}: forbidden output matched {pattern}: {rendered}")

    for item in output.get("stdout_must_contain", []):
        if item.lower() not in stdout_text.lower():
            errors.append(f"{fixture_name}: stdout missing {item!r}")

    for rel, tokens in output.get("files_must_contain", {}).items():
        target = output_dir / rel
        if not target.is_file():
            errors.append(f"{fixture_name}: cannot check missing file {rel}")
            continue
        text = read_output_file(target)
        for token in tokens:
            if token.lower() not in text.lower():
                errors.append(f"{fixture_name}: {rel} missing {token!r}")

    for rel, tokens in output.get("files_must_not_contain", {}).items():
        target = output_dir / rel
        if not target.is_file():
            continue
        text = read_output_file(target)
        for token in tokens:
            if token.lower() in text.lower():
                errors.append(f"{fixture_name}: {rel} contains forbidden {token!r}")

    all_text = "\n".join(read_output_file(path) for path in output_files(output_dir))
    for token in output.get("any_file_must_contain", []):
        if token.lower() not in all_text.lower():
            errors.append(f"{fixture_name}: no output file contains {token!r}")
    return errors


def check_contract(fixture: Path, data: dict, expected_skills: set[str]) -> list[str]:
    errors: list[str] = []
    if data.get("status") != "active":
        errors.append(f"{fixture.name}: contract must be active")
    skill = data.get("skill")
    if not skill or not str(skill).startswith("/"):
        errors.append(f"{fixture.name}: contract must declare /skill")
    elif skill not in expected_skills:
        errors.append(f"{fixture.name}: contract skill {skill} not in route snapshot skills {sorted(expected_skills)}")
    for file_name, contract in data.get("contract_files", {}).items():
        errors.extend(check_text_contract(fixture, file_name, contract))
    errors.extend(check_output_contract(fixture, data))
    return errors


def all_contracts() -> dict[str, dict]:
    expected = route_fixtures()
    registry = load_registry()
    contracts: dict[str, dict] = {}
    for name in expected:
        fixture = FIXTURES / name
        contracts[name] = load_contract(fixture, registry)
    return contracts


def main() -> None:
    expected = route_fixtures()
    registry = load_registry()
    if not registry:
        fail("tests/fixture-contracts.json is missing or empty")
    errors: list[str] = []
    for name, skills in sorted(expected.items()):
        fixture = FIXTURES / name
        if not fixture.is_dir():
            errors.append(f"{name}: route snapshot references missing fixture")
            continue
        data = load_contract(fixture, registry)
        if not data:
            errors.append(f"{name}: missing behavioural contract")
            continue
        errors.extend(check_contract(fixture, data, skills))
    if errors:
        print("Fixture contract drift found:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"OK: {len(expected)} behavioural fixture contract(s) validated")


if __name__ == "__main__":
    main()
