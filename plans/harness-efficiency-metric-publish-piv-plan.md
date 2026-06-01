# PIV Plan: harness-efficiency-metric-publish

Project: `product-factory-os`
Created: 2026-06-01T19:45:04+00:00
Implementation report: `reports/harness-efficiency-metric-publish-implementation-report.md`

## Goal

Add harness efficiency metric, verify PFO compatibility, commit all changes, push branch, and open a PR

## Read Before Implementing

- CODEX.md
- .codex-memory/STATE.json
- .pfo/PROJECT_CONTRACT.md
- .pfo/SCOPE_LOCK.md
- .pfo/EXECUTION_POLICY.json
- .pfo/PERMISSION_MATRIX.md
- .pfo/PERMISSION_MATRIX.json
- .pfo/VERIFICATION_CONTRACT.json
- .pfo/TOOL_CAPABILITY_REGISTRY.json
- IDEA_SCORECARD.md
- VALIDATION_PLAN.md
- PRODUCT_BLUEPRINT.md
- BUILD_PLAN.md
- EXECUTION_GRAPH.md
- active PIV plan under plans/ before implementation
- active implementation report under reports/ before review
- NEXT_STEP.md with approved or changed user-facing next step
- FEEDBACK_LOG.md and FUNNEL_MODEL.md when user acquisition or iteration is in scope
- PHASE_CONTEXT.md when present
- .pfo/EXPERIMENT_PROGRAM.md when autonomous measurement-driven iteration is in scope
- .pfo/EXPERIMENTS.tsv when autonomous measurement-driven iteration is in scope
- HANDOFF.md when switching sessions, roles, delegated agents, AFK execution, compaction, or recovery
- ROOT_CAUSE.md for bugfix units

## Scope

Allowed writes:

- files listed by the active execution graph node
- tests for changed behavior
- PFO_REPORT.md
- plans/
- reports/
- .codex-memory/STATE.json
- .codex-memory/MEMORY.md
- .codex-memory/events.jsonl

Forbidden changes:

- scope outside `.pfo/SCOPE_LOCK.md`
- silent production data substitution
- unapproved deployment, migration, DNS, or production mutation
- golden-flow behavior changes without verification evidence
- commands or writes outside `.pfo/EXECUTION_POLICY.json` and `.pfo/PERMISSION_MATRIX.md`

## Harness Policy

- Pair feedforward guides with feedback sensors where practical.
- Regulate maintainability, architecture fitness, and behaviour explicitly.
- Run fast computational sensors before broader or inferential gates.
- Use human steering for unclear intent, accepted risk, load-bearing conventions, or missing sensor evidence.

## Ordered Tasks

### Task 1 - Context lock

- What: read the required inputs and identify exact files before editing.
- Validate: active `.pfo/UNIT_CONTEXT_MANIFEST.json` and `.pfo/VERIFICATION_CONTRACT.json` exist.

### Task 2 - Implement the smallest unit

- What: change only the scoped files needed for the unit goal.
- Pattern: follow the closest existing implementation in the target project.
- Gotcha: behavior changes need red and green evidence; bugfixes need `ROOT_CAUSE.md`.
- Validate: run the narrowest relevant command before continuing.

### Task 3 - Full validation gate

- What: run every command declared in `.pfo/VERIFICATION_CONTRACT.json`.
- Validate:

```bash
/usr/bin/python3 /home/hihol/projects/product-factory-os/scripts/pfo_contract_gate.py /home/hihol/projects/product-factory-os
```

### Task 4 - Report and review

- What: record implementation evidence in `reports/harness-efficiency-metric-publish-implementation-report.md`.
- Validate: run spec compliance review before code quality review.

## Acceptance Criteria

- [ ] Unit goal is satisfied.
- [ ] Required commands pass or recovery is recorded.
- [ ] `pfo verify-work /home/hihol/projects/product-factory-os --evidence "<commands passed>" --pass-gate` writes `reports/harness-efficiency-metric-publish-implementation-report.md`.
- [ ] Spec compliance review is recorded before code quality review.
