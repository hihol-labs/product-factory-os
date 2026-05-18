---
name: explain
description: Explain code, architecture, or workflow without changing files.
argument-hint: file, function, concept, or subsystem
license: MIT
metadata:
  category: daily-work
  tags: [explain, learning, read-only]
  effort: low
  side_effect: read-only
  explicit_invocation: false
---

# Explain

Explain how something works.

## Process

1. Read the relevant files.
2. Start with the big picture.
3. Walk through the control flow or data flow.
4. Name surprising decisions, risks, and extension points.
5. Use small diagrams when they clarify.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Read-only unless the user separately asks for edits.
- Prefer concrete file references.
- Distinguish facts from guesses.
