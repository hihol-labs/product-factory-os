---
name: harden
description: Production readiness workflow for services before deployment.
argument-hint: service, project, or production target
license: MIT
metadata:
  category: operations
  tags: [production, hardening, sre]
---

# Harden

Prepare a service for production.

The canonical production readiness rubric lives in `docs/rubrics/production.md`.

## Checklist

- Health checks
- Graceful shutdown
- Structured logs
- Error handling
- Rate limiting where needed
- Backup and restore notes
- Environment variable documentation
- Metrics or observability notes
- Runbook for common failures
- SLO or expected uptime assumption
- Alerting or diagnostics path
- Migration and rollback sequence
- Smoke test after deployment
- Incident response and credential rotation notes

## Rules

- Generate artifacts only after user approval when changes are broad.
- Do not deploy as part of hardening.
- Return `BLOCKED` if a production-critical gap remains.
- If the rubric and this skill conflict, follow the rubric and update this skill later.
- Do not mark `READY_FOR_DEPLOY` unless rollback or recovery is documented.
