# Security Review: self-runtime contract gate

## Scope

- Scan mode: diff
- Target: self-runtime changes for `scripts/pfo_contract_gate.py`, `scripts/validate_self_contracts.py`, installer wiring, and related validation docs.
- Context: threat model -> discovery -> validation -> attack path -> final report
- Explicit exclusions: generated PFO runtime reports are treated as runtime evidence, not product implementation.
- Runtime/test status: bounded static review plus local validators listed in this report.

## Threat Model

Assets are PFO adoption integrity, contract gate correctness, CLI wrapper availability, and release validation. Actors are local Codex agents and repository maintainers. Trust boundaries are project-owned source files, generated PFO runtime reports, WSL PATH resolution, and security evidence generation. The key invariant is that runtime reports must not create unrelated security blockers, while real security-sensitive source changes still require evidence.

## Discovery

Reviewed the diff surfaces that can affect gate decisions:

- `scripts/pfo_contract_gate.py`
- `scripts/validate_self_contracts.py`
- `scripts/install_workspace.py`
- validator wiring in CI, release, production readiness, runtime, and install sync
- concrete self `.pfo` contracts

Required coverage artifacts:

- `deep_review_input.csv`
- `work_ledger.jsonl`
- `repository_coverage_ledger.md`
- `candidate_ledger.jsonl`

## Validation

Validated that runtime report files are excluded before risk classification, documentation/test-only changes do not require security evidence, and self-adopted PFO repositories fail closed when required `.pfo` contracts contain template tokens. Direct WSL wrapper execution was verified with `wsl pfo --help`.

## Attack Path

Potential attack paths considered:

- A stale generated report mentions security terms and blocks unrelated adoption.
- A self-adopted PFO repo keeps template contract lines and passes readiness.
- A real change to gate code avoids security evidence.

The implemented gate keeps runtime-only files out of product change classification, adds self-contract validation, and still requires coverage artifacts for this real gate change.

## Findings

### No findings

No reportable findings survived discovery, validation, and attack-path analysis.

## Coverage Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Deep review input | `reports/self-runtime-security/deep_review_input.csv` | Canonical diff worklist |
| Work ledger | `reports/self-runtime-security/work_ledger.jsonl` | Completion receipts for reviewed rows |
| Coverage ledger | `reports/self-runtime-security/repository_coverage_ledger.md` | Closed surfaces and dispositions |
| Candidate ledger | `reports/self-runtime-security/candidate_ledger.jsonl` | Discovery, validation, and attack_path receipts |

## Final Decision

Status: `PASSED`.
