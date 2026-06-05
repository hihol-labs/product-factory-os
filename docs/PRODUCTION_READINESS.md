# Production Readiness

Product Factory OS is production-grade when the repository passes:

```bash
python3 scripts/production_readiness.py
```

This gate runs:

- structure validation
- Engineering Discipline v2 self-check
- control harness validation
- defensive layer diagnostics
- self-adopted contract validation
- route fixtures
- trigger drift verification
- behavioural fixture contracts
- headless fixture mock validation
- release live-headless config validation
- eval layer validation
- skill risk profile validation
- execution graph validation
- runtime asset validation
- security report contract validation
- hook validation
- manifest drift verification
- install/hook sync verification
- benchmark suite
- meta-review

## Real Headless Execution

CI runs mock headless mode because real Codex execution requires credentials and budget. For a live run, use the adapter:

```bash
python3 scripts/run_headless_fixtures.py \
  --mode command \
  --fixture planning-only \
  --command-template 'python3 {root}/scripts/pfo_headless_adapter.py'
```

The command also receives:

- `PFO_FIXTURE`
- `PFO_FIXTURE_DIR`
- `PFO_PROMPT_FILE`
- `PFO_OUTPUT_DIR`
- `PFO_ROOT`

The runner validates generated output against the same behavioural contracts used in CI and writes expected/actual comparison reports under the output root.

Before release, run:

```bash
python3 scripts/release_check.py
```

`release_check.py` requires command-mode live proof for the 7 critical fixtures through `scripts/validate_release_live_headless.py`.

See `docs/HEADLESS_EXECUTION.md` for provider options and the release proof set.
