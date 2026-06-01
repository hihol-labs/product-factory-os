---
name: strategy
description: Replan an existing product or project after context changes.
argument-hint: project context, pivot, launch, roadmap, or constraints
license: MIT
metadata:
  category: strategy
  tags: [strategy, roadmap, backlog, adr]
  effort: high
  side_effect: docs-write
  explicit_invocation: false
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
- `.pfo/EXPERIMENT_PROGRAM.md`
- `.pfo/EXPERIMENTS.tsv`
- `ASSET_REGISTER.md`
- `CONTENT_BACKLOG.md`
- `LAUNCH_PLAN.md`
- `LAUNCH_MATURITY_GATE.md` when launch-stage ops readiness is in scope
- `SCALE_MOAT_REGISTER.md` when scale, enterprise, or defensibility is in scope
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
   - evidence quality: real conversations, past behavior evidence, contradicting evidence, BUILD truth conditions
   - validation experiments and exit criteria
   - adversarial discovery: failure case, competitor win case, current alternatives, ignored uncomfortable signals
   - monetization or value-capture model
   - acquisition path
   - funnel stages, MVP measurement contract, false-positive traction, and bottleneck
   - feedback loop and iteration decision
   - optional launch maturity audit when the founder or operator is becoming a bottleneck
   - optional scale moat register when domain knowledge, edge cases, data flywheel, workflow integration, or switching cost matter
   - fixed metric experiment loop when autonomous self-improvement is requested
   - asset and content candidates
   - launch success metrics
   - strategic risk matrix
6. Generate options and tradeoffs.
7. Record the chosen direction as an ADR.
8. Update backlog and launch plan.
9. Update `.codex-memory/STATE.json` decision log when present.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Planning docs only unless the user asks for implementation.
- Do not rewrite history; append dated decisions.
- Do not allow large implementation work to start when strategy Critical checks fail for a non-trivial product.
- Do not count activity as progress unless it changes a signal, gate, decision, or reusable asset.
- Do not count founder enthusiasm, compliments, or future-intent answers as strong demand evidence.
- For Autoresearch-style work, use one metric, fixed budget, protected evaluation, baseline-first logging, and keep/discard/crash decisions.
- Do not treat recent social buzz as validated demand. Convert it into `VALIDATION_PLAN.md` experiments and decision criteria.
