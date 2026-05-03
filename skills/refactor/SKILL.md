---
name: refactor
description: Improve structure while preserving behavior.
argument-hint: file, module, subsystem, or smell
license: MIT
metadata:
  category: daily-work
  tags: [refactor, maintainability]
---

# Refactor

Improve maintainability without behavior changes.

## Process

1. Read the current implementation and tests.
2. Identify the smallest structural improvement.
3. Keep public APIs stable unless the user approves a breaking change.
4. Run tests before and after when possible.
5. Document any risk or behavior uncertainty.

## Rules

- No unrelated cleanup.
- No opportunistic dependency changes.
- Add tests first if behavior is not protected.

