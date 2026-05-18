---
name: migrate
description: Safely apply database or data migrations with backup and rollback notes.
argument-hint: migration file, SQL, version, or environment
license: MIT
metadata:
  category: operations
  tags: [database, migration, rollback]
  effort: high
  side_effect: data-migration
  explicit_invocation: true
---

# Migrate

Apply migrations carefully.

## Process

1. Identify target database and environment.
2. Inspect migration and current schema.
3. Require explicit confirmation for production.
4. Create or verify backup where practical.
5. Apply migration.
6. Verify schema and application health.
7. Document rollback.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- No production mutation without confirmation.
- No destructive migration without rollback discussion.
- Prefer transactional migrations when supported.
