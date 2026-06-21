# Repository Coverage Ledger

## Acceptance Runtime Enforcement

- `scripts/pfo.py`: acceptance contract creation, CLI commands, and `verify-work --pass-gate` blocking behavior.
- `scripts/validate_acceptance_contract.py`: deterministic validation of source-traced criteria, evidence, status, and changed-validator independence.
- `scripts/production_readiness.py`, `scripts/validate_structure.py`, `scripts/validate_runtime.py`, `scripts/validate_control_harness.py`: repository-level wiring.
- `docs/METHODOLOGY.md`, `docs/CONTROL_HARNESS.md`, `docs/gates/acceptance-contract-gate.md`: Harness Engineering guide/sensor documentation.
- `.pfo/ACCEPTANCE_CONTRACT.json`: active acceptance proof for this fix.
- `scripts/validate_control_harness.py`: CI-safe runtime-only artifact handling for `.codex-memory/` and `.pfo/` references.

Security-sensitive review focused on local runtime policy enforcement. No new network, secret, deploy, auth, or destructive filesystem capability was added.
