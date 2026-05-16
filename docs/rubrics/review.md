# Review Rubric

The review rubric is binary at the critical tier. One failed Critical check means `BLOCKED`.

## Critical

| ID | Check | Pass Criteria |
|---|---|---|
| C1 | P0 coverage | Every P0 requirement has architecture and implementation coverage. |
| C2 | Entity consistency | Core entities use the same names across PRD, architecture, plan, and code. |
| C3 | Data design | Persistent data has fields, relationships, and migration notes, or a no-DB rationale. |
| C4 | API/user flow coverage | User-facing flows have endpoints, commands, pages, handlers, or equivalent implementation paths. |
| C5 | Auth and permissions | Auth, roles, and permission boundaries are explicit when user data or admin actions exist. |
| C6 | Secret handling | Secrets are environment-driven and not hardcoded. |
| C7 | Verification plan | Each implementation step has a concrete verification command or manual check. |
| C8 | Test coverage | Changed behavior has tests, or a documented reason tests are not practical yet. |
| C9 | Build viability | The project has clear install/run commands and no known uncompilable state. |
| C10 | Deploy safety | Deployment docs include env vars, health check, and rollback or recovery notes when deployment is in scope. |
| C11 | Two-stage review | Implementation units pass spec compliance before code quality review. |
| C12 | Root cause discipline | Bugfixes include root-cause evidence before the fix is accepted. |

## Important

| ID | Check | Pass Criteria |
|---|---|---|
| I1 | MVP focus | Scope is small enough for a first working release. |
| I2 | Error handling | Expected failure modes are represented in architecture or code. |
| I3 | Observability | Logs, health checks, or diagnostics exist for server-side services. |
| I4 | Accessibility | User interfaces consider keyboard, labels, contrast, and responsive behavior. |
| I5 | Developer experience | Setup docs are complete enough for a new developer. |
| I6 | Maintainability | Code avoids obvious god modules, duplicated logic, and hidden coupling. |
| I7 | Migration path | Data or API changes mention compatibility or migration strategy. |
| I8 | Performance risk | Known scale or latency risks are acknowledged. |
| I9 | Branch finish hygiene | PR, merge, keep, or discard decision is explicit and backed by fresh verification. |

## Nice To Have

| ID | Check | Pass Criteria |
|---|---|---|
| N1 | ADRs | Major decisions are recorded. |
| N2 | Demo path | README contains a short demo or smoke path. |
| N3 | Backlog | Deferred features are captured. |
| N4 | Ownership | Operational ownership and maintenance notes are clear. |

## Report Format

```markdown
## Findings

- [severity] [id] file:line - finding and impact

## Gate

Status: BLOCKED | PASSED_WITH_WARNINGS | PASSED

| Tier | Pass | Total | Status |
|---|---:|---:|---|
| Critical | X | 10 | pass/fail |
| Important | Y | 8 | pass/warn |
| Nice | Z | 4 | info |

## Open Questions

## Summary
```
