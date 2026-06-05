# Engineering Discipline v2

Product Factory OS remains the source of truth for artifacts, state, routing, gates, and project contracts. The Superpowers ideas are adopted as an internal engineering discipline layer, not as an external plugin dependency.

## Adopted Mechanics

- TDD evidence gate: behavior changes require red, green, and refactor evidence or an explicit no-refactor note.
- Root-cause gate: bugfix work requires reproduction evidence and a fix hypothesis before implementation.
- Strict executable plans: implementation tasks name exact files, exact verification commands, expected output, and exit criteria.
- Brainstorm route: rough ideas go through `/brainstorm` before discovery, advisory, stress-test, strategy, or planning-only artifacts.
- Two-stage review: spec compliance is recorded before code quality review.
- Branch finish: every completed branch records PR, merge, keep, or discard plus fresh verification.

## PFO Runtime Mapping

| Engineering Discipline v2 Pattern | PFO Surface |
|---|---|
| TDD evidence | `pfo tdd-evidence`, `TEST_PLAN.md`, `QUALITY_GATES.md`, `.codex-memory/STATE.json` |
| Root cause | `pfo root-cause`, `ROOT_CAUSE.md`, `PFO_RECOVERY.md` |
| Strict executable plans | `BUILD_PLAN.md`, `scripts/validate_plan_quality.py` |
| Brainstorm | `/brainstorm`, `/discover`, `/advisor`, `/grill-me`, `/strategy`, `/blueprint` |
| Behavior-change metadata | `.pfo/UNIT_CONTEXT_MANIFEST.json` `engineeringDiscipline.behaviorChange` |
| Bugfix metadata | `.pfo/UNIT_CONTEXT_MANIFEST.json` `engineeringDiscipline.bugfix` |
| Two-stage review | `pfo review-stage --stage spec`, then `--stage quality` |
| Branch finish | `pfo finish-branch`, `BRANCH_FINISH.md` |

## Enforcement

- `scripts/validate_plan_quality.py <project>` blocks plans with executable `TBD`, `TODO`, vague "add tests", vague "handle errors", or incomplete module rows.
- `scripts/validate_project.py <project>` runs Engineering Discipline v2 gates as part of project validation.
- `hooks/review-before-commit.py` runs `scripts/validate_plan_quality.py --self-check` before methodology commits.
- `pfo manifest --behavior-change` marks a unit as requiring TDD evidence.
- `pfo manifest --bugfix` marks a unit as requiring `ROOT_CAUSE.md`.

## Not Adopted

- Mandatory external Superpowers artifact paths.
- External plugin dependency or second source of truth.
- Deleting existing implementation code as a universal rule.
- Always-on subagent execution without `.pfo/UNIT_CONTEXT_MANIFEST.json`.
- Branch deletion or discard without explicit confirmation.

PFO keeps these rules portable across Codex CLI, Codex app, local workspaces, and generated products.
