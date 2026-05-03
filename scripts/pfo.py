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
    argv = ["--write"]
    if args.project:
        argv.extend(["--project", str(args.project)])
    else:
        argv.extend(["--workspace", str(args.workspace)])
    if args.json:
        argv.append("--json")
    code = run_script("adoption_check.py", argv)
    if code == 0 and args.analyze and args.project:
        analyze_args = [str(args.project)]
        if args.run_gates:
            analyze_args.append("--run-gates")
        return run_script("existing_project_analyzer.py", analyze_args)
    return code


def cmd_analyze(args: argparse.Namespace) -> int:
    argv = [str(args.project)]
    if args.run_gates:
        argv.append("--run-gates")
    if args.json:
        argv.append("--json")
    argv.extend(["--timeout", str(args.timeout)])
    code = run_script("existing_project_analyzer.py", argv)
    if code == 0 and args.report:
        return run_script("pfo_report.py", [str(args.project)])
    return code


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


def cmd_contracts(args: argparse.Namespace) -> int:
    argv = [str(args.project)]
    if args.json:
        argv.append("--json")
    if args.write:
        argv.append("--write")
    if args.strict:
        argv.append("--strict")
    return run_script("pfo_contract_gate.py", argv)


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
    adopt.add_argument("project", type=Path, nargs="?")
    adopt.add_argument("--workspace", type=Path, default=WORKSPACE)
    adopt.add_argument("--json", action="store_true")
    adopt.add_argument("--analyze", action="store_true", help="Run existing-project analyzer after adopting a single project.")
    adopt.add_argument("--run-gates", action="store_true", help="Run detected gates during analysis.")
    adopt.set_defaults(func=cmd_adopt)

    analyze = sub.add_parser("analyze", help="Analyze an existing project, detect stack/commands, run gates, and update PFO state.")
    analyze.add_argument("project", type=Path)
    analyze.add_argument("--run-gates", action="store_true")
    analyze.add_argument("--timeout", type=int, default=90)
    analyze.add_argument("--json", action="store_true")
    analyze.add_argument("--report", action="store_true", help="Regenerate PFO_REPORT.md after analysis.")
    analyze.set_defaults(func=cmd_analyze)

    for name, func in [
        ("status", cmd_status),
        ("plan", cmd_plan),
        ("build", cmd_build),
        ("test", cmd_test),
        ("review", cmd_review),
        ("validate", cmd_validate),
        ("contracts", cmd_contracts),
        ("resume", cmd_resume),
        ("report", cmd_report),
    ]:
        item = sub.add_parser(name)
        item.add_argument("project", type=Path)
        if name == "plan":
            item.add_argument("--note", default="")
        if name == "contracts":
            item.add_argument("--json", action="store_true")
            item.add_argument("--write", action="store_true")
            item.add_argument("--strict", action="store_true")
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
