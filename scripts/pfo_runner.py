#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import sys


def ensure_autonomy_state(state: dict) -> None:
    state.setdefault("currentPhase", "")
    state.setdefault(
        "currentUnit",
        {"id": "", "goal": "", "status": "", "owner": "", "startedAt": "", "completedAt": ""},
    )
    state.setdefault("dispatchJournal", [])
    state.setdefault(
        "telemetry",
        {
            "unitCount": 0,
            "verificationCount": 0,
            "lastCommand": "",
            "lastDurationSeconds": None,
            "tokenNotes": "",
            "costNotes": "",
        },
    )
    gates = state.setdefault("gateResults", {})
    gates.setdefault("nextStepApproval", "PENDING")
    if not gates.get("nextStepApproval"):
        gates["nextStepApproval"] = "PENDING"
    steering = state.setdefault(
        "humanSteering",
        {
            "approvalRequired": True,
            "approvalStatus": "PENDING",
            "approvedBy": "",
            "approvedAt": "",
            "lastPrompt": "Ask the user to confirm, change, or stop before implementation.",
            "lastIterationSummary": "PFO runtime is active and waiting for next-step steering.",
            "recommendedNextStep": "Choose and approve the next task-specific implementation step.",
            "alternatives": [
                "Approve the recommended next step.",
                "Change scope or priority.",
                "Pause and review the plan."
            ],
            "pendingQuestions": [
                "Do you approve the recommended next step?",
                "Should scope or priority change before implementation?"
            ],
            "visibleRoadmap": [],
            "completedIterations": [],
        },
    )
    if not isinstance(steering, dict):
        state["humanSteering"] = {}
        steering = state["humanSteering"]
    defaults = {
        "approvalRequired": True,
        "approvalStatus": "PENDING",
        "approvedBy": "",
        "approvedAt": "",
        "lastPrompt": "Ask the user to confirm, change, or stop before implementation.",
        "lastIterationSummary": "PFO runtime is active and waiting for next-step steering.",
        "recommendedNextStep": "Choose and approve the next task-specific implementation step.",
        "alternatives": [
            "Approve the recommended next step.",
            "Change scope or priority.",
            "Pause and review the plan."
        ],
        "pendingQuestions": [
            "Do you approve the recommended next step?",
            "Should scope or priority change before implementation?"
        ],
        "visibleRoadmap": [],
        "completedIterations": [],
    }
    for key, value in defaults.items():
        steering.setdefault(key, value)
    if not steering.get("approvalStatus"):
        steering["approvalStatus"] = "PENDING"
    if steering.get("approvalStatus") == "PENDING":
        steering["approvalRequired"] = True
    if not steering.get("recommendedNextStep"):
        steering["recommendedNextStep"] = defaults["recommendedNextStep"]


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


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def add_artifact(state: dict, artifact: str) -> None:
    artifacts = set(state.get("artifacts", []))
    artifacts.add(artifact)
    state["artifacts"] = sorted(artifacts)


def append_event(project: Path, state: dict, event_type: str, status: str, payload: dict) -> None:
    timestamp = now_iso()
    event_id = f"event-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{len(state.get('verificationHistory', [])) + 1}"
    event = {
        "id": event_id,
        "timestamp": timestamp,
        "eventType": event_type,
        "status": status,
        "project": project.name,
        "source": "pfo-runner",
        "payload": payload,
    }
    path = project / ".codex-memory" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    state["eventLog"] = {
        "path": ".codex-memory/events.jsonl",
        "lastEventId": event_id,
        "lastEventAt": timestamp,
    }
    add_artifact(state, ".codex-memory/events.jsonl")


def next_graph_node(project: Path, current: str) -> str:
    graph = project / "EXECUTION_GRAPH.md"
    if not graph.is_file():
        return ""
    text = graph.read_text(encoding="utf-8")
    nodes = []
    for line in text.splitlines():
        if line.startswith("| N"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells and cells[0].startswith("N") and cells[0][1:].isdigit():
                nodes.append(cells[0])
    if not nodes:
        return ""
    if not current or current not in nodes:
        return nodes[0]
    index = nodes.index(current)
    return nodes[index + 1] if index + 1 < len(nodes) else ""


def roadmap(project: Path, current: str) -> list[tuple[str, str]]:
    graph = project / "EXECUTION_GRAPH.md"
    if not graph.is_file():
        return []
    items = []
    for line in graph.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| N"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 2 and cells[0].startswith("N") and cells[0][1:].isdigit():
            status = "current" if cells[0] == current else "pending"
            items.append((cells[0], f"{cells[1]} ({status})"))
    return items[:12]


def write_next_step(project: Path, state: dict, summary: str, recommended: str) -> None:
    steering = state.setdefault("humanSteering", {})
    steering["approvalRequired"] = True
    steering["approvalStatus"] = "PENDING"
    steering["approvedBy"] = ""
    steering["approvedAt"] = ""
    steering["lastIterationSummary"] = summary
    steering["recommendedNextStep"] = recommended
    steering["alternatives"] = [
        "Approve the recommended step.",
        "Change scope or priority.",
        "Pause and review the plan.",
    ]
    steering["pendingQuestions"] = ["Confirm, change, or stop before the next major implementation step."]
    steering["visibleRoadmap"] = [
        {"step": step, "outcome": outcome, "status": "current" if step == state.get("currentNode", "") else "pending"}
        for step, outcome in roadmap(project, state.get("currentNode", ""))
    ]
    state.setdefault("gateResults", {})["nextStepApproval"] = "PENDING"
    add_artifact(state, "NEXT_STEP.md")
    rows = "\n".join(
        f"| {item['step']} | {item['outcome']} | {item['status']} |"
        for item in steering["visibleRoadmap"]
    ) or "| 1 | Choose the next product step | pending |"
    (project / "NEXT_STEP.md").write_text(
        "# Next Step\n\n"
        "This is the user-facing steering checkpoint.\n\n"
        "## Where We Are\n\n"
        f"- Current outcome: {summary}\n"
        f"- Recommended next step: {recommended}\n"
        f"- Approval status: {steering['approvalStatus']}\n\n"
        "## Visible Roadmap\n\n"
        "| Step | Outcome | Status |\n|---|---|---|\n"
        f"{rows}\n\n"
        "## Decision Needed\n\n"
        "Confirm, change, or stop before another major implementation iteration starts.\n",
        encoding="utf-8",
    )


def next_step_is_approved(state: dict) -> bool:
    steering = state.get("humanSteering", {}) if isinstance(state.get("humanSteering"), dict) else {}
    return state.get("gateResults", {}).get("nextStepApproval") == "PASSED" and steering.get("approvalStatus") == "APPROVED"


def unit_context_is_ready(project: Path) -> bool:
    manifest = project / ".pfo" / "UNIT_CONTEXT_MANIFEST.json"
    contract = project / ".pfo" / "VERIFICATION_CONTRACT.json"
    if not manifest.is_file() or not contract.is_file():
        return False
    try:
        data = json.loads(contract.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    commands = data.get("commands", [])
    if not isinstance(commands, list) or not commands:
        return False
    return all(isinstance(item, dict) and item.get("command") for item in commands)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute one Product Factory OS runtime step.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--mode", choices=["build", "test", "review"], default="build")
    args = parser.parse_args()

    project = args.project.resolve()
    state_path, state = load_state(project)
    ensure_autonomy_state(state)
    history = state.setdefault("verificationHistory", [])

    if args.mode == "build":
        if not unit_context_is_ready(project):
            state["currentStage"] = "NEXT_STEP_REVIEW"
            write_next_step(
                project,
                state,
                "Implementation is blocked until the unit context and verification contract are ready.",
                "Run `pfo manifest <project> --unit <id> --goal <goal>`, then request next-step approval.",
            )
            append_event(project, state, "gate", "BLOCKED", {"mode": "build", "reason": "unit context manifest or verification contract missing"})
            save(state_path, state)
            fail("unit context is not ready; run `pfo manifest <project> --unit <id> --goal <goal>` before build")
        if not next_step_is_approved(state):
            recommended = state.get("humanSteering", {}).get("recommendedNextStep", "") if isinstance(state.get("humanSteering"), dict) else ""
            state["currentStage"] = "NEXT_STEP_REVIEW"
            write_next_step(
                project,
                state,
                "Implementation is blocked until the user approves the next step.",
                recommended or "Approve the next implementation slice.",
            )
            append_event(project, state, "approval", "BLOCKED", {"mode": "build", "reason": "next step approval missing"})
            save(state_path, state)
            fail("next step is not approved; run `pfo approve-next <project>` after user confirmation")
        node = state.get("currentNode", "") if state.get("currentStage") == "UNIT_CONTEXT_READY" else ""
        node = node or next_graph_node(project, state.get("currentNode", ""))
        state["currentNode"] = node
        state["currentStage"] = "UNIT_DISPATCHED" if node else "READY_FOR_DEPLOY"
        if node:
            state["currentUnit"] = {
                "id": node,
                "goal": f"Implement execution graph node {node}.",
                "status": "DISPATCHED",
                "owner": "PFO",
                "startedAt": "",
                "completedAt": "",
            }
            state["dispatchJournal"].append({"unit": node, "mode": "build", "status": "DISPATCHED"})
            state["telemetry"]["unitCount"] = int(state["telemetry"].get("unitCount") or 0) + 1
            state["humanSteering"]["approvalStatus"] = "CONSUMED"
        state["nextAction"] = f"Implement execution graph node {node}." if node else "Run deployment readiness gates."
    elif args.mode == "test":
        state["currentStage"] = "TESTING"
        state["gateResults"]["tests"] = "PENDING"
        state["nextAction"] = "Run product-type test matrix from TEST_PLAN.md."
    else:
        state["currentStage"] = "REVIEWING"
        state["gateResults"]["review"] = "PENDING"
        next_node = next_graph_node(project, state.get("currentNode", ""))
        if next_node:
            write_next_step(
                project,
                state,
                f"Review is pending for {state.get('currentNode', '')}.",
                f"After review passes, approve and execute {next_node}.",
            )
            state["nextAction"] = "Finish review, then ask the user to approve the next step."
        else:
            state["nextAction"] = "Run review, PFO, strategy, testing, security, dependency, and hardening gates as applicable."

    history.append({"mode": args.mode, "stage": state["currentStage"], "node": state.get("currentNode", "")})
    append_event(project, state, "state-change", state["currentStage"], {"mode": args.mode, "node": state.get("currentNode", "")})
    save(state_path, state)
    print(f"OK: {args.mode} step recorded for {project}")


if __name__ == "__main__":
    main()
