---
name: adopt
description: Onboard an existing repository into Product Factory OS.
argument-hint: repository path
license: MIT
metadata:
  category: workflow
  tags: [adoption, existing-project, bootstrap]
  effort: medium
  side_effect: project-metadata-write
  explicit_invocation: false
---

# Adopt

Add Product Factory OS context to an existing project.

## Process

1. Inspect repository structure, stack, scripts, and docs.
2. Detect whether the project has PFO adoption files:
   - `AGENTS.md`
   - `CODEX.md`
   - `.codex-memory/MEMORY.md`
   - `.codex-memory/STATE.json`
   - `.pfo/` contracts
3. Create or update `AGENTS.md` and `CODEX.md` with marked Product Factory OS sections.
4. Create `.codex-memory/`, `.pfo/`, and initial state.
5. Record stack, available commands, known docs, and current task route in `.codex-memory/STATE.json`.
6. Add missing Product Compiler docs only when needed for the requested change:
   - `PRODUCT_BLUEPRINT.md`
   - `BUILD_PLAN.md`
   - `EXECUTION_GRAPH.md`
7. Route to `/task` after adoption.

## Existing Project State

Use the existing-project state path:

```text
EXISTING_PROJECT_DETECTED
  -> ADOPTION_REQUIRED
  -> ADOPTED
  -> EXISTING_PROJECT_ANALYZED
  -> TASK_CLASSIFIED
```

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Marker-based idempotency: re-running should not duplicate sections.
- Do not reverse-engineer huge docs without user approval.
- Do not alter application behavior.
- Do not overwrite existing project-local instructions; append/update marked PFO sections.
- Do not skip `.codex-memory/STATE.json`.
- Do not start major implementation until the existing project has been analyzed and the task route is classified.
