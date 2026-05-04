---
name: kickstart
description: Full Product Factory OS lifecycle from idea or approved docs to implemented, tested, reviewed, and deployable project.
argument-hint: product idea or existing project docs
license: MIT
metadata:
  category: creation
  tags: [kickstart, full-cycle, implementation, deploy]
---

# Kickstart

Use this skill for full-cycle Product Factory OS project creation.

## Mode Selection

Choose one mode:

- `fresh`: no docs or code exist.
- `docs-ready`: planning docs exist and need implementation.
- `resume`: code exists and `CODEX.md` or git history shows progress.
- `adopted`: existing project is being brought into the methodology.

Announce the selected mode and why.

## Phases

1. Detect existing docs and code.
2. Load PFO runtime contracts:
   - `routing/product-classifier.json`
   - `templates/product-templates.json`
   - `core/product-compiler.md`
   - `pipelines/execution-pipeline.json`
   - `execution/state-machine.json`
   - `deployment/deployment-targets.json`
   - `memory/session-state.schema.json`
   - `docs/rubrics/pfo.md`
   - `docs/rubrics/testing.md`
   - `docs/rubrics/strategy.md`
3. If docs are missing, run discovery and blueprint work.
4. Ensure Product Compiler outputs exist: `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, and `EXECUTION_GRAPH.md`.
5. Use `/mcp-docs` when dependency, SDK, framework, or platform details may be stale.
6. Run `/review` before writing application code.
7. Scaffold project structure, tooling, environment examples, and test framework.
8. Implement modules from `BUILD_PLAN.md` and `EXECUTION_GRAPH.md` step by step.
9. After each behavior change, run or create tests via `/test`.
10. For user-facing browser flows, run `/browser-check` before ship readiness.
11. Review significant changes with `/review`.
12. Before production work, run `/security-audit`, `/deps-audit`, and `/harden`.
13. Use `/github-workflow` and `/tool-sync` when PR, CI, release, or external roadmap sync is in scope.
14. Deploy only after explicit user confirmation.
15. Run `/session-save`.

## Phase Details

### 1. Discovery And Planning

- If `DISCOVERY.md`, `PRD.md`, `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, and `IMPLEMENTATION_PLAN.md` are absent, run the `/blueprint` behavior first.
- If only some docs exist, supplement missing docs and preserve existing decisions.
- If docs conflict, run `/review` and fix docs before code.

### 2. Implementation Gate

Implementation can start only when:

- `PRD.md` exists.
- `PRODUCT_BLUEPRINT.md` exists.
- `PROJECT_ARCHITECTURE.md` exists.
- `BUILD_PLAN.md` exists.
- `EXECUTION_GRAPH.md` exists.
- `IMPLEMENTATION_PLAN.md` exists.
- Review status is not `BLOCKED`.
- The user has approved the plan when the project is new.

### 3. Scaffold

Create the minimum viable structure implied by the architecture:

- Package/project manifests
- Source directories
- Test directories
- Lint/format/test scripts when idiomatic
- `.env.example`
- Docker or platform config only when deployment target is known

### 4. Step Loop

For each execution graph node or implementation step:

1. Restate the step and intended files.
2. Make the smallest coherent change.
3. Add or update tests.
4. Run the narrowest relevant verification.
5. Fix failures before continuing.
6. Update `CODEX.md` status.
7. Update `.codex-memory/STATE.json` when the milestone changes.

### 5. Ship Gate

Before deploy:

- `/review` is not `BLOCKED`.
- `/security-audit` has no Critical findings.
- `/deps-audit` has no Critical findings or accepted risk.
- `/harden` has no Critical production gaps.
- `/browser-check` has no blocking user-facing failures when a browser UI exists.
- `EXECUTION_GRAPH.md` has reached `READY_FOR_DEPLOY`.
- User explicitly confirms target environment.

## Rules

- Prefer the repository's existing patterns if any code exists.
- Commit or summarize work at meaningful step boundaries when git is available.
- Do not skip tests for user-facing behavior.
- Do not deploy or migrate production data without explicit confirmation.
- Keep `CODEX.md` status updated as steps complete.
- Keep `.codex-memory/STATE.json` aligned with the state machine.
- Never continue past a `BLOCKED` gate unless the user explicitly changes the requirement or accepts a documented non-production limitation.
- Preserve unrelated user changes in the worktree.
- If dependency installation or network access fails, report it and keep working with local verification where possible.

## Failure Handling

- Build fails: fix before the next implementation step.
- Tests fail: diagnose whether test or code is wrong, then fix.
- Review blocked: stop and address Critical findings.
- Deployment fails: stop, report health check output, and provide rollback steps.
- State transition invalid: stop, repair missing artifact or failed gate, then resume from the previous valid state.
- Ambiguous product decision: ask once, then record a conservative assumption if the user delegates.

## Done Criteria

- Project runs locally.
- Tests pass or known gaps are documented.
- Review status is not `BLOCKED`.
- README explains setup and deployment.
- Product Factory OS state is saved in `.codex-memory/STATE.json`.
- `QUALITY_GATES.md` or equivalent state gate results are updated.
- Session memory is saved.

## Final Report

End with:

- What was built
- How to run it
- Verification performed
- Known gaps
- Next recommended step
