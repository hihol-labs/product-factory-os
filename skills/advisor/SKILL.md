---
name: advisor
description: Read-only advisory mode for product, architecture, and engineering decisions.
argument-hint: question, tradeoff, strategy, or decision
license: MIT
metadata:
  category: strategy
  tags: [advisor, consulting, tradeoffs]
  effort: high
  side_effect: read-only
  explicit_invocation: false
---

# Advisor

Analyze without editing files.

Use `docs/rubrics/strategy.md` for product, idea-gate, validation, funnel, feedback, asset, content, market, and launch decisions. Use `docs/rubrics/review.md` for engineering readiness decisions.

## Process

1. Clarify the decision if needed.
2. List viable options.
3. Compare impact, risk, cost, reversibility, time, strategic fit, and validation path.
4. Give a recommendation with assumptions.
5. Name what would change the recommendation.
6. Identify the next artifact that should change if the decision is accepted, such as `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md`, `MARKET_BRIEF.md`, `FUNNEL_MODEL.md`, `GO_TO_MARKET.md`, `LAUNCH_MATURITY_GATE.md`, `SCALE_MOAT_REGISTER.md`, `ITERATION_REVIEW.md`, `ASSET_REGISTER.md`, or `CONTENT_BACKLOG.md`.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Read-only.
- Make assumptions explicit.
- Prefer decision quality over false certainty.
