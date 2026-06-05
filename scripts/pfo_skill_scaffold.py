#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


SIDE_EFFECTS = {
    "read-only",
    "docs-write",
    "code-write",
    "methodology-write",
    "external-write",
    "infrastructure-write",
    "data-migration",
    "production-impact",
}
EFFORTS = {"low", "medium", "high"}
DANGEROUS_EFFECTS = {"external-write", "infrastructure-write", "data-migration", "production-impact"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def normalize_name(value: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    name = re.sub(r"-{2,}", "-", name)
    if not name:
        fail("skill name must contain at least one letter or digit")
    if len(name) > 64:
        fail("skill name must be 64 characters or fewer")
    return name


def title(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split("-"))


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def load_json(path: str) -> dict:
    return json.loads(read(path))


def write_json(path: str, data: dict) -> None:
    write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def ensure_missing(path: Path, force: bool) -> None:
    if path.exists() and not force:
        fail(f"{path.relative_to(ROOT)} already exists; pass --force to overwrite generated files")


def skill_md(args: argparse.Namespace, skill: str) -> str:
    explicit = "true" if args.explicit_invocation or args.side_effect in DANGEROUS_EFFECTS else "false"
    tags = ", ".join(args.tag or ["workflow"])
    output = args.output or ["Task-specific result"]
    output_rows = "\n".join(f"- {item}" for item in output)
    validation = "\n".join(f"- `{item}`" for item in args.validation_command) or "- Run the fixture and gates named by `/skill-create`."
    return f"""---
name: {skill}
description: {args.description}
argument-hint: {args.argument_hint or 'target, files, or task context'}
license: MIT
metadata:
  category: {args.category}
  tags: [{tags}]
  effort: {args.effort}
  side_effect: {args.side_effect}
  explicit_invocation: {explicit}
---

# {title(skill)}

Use this skill for the route described in the frontmatter. Keep work inside the PFO contracts and state the gate status before finishing.

## Inputs To Collect

- User request and target project path.
- Required files, APIs, or artifacts.
- Side effects and approval boundary.
- Verification commands or review evidence.

## Process

1. Read the relevant project docs and `.pfo/` contracts.
2. Confirm scope, side effects, and expected output.
3. Produce the smallest result that satisfies the request.
4. Run the validation below or report exact blockers.
5. Save state or handoff when the work changes project context.

## Expected Output

{output_rows}

## Validation

{validation}

## Self-validation

Before final output, verify:

- Scope and side effects match the skill contract.
- Required artifacts or read-only result are explicit.
- Gate status is `BLOCKED`, `PASSED_WITH_WARNINGS`, or `PASSED`.

## Rules

- Do not expand scope silently.
- Do not overwrite user work without approval.
- Require explicit confirmation for external, infrastructure, migration, or production side effects.
- Prefer deterministic validation when available.
"""


def write_skill(args: argparse.Namespace, skill: str) -> list[str]:
    skill_dir = ROOT / "skills" / skill
    ensure_missing(skill_dir, args.force)
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_md(args, skill), encoding="utf-8")
    for resource in args.resource:
        if resource not in {"scripts", "references", "assets"}:
            fail(f"unknown resource {resource!r}")
        (skill_dir / resource).mkdir(exist_ok=True)
    return [f"skills/{skill}/SKILL.md"]


def insert_line_once(text: str, marker: str, line: str) -> str:
    if line in text:
        return text
    if marker not in text:
        fail(f"marker not found: {marker!r}")
    return text.replace(marker, line + "\n" + marker, 1)


def update_skill_contracts(args: argparse.Namespace, skill: str) -> str:
    path = "docs/SKILL_CONTRACTS.md"
    text = read(path)
    if f"`/{skill}`" in text:
        return path
    explicit = "Requires confirmation" if args.side_effect in DANGEROUS_EFFECTS else "Safe with review"
    row = f"| `/{skill}` | {args.input or 'Task request'} | {', '.join(args.output or ['Task-specific result'])} | {args.side_effect} | {explicit} |\n"
    return write_and_return(path, text.rstrip() + "\n" + row)


def write_and_return(path: str, text: str) -> str:
    write(path, text)
    return path


def trigger_pattern(triggers: list[str]) -> str:
    terms = [item.strip().lower() for item in triggers if item.strip()]
    if not terms:
        fail("at least one --trigger is required for a routable skill")
    escaped = [re.escape(item).replace(r"\ ", r"\s+") for item in terms]
    return r"(?:%s)" % "|".join(escaped)


def update_triggers(args: argparse.Namespace, skill: str) -> str:
    path = "docs/TRIGGERS.md"
    text = read(path)
    if f"`/{skill}`" in text:
        return path
    english = ", ".join(args.trigger)
    russian = args.russian_triggers or "-"
    row = f"| `/{skill}` | {english} | {russian} |\n"
    return write_and_return(path, insert_line_once(text, "## Quality And Operations", row))


def update_call_graph(skill: str) -> str:
    path = "docs/CALL_GRAPH.md"
    text = read(path)
    line = f"  -> /{skill}"
    if line in text:
        return path
    return write_and_return(path, insert_line_once(text, "  -> /browser-check", line))


def update_route_reminder(args: argparse.Namespace, skill: str) -> str:
    path = "hooks/route-reminder.py"
    text = read(path)
    route = f"/task -> /{skill}"
    if route in text:
        return path
    line = f'    (r"{trigger_pattern(args.trigger)}", "{route}"),'
    return write_and_return(path, insert_line_once(text, "    (r\"\\b(open localhost|browser smoke", line))


def fixture_text(args: argparse.Namespace, skill: str, fixture: str) -> dict[str, str]:
    expected = args.expected_file or ["NONE"]
    expected_text = "\n".join(expected) + "\n"
    return {
        "idea.md": f"""# Fixture: {title(skill)}

User request:

```text
{args.prompt or args.trigger[0]}
```

Expected route:

```text
/task -> /{skill}
```
""",
        "notes.md": f"""# Fixture Notes: {title(skill)}

This fixture checks {args.notes or args.description}
""",
        "expected-files.txt": expected_text,
    }


def write_fixture(args: argparse.Namespace, skill: str, fixture: str) -> str:
    fixture_dir = ROOT / "tests" / "fixtures" / fixture
    ensure_missing(fixture_dir, args.force)
    fixture_dir.mkdir(parents=True, exist_ok=True)
    for name, body in fixture_text(args, skill, fixture).items():
        (fixture_dir / name).write_text(body, encoding="utf-8")
    return f"tests/fixtures/{fixture}/"


def update_snapshots(args: argparse.Namespace, skill: str, fixture: str) -> str:
    path = "tests/snapshots/route-snapshots.json"
    data = load_json(path)
    snapshots = data.setdefault("snapshots", [])
    if any(item.get("skill") == f"/{skill}" for item in snapshots):
        return path
    snapshots.append(
        {
            "skill": f"/{skill}",
            "fixture": fixture,
            "expectedRoute": f"/task -> /{skill}",
            "reminderPrompt": args.trigger[0],
        }
    )
    write_json(path, data)
    return path


def output_contract(args: argparse.Namespace) -> dict:
    contract: dict[str, object] = {}
    required_files = args.required_file or [item for item in args.expected_file if item != "NONE"]
    if required_files:
        contract["required_files"] = required_files
    if args.stdout_token:
        contract["stdout_must_contain"] = args.stdout_token
    if args.any_file_token:
        contract["any_file_must_contain"] = args.any_file_token
    if not contract:
        contract["stdout_must_contain"] = [args.trigger[0]]
    return contract


def update_fixture_contracts(args: argparse.Namespace, skill: str, fixture: str) -> str:
    path = "tests/fixture-contracts.json"
    data = load_json(path)
    fixtures = data.setdefault("fixtures", {})
    if fixture in fixtures and not args.force:
        return path
    fixtures[fixture] = {
        "skill": f"/{skill}",
        "status": "active",
        "contract_files": {
            "expected-files.txt": {"must_contain": args.expected_file or ["NONE"]},
            "notes.md": {"must_contain": [args.notes_token or "fixture"]},
        },
        "output_contract": output_contract(args),
    }
    write_json(path, data)
    return path


def scaffold(args: argparse.Namespace) -> int:
    skill = normalize_name(args.skill_name)
    fixture = normalize_name(args.fixture or skill)
    if args.effort not in EFFORTS:
        fail(f"--effort must be one of {sorted(EFFORTS)}")
    if args.side_effect not in SIDE_EFFECTS:
        fail(f"--side-effect must be one of {sorted(SIDE_EFFECTS)}")
    if not args.description:
        fail("--description is required")
    if not args.trigger:
        fail("--trigger is required")

    changed = []
    changed.extend(write_skill(args, skill))
    changed.append(write_fixture(args, skill, fixture))
    changed.append(update_skill_contracts(args, skill))
    changed.append(update_triggers(args, skill))
    changed.append(update_call_graph(skill))
    changed.append(update_route_reminder(args, skill))
    changed.append(update_snapshots(args, skill, fixture))
    changed.append(update_fixture_contracts(args, skill, fixture))

    print(f"OK: scaffolded /{skill}")
    for item in sorted(set(changed)):
        print(f"- {item}")
    print("Next gates:")
    print(f"- python3 hooks/skill-completeness.py --skill {skill}")
    print(f"- python3 scripts/run_headless_fixtures.py --mode mock --fixture {fixture}")
    print("- python3 scripts/validate_structure.py")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a PFO-aware skill scaffold and synchronized route fixtures.")
    parser.add_argument("skill_name")
    parser.add_argument("--description", required=True)
    parser.add_argument("--trigger", action="append", required=True, help="Natural-language trigger phrase. Repeatable.")
    parser.add_argument("--russian-triggers", default="")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--input", default="")
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--expected-file", action="append", default=[])
    parser.add_argument("--required-file", action="append", default=[])
    parser.add_argument("--stdout-token", action="append", default=[])
    parser.add_argument("--any-file-token", action="append", default=[])
    parser.add_argument("--notes", default="")
    parser.add_argument("--notes-token", default="fixture")
    parser.add_argument("--validation-command", action="append", default=[])
    parser.add_argument("--argument-hint", default="")
    parser.add_argument("--category", default="daily-work")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--effort", choices=sorted(EFFORTS), default="medium")
    parser.add_argument("--side-effect", choices=sorted(SIDE_EFFECTS), default="read-only")
    parser.add_argument("--explicit-invocation", action="store_true")
    parser.add_argument("--resource", action="append", default=[])
    parser.add_argument("--fixture", default="")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    raise SystemExit(scaffold(parser.parse_args()))


if __name__ == "__main__":
    main()
