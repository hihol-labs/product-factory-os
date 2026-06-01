# Harness Engineering Demo Integration

Source: https://github.com/coleam00/harness-engineering-demo

Related source: https://addyosmani.com/blog/agent-harness-engineering/

Related source: https://martinfowler.com/articles/harness-engineering.html

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

## Addy Osmani Harness Engineering Mapping

PFO also adopts the broader agent harness engineering frame: model capability depends on the surrounding prompts, tools, state, hooks, context policy, verification, and recovery paths.

| Article Pattern | PFO Integration |
|---|---|
| Agent = model + harness | `docs/CONTROL_HARNESS.md` and `docs/AGENT_HARNESS_ENGINEERING.md` make harness controls explicit. |
| Every mistake becomes a rule | `.pfo/LEARNING_PROMOTION_GATE.md`, `scripts/pfo_learn.py`, and `memory/LEARNING_REGISTRY.json` convert evidence into promoted controls. |
| Context rot requires active management | `/handoff`, `session-diagnostics.py`, unit context policy, and output offloading keep long work reloadable. |
| Tool menus are trusted prompt surface | `.pfo/TOOL_CAPABILITY_REGISTRY.json` declares side effects, explicit degraded modes, approvals, and progressive disclosure policy. |
| Hooks enforce what prompts only request | `hooks/security-guard.py`, `review-before-commit.py`, validators, and verification contracts block repeatable risks. |
| Planner/generator/evaluator split | PFO keeps PIV planning, implementation, executable validation, and two-stage review as separate lifecycle steps. |

## Martin Fowler Harness Engineering Mapping

PFO also adopts Fowler's coding-agent user harness vocabulary and lifecycle placement rules.

| Article Pattern | PFO Integration |
|---|---|
| Guides and sensors | Feedforward controls are guides; feedback controls are sensors in `docs/CONTROL_HARNESS.md` and `docs/AGENT_HARNESS_ENGINEERING.md`. |
| Quality left | Fast computational sensors run locally and before handoff; broader or expensive sensors repeat in CI, release, or production-readiness gates. |
| Maintainability, architecture fitness, behaviour | PFO classifies harness controls and product templates by the category they regulate. |
| Harnessability | PFO treats clear module boundaries, typed contracts, golden flows, logs, and fixtures as first-class generation constraints. |
| Harness templates | `templates/product-templates.json` carries topology-level guide/sensor bundles, backed by starter packs and golden paths. |
| Human steering | `NEXT_STEP.md`, `.codex-memory/STATE.json`, review roles, and approval gates route human attention to unclear intent, accepted risk, and harness gaps. |

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
