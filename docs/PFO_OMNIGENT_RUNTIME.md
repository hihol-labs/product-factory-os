# PFO Omnigent Runtime

Product Factory OS adopts the effective runtime mechanics from Omnigent without becoming hosted-first or adding an Omnigent dependency. The adopted layer is local-first, contract-driven, and mapped into Harness Engineering as guide/sensor pairs.

## Adopted Runtime Surfaces

| ID | Omnigent-inspired mechanism | PFO implementation | Harness role |
|---|---|---|---|
| O1 | Declarative agent YAML | `docs/templates/PFO_AGENT_SPEC.yaml`, `agents/*.yaml`, `pfo agent-spec` | Feedforward guide |
| O2 | Policy engine verdicts | `pfo policy-eval` returns `ALLOW`, `DENY`, or `ASK` from runtime events | Computational sensor |
| O3 | Runner/server envelope | `pfo exec`, `pfo session export`, `.pfo/session/live-status.json` | Guide plus sensor |
| O4 | Multi-agent dispatch | `pfo dispatch` writes `.pfo/dispatch/*.json` with purpose, agent, harness, model, and worktree envelope | Feedforward guide |
| O5 | Cross-harness review | `pfo cross-review` requires a different reviewer harness for high-risk review envelopes | Inferential feedback gate |
| O6 | Cost/risk routing | `pfo cost-route` and `pfo policy-eval` record risk score, estimated cost, model tier, and budget decision | Computational guide |
| O7 | Live observability | `pfo telemetry`, `.pfo/session/live-status.json`, `.pfo/telemetry/` expose gates, artifacts, dispatch, review, policy, and cost state for live observability | Computational sensor |
| O8 | Session fork/attach/share substrate | `pfo session export/import/status` creates forkable context packets from state, gates, artifacts, and event pointers | Feedforward guide |
| O9 | Sandbox in agent/unit specs | `sandbox:` in `agents/*.yaml` and `.pfo/UNIT_CONTEXT_MANIFEST.json` declares `read_paths`, `write_paths`, network, env, and policy boundaries | Computational feedforward |

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
