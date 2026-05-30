---
name: kickstart
description: Full Product Factory OS lifecycle from idea or approved docs to implemented, tested, reviewed, and deployable project.
argument-hint: product idea or existing project docs
license: MIT
metadata:
  category: creation
  tags: [kickstart, full-cycle, implementation, deploy]
  effort: high
  side_effect: code-docs-memory-write
  explicit_invocation: false
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
4. Ensure `IDEA_SCORECARD.md` and `VALIDATION_PLAN.md` exist before broad implementation scope.
5. Ensure Product Compiler outputs exist: `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, and `EXECUTION_GRAPH.md`.
6. Use `/mcp-docs` when dependency, SDK, framework, or platform details may be stale.
7. Run `/review` before writing application code.
8. Run `/handoff` before switching sessions, roles, delegated agents, AFK execution, compaction, or recovery.
9. Before each major implementation iteration, write or update `NEXT_STEP.md`, show the visible roadmap, recommend one next step, list alternatives, and get user approval or changed direction.
10. Scaffold project structure, tooling, environment examples, and test framework.
11. Implement modules from `BUILD_PLAN.md` and `EXECUTION_GRAPH.md` step by step.
12. After each behavior change, run or create tests via `/test`.
13. For user-facing browser flows, run `/browser-check` before ship readiness.
14. Capture feedback and iteration outcomes in `FEEDBACK_LOG.md` and `ITERATION_REVIEW.md` when users or tests produce signals.
15. Promote reusable solutions into `ASSET_REGISTER.md` and `CONTENT_BACKLOG.md` when evidence exists.
16. Review significant changes with `/review`.
17. Before production work, run `/security-audit`, `/deps-audit`, and `/harden`.
18. Use `/github-workflow` and `/tool-sync` when PR, CI, release, or external roadmap sync is in scope.
19. Deploy only after explicit user confirmation.
20. Run `/session-save`.

## Phase Details

### 1. Discovery And Planning

- If `DISCOVERY.md`, `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md`, `PRD.md`, `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, and `IMPLEMENTATION_PLAN.md` are absent, run the `/blueprint` behavior first.
- If only some docs exist, supplement missing docs and preserve existing decisions.
- If docs conflict, run `/review` and fix docs before code.

### 2. Implementation Gate

Implementation can start only when:

- `PRD.md` exists.
- `IDEA_SCORECARD.md` exists and does not say `KILL` for the current scope.
- `VALIDATION_PLAN.md` exists or the project has a documented non-market/internal reason to build.
- `PRODUCT_BLUEPRINT.md` exists.
- `PROJECT_ARCHITECTURE.md` exists.
- `BUILD_PLAN.md` exists.
- `EXECUTION_GRAPH.md` exists.
- `IMPLEMENTATION_PLAN.md` exists.
- `HANDOFF.md` exists when implementation is transferred to another session, role, delegated agent, AFK run, or recovery pass.
- `NEXT_STEP.md` exists and the user has approved or changed the next major implementation step.
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

1. Close the previous iteration with: where we are, what changed, verification, blockers, and what remains.
2. Show the visible roadmap from `EXECUTION_GRAPH.md` in user-facing language.
3. Recommend exactly one next step, plus 2-3 alternatives.
4. Ask the user to confirm, change, or stop before major implementation starts.
5. Record the decision in `NEXT_STEP.md` and `.codex-memory/STATE.json`.
6. Restate the approved step and intended files.
7. Make the smallest coherent change.
8. Add or update tests.
9. Run the narrowest relevant verification.
10. Fix failures before continuing.
11. Update `CODEX.md` status.
12. Update `.codex-memory/STATE.json` when the milestone changes.

### 5. Ship Gate

Before deploy:

- `/review` is not `BLOCKED`.
- `/security-audit` has no Critical findings.
- `/deps-audit` has no Critical findings or accepted risk.
- `/harden` has no Critical production gaps.
- `/browser-check` has no blocking user-facing failures when a browser UI exists.
- `EXECUTION_GRAPH.md` has reached `READY_FOR_DEPLOY`.
- User explicitly confirms target environment.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, visible roadmap, recommended next step, alternatives, and required user decision are stated.

## Rules

- Prefer the repository's existing patterns if any code exists.
- Commit or summarize work at meaningful step boundaries when git is available.
- Do not skip tests for user-facing behavior.
- Do not deploy or migrate production data without explicit confirmation.
- Keep `CODEX.md` status updated as steps complete.
- Keep `.codex-memory/STATE.json` aligned with the state machine.
- Do not start a major implementation step without `NEXT_STEP.md` and recorded next-step approval.
- Do not expose internal state-machine jargon as the primary user instruction; translate it into product-owner language.
- Do not expand from a `TEST` idea into a full `BUILD` scope without validation evidence.
- Do not treat meetings, commits, or generated docs as progress unless a gate, signal, decision, or reusable asset changes.
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
- `NEXT_STEP.md` explains the visible roadmap, recommended next step, alternatives, and decision needed.
- `QUALITY_GATES.md` or equivalent state gate results are updated.
- Session memory is saved.

## Final Report

End with:

- What was built
- How to run it
- Verification performed
- Known gaps
- Next recommended step
- Decision needed from the user
