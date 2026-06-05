---
name: brainstorm
description: Structured ideation router for turning rough ideas into decision-ready PFO paths.
argument-hint: rough idea, product concept, feature concept, naming, options, or opportunity
license: MIT
metadata:
  category: strategy
  tags: [brainstorm, ideation, discovery, planning, decision-quality]
  effort: medium
  side_effect: read-only
  explicit_invocation: false
---

# Brainstorm

Use this skill when the user wants ideas, options, product concepts, names, feature variants, or a structured brainstorming pass before committing to a PFO plan.

This is a routing and decision-quality layer over `/discover`, `/advisor`, `/grill-me`, `/strategy`, and `/blueprint`.

## Process

1. Capture the raw idea, target user, desired outcome, constraints, and uncertainty.
2. Generate a small option set, not an unbounded list.
3. Compare options by impact, evidence needed, cost, reversibility, risk, and fastest validation path.
4. Route the next step:
   - `/discover` when the problem, ICP, market, or demand evidence is unclear.
   - `/advisor` when the user needs a recommendation between known options.
   - `/grill-me` when the plan or assumption needs adversarial stress testing.
   - `/strategy` when an existing product direction or roadmap needs to change.
   - `/blueprint` when the user approves a planning-only artifact pass.
5. Name the artifact that should change next, such as `DISCOVERY.md`, `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md`, `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, or an ADR.

## Output Shape

```markdown
Options:
- ...

Recommendation:
- ...

Next PFO route:
- ...

Artifact to change next:
- ...
```

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Read-only by default.
- Do not produce a large idea dump; keep options decision-ready.
- Do not skip validation when demand, ICP, or problem evidence is weak.
- Do not route directly to implementation unless an approved PFO plan already exists.
- Prefer `/grill-me` before `/blueprint` when assumptions are risky.
