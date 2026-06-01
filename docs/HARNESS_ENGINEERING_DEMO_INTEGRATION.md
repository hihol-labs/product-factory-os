# Harness Engineering Demo Integration

Source: https://github.com/coleam00/harness-engineering-demo

PFO adopts the useful mechanics from the demo without copying the sample application.

## Imported Patterns

| Demo Pattern | PFO Integration |
|---|---|
| PIV loop: Plan -> Implement -> Validate | `pfo manifest` now writes `plans/<unit>-piv-plan.md`; `pfo verify-work --pass-gate` writes `reports/<unit>-implementation-report.md`. |
| Per-task validation before moving on | The generated PIV plan requires narrow validation per task and the full `.pfo/VERIFICATION_CONTRACT.json` before completion. |
| Stop-style validation gate | PFO keeps this as deterministic feedback gates: `review-before-commit.py`, `validate_project.py`, `pfo_contract_gate.py`, and project verification contracts. |
| PreToolUse security guard | `hooks/security-guard.py` blocks real `.env` access and recursive directory deletion. |
| Codebase-search MCP idea | PFO keeps this in the tool-capability layer; project-specific symbol search should be declared in `.pfo/TOOL_CAPABILITY_REGISTRY.json` before use. |
| Ralph-style repeated headless sessions | PFO maps this to `docs/HEADLESS_EXECUTION.md`, fixture execution, handoff, worktree isolation state, and experiment loops. |

## Operating Rule

For implementation units, prefer this sequence:

1. `pfo manifest <project> --unit <id> --goal "<goal>"`
2. Read `plans/<unit>-piv-plan.md`.
3. Implement one task at a time.
4. Run task-level validation immediately.
5. Run the full verification contract.
6. `pfo verify-work <project> --evidence "<commands passed>" --pass-gate`
7. Record spec compliance review, then code quality review.

This gives PFO the demo's fast handoff loop while preserving PFO's stronger product contracts, memory, policy, and gates.
