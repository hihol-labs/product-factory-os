# Repository Coverage Ledger

## Acceptance Runtime Enforcement

- `scripts/pfo.py`: acceptance contract creation, CLI commands, and `verify-work --pass-gate` blocking behavior.
- `scripts/validate_acceptance_contract.py`: deterministic validation of source-traced criteria, evidence, status, and changed-validator independence.
- `scripts/production_readiness.py`, `scripts/validate_structure.py`, `scripts/validate_runtime.py`, `scripts/validate_control_harness.py`: repository-level wiring.
- `docs/METHODOLOGY.md`, `docs/CONTROL_HARNESS.md`, `docs/gates/acceptance-contract-gate.md`: Harness Engineering guide/sensor documentation.
- `.pfo/ACCEPTANCE_CONTRACT.json`: active acceptance proof for this fix.
- `scripts/validate_control_harness.py`: CI-safe runtime-only artifact handling for `.codex-memory/` and `.pfo/` references.

Security-sensitive review focused on local runtime policy enforcement. No new network, secret, deploy, auth, or destructive filesystem capability was added.

## Omnigent O1-O9 Runtime Completion

- `scripts/pfo.py`: policy event schema, runner/server commands, dispatch worktree creation, cross-vendor review, cost-route, live session payload, attach/share, and sandbox generation.
- `scripts/validate_omnigent_runtime.py`: behavior-level O1-O9 validation.
- `agents/*.yaml`, `docs/templates/PFO_AGENT_SPEC.yaml`: terminals and sandbox profile coverage.
- `.pfo/PERMISSION_MATRIX.json`, `docs/templates/pfo/PERMISSION_MATRIX.json`: cost/risk routing fields including `downgradeAllowed`.
- `docs/CONTROL_HARNESS.md`: runner-server-separation control and O1-O9 Harness Engineering mapping.
