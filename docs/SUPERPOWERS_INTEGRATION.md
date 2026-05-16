# Superpowers Integration Notes

Product Factory OS already owns the product lifecycle, product strategy artifacts, project contracts, and runtime gates. Superpowers is strongest at engineering discipline inside each implementation unit. PFO adopts those mechanics as gates instead of depending on the external plugin.

## Adopted From Superpowers

- TDD evidence: red, green, and refactor verification for behavior changes.
- Root-cause discipline: no bugfix acceptance without reproduction, evidence, and a fix hypothesis.
- Two-stage review: spec compliance first, code quality second.
- Strict executable plans: exact files, exact commands, expected output, and exit criteria.
- Branch finish workflow: PR, merge, keep, or discard decision with fresh verification and cleanup policy.

## PFO Runtime Mapping

| Superpowers Pattern | PFO Surface |
|---|---|
| test-driven-development | `pfo tdd-evidence`, `QUALITY_GATES.md`, `TEST_PLAN.md` |
| systematic-debugging | `pfo root-cause`, `ROOT_CAUSE.md`, `PFO_RECOVERY.md` |
| verification-before-completion | `pfo verify-work`, fail-closed state, verification history |
| subagent-driven-development review | `pfo review-stage --stage spec`, then `--stage quality` |
| writing-plans | strict `BUILD_PLAN.md` task contract |
| finishing-a-development-branch | `pfo finish-branch`, `BRANCH_FINISH.md` |

## Not Adopted

- Mandatory external Superpowers artifact paths.
- Deleting existing implementation code as a universal rule.
- Always-on subagent execution without PFO unit manifests.
- Branch deletion or discard without explicit confirmation.

PFO keeps these ideas as portable runtime contracts that work for Codex CLI, Codex app, local workspaces, and generated products.
