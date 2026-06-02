# Security Review: security-audit v2 methodology diff

## Scope

- Scan mode: diff
- Target: Product Factory OS methodology changes that introduce security-audit v2, security evidence gating, report validation, and fix-finding rules.
- Context: threat model -> discovery -> validation -> attack path -> final report
- Explicit exclusions: no application runtime code or production system was in scope.
- Runtime/test status: PFO validators are the runtime evidence for this methodology change.

## Threat Model

Assets:

- PFO gate integrity.
- Project security review evidence.
- Generated-project deploy readiness decisions.

Trust boundaries:

- Agent output versus deterministic PFO gates.
- Security findings versus validated evidence.
- User-approved security-changing diffs versus unreviewed changes.

Security invariants:

- A `security_change` diff must not pass without Codex Security diff-scan evidence or a PFO-equivalent report.
- Candidate findings must not become final findings without discovery, validation, and attack_path receipts.
- Security fixes must prove the original vulnerable path is closed.

## Discovery

The review worklist covers the files that define the new security workflow, gate, report validator, fixtures, and validation wiring.

Required coverage artifacts:

- `reports/security-audit-v2/artifacts/02_discovery/deep_review_input.csv`
- `reports/security-audit-v2/artifacts/02_discovery/work_ledger.jsonl`
- `reports/security-audit-v2/artifacts/03_coverage/repository_coverage_ledger.md`
- `reports/security-audit-v2/artifacts/05_findings/no-findings/candidate_ledger.jsonl`

Discovery found no reportable security vulnerability in the methodology change itself. The main risk is workflow regression: introducing a stricter gate that is not wired into validation, fixtures, or self-evidence.

## Validation

Validation checks:

- `scripts/validate_security_report.py --self-check` validates the report template contract.
- `scripts/validate_security_report.py reports/security-audit-v2-security-review.md --require-artifacts --artifacts-dir reports/security-audit-v2/artifacts` validates this report and its coverage artifacts.
- PFO structure, fixture, route, control-harness, contract-gate, and production-readiness validators confirm the methodology wiring.

All candidate rows are closed as `not_applicable` or `suppressed` in the coverage ledger because this PR changes methodology controls, not a deployed application attack surface.

## Attack Path

Potential attack path considered:

1. A security-sensitive methodology diff is made.
2. The diff is classified as `security_change`.
3. Without an evidence gate, the change could pass based only on prose review.
4. A later project could rely on incomplete security review and reach deploy readiness with missing proof.

The implemented control breaks that path by making `security_change` require a validated report and coverage artifacts. The strongest counterevidence is that this is a methodology repository, not an application runtime; therefore the risk is process integrity rather than direct external exploitation.

## Findings

### No findings

No reportable findings survived discovery, validation, and attack-path analysis for this methodology diff.

## Coverage Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Deep review input | `reports/security-audit-v2/artifacts/02_discovery/deep_review_input.csv` | Canonical file worklist |
| Work ledger | `reports/security-audit-v2/artifacts/02_discovery/work_ledger.jsonl` | Completion receipts for reviewed rows |
| Coverage ledger | `reports/security-audit-v2/artifacts/03_coverage/repository_coverage_ledger.md` | Closed surfaces and dispositions |
| Candidate ledger | `reports/security-audit-v2/artifacts/05_findings/no-findings/candidate_ledger.jsonl` | discovery, validation, and attack_path no-finding receipts |

## Final Decision

Status: `PASSED_WITH_WARNINGS`.

Reason: no reportable methodology security finding was identified, and the new gate improves PFO evidence requirements. Warning remains because this is a PFO-equivalent local report, not an upstream Codex Security diff-scan.
