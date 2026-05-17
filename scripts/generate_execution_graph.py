#!/usr/bin/env python3
from pathlib import Path
import argparse
import re


def module_rows(text: str) -> list[tuple[str, str]]:
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 2 and cells[0].isdigit():
            rows.append((f"N{cells[0]}", cells[1]))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate EXECUTION_GRAPH.md from BUILD_PLAN.md.")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    build_plan = project / "BUILD_PLAN.md"
    if not build_plan.is_file():
        raise SystemExit(f"ERROR: missing {build_plan}")
    nodes = module_rows(build_plan.read_text(encoding="utf-8"))
    if not nodes:
        nodes = [("N1", "scaffold"), ("N2", "core"), ("N3", "deploy-ready")]
    lines = [
        "# Execution Graph",
        "",
        "## State",
        "",
        "```text",
        "CURRENT_STATE: PLAN_READY",
        "NEXT_STATE: BUILDING",
        "```",
        "",
        "## Nodes",
        "",
        "| Node | Module Or Stage | Inputs | Outputs | Validation |",
        "|---|---|---|---|---|",
    ]
    for node, module in nodes:
        lines.append(f"| {node} | {module} | BUILD_PLAN.md | module output | verification command |")
    lines.extend(["", "## Transitions", "", "| From | To | Requires | On Failure |", "|---|---|---|---|"])
    lines.append("| PLAN_READY | N1 | idea gate not KILL and review not blocked | fix planning or validation docs |")
    for idx, (node, _) in enumerate(nodes):
        target = nodes[idx + 1][0] if idx + 1 < len(nodes) else "READY_FOR_DEPLOY"
        lines.append(f"| {node} | {target} | {node} verified | repair {node} |")
    lines.extend([
        "",
        "## Validation Checkpoints",
        "",
        "- Architecture Validation: required before N1.",
        "- Idea Gate: required before broad BUILD scope.",
        "- Market Validation: required when market risk is material.",
        "- Feedback/Funnel Check: required for iteration, acquisition, or conversion work.",
        "- Handoff: required before session transfer, role switch, delegation, AFK, compaction, or recovery.",
        "- Dependency Check: required before READY_FOR_DEPLOY.",
        "- Test Coverage Check: required after behavior nodes.",
        "- Security Review: required before deploy-ready.",
        "- Deployment Validation: required before READY_FOR_DEPLOY.",
        "",
        "## Repair Paths",
        "",
        "Failed validation returns to the failed node with a repair action.",
        "Weak idea or missing market signal returns to IDEA_SCORECARD.md and VALIDATION_PLAN.md.",
    ])
    (project / "EXECUTION_GRAPH.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: wrote {project / 'EXECUTION_GRAPH.md'}")


if __name__ == "__main__":
    main()
