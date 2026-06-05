# Defensive Layers

Source: https://walkinglabs.github.io/learn-harness-engineering/ru/

PFO uses five defensive layers before treating a failure as a model problem. The point is diagnostic discipline: rule out the common harness causes first, then repair the smallest failing layer.

## Five Layers

| ID | Layer | Common Failure It Catches | PFO Guides | PFO Sensors | Exit Condition |
|---|---|---|---|---|---|
| task-specification | Task specification | Ambiguous intent, missing acceptance criteria, hidden non-goals, oversized scope. | `docs/templates/PRD.md`, `docs/templates/BUILD_PLAN.md`, `docs/templates/EXECUTION_GRAPH.md`, `docs/templates/pfo/SCOPE_LOCK.md`, `docs/templates/UNIT_CONTEXT_MANIFEST.json` | `scripts/validate_plan_quality.py`, `scripts/validate_execution_graph.py`, spec review stage | The unit has exact goal, allowed writes, non-goals, verification commands, and exit criteria. |
| context-provisioning | Context provisioning | Wrong or stale context, raw history overload, missing source artifacts, lost handoff. | `AGENTS.md`, `CODEX.md`, `docs/AGENT_HARNESS_ENGINEERING.md`, `docs/templates/HANDOFF.md`, `docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json` | `scripts/validate_context_runtime.py`, `hooks/context-budget.py`, `hooks/session-diagnostics.py` | The active unit can be resumed from bounded artifacts, not chat memory. |
| execution-environment | Execution environment | Wrong tool, undeclared write, unsafe command, missing adoption, missing runtime contract. | `scripts/adoption_check.py`, `docs/templates/pfo/EXECUTION_POLICY.json`, `docs/templates/pfo/PERMISSION_MATRIX.json`, `docs/templates/pfo/PROJECT_CONTRACT.md` | `scripts/pfo_permission_gate.py`, `scripts/pfo_contract_gate.py`, `scripts/validate_self_contracts.py`, `scripts/validate_runtime.py` | Commands, writes, network access, approvals, and degraded modes are declared before execution. |
| verification-feedback | Verification feedback | Success declared without runnable proof, stale artifacts, unpaired guide/sensor, weak evidence. | `docs/templates/pfo/VERIFICATION_CONTRACT.json`, `docs/templates/TEST_PLAN.md`, `docs/templates/QUALITY_GATES.md`, `docs/CONTROL_HARNESS.md` | `scripts/production_readiness.py`, `scripts/validate_control_harness.py`, `scripts/pfo_contract_gate.py`, test and fixture commands | Fast local sensors and broader gates give current evidence or fail closed. |
| state-management | State management | Progress lost across sessions, stale blockers, unrecorded decisions, branch state drift. | `memory/session-state.schema.json`, `docs/templates/HANDOFF.md`, `docs/templates/BRANCH_FINISH.md`, `.codex-memory/STATE.json` when present | `scripts/validate_state.py`, `scripts/pfo_context_runtime.py`, `hooks/session-diagnostics.py` | State, events, resume packet, branch decision, and next action match the current unit. |

## Diagnostic Triage

When PFO output is wrong, check layers in this order:

1. `task-specification`: Is the task exact enough to judge success?
2. `context-provisioning`: Did the agent load the right bounded context?
3. `execution-environment`: Were tools, writes, permissions, and runtime assumptions valid?
4. `verification-feedback`: Did fresh sensors prove the result?
5. `state-management`: Was the result saved into durable state without stale blockers?

This mirrors clinical triage: common causes are eliminated before rare explanations are accepted.

## Evidence Matrix

Each layer must have both:

- A guide that shapes behavior before execution.
- A sensor that proves, blocks, or repairs behavior after execution.

A layer without a guide creates repeated repair churn. A layer without a sensor becomes a reminder, not a control. New PFO controls should name the affected layer in the PIV plan, implementation report, or control harness entry when the change is durable.

## Systematic Check

Run:

```bash
python3 scripts/validate_defensive_layers.py
```

The validator checks that:

- all five layer IDs are documented;
- each layer maps to concrete guide and sensor artifacts;
- the diagnostic triage order is present;
- the validator is wired into structure validation, runtime validation, CI, release checks, production readiness, and install docs;
- `docs/CONTROL_HARNESS.md` contains a durable feedback control for this diagnostic gate.

## Current Coverage Decision

Before this gate, PFO had most of the mechanisms as separate harness controls. The missing piece was a single fail-closed diagnostic check that confirms the five layers remain connected and prevents future harness work from drifting back into scattered reminders.
