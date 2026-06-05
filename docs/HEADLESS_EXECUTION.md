# Headless Execution

PFO supports real behavioural fixture execution through:

```bash
python3 scripts/run_headless_fixtures.py --mode command \
  --fixture planning-only \
  --output-root .pfo-headless-runs/live \
  --command-template 'python3 {root}/scripts/pfo_headless_adapter.py'
```

The runner creates one isolated output directory per fixture, validates generated files/stdout against `tests/fixture-contracts.json`, and writes expected/actual comparison artifacts:

- `PFO_HEADLESS_COMPARISON.md`
- `PFO_HEADLESS_COMPARISON.json`
- `<fixture>/logs/comparison.md`
- `<fixture>/logs/comparison.json`

## Provider

The adapter uses `codex exec`. PFO live proof is Codex-only.

Environment variables:

- `PFO_HEADLESS_MODEL`

## Recommended Proof Set

Minimal live proof:

```bash
python3 scripts/run_headless_fixtures.py --mode command \
  --fixture planning-only \
  --fixture pfo-bot \
  --fixture adopt-existing \
  --fixture market-scan \
  --fixture review-quality \
  --output-root .pfo-headless-runs/live \
  --command-template 'python3 {root}/scripts/pfo_headless_adapter.py'
```

Run this manually before public releases or through `workflow_dispatch` when Codex auth and budget are available.

For a single high-risk skill, choose 2 or 3 representative fixtures and inspect `PFO_HEADLESS_COMPARISON.md` before accepting the skill as validated.

CI keeps using `--mode mock` because real Codex execution depends on account auth, budget, and rate limits.
