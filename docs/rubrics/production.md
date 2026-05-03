# Production Readiness Rubric

Use this rubric from `/harden` and `/deploy`.

## Critical

- Health check exists and is documented.
- Required environment variables are listed.
- Secrets are not committed.
- Persistent data has backup or recovery notes.
- Deploy has rollback or restore instructions.
- Logs are sufficient to debug startup and request failures.
- Graceful shutdown exists for long-running services where applicable.

## Important

- Metrics or diagnostics exist.
- Rate limits protect expensive or abusive endpoints.
- Migrations are run in an explicit step.
- Static assets and uploads have ownership and storage notes.
- CI runs build and tests.

## Recommended

- Runbook for common incidents.
- Load smoke test.
- Alerting notes.
- Disaster recovery drill.

