# Tests

This directory contains methodology fixtures, routing snapshots, and validation helpers.

Run:

```bash
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/validate_hooks.py
```

Fixtures are intentionally small. They prove that routing expectations, required outputs, route reminders, and docs stay synchronized as the methodology evolves.

## Snapshot Contract

`tests/snapshots/route-snapshots.json` is the machine-readable source of truth for route coverage. Every PFO skill must have at least one snapshot entry that points to a fixture directory with:

- `idea.md`: user request and expected route
- `expected-files.txt`: expected artifacts or `NONE`
- `notes.md`: behavioral expectation and guardrails

`hooks/skill-completeness.py` uses this snapshot file to prevent skills from drifting away from docs and fixtures.
