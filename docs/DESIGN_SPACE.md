# Product Factory OS Design Space

This map tracks which external agent-engineering principles are covered by Product Factory OS and where the next leverage points are.

## Coverage Summary

| Principle | PFO Coverage | Current Mechanism | Next Improvement |
|---|---|---|---|
| Think before coding | Full | `/blueprint`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, strict plan validator | Keep behavioural fixture contracts active |
| Surgical changes | Full | `.pfo/FORBIDDEN_CHANGES.md`, scope lock, diff risk gate | Add more starter-specific negative contracts |
| Goal-driven execution | Full | execution graph nodes, unit manifests, done criteria | Strengthen generated-project validators |
| Context budgeting | Partial | `/handoff`, `/session-save`, `session-diagnostics.py` | Add context budget thresholds per project type |
| Context economy | Full | `docs/AGENT_HARNESS_ENGINEERING.md`, `HANDOFF.md`, unit context policy | Add numeric thresholds after more real traces |
| Durable checkpoints beyond git | Partial | `.codex-memory/STATE.json`, `HANDOFF.md`, `PFO_RECOVERY.md` | Add checkpoint restore smoke tests |
| Tool trust boundary | Full | hook layer, explicit side-effect metadata, explicit invocation gates | Keep dangerous route list synced with metadata |
| Tool surface discipline | Full | tool selection policy, capability registry, approval metadata | Prune overlapping tools from real usage traces |
| Control harness taxonomy | Full | `docs/CONTROL_HARNESS.md`, `validate_control_harness.py`, CI/release wiring | Promote repeated inferential findings into deterministic gates |
| Harness ratchet | Full | `LEARNING_PROMOTION_GATE.md`, `pfo_learn.py`, `memory/LEARNING_REGISTRY.json` | Add automatic stale-rule review later |
| Skill discovery | Full | trigger registry, `verify_triggers.py`, route snapshots | Add regression prompts from real misses |
| Behavioural regression testing | Partial | fixture contracts for key skills | Expand contracts to all 32 skills over time |
| Drift prevention | Full | meta-review, manifest drift, install sync, skill profiles | Add table row integrity checks for more docs |
| Production safety | Full | `/deploy`, `/migrate`, `/infra`, confirmation rules | Add live-op dry-run fixtures |
| External evidence | Full | `/market-scan`, `/mcp-docs`, connector routes | Add source freshness confidence scoring |
| Self-improving experiment loops | Full | `pfo experiment-init`, `pfo experiment-record`, `.pfo/EXPERIMENTS.tsv` | Add optional managed runners later |
| Adversarial review | Partial | `/grill-me`, two-stage review | Embed architecture debate in `/blueprint` |
| Memory continuity | Full | session save, handoff, state schema, diagnostics | Add stale-state auto-repair suggestions |
| Marketplace/onboarding | Partial | one-command install, marketplace metadata, demo image | Add screenshots and install telemetry later |

## Adopted From idea-to-deploy Changelog

- Behavioural fixture contracts: PFO now validates key route fixtures beyond route matching.
- Trigger drift verifier: documented trigger phrases must route to the expected skill.
- Manifest drift gates: plugin, marketplace, public counts, and changelog version are checked.
- Explicit side-effect metadata: every skill declares `effort`, `side_effect`, and `explicit_invocation`.
- Dangerous route guard: production, migration, infrastructure, GitHub, and tool-sync routes print a risk warning.
- Skill self-validation: every skill must perform a final contract check before reporting completion.
- Session diagnostics: project state freshness, recovery, handoff, and telemetry are surfaced at prompt time.
- Install sync guard: hook manifest, installer, docs, and CI must remain aligned.
- Marketplace polish: local marketplace metadata includes a hero image.
- Agent harness engineering: PFO now maps model-plus-harness failures to context economy, tool surface discipline, evaluator split, and learning ratchet controls.

## Open Gaps

1. Context budget thresholds are not yet numeric.
2. Behavioural contracts cover the highest-risk skills first, not all 32.
3. Marketplace screenshots are represented by a generated hero image, not a real product screenshot.
4. Live deployment and migration dry-runs are still contract-level, not environment-level.
