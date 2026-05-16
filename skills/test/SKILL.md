---
name: test
description: Create, repair, or run tests for changed behavior.
argument-hint: file, module, feature, or failing test output
license: MIT
metadata:
  category: quality
  tags: [tests, qa, coverage]
---

# Test

Use this skill to add or fix focused tests.

The canonical testing rubric lives in `docs/rubrics/testing.md`.

## Process

1. Detect the test framework and naming conventions.
2. Identify behavior under test.
3. Identify product type and minimum test set from `docs/rubrics/testing.md`.
4. For changed behavior, write the failing test first and record the red evidence.
5. Add unit tests first, integration tests when boundaries are involved, and E2E/smoke tests for deployable user flows.
6. Include edge cases, negative cases, permission cases, and regression cases for bugs.
7. Add contract tests for API, bot, CLI, webhook, queue, or integration boundaries.
8. Run the smallest relevant test command, then broader tests if risk warrants it.
9. Update `TEST_PLAN.md` and record green/refactor evidence in `QUALITY_GATES.md` or `.codex-memory/STATE.json`.

## Rules

- Do not rewrite the app to make tests easy.
- Prefer stable behavior assertions over snapshots.
- Mock external services at process boundaries.
- Report commands run and failures that remain.
- Do not mark a gate as passing without a command or explicit manual check.
- Do not count a new behavior test as valid unless it was observed failing before implementation, or the exception is explicit.
- For production-facing products, ensure a smoke path exists before deploy readiness.
