# Contributing

This repository is a methodology plugin. Changes should preserve the workflow contract.

## Contribution Rules

- Keep skill names stable unless there is a migration note.
- Update `docs/SKILL_CONTRACTS.md` when a skill input, output, side effect, or idempotency changes.
- Update `docs/CALL_GRAPH.md` when skills call or route to different skills.
- Add or update validation checks when changing required structure.
- Run:

```bash
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/meta_review.py
```

## Review Standard

Every change should answer:

- What user workflow changed?
- What files or docs are produced?
- Is the change read-only, project-local, or production-impacting?
- Can it be run twice safely?

## Documentation Standard

When changing user-facing behavior, update:

- `README.md` for English overview changes
- `README.ru.md` for Russian overview changes
- `docs/INSTALL.md` for local testing or installation changes
- `docs/examples/` when the golden path changes
