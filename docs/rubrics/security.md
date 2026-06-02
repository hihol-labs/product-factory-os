# Security Audit Rubric

Security audits are source-read-only by default. Remediation is a separate user-approved step.

## Security Audit v2

Use this sequence for non-trivial security work:

```text
threat model -> discovery -> validation -> attack path -> final report
```

Required evidence for a PFO-equivalent audit:

- `deep_review_input.csv`: reviewed file or shard worklist.
- `work_ledger.jsonl`: completion receipt for each reviewed row.
- `repository_coverage_ledger.md`: reviewed surfaces and dispositions.
- `candidate_ledger.jsonl`: discovery, validation, and attack_path receipts per candidate.
- A report validated by `scripts/validate_security_report.py`.

If `diffRisk` reports `security_change`, require Codex Security diff-scan evidence or the PFO-equivalent artifacts above.

## Critical

- Authentication bypass or missing auth on sensitive actions.
- Authorization bypass between users, tenants, or admin roles.
- Hardcoded production secrets or tokens.
- Direct SQL/command/template injection with plausible exploit path.
- Unsafe file upload or path traversal that can read or write arbitrary files.
- Public exposure of sensitive personal data.

## Important

- Weak session/cookie configuration.
- Missing CSRF protection where cookie auth is used.
- Overbroad CORS.
- Missing rate limiting on auth or expensive endpoints.
- Sensitive data in logs.
- Dependency with known high-severity CVE and reachable usage.
- Missing security headers for browser apps.

## Recommended

- Add structured security logging.
- Add dependency audit to CI.
- Add secret scanning.
- Add threat model for privileged flows.
- Document incident rollback and credential rotation.

## Output

Use `docs/templates/SECURITY_AUDIT_REPORT.md`. Findings must include:

- severity
- confidence
- CWE
- affected lines
- validation evidence
- reachability or attack path
- remediation

`BLOCKED` means at least one Critical finding exists.

Also return `BLOCKED` when required coverage artifacts are missing, a candidate lacks receipts, or security-changing work lacks a validated Codex Security or PFO-equivalent report.
