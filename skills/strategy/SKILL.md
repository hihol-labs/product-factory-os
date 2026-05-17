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
- `IDEA_SCORECARD.md`
- `VALIDATION_PLAN.md`
- `FUNNEL_MODEL.md`
- `FEEDBACK_LOG.md`
- `ITERATION_REVIEW.md`
- `ASSET_REGISTER.md`
- `CONTENT_BACKLOG.md`
- `LAUNCH_PLAN.md`
- `BACKLOG.md`
- `docs/adr/YYYY-MM-DD-decision.md`

## Process

1. Read current docs and project state.
2. Apply `docs/rubrics/strategy.md`.
3. Run `/market-scan` when roadmap, pivot, launch, ICP, competitor, pricing, or feedback decisions depend on fresh public market/community signals.
4. Identify gaps across product, tech, delivery, operations, monetization, acquisition, and go-to-market.
5. Define or update:
   - problem
   - ICP
   - value proposition
   - MVP scope
   - idea score and KILL/TEST/BUILD decision
   - validation experiments and exit criteria
   - monetization or value-capture model
   - acquisition path
   - funnel stages and bottleneck
   - feedback loop and iteration decision
   - asset and content candidates
   - launch success metrics
   - strategic risk matrix
6. Generate options and tradeoffs.
7. Record the chosen direction as an ADR.
8. Update backlog and launch plan.
9. Update `.codex-memory/STATE.json` decision log when present.

## Rules

- Planning docs only unless the user asks for implementation.
- Do not rewrite history; append dated decisions.
- Do not allow large implementation work to start when strategy Critical checks fail for a non-trivial product.
- Do not count activity as progress unless it changes a signal, gate, decision, or reusable asset.
- Do not treat recent social buzz as validated demand. Convert it into `VALIDATION_PLAN.md` experiments and decision criteria.
