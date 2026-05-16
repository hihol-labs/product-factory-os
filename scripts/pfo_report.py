#!/usr/bin/env python3
from pathlib import Path
import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PFO_REPORT.md for a project.")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    state_path = project / ".codex-memory" / "STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    starter = {}
    starter_path = project / ".pfo-starter.json"
    if starter_path.is_file():
        starter = json.loads(starter_path.read_text(encoding="utf-8"))
    classification = state.get("classification", {})
    existing = state.get("existingProject", {})

    report = [
        "# Product Factory OS Report",
        "",
        f"Project: `{project.name}`",
        f"Starter: `{starter.get('id', '')}`",
        f"Product Type: `{starter.get('productType', classification.get('productType', state.get('productTypeHint', '')))}`",
        f"Architecture: `{state.get('architecture', {}).get('pattern', '')}`",
        "",
        "## State",
        "",
        f"- Current stage: `{state.get('currentStage', '')}`",
        f"- Current node: `{state.get('currentNode', '')}`",
        f"- Current unit: `{state.get('currentUnit', {}).get('id', '')}`",
        f"- Last successful state: `{state.get('lastSuccessfulState', '')}`",
        f"- Next action: {state.get('nextAction', '')}",
        f"- Recovery: `{state.get('recoveryState', {}).get('status', '')}` {state.get('recoveryState', {}).get('reason', '')}",
        f"- Root cause: `{state.get('rootCause', {}).get('status', '')}` {state.get('rootCause', {}).get('summary', '')}",
        "",
        "## Existing Project Analysis",
        "",
        f"- Detected stack: {', '.join(existing.get('detectedStack', [])) or 'none'}",
        f"- Available commands: {', '.join(existing.get('availableCommands', [])) or 'none'}",
        f"- Summary: {existing.get('lastAnalysisSummary', '')}",
        "",
        "## Gates",
        "",
        "| Gate | Status |",
        "|---|---|",
    ]
    for gate, status in state.get("gateResults", {}).items():
        report.append(f"| {gate} | {status} |")
    report.extend([
        "",
        "## Blockers",
        "",
    ])
    blockers = state.get("blockers", [])
    report.extend([f"- {item}" for item in blockers] or ["- none"])
    report.extend([
        "",
        "## Verification History",
        "",
    ])
    history = state.get("verificationHistory", [])
    report.extend([f"- {item}" for item in history] or ["- none"])
    report.extend([
        "",
        "## TDD Evidence",
        "",
    ])
    tdd = state.get("tddEvidence", {})
    report.extend([
        f"- Red: {tdd.get('red', '') or 'none'}",
        f"- Green: {tdd.get('green', '') or 'none'}",
        f"- Refactor: {tdd.get('refactor', '') or 'none'}",
    ])
    review_stages = state.get("reviewStages", {})
    report.extend([
        "",
        "## Review Stages",
        "",
        f"- Spec compliance: `{review_stages.get('specCompliance', {}).get('status', '')}` {review_stages.get('specCompliance', {}).get('evidence', '')}",
        f"- Code quality: `{review_stages.get('codeQuality', {}).get('status', '')}` {review_stages.get('codeQuality', {}).get('evidence', '')}",
    ])
    branch_finish = state.get("branchFinish", {})
    report.extend([
        "",
        "## Branch Finish",
        "",
        f"- Mode: `{branch_finish.get('mode', '')}`",
        f"- Status: `{branch_finish.get('status', '')}`",
        f"- Verification: {branch_finish.get('verification', '') or 'none'}",
        f"- PR: {branch_finish.get('prUrl', '') or 'none'}",
    ])
    report.extend([
        "",
        "## Dispatch Journal",
        "",
    ])
    dispatches = state.get("dispatchJournal", [])
    report.extend([f"- {item}" for item in dispatches] or ["- none"])
    telemetry = state.get("telemetry", {})
    report.extend([
        "",
        "## Telemetry",
        "",
        f"- Units: `{telemetry.get('unitCount', 0)}`",
        f"- Verifications: `{telemetry.get('verificationCount', 0)}`",
        f"- Token notes: {telemetry.get('tokenNotes', '') or 'none'}",
        f"- Cost notes: {telemetry.get('costNotes', '') or 'none'}",
    ])
    (project / "PFO_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"OK: wrote {project / 'PFO_REPORT.md'}")


if __name__ == "__main__":
    main()
