# Security Review: <target>

## Scope

- Scan mode: repository | scoped-path | diff | fix-finding | deep
- Target: <project, path, PR, branch, or finding id>
- Context: threat model -> discovery -> validation -> attack path -> final report
- Explicit exclusions: <none or listed>
- Runtime/test status: <commands or bounded static review>

## Threat Model

Record assets, actors, trust boundaries, attacker-controlled inputs, security invariants, and assumptions that govern this review.

## Discovery

Record the inspected worklist and candidate inventory.

Required coverage artifacts:

- `deep_review_input.csv`
- `work_ledger.jsonl`
- `repository_coverage_ledger.md`
- `candidate_ledger.jsonl`

## Validation

For each candidate, record the validation method, evidence, proof gaps, and disposition: `reportable`, `suppressed`, `not_applicable`, or `deferred`.

## Attack Path

Map surviving candidates from source to sink, include reachability, preconditions, counterevidence, severity rationale, and final reportability decision.

## Findings

Start with a summary table, then either use `### No findings` or numbered findings.

### No findings

No reportable findings survived discovery, validation, and attack-path analysis.

### [1] <finding title>

| Field | Value |
|---|---|
| Severity | critical, high, medium, or low |
| Confidence | high, medium, or low |
| CWE | CWE id and name, or none |
| Affected lines | path:line list |

#### Summary

Explain why the issue matters.

#### Validation

State method, evidence, and remaining uncertainty.

#### Dataflow

Show attacker input -> control -> sink -> impact.

#### Reachability

State attacker role, boundary, preconditions, and counterevidence.

#### Remediation

Give the minimal fix and regression checks.

## Coverage Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Deep review input | `<artifacts>/02_discovery/deep_review_input.csv` | Canonical file or shard worklist |
| Work ledger | `<artifacts>/02_discovery/work_ledger.jsonl` | Completion receipts for reviewed rows |
| Coverage ledger | `<artifacts>/03_coverage/repository_coverage_ledger.md` | Closed surfaces and dispositions |
| Candidate ledger | `<artifacts>/05_findings/<candidate_id>/candidate_ledger.jsonl` | Discovery, validation, and attack_path receipts |

## Final Decision

Status: `PASSED`, `PASSED_WITH_WARNINGS`, or `BLOCKED`.

Use `BLOCKED` when critical findings exist, required coverage artifacts are missing, a candidate lacks required receipts, or security-changing work lacks Codex Security diff-scan evidence or a PFO-equivalent report.
