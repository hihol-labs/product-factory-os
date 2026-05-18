---
name: grill-me
description: Interactive read-only stress test for plans, designs, architecture, strategy, and risky decisions.
argument-hint: plan, design, architecture, strategy, migration, deploy, or decision
license: MIT
metadata:
  category: strategy
  tags: [interview, stress-test, planning, decision-quality]
  effort: medium
  side_effect: read-only
  explicit_invocation: false
---

# Grill Me

Use this skill when the user wants to stress-test a plan, design, product decision, architecture, migration, deploy plan, or says "grill me".

## Process

1. Read relevant project docs and code when an answer can be discovered locally.
2. Ask one question at a time.
3. For each question, include the recommended answer.
4. Walk the decision tree until assumptions, risks, dependencies, and next actions are clear.
5. End with unresolved risks and the next artifact that should change if the direction is accepted.

## Question Shape

Use this shape for each question:

```markdown
Question: ...

Recommended answer: ...

Why it matters: ...
```

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Read-only by default.
- Prefer repository evidence over asking the user.
- Do not replace `/review`; use this before review to improve decision quality.
- Do not edit files unless the user explicitly asks to turn the result into artifacts.
- Ask questions one at a time.
- Stop when the remaining unknowns no longer change architecture, scope, validation, security, rollout, or cost.
