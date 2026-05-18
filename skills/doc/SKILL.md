---
name: doc
description: Create or update project documentation in the local style.
argument-hint: README, API docs, module docs, or usage guide
license: MIT
metadata:
  category: daily-work
  tags: [docs, readme, api]
  effort: low
  side_effect: docs-write
  explicit_invocation: false
---

# Doc

Write documentation that matches the project.

## Process

1. Read existing docs and code.
2. Identify the audience: user, developer, operator, maintainer.
3. Update the smallest relevant document.
4. Include commands, environment variables, and examples when useful.
5. Verify commands if practical.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Do not document features that do not exist.
- Do not create a new docs system for a small change.
- Keep generated docs concise and maintainable.
