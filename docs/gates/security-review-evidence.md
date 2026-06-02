# Security Review Evidence Gate

Purpose: make security review coverage auditable, not just asserted.

This gate applies when `/security-audit` runs, when deploy readiness depends on security review, and whenever `diffRisk` classifies a change as `security_change`.

Required sequence:

```text
threat model -> discovery -> validation -> attack path -> final report
```

Required artifacts for a PFO-equivalent security review:

- `deep_review_input.csv`
- `work_ledger.jsonl`
- `repository_coverage_ledger.md`
- `candidate_ledger.jsonl` for every candidate that reaches discovery
- `SECURITY_AUDIT_REPORT.md` or a report under `reports/` validated by `scripts/validate_security_report.py`

Gate output:

- `PASS`: report validates, required coverage artifacts exist, and no critical finding remains open.
- `PASS_WITH_WARNINGS`: report validates but has deferred or low-confidence rows with explicit proof gaps.
- `BLOCKED`: security-changing work has no Codex Security diff-scan or PFO-equivalent report, required artifacts are missing, candidates lack receipts, or a critical finding remains.

Deep scan mode is optional and expensive. Use it only for release readiness, high-risk scopes, security-sensitive regressions, or explicit user request.
