#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent


def run_script(name: str, args: list[str]) -> int:
    command = [sys.executable, str(ROOT / "scripts" / name), *args]
    return subprocess.run(command, cwd=ROOT).returncode


def load_state(project: Path) -> dict:
    state_path = project / ".codex-memory" / "STATE.json"
    if not state_path.is_file():
        raise SystemExit(f"ERROR: missing state file: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(project: Path, state: dict) -> None:
    state_path = project / ".codex-memory" / "STATE.json"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_new(args: argparse.Namespace) -> int:
    return run_script("pfo_new_project.py", [args.name, "--idea", args.idea, "--workspace", str(args.workspace)])


def cmd_adopt(args: argparse.Namespace) -> int:
    argv = ["--workspace", str(args.workspace), "--write"]
    if args.json:
        argv.append("--json")
    return run_script("adoption_check.py", argv)


def cmd_status(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    print(json.dumps({
        "project": str(project),
        "currentStage": state.get("currentStage"),
        "currentNode": state.get("currentNode"),
        "nextAction": state.get("nextAction"),
        "blockers": state.get("blockers", []),
        "gateResults": state.get("gateResults", {}),
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    state["currentStage"] = "PLAN_READY"
    state["nextAction"] = "Create or update PRODUCT_BLUEPRINT.md, BUILD_PLAN.md, EXECUTION_GRAPH.md, TEST_PLAN.md, and QUALITY_GATES.md."
    state.setdefault("decisionLog", []).append({"event": "pfo plan requested", "note": args.note})
    save_state(project, state)
    print("OK: plan stage recorded")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    return run_script("pfo_runner.py", [str(args.project), "--mode", "build"])


def cmd_test(args: argparse.Namespace) -> int:
    return run_script("pfo_runner.py", [str(args.project), "--mode", "test"])


def cmd_review(args: argparse.Namespace) -> int:
    return run_script("pfo_runner.py", [str(args.project), "--mode", "review"])


def cmd_validate(args: argparse.Namespace) -> int:
    return run_script("validate_project.py", [str(args.project)])


def cmd_resume(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    print("CURRENT STATE:", state.get("currentStage", ""))
    print("CURRENT NODE:", state.get("currentNode", ""))
    print("NEXT ACTION:", state.get("nextAction", ""))
    return 0


def cmd_voice(args: argparse.Namespace) -> int:
    return run_script("voice_intent.py", [args.text, "--workspace", str(args.workspace)])


def cmd_metrics(args: argparse.Namespace) -> int:
    return run_script("pfo_metrics.py", [str(args.workspace)])


def cmd_report(args: argparse.Namespace) -> int:
    return run_script("pfo_report.py", [str(args.project)])


def cmd_export(args: argparse.Namespace) -> int:
    return run_script("export_integrations.py", [str(args.project), "--target", args.target])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pfo", description="Product Factory OS runtime CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="Bootstrap a new PFO project.")
    new.add_argument("name")
    new.add_argument("--idea", default="")
    new.add_argument("--workspace", type=Path, default=WORKSPACE)
    new.set_defaults(func=cmd_new)

    adopt = sub.add_parser("adopt", help="Adopt existing workspace projects into PFO.")
    adopt.add_argument("--workspace", type=Path, default=WORKSPACE)
    adopt.add_argument("--json", action="store_true")
    adopt.set_defaults(func=cmd_adopt)

    for name, func in [
        ("status", cmd_status),
        ("plan", cmd_plan),
        ("build", cmd_build),
        ("test", cmd_test),
        ("review", cmd_review),
        ("validate", cmd_validate),
        ("resume", cmd_resume),
        ("report", cmd_report),
    ]:
        item = sub.add_parser(name)
        item.add_argument("project", type=Path)
        if name == "plan":
            item.add_argument("--note", default="")
        item.set_defaults(func=func)

    voice = sub.add_parser("voice", help="Normalize a voice command into PFO intent.")
    voice.add_argument("text")
    voice.add_argument("--workspace", type=Path, default=WORKSPACE)
    voice.set_defaults(func=cmd_voice)

    metrics = sub.add_parser("metrics", help="Collect workspace PFO metrics.")
    metrics.add_argument("--workspace", type=Path, default=WORKSPACE)
    metrics.set_defaults(func=cmd_metrics)

    export = sub.add_parser("export", help="Export project state for external tools.")
    export.add_argument("project", type=Path)
    export.add_argument("--target", choices=["github", "linear", "notion"], required=True)
    export.set_defaults(func=cmd_export)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
