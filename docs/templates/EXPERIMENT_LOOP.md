# Experiment Loop

## Contract

- Tag:
- Primary metric:
- Direction: lower | higher
- Fixed budget seconds:
- Baseline command:
- Experiment command:
- Results TSV: `.pfo/EXPERIMENTS.tsv`

## Scope

Allowed write areas:

- Files named by the active `.pfo/UNIT_CONTEXT_MANIFEST.json`

Protected files and behavior:

- Evaluation harness
- Production data and provider outputs
- `.pfo/` project contracts
- Golden flows unless verification evidence is explicit

## Baseline

| Run ID | Commit | Metric | Value | Runtime | Memory | Status | Notes |
|---|---|---|---:|---:|---:|---|---|

## Candidates

| Run ID | Commit | Idea | Metric Value | Complexity Cost | Status | Decision |
|---|---|---|---:|---:|---|---|

## Rules

1. Record a baseline before implementation changes.
2. Keep a single primary metric and fixed run budget for comparable results.
3. Treat missing metric output as failed verification.
4. Keep changes only when the metric improves, or when equal metric quality comes with simpler code.
5. Discard regressions and crashes unless the crash fix is trivial and in scope.
6. Promote durable lessons through `pfo learnings` and `pfo improve --from-learnings --propose`.
