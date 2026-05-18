---
name: guide
description: Convert existing project documents into a step-by-step Codex execution guide.
argument-hint: project path or docs folder
license: MIT
metadata:
  category: planning
  tags: [guide, prompts, execution]
  effort: medium
  side_effect: docs-write
  explicit_invocation: false
---

# Guide

Create `CODEX_GUIDE.md` from existing project documents.

## Inputs

Look for:

- `PROJECT_ARCHITECTURE.md`
- `IMPLEMENTATION_PLAN.md`
- `PRD.md`
- `CODEX.md`
- `README.md`

## Output

`CODEX_GUIDE.md` should include:

- Project context summary
- Required operating rules
- Ordered implementation prompts
- Verification commands per step
- Review/test checkpoints
- Resume instructions for later sessions

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Do not change architecture decisions while creating the guide.
- If docs conflict, stop and ask whether to fix docs via `/review`.
- Make each step small enough to verify independently.
