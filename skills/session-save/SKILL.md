---
name: session-save
description: Save PFO work context, state, decisions, blockers, and next steps for continuity.
argument-hint: session summary or project path
license: MIT
metadata:
  category: workflow
  tags: [memory, context, session]
---

# Session Save

Preserve continuity between sessions.

## Output

Write a dated session note under a project memory location, for example:

```text
.codex-memory/STATE.json
.codex-memory/session_YYYY-MM-DD.md
.codex-memory/MEMORY.md
```

## Include

- What changed
- Decisions made
- Commands/tests run
- Current status
- Blockers
- Next steps
- Files touched
- PFO current state
- Product classification
- Idea, validation, feedback, funnel, asset, and content status when present
- Completed modules
- Failed validations

## Template

```markdown
# Session YYYY-MM-DD

## Summary

## Changes

## Decisions

## Verification

## Blockers

## Next Steps

## Files Touched
```

Update `.codex-memory/MEMORY.md` with a newest-first index:

```markdown
# Memory

- YYYY-MM-DD: one-line session summary -> session_YYYY-MM-DD.md
```

Update `.codex-memory/STATE.json` using `memory/session-state.schema.json`:

```json
{
  "sessionState": "ACTIVE",
  "currentStage": "PLAN_READY",
  "intent": "short user intent",
  "classification": {
    "productType": "saas",
    "domain": "subscriptions",
    "complexity": "medium",
    "requiredModules": ["auth", "billing", "database"],
    "infrastructure": ["docker"]
  },
  "architecture": {
    "pattern": "modular_monolith",
    "backend": "selected backend",
    "frontend": "selected frontend",
    "database": "selected database",
    "auth": "selected auth",
    "deployment": "selected deployment"
  },
  "artifacts": ["PRODUCT_BLUEPRINT.md", "BUILD_PLAN.md", "EXECUTION_GRAPH.md"],
  "completedModules": [],
  "failedValidations": [],
  "blockers": [],
  "nextAction": "begin modular build"
}
```

## Rules

- Do not store secrets.
- Prefer concise, resume-friendly notes.
- Update the memory index after creating a new session file.
- Keep `STATE.json` reloadable and machine-readable.
- If `.codex-memory/` is not appropriate for the project, ask once and use the project-local convention the user chooses.
