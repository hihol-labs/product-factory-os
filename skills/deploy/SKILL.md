---
name: deploy
description: Deploy a reviewed service with explicit confirmation and verification.
argument-hint: service name, target environment, or release
license: MIT
metadata:
  category: operations
  tags: [deploy, release, production]
---

# Deploy

Deploy only after explicit confirmation.

Use `docs/rubrics/production.md` for production readiness preflight.

## Preflight

Check:

- Current git status and target commit
- Tests or accepted test gap
- Review status is not `BLOCKED`
- Browser-facing flows have no blocking `/browser-check` failures and include target, engine, flow, and screenshot/log evidence when applicable
- GitHub CI or equivalent release verification is known when `/github-workflow` is in scope
- Required env vars are documented
- Rollback path exists

## Confirmation

Before any real deployment command, ask:

```text
Confirm deployment target and impact: deploy <service> to <environment>? This may restart services.
```

Proceed only after explicit confirmation.

## Process

1. Ask for target environment and confirmation.
2. Build or package.
3. Apply deployment steps.
4. Run health checks.
5. Verify the main user flow when possible.
6. Run `/tool-sync` or `/github-workflow` when external release status must be updated.
7. Save session context.

## Verification

At minimum:

- Build artifact exists or image builds.
- Service starts.
- Health check returns success.
- Main user flow is smoke-tested when practical.
- Logs do not show startup errors.

## Rollback

Every deploy report must include one:

- Exact rollback command
- Previous artifact/image/commit to restore
- Reason rollback is not available

## Rules

- Never deploy production by implication.
- Never print secrets.
- If verification fails, report rollback steps.
- Stop immediately on unknown target, missing credentials, or failed health check.
- Always run `/session-save` after a production deploy attempt.
