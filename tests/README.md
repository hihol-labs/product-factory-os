# Tests

This directory contains methodology fixtures, routing snapshots, and validation helpers.

Run:

```bash
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/verify_fixture_contracts.py
python3 scripts/run_headless_fixtures.py --mode mock
python3 scripts/validate_hooks.py
python3 scripts/production_readiness.py
```

Fixtures are intentionally small. They prove that routing expectations, required outputs, route reminders, and docs stay synchronized as the methodology evolves.

## Snapshot Contract

`tests/snapshots/route-snapshots.json` is the machine-readable source of truth for route coverage. Every PFO skill must have at least one snapshot entry that points to a fixture directory with:

- `idea.md`: user request and expected route
- `expected-files.txt`: expected artifacts or `NONE`
- `notes.md`: behavioral expectation and guardrails

`hooks/skill-completeness.py` uses this snapshot file to prevent skills from drifting away from docs and fixtures.

## Behavioural Contracts

`tests/fixture-contracts.json` defines the expected behavioural output for every route fixture. Fixture-local `expected-contract.json` files can strengthen the shared registry for high-risk routes.

Validation has three levels:

- `python3 scripts/verify_fixture_contracts.py`: validates fixture docs and expected output contracts.
- `python3 scripts/run_headless_fixtures.py --mode mock`: exercises the output validator against generated mock artifacts for all fixtures.
- `python3 scripts/run_headless_fixtures.py --mode command --command-template "<command>"`: runs a real headless generator. The command receives `PFO_FIXTURE_DIR`, `PFO_PROMPT_FILE`, and `PFO_OUTPUT_DIR` and must write artifacts into `PFO_OUTPUT_DIR`.

CI runs the mock headless mode. Real LLM-backed execution is intentionally opt-in because it needs credentials, budget, and rate-limit control.
