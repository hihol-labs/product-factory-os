# Product Factory OS v1.0.0

This release promotes PFO from methodology runtime to production-grade local platform.

## Highlights

- Behavioural contracts cover every route fixture in `tests/fixture-contracts.json`.
- `scripts/run_headless_fixtures.py` adds contract-only, mock, and command-backed headless fixture execution.
- CI, meta-review, release checks, and review-before-commit gates run behavioural contracts and headless mock validation.
- Every skill declares `effort`, `side_effect`, and `explicit_invocation`.
- Every skill has a `## Self-validation` section.
- Dangerous routes warn before production, migration, infrastructure, GitHub, or external tool writes.
- `session-diagnostics.py` reports stale state, recovery, handoff, and telemetry warnings.
- `docs/DESIGN_SPACE.md` tracks external methodology coverage and remaining gaps.
- `/blueprint` now requires architecture variants, adversarial debate, and ADR capture.

## Verification

```text
python3 scripts/production_readiness.py
python3 scripts/release_check.py
python3 hooks/review-before-commit.py --full
```

All three gates must pass before tagging `v1.0.0`.
