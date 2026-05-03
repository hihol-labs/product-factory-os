---
name: bugfix
description: Systematically reproduce, diagnose, fix, and regression-test a bug.
argument-hint: symptom, stack trace, failing test, or bug report
license: MIT
metadata:
  category: daily-work
  tags: [bugfix, debug, regression]
---

# Bugfix

Fix the root cause, not just the symptom.

## Process

1. Reproduce the issue or identify why it cannot be reproduced.
2. Trace from failing behavior to responsible code.
3. Make the smallest correct fix.
4. Add a regression test when feasible.
5. Run relevant tests.
6. Summarize root cause and verification.

## Rules

- Do not apply broad rewrites while fixing a narrow bug.
- Preserve user changes in the worktree.
- If the symptom points to production data, ask before destructive inspection or mutation.

