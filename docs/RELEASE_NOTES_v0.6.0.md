# Product Factory OS v0.6.0

This release turns PFO from a documented methodology scaffold into a more executable Codex product-runtime.

## Highlights

- `pfo plan` now generates missing planning artifacts and an execution graph skeleton.
- Hook parity layer added: route reminders, preflight context, skill completeness, commit completeness, and review-before-commit gates.
- Route snapshot coverage now maps every skill to at least one fixture.
- Install/onboarding now includes a smoke-tested `new -> plan -> validate` path.
- README and methodology docs now state explicit non-goals and production boundaries.
- Roadmap now defines 0.6/0.7/0.8/0.9 milestones on the way to 1.0.
- Documentation now consistently reflects hook gates, route snapshots, `pfo plan`, starter validation, and open-core boundaries.

## Validation

Run:

```bash
python3 scripts/release_check.py
```

Expected result:

```text
OK: release checks passed for 0.6.0
```
