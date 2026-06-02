---
name: security-audit
description: Security-audit v2 workflow for application, repository, scoped path, PR, branch, or working-tree security review. Use for security audit, OWASP, secrets, threat model, attack path, Codex Security diff scan, release security gate, or security_change evidence requests.
argument-hint: project, service, file, or changed area
license: MIT
metadata:
  category: quality
  tags: [security, audit, owasp]
  effort: high
  side_effect: local-filesystem-write
  explicit_invocation: false
---

# Security Audit

Run a source-read-only security audit. Writing the audit report and coverage artifacts is allowed; changing application code is not.

The canonical rubric lives in `docs/rubrics/security.md`. Use it as the source of truth.

Use `docs/templates/THREAT_MODEL.md` and `docs/templates/DATA_CLASSIFICATION.md` for non-trivial SaaS, API, e-commerce, mini app, internal automation, and bot projects.

Use `docs/templates/SECURITY_AUDIT_REPORT.md` for the report shape. Validate completed reports with:

```bash
python3 scripts/validate_security_report.py SECURITY_AUDIT_REPORT.md --require-artifacts --artifacts-dir <artifacts-dir>
```

When a full repository, scoped path, PR, branch, or working-tree security scan is requested, prefer the Codex Security plugin workflow when available:

```text
threat model -> finding discovery -> validation -> attack-path analysis -> final report
```

If Codex Security is unavailable, run the PFO-equivalent workflow below and mark the report as `PFO-equivalent`.

## Phase Contract

Keep phases separate. Do not collapse discovery, validation, and severity judgment into one pass.

1. Threat model: identify assets, trust boundaries, attacker-controlled inputs, security invariants, and assumptions.
2. Discovery: build the review worklist, inspect files, and record plausible candidates without final severity claims.
3. Validation: validate or suppress each candidate with runtime proof, focused tests, or bounded source tracing.
4. Attack path: map surviving candidates from realistic attacker boundary to impact, including counterevidence.
5. Final report: write the report and validate its shape.

## Coverage Artifacts

Write artifacts under `reports/security-audit/<scan-id>/artifacts/` unless the project already has a better security-scan artifact convention.

Required artifacts:

- `02_discovery/deep_review_input.csv`: canonical file or shard worklist.
- `02_discovery/work_ledger.jsonl`: completion receipts for every reviewed row.
- `03_coverage/repository_coverage_ledger.md`: surfaces closed as `reportable`, `suppressed`, `not_applicable`, or `deferred`.
- `05_findings/<candidate_id>/candidate_ledger.jsonl`: discovery, validation, and attack_path receipts for every candidate that reaches discovery.

Every candidate must have a stable id. Do not finalize a reportable finding until its candidate ledger has discovery, validation, and attack_path receipts, or a precise deferred proof gap.

## Review Areas

- Authentication and authorization
- Secret handling
- Injection risks
- File upload and path traversal
- CORS, CSP, cookies, sessions
- Dependency and supply-chain exposure
- Logging of sensitive data
- Rate limiting and abuse controls
- Threat model coverage
- Data classification and retention
- Tenant isolation and role boundaries
- Security test coverage for sensitive flows

## Diff Security Gate

When `PFO_CONTRACT_GATE.json` or `pfo_contract_gate.py` reports `security_change`, require one of:

- Codex Security diff-scan artifacts.
- A PFO-equivalent security report validated by `scripts/validate_security_report.py`.

No report means `BLOCKED`, even if the change looks small.

## Deep Scan Mode

Deep scan mode is expensive. Use it only for release readiness, high-risk scopes, explicit user request, or security-sensitive regressions.

Deep mode must still use the same final report contract. Extra discovery passes improve recall, but validation and attack-path analysis still decide reportability.

## Output

Use `docs/templates/SECURITY_AUDIT_REPORT.md`. Each numbered finding must include:

- Severity
- Confidence
- CWE
- Affected lines
- Summary
- Validation
- Dataflow
- Reachability
- Remediation

Return `BLOCKED` when Critical findings exist.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required report and coverage artifacts are explicit.
- The final report validates with `scripts/validate_security_report.py`.
- Verification, blockers, and next route are stated.

## Rules

- Do not apply fixes unless the user explicitly asks for remediation.
- Do not print secrets.
- Prefer exploitability and impact over theoretical noise.
- If the rubric and this skill conflict, follow the rubric and update this skill later.
- Return `BLOCKED` if a product handles sensitive data and has no threat model or data classification before deploy readiness.
- Use plugin-assisted findings as candidates until they are validated against local code paths.
- Treat missing candidate receipts, missing worklist coverage, or unclosed `security_change` evidence as `BLOCKED`.
