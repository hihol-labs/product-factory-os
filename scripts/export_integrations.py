#!/usr/bin/env python3
from pathlib import Path
import argparse
import json


def load_state(project: Path) -> dict:
    path = project / ".codex-memory" / "STATE.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export PFO project state as integration payloads.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--target", choices=["github", "linear", "notion"], required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    state = load_state(project)
    payload = {
        "target": args.target,
        "project": project.name,
        "currentStage": state.get("currentStage", ""),
        "currentNode": state.get("currentNode", ""),
        "nextAction": state.get("nextAction", ""),
        "blockers": state.get("blockers", []),
        "gateResults": state.get("gateResults", {}),
        "decisionLog": state.get("decisionLog", []),
    }
    out_dir = project / ".pfo-integrations"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{args.target}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: wrote {out}")


if __name__ == "__main__":
    main()

