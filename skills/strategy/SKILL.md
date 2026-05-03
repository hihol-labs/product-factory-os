---
name: strategy
description: Replan an existing product or project after context changes.
argument-hint: project context, pivot, launch, roadmap, or constraints
license: MIT
metadata:
  category: strategy
  tags: [strategy, roadmap, backlog, adr]
---

# Strategy

Update direction for an existing project.

The canonical strategy rubric lives in `docs/rubrics/strategy.md`.

## Outputs

As needed:

- `MARKET_BRIEF.md`
- `ICP.md`
- `BUSINESS_MODEL.md`
- `GO_TO_MARKET.md`
- `LAUNCH_PLAN.md`
- `BACKLOG.md`
- `docs/adr/YYYY-MM-DD-decision.md`

## Process

1. Read current docs and project state.
2. Apply `docs/rubrics/strategy.md`.
3. Identify gaps across product, tech, delivery, operations, monetization, acquisition, and go-to-market.
4. Define or update:
   - problem
   - ICP
   - value proposition
   - MVP scope
   - monetization or value-capture model
   - acquisition path
   - launch success metrics
   - strategic risk matrix
5. Generate options and tradeoffs.
6. Record the chosen direction as an ADR.
7. Update backlog and launch plan.
8. Update `.codex-memory/STATE.json` decision log when present.

## Rules

- Planning docs only unless the user asks for implementation.
- Do not rewrite history; append dated decisions.
- Do not allow large implementation work to start when strategy Critical checks fail for a non-trivial product.
