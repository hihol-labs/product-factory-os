---
name: review
description: Deterministic project review for docs, code, consistency, and readiness.
argument-hint: project path, file, pull request, or changed area
license: MIT
metadata:
  category: quality
  tags: [review, quality, validation]
  effort: high
  side_effect: read-only
  explicit_invocation: false
---

# Review

Review project documents and code. Lead with findings.

The canonical rubric lives in `docs/rubrics/review.md`. Use it as the source of truth.

For Product Factory OS projects, also apply `docs/rubrics/pfo.md`, `docs/rubrics/strategy.md` when strategy artifacts are in scope, and `docs/rubrics/testing.md` when implementation or deploy readiness is in scope.

## Status

Return one:

- `BLOCKED`: at least one critical issue prevents the next step.
- `PASSED_WITH_WARNINGS`: critical checks pass, important issues remain.
- `PASSED`: critical and important checks pass.

## Critical Checks

- Apply every Critical check from `docs/rubrics/review.md`.
- Apply Important and Nice-to-have checks after Critical checks.
- Do not invent additional blocking criteria unless they are security-critical.

## Procedure

1. Detect scope:
   - Planning docs only
   - Code only
   - Full project
   - Methodology repository
2. Read the canonical rubric.
3. Inspect the required files for the selected scope.
4. For PFO projects, validate:
   - product classification confidence and ambiguity
   - template compliance
   - Product Compiler artifacts
   - execution graph semantics
   - state consistency
   - gate traceability
   - Engineering Discipline v2 via `scripts/validate_plan_quality.py <project>`
5. For browser-facing changes, require `/browser-check` target, engine, flow, and screenshot/log evidence before deploy readiness.
6. For SDK, framework, or platform questions, use `/mcp-docs` before flagging documentation-sensitive findings.
7. Apply checks as binary pass/fail at Critical tier.
8. Run spec compliance review before code quality review for implementation units.
9. Produce findings first.
10. Set gate status from rubric results.

## Scope Rules

- If no source code exists, skip code-only concerns and say docs-only review.
- If planning docs are missing, review available code but mark missing docs as Critical only when the workflow expects planning docs.
- If reviewing the methodology repository itself, run `scripts/meta_review.py` when available and include its result.
- If `EXECUTION_GRAPH.md` exists, run `scripts/validate_execution_graph.py` when available.
- If `.codex-memory/STATE.json` exists, check it matches current stage, current node, gate results, and next action.
- If TDD evidence is required, check red and green evidence before accepting the testing gate.
- If the work is a bugfix, check `ROOT_CAUSE.md` or equivalent state evidence before accepting the fix.

## Output Format

1. Findings ordered by severity with file references.
2. Status enum.
3. Open questions.
4. Short summary.

Use this shape:

```markdown
## Findings

- [Critical] C1 path:line - finding and impact.

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

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Be concrete: cite files and lines when possible.
- Do not soften `BLOCKED` by request.
- If no issues are found, say so and name residual risks.
- If the rubric and this skill conflict, follow the rubric and update this skill later.
- Separate findings from suggestions.
- Do not edit files during review unless the user explicitly asks for remediation after the report.

## Common Failure Modes

- Missing acceptance criteria: block planning-to-code transition.
- Architecture names an entity that PRD never mentions: warn unless it creates implementation ambiguity.
- Tests missing for a changed user flow: block if release/deploy is requested, warn during early scaffolding.
- No deployment docs: block only when deploy is in scope.
