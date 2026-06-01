# Scope Lock

## Current Task

- Integrate an SEO optimization workflow into the Product Factory OS plugin runtime.

## Allowed Change Areas

- `skills/seo/`
- `docs/SKILL_CONTRACTS.md`
- `docs/TRIGGERS.md`
- `docs/CALL_GRAPH.md`
- `docs/CONTROL_HARNESS.md`
- `hooks/route-reminder.py`
- `scripts/validate_structure.py`
- `scripts/validate_control_harness.py`
- `tests/fixtures/seo-optimization/`
- `tests/snapshots/route-snapshots.json`
- `tests/fixture-contracts.json`
- public plugin docs and metadata: `README.md`, `README.ru.md`, `CHANGELOG.md`, `.codex-plugin/plugin.json`, `marketplace/marketplace-entry.json`
- PFO state, plans, reports, and contract artifacts for this unit.

## Forbidden Change Areas

- Existing application starters and generated project behavior.
- Production, deployment, migration, DNS, billing, or external-write behavior.
- Existing user-authored dirty changes outside the allowed change areas.

## Review Rule

If the diff touches an area outside allowed scope, pause and reclassify the task before continuing.
