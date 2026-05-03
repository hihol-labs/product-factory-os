# Security Audit Rubric

Security audits are read-only by default. Remediation is a separate user-approved step.

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

Use:

- Critical
- Important
- Recommended
- Informational

`BLOCKED` means at least one Critical finding exists.

