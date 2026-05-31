# AGENTS

This project is governed by Product Factory OS.

## Runtime Rule

- New product work routes through `/project -> /kickstart`.
- Existing project work routes through `/task`.
- Significant work updates `.codex-memory/STATE.json`.
- Broad product scope requires `IDEA_SCORECARD.md` and `VALIDATION_PLAN.md`.
- Broad market-facing scope also requires evidence quality: real conversations, past behavior, contradicting evidence, and BUILD truth conditions.
- Launch/scale maturity artifacts are optional and used only when that stage is in scope.
- Scope, data, fallback, and golden-flow rules live in `.pfo/`.
- Execution policy lives in `.pfo/EXECUTION_POLICY.json`.
- Permissions live in `.pfo/PERMISSION_MATRIX.json` and `.pfo/PERMISSION_MATRIX.md`.
- Tool capabilities live in `.pfo/TOOL_CAPABILITY_REGISTRY.json`.
- Autonomous or delegated work requires `.pfo/UNIT_CONTEXT_MANIFEST.json`.
- Active units require `.pfo/VERIFICATION_CONTRACT.json`.
- Major implementation requires `NEXT_STEP.md` and `gateResults.nextStepApproval=PASSED`.
- Autonomous self-improvement requires `.pfo/EXPERIMENT_PROGRAM.md`, a fixed metric/budget, and `.pfo/EXPERIMENTS.tsv`.
- Session or role transfer requires `HANDOFF.md`.
- Behavior changes require TDD red/green evidence.
- Bugfixes require root-cause evidence before fixes.
- Reviews run spec compliance first, code quality second.
- Engineering Discipline v2 is enforced by `scripts/validate_plan_quality.py` when PFO validation runs.
- Verification fails closed when evidence is missing or ambiguous.
- Commands, gates, approvals, verification, errors, and learning events go to `.codex-memory/events.jsonl`.
- Validate permissions with `pfo permission-check .`; validate tools with `pfo tool-registry .`; validate events with `pfo event validate .`.
- Iteration must reference feedback, metric, validation, or strategy evidence.
- Repeated errors promote only through `.pfo/LEARNING_PROMOTION_GATE.md`.

## Before Substantial Work

Run or confirm:

```bash
pfo adopt . --analyze
```

Then use the smallest relevant PFO gate before finishing.
