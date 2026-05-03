#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = ROOT / "docs" / "examples" / "golden-path-booking-app" / "EXECUTION_GRAPH.md"
CHECKPOINTS = [
    "Architecture Validation",
    "Dependency Check",
    "Test Coverage Check",
    "Security Review",
    "Deployment Validation",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def parse_table(text: str, heading: str) -> list[dict[str, str]]:
    pattern = rf"## {re.escape(heading)}\s*\n\n((?:\|.*\|\n)+)"
    match = re.search(pattern, text)
    if not match:
        fail(f"missing markdown table for section: {heading}")

    lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    if len(lines) < 3:
        fail(f"section {heading} must include header, separator, and at least one row")

    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    separator = lines[1]
    if not re.fullmatch(r"\|[\s:\-|]+\|", separator):
        fail(f"section {heading} has an invalid table separator")

    rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            fail(f"section {heading} has row with {len(cells)} cells, expected {len(headers)}: {line}")
        rows.append(dict(zip(headers, cells)))

    return rows


def parse_state_block(text: str) -> tuple[str, str]:
    match = re.search(r"```text\s*(.*?)\s*```", text, re.S)
    if not match:
        fail("missing fenced text state block")

    values = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()

    current = values.get("CURRENT_STATE")
    next_state = values.get("NEXT_STATE")
    if not current or not next_state:
        fail("state block must include CURRENT_STATE and NEXT_STATE")
    return current, next_state


def validate_graph(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    state_machine = json.loads((ROOT / "execution" / "state-machine.json").read_text(encoding="utf-8"))
    allowed_states = set(state_machine.get("states", []))

    current_state, next_state = parse_state_block(text)
    for state in [current_state, next_state]:
        if state not in allowed_states:
            fail(f"{path}: unknown state in state block: {state}")

    nodes = parse_table(text, "Nodes")
    transitions = parse_table(text, "Transitions")

    node_ids = set()
    for row in nodes:
        node = row.get("Node", "")
        if not node:
            fail(f"{path}: node row is missing Node")
        if node in node_ids:
            fail(f"{path}: duplicate node id: {node}")
        node_ids.add(node)
        for required in ["Module Or Stage", "Inputs", "Outputs", "Validation"]:
            if not row.get(required):
                fail(f"{path}: node {node} is missing {required}")

    valid_refs = node_ids | allowed_states
    has_ready_transition = False
    has_failure_path = False
    referenced_nodes = set()

    for row in transitions:
        source = row.get("From", "")
        target = row.get("To", "")
        requires = row.get("Requires", "")
        failure = row.get("On Failure", "")
        if not source or not target:
            fail(f"{path}: transition row must include From and To")
        if source not in valid_refs:
            fail(f"{path}: transition source references unknown node/state: {source}")
        if target not in valid_refs:
            fail(f"{path}: transition target references unknown node/state: {target}")
        if not requires:
            fail(f"{path}: transition {source} -> {target} is missing Requires")
        if not failure:
            fail(f"{path}: transition {source} -> {target} is missing On Failure")
        if source in node_ids:
            referenced_nodes.add(source)
        if target in node_ids:
            referenced_nodes.add(target)
        if target == "READY_FOR_DEPLOY":
            has_ready_transition = True
        if failure == "DEPLOY_BLOCKED" or "repair" in failure.lower() or "fix" in failure.lower():
            has_failure_path = True

    unreachable_nodes = node_ids - referenced_nodes
    if unreachable_nodes:
        fail(f"{path}: nodes are not referenced by transitions: {', '.join(sorted(unreachable_nodes))}")
    if not has_ready_transition:
        fail(f"{path}: execution graph must include a transition to READY_FOR_DEPLOY")
    if not has_failure_path:
        fail(f"{path}: execution graph must include at least one repair or blocked failure path")

    missing_checkpoints = [checkpoint for checkpoint in CHECKPOINTS if checkpoint not in text]
    if missing_checkpoints:
        fail(f"{path}: missing validation checkpoints: {', '.join(missing_checkpoints)}")

    if "## Repair Paths" not in text:
        fail(f"{path}: missing Repair Paths section")
    repair_text = text.split("## Repair Paths", 1)[1].strip()
    if not repair_text:
        fail(f"{path}: Repair Paths section must not be empty")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Product Factory OS EXECUTION_GRAPH.md semantics.")
    parser.add_argument("paths", nargs="*", type=Path, default=[DEFAULT_GRAPH])
    args = parser.parse_args()

    for path in args.paths:
        candidate = path if path.is_absolute() else ROOT / path
        if not candidate.is_file():
            fail(f"missing execution graph: {candidate}")
        validate_graph(candidate)

    print(f"OK: validated {len(args.paths)} execution graph(s)")


if __name__ == "__main__":
    main()
