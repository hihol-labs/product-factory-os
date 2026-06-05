# Scope Lock

## Current Task

- Add explicit five-layer defensive diagnostics to the Product Factory OS runtime.

## Allowed Change Areas

- `docs/DEFENSIVE_LAYERS.md`
- `docs/CONTROL_HARNESS.md`
- `docs/METHODOLOGY.md`
- `docs/PFO_ARCHITECTURE.md`
- `docs/AGENT_HARNESS_ENGINEERING.md`
- `docs/DESIGN_SPACE.md`
- `docs/rubrics/pfo.md`
- `docs/INSTALL.md`
- `docs/PRODUCTION_READINESS.md`
- `.github/workflows/validate.yml`
- `scripts/validate_defensive_layers.py`
- `scripts/validate_structure.py`
- `scripts/validate_runtime.py`
- `scripts/validate_control_harness.py`
- `scripts/production_readiness.py`
- `scripts/release_check.py`
- `scripts/meta_review.py`
- `scripts/verify_install_sync.py`
- public plugin docs and metadata: `CHANGELOG.md`
- PFO state, plans, reports, and contract artifacts for this unit.

## Forbidden Change Areas

- Existing application starters and generated project behavior.
- Production, deployment, migration, DNS, billing, or external-write behavior.
- Existing user-authored dirty changes outside the allowed change areas.

## Review Rule

If the diff touches an area outside allowed scope, pause and reclassify the task before continuing.
