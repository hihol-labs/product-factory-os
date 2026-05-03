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
4. Add unit tests first, integration tests when boundaries are involved, and E2E/smoke tests for deployable user flows.
5. Include edge cases, negative cases, permission cases, and regression cases for bugs.
6. Add contract tests for API, bot, CLI, webhook, queue, or integration boundaries.
7. Run the smallest relevant test command, then broader tests if risk warrants it.
8. Update `TEST_PLAN.md` or `.codex-memory/STATE.json` verification history when the project uses PFO artifacts.

## Rules

- Do not rewrite the app to make tests easy.
- Prefer stable behavior assertions over snapshots.
- Mock external services at process boundaries.
- Report commands run and failures that remain.
- Do not mark a gate as passing without a command or explicit manual check.
- For production-facing products, ensure a smoke path exists before deploy readiness.
