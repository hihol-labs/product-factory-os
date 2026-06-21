# PFO Omnigent Runtime

Product Factory OS adopts the effective runtime mechanics from Omnigent without becoming hosted-first or adding an Omnigent dependency. The adopted layer is local-first, contract-driven, and mapped into Harness Engineering as guide/sensor pairs.

## Adopted Runtime Surfaces

| ID | Omnigent-inspired mechanism | PFO implementation | Harness role |
|---|---|---|---|
| O1 | Declarative agent YAML | `docs/templates/PFO_AGENT_SPEC.yaml`, `agents/*.yaml`, `pfo agent-spec`; each profile declares role instructions, executor harness/model, tools, policies, terminals, and sandbox | Feedforward guide |
| O2 | Policy engine verdicts | `pfo policy-eval` normalizes runtime events with `type`, `target`, `data`, `actor`, `usage`, `session_state`, and `result`, then returns `ALLOW`, `DENY`, or `ASK` | Computational sensor |
| O3 | Runner/server envelope | `pfo runner register/status` writes `.pfo/runner/runner-host.json`; `pfo server register/status` writes `.pfo/server/control-plane.json`; local PFO artifacts remain source of truth while server coordinates sessions, telemetry, gates, and approvals | Guide plus sensor |
| O4 | Multi-agent dispatch | `pfo dispatch --worktree` creates an independent git worktree under `../.pfo-worktrees/<project>/...` and writes `.pfo/dispatch/*.json` with purpose, agent, harness, model, inbox, and isolation metadata | Feedforward guide |
| O5 | Cross-harness/vendor review | `pfo cross-review --risk security|migration|deploy|auth|payments|data-loss` requires independent agent, harness, vendor, or model when another vendor is available | Inferential feedback gate |
| O6 | Cost/risk routing | `pfo cost-route` and `.pfo/PERMISSION_MATRIX.json` carry `riskScore`, `estimatedCost`, `modelTier`, `budgetDecision`, `downgradeAllowed`, daily budget, and expensive-model gates into state and telemetry | Computational guide |
| O7 | Live observability | `pfo session export/status` writes `.pfo/session/live-status.json` with active goal, route, current unit, running command, subagents, inbox, approvals, gates, diff, verification, and cost/policy state | Computational sensor |
| O8 | Session fork/attach/share substrate | `pfo session export/import/attach/share/status` creates forkable packets with snapshot, unit manifest, event range, active artifacts, gates, dispatches, and review state | Feedforward guide |
| O9 | Sandbox in agent/unit specs | `sandbox:` in `agents/*.yaml`, `docs/templates/PFO_AGENT_SPEC.yaml`, and unit manifests declares `sandbox.type`, `read_paths`, `write_paths`, `allow_network`, and `env_passthrough` | Computational feedforward |

## Operating Rules

- PFO remains local-first; hosted coordination is optional and must consume local artifacts instead of replacing them.
- Runtime policies fail closed: `DENY` blocks, `ASK` requires explicit approval, and ambiguous evidence cannot pass gates.
- Dispatch envelopes do not imply uncontrolled fan-out. Route profiles decide when multi-agent work is justified.
- Cross-review is required for high-risk diffs when another harness or vendor is available; otherwise PFO records the blocker.
- Cost/risk routing downgrades trivial work and escalates high-risk work before tokens are spent.
- Session exports are compact transfer packets, not a second source of truth.

## Verification

Run:

```bash
python3 scripts/validate_omnigent_runtime.py
```

The validator checks that all O1-O9 mechanisms have a CLI surface, artifact, documentation entry, control-harness entry, and production-readiness wiring.

- `pfo session attach` is part of the behavioral O1-O9 acceptance surface.

- `pfo session share` is part of the behavioral O1-O9 acceptance surface.
