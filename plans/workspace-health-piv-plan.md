# PIV Plan: workspace-health

Project: `product-factory-os`
Created: 2026-06-05T23:06:36+00:00
Implementation report: `reports/workspace-health-implementation-report.md`

## Goal

Improve workspace health metrics, detection, coverage, and dashboard

## Read Before Implementing

- AGENTS.md
- CODEX.md
- .codex-memory/STATE.json
- .pfo/PROJECT_CONTRACT.md
- .pfo/SCOPE_LOCK.md
- .pfo/EXECUTION_POLICY.json
- .pfo/PERMISSION_MATRIX.json
- .pfo/TOOL_CAPABILITY_REGISTRY.json
- .pfo/UNIT_CONTEXT_MANIFEST.json
- .pfo/VERIFICATION_CONTRACT.json
- active PIV plan under plans/ before implementation
- active implementation report under reports/ before review
- NEXT_STEP.md with approved or changed user-facing next step

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
- .codex-memory/context-index.json
- .codex-memory/resume-snapshot.md
- .codex-memory/context-summary.md

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
/usr/bin/python3 /home/hihol/projects/product-factory-os/scripts/validate_context_runtime.py
```

### Task 4 - Report and review

- What: record implementation evidence in `reports/workspace-health-implementation-report.md`.
- Validate: run spec compliance review before code quality review.

## Acceptance Criteria

- [ ] Unit goal is satisfied.
- [ ] Required commands pass or recovery is recorded.
- [ ] `pfo verify-work /home/hihol/projects/product-factory-os --evidence "<commands passed>" --pass-gate` writes `reports/workspace-health-implementation-report.md`.
- [ ] Spec compliance review is recorded before code quality review.
