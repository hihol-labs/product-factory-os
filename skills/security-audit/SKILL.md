---
name: security-audit
description: Read-only security review for application and configuration risks.
argument-hint: project, service, file, or changed area
license: MIT
metadata:
  category: quality
  tags: [security, audit, owasp]
---

# Security Audit

Run a read-only security audit.

The canonical rubric lives in `docs/rubrics/security.md`. Use it as the source of truth.

Use `docs/templates/THREAT_MODEL.md` and `docs/templates/DATA_CLASSIFICATION.md` for non-trivial SaaS, API, e-commerce, mini app, internal automation, and bot projects.

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

## Output

Group findings as:

- Critical
- Important
- Recommended
- Informational

Return `BLOCKED` when Critical findings exist.

## Rules

- Do not apply fixes unless the user explicitly asks for remediation.
- Do not print secrets.
- Prefer exploitability and impact over theoretical noise.
- If the rubric and this skill conflict, follow the rubric and update this skill later.
- Return `BLOCKED` if a product handles sensitive data and has no threat model or data classification before deploy readiness.
