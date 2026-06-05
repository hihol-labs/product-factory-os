# Repository Coverage Ledger

| Row | Surface | Risk Area | Outcome | Notes |
|---|---|---|---|---|
| route-profiles-overhead-001 | `routing/route-profiles.json` | skipped gates for small tasks | No issue found | Minimal is explicitly bounded to adoption, scope, targeted verification, review, and state-save. |
| route-profiles-overhead-002 | `scripts/pfo.py` | unsafe route downgrade | No issue found | Full route hints include deploy, migration, security, production, release, and broad architecture terms. |
| route-profiles-overhead-003 | `scripts/pfo_metrics.py` | misleading artifact evidence | No issue found | Metric is reporting-only and separates missing required artifacts from tracked extras. |
| route-profiles-overhead-004 | `scripts/validate_route_profiles.py` | validator gap | No issue found | Minimal exact step order and default command limits are enforced. |
| route-profiles-overhead-005 | `README.md` | incorrect operator guidance | No issue found | Docs state when each profile applies and name minimal exclusions. |
| route-profiles-overhead-006 | `docs/WORKSPACE_DEFAULTS.md` | workspace policy drift | No issue found | Workspace defaults require the smallest profile that fits risk. |
