# AGENTS

This project is governed by Product Factory OS.

## Runtime Rule

- New product work routes through `/project -> /kickstart`.
- Existing project work routes through `/task`.
- Significant work updates `.codex-memory/STATE.json`.
- Broad product scope requires `IDEA_SCORECARD.md` and `VALIDATION_PLAN.md`.
- Scope, data, fallback, and golden-flow rules live in `.pfo/`.
- Autonomous or delegated work requires `.pfo/UNIT_CONTEXT_MANIFEST.json`.
- Autonomous self-improvement requires `.pfo/EXPERIMENT_PROGRAM.md`, a fixed metric/budget, and `.pfo/EXPERIMENTS.tsv`.
- Session or role transfer requires `HANDOFF.md`.
- Behavior changes require TDD red/green evidence.
- Bugfixes require root-cause evidence before fixes.
- Reviews run spec compliance first, code quality second.
- Engineering Discipline v2 is enforced by `scripts/validate_plan_quality.py` when PFO validation runs.
- Verification fails closed when evidence is missing or ambiguous.
- Iteration must reference feedback, metric, validation, or strategy evidence.

## Before Substantial Work

Run or confirm:

```bash
pfo adopt . --analyze
```

Then use the smallest relevant PFO gate before finishing.
