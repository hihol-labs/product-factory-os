# Security Review: target-100 PFO gate hardening

## Scope

Reviewed the current working-tree changes for target workspace criteria and global PFO auto-adoption enforcement:

- `scripts/pfo_metrics.py`
- `scripts/validate_workspace_targets.py`
- `scripts/production_readiness.py`
- `scripts/release_check.py`
- `scripts/install_workspace.py`
- `scripts/pfo_contract_gate.py`
- `reports/target-100-workspace-metrics.json`
- `dashboard/index.html`
- `README.md`
- `docs/INSTALL.md`

Coverage artifacts:

- `reports/target-100-security/artifacts/02_discovery/deep_review_input.csv`
- `reports/target-100-security/artifacts/02_discovery/work_ledger.jsonl`
- `reports/target-100-security/artifacts/03_coverage/repository_coverage_ledger.md`
- `reports/target-100-security/artifacts/05_findings/no-findings/candidate_ledger.jsonl`

## Threat Model

Assets are deterministic PFO gate correctness, release-readiness enforcement, workspace metric integrity, and global auto-adoption policy clarity. Actors are local Codex agents and repository maintainers. Trust boundaries are local project state files, generated metrics JSON, installer-written policy files, and release validation scripts.

The main abuse case is a false PASS where release or readiness proceeds despite missing live eval proof, sub-target verification pass rate, excessive repair loops, placeholder self-contracts, or non-adopted local projects.

## Discovery

Discovery reviewed the new metric thresholds, target validator, readiness/release wiring, dashboard rendering, and installer policy fields. The changes do not parse network input, evaluate dynamic code, read secrets, execute user-controlled commands, or broaden filesystem permissions beyond existing installer behavior.

## Validation

Validation focused on fail-closed behavior:

- `validate_workspace_targets.py` exits non-zero when context coverage, verification pass rate, repair-loop ratio, or live eval status miss target.
- `validate_workspace_targets.py` can validate either live workspace state or a committed metrics proof for CI environments that do not have the local machine workspace.
- `production_readiness.py` and `release_check.py` both invoke the new target validator.
- `release_check.py` still requires `validate_release_live_headless.py`, so live command-mode proof remains mandatory for release.
- `install_workspace.py` only writes stricter global policy metadata and managed AGENTS text.
- `pfo_contract_gate.py` narrows dependency-change matching to changed dependency manifest and lockfile names instead of scanning arbitrary diff text.

## Attack Path

No exploitable attack path was found. The changed code reads local JSON/markdown state, computes ratios, and returns deterministic pass/fail output. The committed metrics proof contains only aggregate target values and no secrets. The dashboard change renders numeric fields from local `metrics.json` using the existing escaping helper. The installer change adds policy keys and text but does not add new command execution paths. The contract-gate change removes over-broad text matching and does not suppress real changed dependency manifest or lockfile paths.

## Findings

### No findings

No security findings were identified in the scoped diff.

## Coverage Artifacts

Artifacts reviewed and included:

- `deep_review_input.csv`
- `work_ledger.jsonl`
- `repository_coverage_ledger.md`
- `candidate_ledger.jsonl`

## Final Decision

PASSED. Continue to deterministic PFO gates. The target validator intentionally blocks the current workspace until verification pass rate is above 95%.
