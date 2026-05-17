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
3. Record root-cause evidence in `ROOT_CAUSE.md` or `.codex-memory/STATE.json`.
4. Add a regression test and verify it fails for the expected reason when feasible.
5. Make the smallest correct fix.
6. Verify the regression test passes.
7. Run spec compliance review, then code quality review for the touched unit.
8. Run or satisfy `scripts/validate_plan_quality.py <project>`.
9. Summarize root cause and verification.

## Rules

- Do not apply broad rewrites while fixing a narrow bug.
- Do not fix before root-cause evidence exists.
- Engineering Discipline v2 blocks bugfix work without `ROOT_CAUSE.md` and root-cause state evidence.
- If three fix attempts fail, stop and question the architecture before continuing.
- Preserve user changes in the worktree.
- If the symptom points to production data, ask before destructive inspection or mutation.
