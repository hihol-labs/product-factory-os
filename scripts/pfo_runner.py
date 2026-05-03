#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def load_state(project: Path) -> tuple[Path, dict]:
    path = project / ".codex-memory" / "STATE.json"
    if not path.is_file():
        fail(f"missing state file: {path}")
    return path, json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def next_graph_node(project: Path, current: str) -> str:
    graph = project / "EXECUTION_GRAPH.md"
    if not graph.is_file():
        return ""
    text = graph.read_text(encoding="utf-8")
    nodes = []
    for line in text.splitlines():
        if line.startswith("| N"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells:
                nodes.append(cells[0])
    if not nodes:
        return ""
    if not current or current not in nodes:
        return nodes[0]
    index = nodes.index(current)
    return nodes[index + 1] if index + 1 < len(nodes) else ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute one Product Factory OS runtime step.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--mode", choices=["build", "test", "review"], default="build")
    args = parser.parse_args()

    project = args.project.resolve()
    state_path, state = load_state(project)
    history = state.setdefault("verificationHistory", [])

    if args.mode == "build":
        node = next_graph_node(project, state.get("currentNode", ""))
        state["currentNode"] = node
        state["currentStage"] = "BUILDING" if node else "READY_FOR_DEPLOY"
        state["nextAction"] = f"Implement execution graph node {node}." if node else "Run deployment readiness gates."
    elif args.mode == "test":
        state["currentStage"] = "TESTING"
        state["gateResults"]["tests"] = "PENDING"
        state["nextAction"] = "Run product-type test matrix from TEST_PLAN.md."
    else:
        state["currentStage"] = "REVIEWING"
        state["gateResults"]["review"] = "PENDING"
        state["nextAction"] = "Run review, PFO, strategy, testing, security, dependency, and hardening gates as applicable."

    history.append({"mode": args.mode, "stage": state["currentStage"], "node": state.get("currentNode", "")})
    save(state_path, state)
    print(f"OK: {args.mode} step recorded for {project}")


if __name__ == "__main__":
    main()

