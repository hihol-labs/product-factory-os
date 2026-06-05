# Security Review: route profiles overhead methodology diff

## Scope

- Scan mode: diff
- Target: Product Factory OS changes for `minimal`, `standard`, and `full` route profiles, minimal route gates, `artifactDebt` metrics, and validators.
- Context: route selection -> manifest generation -> verification contract -> metrics/reporting.
- Explicit exclusions: no deployed application runtime, production data, credentials, authentication flow, or external API integration was in scope.
- Runtime/test status: PFO validators are the runtime evidence for this methodology change.

## Threat Model

Assets:

- PFO gate integrity.
- Accurate route classification.
- Review and verification evidence for small tasks.
- Project-local state and artifact lists.

Trust boundaries:

- User intent versus automatic profile selection.
- Route profile policy versus generated manifest and verification contract.
- Metrics output versus state artifacts accumulated from past work.

Security invariants:

- A small-task route must reduce overhead without skipping adoption, scope, targeted verification, review, or state-save.
- Standard and full routes must not silently downgrade high-risk work.
- `artifactDebt` must report route-required documents and extras without treating missing optional history as a pass/fail security decision.

## Discovery

The review worklist covers the files that define the route profile policy, generated manifests, verification contracts, metrics output, validators, and user-facing documentation.

Required coverage artifacts:

- `reports/route-profiles-overhead-security/artifacts/02_discovery/deep_review_input.csv`
- `reports/route-profiles-overhead-security/artifacts/02_discovery/work_ledger.jsonl`
- `reports/route-profiles-overhead-security/artifacts/03_coverage/repository_coverage_ledger.md`
- `reports/route-profiles-overhead-security/artifacts/05_findings/no-findings/candidate_ledger.jsonl`

Discovery found no reportable security vulnerability in the methodology change. The main risk is process downgrade: a profile could incorrectly skip a required gate for risky work.

## Validation

Validation checks:

- `python3 -m py_compile scripts/pfo.py scripts/pfo_metrics.py scripts/validate_route_profiles.py`
- `python3 scripts/validate_route_profiles.py`
- In-memory minimal manifest assertion proves the minimal route steps are exactly adoption, scope, targetedVerification, review, stateSave and do not require Product Compiler planning docs.
- `python3 scripts/pfo_metrics.py /home/hihol/projects` produced JSON with `artifactDebt`.
- `python3 scripts/validate_context_runtime.py` passed.

All candidate rows are closed as `not_applicable` or `suppressed` in the coverage ledger because this PR changes methodology controls, not an application attack surface.

## Attack Path

Potential attack path considered:

1. A high-risk task is incorrectly classified as `minimal`.
2. The generated manifest skips planning, security, dependency, deploy, or full verification gates.
3. The project records review/state-save with insufficient evidence.
4. Later work relies on incomplete PFO state.

The implemented controls reduce this risk by reserving `minimal` for explicit small/no-risk hints, routing behavior changes and bugfixes to `standard`, routing deploy/security/migration/production/broad architecture hints to `full`, and validating the minimal profile contract with `validate_route_profiles.py`.

## Findings

### No findings

No reportable findings survived discovery, validation, and attack-path analysis for this methodology diff.

## Coverage Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Deep review input | `reports/route-profiles-overhead-security/artifacts/02_discovery/deep_review_input.csv` | Canonical file worklist |
| Work ledger | `reports/route-profiles-overhead-security/artifacts/02_discovery/work_ledger.jsonl` | Completion receipts for reviewed rows |
| Coverage ledger | `reports/route-profiles-overhead-security/artifacts/03_coverage/repository_coverage_ledger.md` | Closed surfaces and dispositions |
| Candidate ledger | `reports/route-profiles-overhead-security/artifacts/05_findings/no-findings/candidate_ledger.jsonl` | discovery, validation, and attack_path no-finding receipts |

## Final Decision

Status: `PASSED_WITH_WARNINGS`.

Reason: no reportable methodology security finding was identified. Warning remains because this is a PFO-equivalent local report, not an upstream Codex Security diff-scan.
