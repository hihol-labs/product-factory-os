---
name: refactor
description: Improve structure while preserving behavior.
argument-hint: file, module, subsystem, or smell
license: MIT
metadata:
  category: daily-work
  tags: [refactor, maintainability]
  effort: medium
  side_effect: code-write
  explicit_invocation: false
---

# Refactor

Improve maintainability without behavior changes.

## Process

1. Read the current implementation and tests.
2. Identify the smallest structural improvement.
3. Keep public APIs stable unless the user approves a breaking change.
4. Run tests before and after when possible.
5. Document any risk or behavior uncertainty.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- No unrelated cleanup.
- No opportunistic dependency changes.
- Add tests first if behavior is not protected.
