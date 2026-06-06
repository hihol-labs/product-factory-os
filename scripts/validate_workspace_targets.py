#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json

import pfo_metrics


ROOT = Path(__file__).resolve().parents[1]


def fail(errors: list[str]) -> None:
    print("Workspace target gate failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)


def load_project_states(workspace: Path) -> list[tuple[Path, dict]]:
    project_states: list[tuple[Path, dict]] = []
    for state_path in workspace.glob("*/.codex-memory/STATE.json"):
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        project_states.append((state_path.parents[1], state))
    return project_states


def load_metrics_payload(metrics_json: Path) -> tuple[dict, dict, dict]:
    payload = json.loads(metrics_json.read_text(encoding="utf-8"))
    harness = payload.get("harnessEfficiency", {}) if isinstance(payload.get("harnessEfficiency"), dict) else {}
    context = payload.get("contextRuntime", {}) if isinstance(payload.get("contextRuntime"), dict) else {}
    live_eval = payload.get("liveEvalStatus", {}) if isinstance(payload.get("liveEvalStatus"), dict) else {}
    return harness, context, live_eval


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate PFO 100/100 workspace target metrics.")
    parser.add_argument("--workspace", type=Path, default=ROOT.parent)
    parser.add_argument(
        "--metrics-json",
        type=Path,
        help="Validate a recorded pfo metrics payload instead of reading live workspace state.",
    )
    args = parser.parse_args()

    if args.metrics_json:
        harness, context, live_eval = load_metrics_payload(args.metrics_json)
    else:
        project_states = load_project_states(args.workspace)
        harness = pfo_metrics.efficiency_metrics(project_states)
        context = pfo_metrics.context_runtime_metrics(project_states)
        blockers = pfo_metrics.blocker_metrics(project_states)
        stale = pfo_metrics.stale_state_metrics(project_states)
        live_eval = pfo_metrics.live_eval_status(project_states, harness, context, blockers, stale)

    errors: list[str] = []
    context_coverage = context.get("completeCoverageRatio")
    verification_rate = harness.get("verificationPassRate")
    repair_rate = harness.get("repairLoopsPerVerifiedUnit")

    if context_coverage is None or context_coverage <= pfo_metrics.TARGET_CONTEXT_COVERAGE:
        errors.append("context coverage must be >90%")
    if verification_rate is None or verification_rate <= pfo_metrics.TARGET_VERIFICATION_PASS_RATE:
        errors.append("verification pass rate must be >95%")
    if repair_rate is None or repair_rate >= pfo_metrics.TARGET_REPAIR_LOOPS_PER_VERIFIED_UNIT:
        errors.append("repair loops per verified unit must be <0.25")
    if live_eval.get("status") != "PASS":
        reasons = ", ".join(live_eval.get("reasons", [])) or "no reason recorded"
        errors.append(f"live eval status must be PASS: {reasons}")

    if errors:
        fail(errors)

    print(
        "OK: workspace targets passed "
        f"(context={context_coverage:.4f}, "
        f"verification={verification_rate:.4f}, "
        f"repairLoopsPerVerifiedUnit={repair_rate:.4f})"
    )


if __name__ == "__main__":
    main()
