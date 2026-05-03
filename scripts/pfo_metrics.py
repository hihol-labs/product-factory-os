#!/usr/bin/env python3
from pathlib import Path
import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Product Factory OS workspace metrics.")
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()

    projects = []
    for state_path in args.workspace.glob("*/.codex-memory/STATE.json"):
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        projects.append(state)

    metrics = {
        "projectCount": len(projects),
        "deployReadyCount": sum(1 for item in projects if item.get("currentStage") == "READY_FOR_DEPLOY"),
        "deployedCount": sum(1 for item in projects if item.get("currentStage") == "DEPLOYED"),
        "blockedCount": sum(1 for item in projects if item.get("blockers")),
        "failedGateCount": sum(len(item.get("failedValidations", [])) for item in projects),
        "verificationEvents": sum(len(item.get("verificationHistory", [])) for item in projects),
    }
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

