---
name: bugfix
description: Systematically reproduce, diagnose, fix, and regression-test a bug.
argument-hint: symptom, stack trace, failing test, or bug report
license: MIT
metadata:
  category: daily-work
  tags: [bugfix, debug, regression]
  effort: high
  side_effect: code-tests-write
  explicit_invocation: false
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

## Security Fix-Finding

When the bug is a security finding, preserve the source, closest control, sink, attacker input, impact, and preconditions before editing code.

Use this stricter order:

1. Reproduce the vulnerable behavior or encode the smallest failing regression test.
2. Make the minimal fix at the correct security boundary.
3. Prove the original source-to-sink path no longer works.
4. Prove legitimate behavior still works.
5. Search nearby call sites or sibling operations for bypasses.
6. Record the validation commands, artifacts, and remaining proof gaps.

Do not claim the security issue is fixed from code inspection alone when a focused test or realistic reproducer is feasible.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Do not apply broad rewrites while fixing a narrow bug.
- Do not fix before root-cause evidence exists.
- Engineering Discipline v2 blocks bugfix work without `ROOT_CAUSE.md` and root-cause state evidence.
- If three fix attempts fail, stop and question the architecture before continuing.
- Preserve user changes in the worktree.
- If the symptom points to production data, ask before destructive inspection or mutation.
- Security fixes must start with reproduction or a clear proof gap, then show that the original vulnerable path is closed.
