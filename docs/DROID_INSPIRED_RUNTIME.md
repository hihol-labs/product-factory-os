# Droid-Inspired PFO Runtime

PFO adopts seven useful ideas from Factory Droid while keeping the runtime local-first and contract-driven.

Each surface is mapped into the PFO Harness Engineering model in `docs/CONTROL_HARNESS.md`. The rule is: every guide has a sensor, every sensor writes evidence, and deterministic controls remain preferred for blocking decisions.

## 1. Readiness

`pfo readiness <project> --write` evaluates five autonomy maturity levels:

- Functional
- Adopted
- Gated
- Measured
- Self-improving

The command writes `PFO_READINESS_REPORT.md`, stores the report in `.codex-memory/STATE.json`, and records a gate event.

`pfo readiness-fix <project> --apply` applies deterministic remediation such as adoption refresh, context indexing, resume snapshot generation, and missing learning artifacts.

## 2. Policy And Autonomy

`pfo policy explain <project> --auto low|medium|high` explains what the selected autonomy level permits.

`pfo policy check <project> --auto medium --capability commit` gives a machine-checkable pass/block result.

The policy surface is intentionally mapped to `.pfo/PERMISSION_MATRIX.json` and `.pfo/EXECUTION_POLICY.json`; PFO route profiles still decide which gates are required.

## 3. Headless Exec

`pfo exec <project> --route readiness|readiness-fix|mission|wiki|qa|telemetry --output-format json` runs a deterministic PFO route as a one-shot command.

The JSON envelope includes route, profile, artifacts, gates, next action, and exit code so CI or another orchestrator can consume it.

## 4. Mission

`pfo mission plan <project> --goal "..."` writes `.pfo/mission.json` and `PFO_MISSION.md`.

`pfo mission run <project> --milestone M1` records milestone validation. `pause`, `continue`, `replan`, and `status` update or read the same mission state.

Missions are milestone-first and validator-aware rather than fully parallel by default.

## 5. Wiki

`pfo wiki generate <project>` writes a local wiki under `.pfo/wiki/` with architecture, modules, commands, gates, and state pages.

`pfo wiki refresh <project>` regenerates the same pages, and `pfo wiki diff <project>` reports changed pages.

## 6. QA

`pfo qa install <project>` writes `.pfo/qa/config.yaml`, a report template, and starter flows.

`pfo qa run <project>` evaluates changed files, writes `.pfo/qa/PFO_QA_REPORT.md`, updates the `qa` gate, and records verification evidence.

## 7. Telemetry

`pfo telemetry export <project> --format jsonl` writes `.pfo/telemetry/pfo-telemetry.jsonl`.

The export summarizes event, artifact, gate, and verification counts for local dashboards or external observability pipelines.

`pfo metrics` includes `platformSurfaces` coverage for readiness, mission, policy, wiki, QA, and telemetry artifacts.

## Harness Pairing

| Surface | Guide Or Sensor | Harness Role |
|---|---|---|
| Readiness | Sensor | Measures maturity before raising autonomy. |
| Policy/autonomy | Guide | Sets allowed capabilities before work. |
| Headless exec | Guide | Produces a bounded execution envelope. |
| Mission | Guide | Turns broad work into milestones and validators. |
| Wiki | Guide | Supplies compact project context. |
| QA | Sensor | Verifies changed surfaces with evidence. |
| Telemetry | Sensor | Measures usage, gates, artifacts, and verification. |
