# Scope Lock Gate

Purpose: prevent a narrow task from silently changing unrelated product behavior.

Universal rule:

- Every non-trivial task must declare allowed change areas before implementation.
- The diff must be reviewed against those allowed areas before commit/deploy.
- Changes outside the declared scope are blocked unless the project contract explicitly allows them or the scope is updated intentionally.

Project-owned inputs:

- `.pfo/SCOPE_LOCK.md`
- `.pfo/FORBIDDEN_CHANGES.md`
- Current task description

Gate output:

- `PASS`: diff stays inside declared scope.
- `PASS_WITH_WARNINGS`: scope is incomplete but no high-risk substitution is detected.
- `BLOCKED`: diff changes forbidden areas or introduces unrelated business/data behavior.

