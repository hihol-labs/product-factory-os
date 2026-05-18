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

When Obsidian export is requested, regenerate the local knowledge layer with:

```bash
python3 scripts/pfo.py export <project> --target obsidian
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
- Latest `HANDOFF.md` status when present
- Product classification
- Idea, validation, feedback, funnel, asset, and content status when present
- Completed modules
- Failed validations

## Template

```markdown
---
title: Session YYYY-MM-DD
tags:
  - pfo/session
  - pfo/memory
aliases:
  - YYYY-MM-DD Session
---

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
---
title: Memory
tags:
  - pfo/memory
  - pfo/project
aliases:
  - Project Memory
---

# Memory

- YYYY-MM-DD: one-line session summary -> session_YYYY-MM-DD.md

## Obsidian Links

- [[STATE]]
- [[LEARNINGS]]
- [[HANDOFF]]
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
- Use Obsidian-compatible frontmatter, wikilinks, and callouts in `.codex-memory/*.md` only as additive Markdown; do not put Obsidian-only syntax in `STATE.json`.
- Keep `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md`, and `QUALITY_GATES.md` as canonical source artifacts; Obsidian notes are regenerated export copies.
- Do not use `/session-save` as a substitute for `/handoff` when another session or role must start from a compact transfer artifact.
- If `.codex-memory/` is not appropriate for the project, ask once and use the project-local convention the user chooses.
