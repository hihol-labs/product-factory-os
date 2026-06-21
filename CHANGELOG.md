# Changelog

## [Unreleased]

### Added

- Droid-inspired PFO platform surfaces: `pfo readiness`, `pfo readiness-fix`, `pfo policy`, `pfo autonomy`, `pfo exec`, `pfo mission`, `pfo wiki`, `pfo qa`, and `pfo telemetry`.
- `PFO_READINESS_REPORT.md`, `.pfo/mission.json`, `.pfo/wiki/`, `.pfo/qa/`, and `.pfo/telemetry/` runtime artifacts for local-first readiness, orchestration, knowledge, QA, and observability.
- `platformSurfaces` metrics in `pfo metrics` to track readiness, mission, policy, wiki, QA, and telemetry coverage across adopted projects.
- `docs/DROID_INSPIRED_RUNTIME.md` documenting the seven implemented Droid-inspired PFO contours.
- Control-harness registry and documentation entries for the new readiness, remediation, autonomy, exec, mission, wiki, QA, and telemetry surfaces, preserving Harness Engineering guide/sensor coverage.

## [1.2.1] - 2026-06-21

### Added

- Acceptance contract runtime gate with `.pfo/ACCEPTANCE_CONTRACT.json`, `pfo acceptance init/add/verify/gate/status`, and `scripts/validate_acceptance_contract.py`.
- Fail-closed `pfo verify-work --pass-gate` enforcement: final verification now requires all source-traced acceptance criteria to be `PASSED`.
- Self-authored validator protection: criteria proved by changed `scripts/validate*.py` files must include independent evidence.
- Production-readiness, structure, runtime, methodology, and control-harness wiring for the acceptance contract as a Harness Engineering feedback sensor.

## [1.2.0] - 2026-06-21

### Added

- Omnigent-inspired PFO runtime v1 with local-first agent YAML specs, `pfo agent-spec`, `pfo policy-eval`, `pfo dispatch`, `pfo cross-review`, `pfo cost-route`, and `pfo session`.
- `docs/PFO_OMNIGENT_RUNTIME.md`, `docs/templates/PFO_AGENT_SPEC.yaml`, and runnable `agents/*.yaml` profiles for orchestrator, builders, reviewers, tester, and memory roles.
- Policy verdict runtime that evaluates events into `ALLOW`, `DENY`, or `ASK`, records state, and supports risk, cost, and tool-call thresholds.
- Dispatch and cross-review envelopes under `.pfo/dispatch/` and `.pfo/cross-review/`, including worktree metadata and different-harness review enforcement for high-risk diffs.
- Cost/risk routing state, session export/import/status packets, live status artifacts, and sandbox specs in agent and unit manifests.
- `scripts/validate_omnigent_runtime.py` plus production-readiness, runtime, structure, and control-harness wiring to prove all O1-O9 mechanisms are implemented.

### Changed

- PFO unit manifests and permission matrices now carry sandbox and cost/risk policy contracts for adopted projects.
- PFO methodology, architecture, README, and control harness now describe supervised live-agent operation as guide/sensor Harness Engineering controls.

## [1.1.0] - 2026-06-06

### Added

- `/brainstorm` skill with trigger coverage, fixture contract, route snapshot, control-harness entry, and Superpowers mapping for structured ideation before discovery, advisor, grill-me, strategy, or blueprint routes.
- `pfo full-cycle` fail-closed lifecycle orchestration for plan, test, implementation dispatch, review, and session-save summaries.
- `pfo next-best-action` state-driven gate recommendation with JSON output and optional `STATE.json` / `NEXT_STEP.md` writeback.
- Root verification entrypoint via `pfo check` / `python3 scripts/check.py`, plus analyzer support for `check` as a root test gate.
- Full workspace runtime enforcement: installer/preflight now complete adoption with analysis, contract gate output, and `PFO_REPORT.md`.
- Default-on Codex `/goal` mode is now part of workspace/global PFO policy, project adoption, `pfo new`, and preflight context.
- Existing-project-safe alias templates and alias target validation gates prevent adopted repositories from being marked fully adopted while index files point to missing canonical docs.
- `pfo new` now auto-generates planning artifacts, execution graph, and report without requiring a separate initial `pfo plan`.
- Autoresearch-style self-improvement loop with `.pfo/EXPERIMENT_PROGRAM.md`, `.pfo/EXPERIMENTS.tsv`, fixed metric/budget state, and `pfo experiment-init` / `pfo experiment-record`.
- Documentation, routing, templates, state schema, and plan-quality gates for baseline-first keep/discard/crash experiment decisions.
- Project-local execution policy, permission matrix, verification contract, structured event log schema, and learning promotion gate.
- `pfo manifest` now writes `.pfo/VERIFICATION_CONTRACT.json`; `pfo verify-work --pass-gate` requires a ready verification contract.
- `pfo learning-gate` blocks unreviewed learning promotions before runtime changes.
- Added machine-readable `.pfo/PERMISSION_MATRIX.json`, `.pfo/TOOL_CAPABILITY_REGISTRY.json`, `pfo permission-check`, `pfo event`, and `pfo tool-registry`.
- PFO Default Stack v1 policy: FastAPI/Pydantic/PostgreSQL/Vue/TypeScript/Vite as the golden path, with documented ADR-style deviations allowed.
- `/seo` skill for technical SEO, search intent, metadata, structured data, content backlog, and organic acquisition measurement work.
- `SEO_GROWTH_GUARANTEE_GATE.md` and `validate_seo_growth_gate.py` for measured SEO growth claims with baseline, target, source, attribution window, implemented changes, exclusions, result decision, and next iteration.
- Context runtime: numeric `pfo context-budget` gate, `pfo context-index`, BM25-style `pfo context-search`, compact `pfo context-snapshot`, pre/post `context-budget.py` hooks, and permission-matrix parity for large output and raw HTTP routing.
- Agent and control harness engineering docs, validators, templates, and control inventory for feedforward/feedback and computational/inferential PFO controls.
- Harness efficiency metrics and harness-template coverage across product templates, including updated `pfo metrics`, runtime validation, and control-harness gates.
- `/caveman` token-efficiency workflow with route triggers, fixture coverage, integration docs, marketplace metadata, and PFO-safe terse response rules.
- Security-audit v2 workflow with explicit phase contracts, coverage artifacts, `validate_security_report.py`, diff security evidence gates, and strengthened fix-finding/deep-scan guidance.
- PFO-aware skill scaffolding with `pfo skill-scaffold`, generating `SKILL.md`, skill contracts, triggers, fixtures, route snapshots, route reminders, and fixture contracts together.
- Headless fixture expected/actual comparison reports for mock and live command runs, including aggregate `PFO_HEADLESS_COMPARISON.md/json` and per-fixture `logs/comparison.md/json` artifacts.
- Release-critical eval layer: mandatory live headless proof for 7 critical fixtures, quality graders for route correctness, artifact quality, tool safety, and state-save evidence, high-risk skill prompt/version datasets, and adversarial prompt-injection/MCP misuse/fake-data fixtures.
- Five-layer defensive diagnostics with `docs/DEFENSIVE_LAYERS.md` and `validate_defensive_layers.py`, wired into CI, release checks, production readiness, structure/runtime validation, and the control harness.
- Self-runtime contract hardening with concrete `.pfo` self-contracts, `validate_self_contracts.py`, WSL direct `pfo` wrapper support, and contract-gate runtime report classification.
- Route profiles for PFO overhead control: `minimal`, `standard`, and `full` profiles now define route-specific steps, gates, artifacts, and verification policy.
- Minimal existing-project routes now stay limited to adoption, scope, targeted verification, review, and state-save without requiring Product Compiler planning artifacts.
- `artifactDebt` metrics in `pfo metrics`, reporting the documents required by the active route, missing required artifacts, and tracked artifacts outside the current route.
- `validate_route_profiles.py` plus production-readiness/runtime/structure wiring to keep route profile contracts deterministic.
- Workspace health metrics in `pfo metrics`: context index/snapshot coverage, live blocked project ratio, blockers by type, stale state, missing gates, and live eval status.
- Static workspace health dashboard sections for blockers by type, blocked projects, stale state, missing gates, and live eval status.
- `.pfo/UNIT_CONTEXT_MANIFEST.json` template in project-local PFO contracts so adopted existing projects satisfy route-profile context coverage.
- `validate_workspace_targets.py` deterministic gate for the 100/100 workspace targets: context coverage above 90%, verification pass rate above 95%, repair loops per verified unit below 0.25, and PASS live eval status.
- Global PFO policy now explicitly covers new and existing local projects anywhere on the computer, including projects outside the default `projects` workspace.

### Changed

- `pfo_contract_gate.py` now treats generated PFO status/report artifacts as runtime diffs and requires security coverage only for real non-doc, non-test security-sensitive product files.
- `pfo_contract_gate.py` now detects dependency risk from changed dependency manifests and lockfiles instead of broad text matches, removing false-positive dependency warnings.
- Production readiness and release checks now run the PFO contract gate and the workspace target gate.
- Production readiness and release checks now validate a committed workspace-target metrics proof so GitHub Actions can run without local machine workspace state, while live workspace validation remains available with `--workspace`.
- `pfo manifest`, generated verification contracts, `pfo verify-work`, and `pfo next-best-action` now honor the active route profile.
- Existing-project adoption and analysis now deep-merge missing JSON contract keys from templates, repairing stale permission matrix, context runtime, tool registry, and unit manifest contracts without overwriting project-local settings.
- Existing-project stack and command detection now covers nested package scripts, Vite/Vue/Svelte/Nuxt/Express/NestJS, Python/pytest/FastAPI/Django/Flask, Make/Just, Go, Rust, Docker Compose, and PFO runtime projects.

---

## [1.0.0] - 2026-05-18

### Added

- GSD-inspired autonomous execution layer: phase discussion, unit context manifest, dispatch journal, fail-closed verification, recovery state, telemetry, learnings, and HTML briefs.
- Runtime commands: `pfo discuss`, `pfo manifest`, `pfo verify-work`, `pfo brief`, and `pfo learnings`.
- Templates for `PHASE_CONTEXT.md`, `.pfo/UNIT_CONTEXT_MANIFEST.json`, `PFO_RECOVERY.md`, and `.codex-memory/LEARNINGS.md`.
- Integration notes documenting what PFO adopts from GSD and what remains intentionally out of scope.
- Superpowers-inspired engineering gates: TDD evidence, root-cause discipline, two-stage review, strict executable plans, and branch finish hygiene.
- Runtime commands: `pfo tdd-evidence`, `pfo root-cause`, `pfo review-stage`, and `pfo finish-branch`.
- Templates for `ROOT_CAUSE.md` and `BRANCH_FINISH.md`.
- `/market-scan` skill for Last30Days-backed public market/community signal research before discovery, blueprint, and strategy decisions.
- Market and validation templates now capture recent community signals, complaints, alternatives, source links, engagement, and confidence.
- `/handoff` skill, `HANDOFF.md` template, state tracking, route fixture, and `pfo handoff` command for session, role, delegation, AFK, compaction, and recovery transfers.
- `/skill-create` skill for extending Product Factory OS with new skills, contracts, triggers, route snapshots, and fixtures.
- Trigger drift verifier, behavioural fixture contracts, manifest drift checks, install/hook sync checks, and skill risk profile validation.
- `session-diagnostics.py` hook for stale state, recovery, handoff, and telemetry warnings.
- `docs/DESIGN_SPACE.md` coverage map and marketplace hero image metadata.
- Skill metadata profiles for `effort`, `side_effect`, and `explicit_invocation`, plus `Self-validation` sections in every skill.
- `/blueprint` architecture variants and adversarial architecture debate before final ADR selection.

## [0.6.1] - 2026-05-09

### Added

- One-command `bash install.sh` workspace installer.
- `scripts/install_workspace.py` for workspace policy, hook install, `pfo` command wrapper, and existing-project adoption.
- Project-level `AGENTS.md` generation for new and adopted projects.
- Workspace-level `AGENTS.md`, `CODEX.md`, and `PFO_WORKSPACE.json` managed runtime block.
- Preflight hook auto-adoption for first-level projects inside the configured workspace.

### Changed

- Installer now installs hooks, writes workspace policy, creates the `pfo` command, and adopts existing projects by default.
- Existing-project adoption now creates `.pfo/` contracts and preserves existing local instructions by appending managed PFO blocks.
- Generated-project validation now requires `AGENTS.md`.
- Install docs now use the short `git clone`, `cd`, `bash install.sh` path.

## [0.6.0] - 2026-05-09

### Added

- Stronger install/onboarding path with smoke-tested `pfo new -> pfo plan -> pfo validate`.
- Hook parity layer: route reminders, preflight context, skill completeness, commit completeness, and review-before-commit gates.
- Hook documentation and `scripts/validate_hooks.py`.
- Route snapshot contract covering every PFO skill.
- Expanded routing fixtures for discovery, guide, review, test, refactor, docs, explain, performance, dependency audit, hardening, infra, browser checks, MCP docs, GitHub workflow, tool sync, strategy, advisor, and session save.
- Explicit "What This Does NOT Do" docs in English and Russian.
- Versioned path to `1.0.0` with 0.6/0.7/0.8/0.9 milestones.
- Documentation consistency pass across README, workspace defaults, core runtime docs, open-core/commercial docs, starter/golden-path docs, marketplace metadata, and public roadmap issues.

### Changed

- `pfo plan` now generates missing `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md`, and `QUALITY_GATES.md` while preserving existing files.
- Generated-project validation now requires planning artifacts once a project reaches `PLAN_READY` or later.
- CI now validates hook contracts and smoke-tests plan generation after project bootstrap.
- Runtime validation now includes hook validation support.
- Packaging installer now validates fixtures/hooks and can copy hooks into the local Codex hook directory.

## [0.5.0] - 2026-05-02

### Added

- Product Factory OS runtime layer with classifier, template library, product compiler, execution pipeline, state machine, memory schema, deployment targets, and voice-first interface.
- Russian PFO master prompt and architecture documentation.
- Product Compiler templates for `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, and `EXECUTION_GRAPH.md`.
- Orchestrator, backend-builder, frontend-builder, and memory-agent role descriptions.
- PFO routing fixture for a Telegram bot product.
- Execution graph semantic validator for nodes, transitions, checkpoints, and repair paths.
- New project bootstrap helper for automatic Product Factory OS adoption.
- Mandatory existing-project Product Factory OS path with adoption, repository analysis, task classification, gates, and state save.
- Strategy, testing, PFO, threat-model, data-classification, and gate templates/rubrics.
- Classifier v2, template library v2, expanded state machine, and memory schema v2 fields.
- `STATE.json` validator for generated or adopted projects.
- Runtime CLI, execution runner, generated-project validator, voice intent normalizer, metrics collector, and release check.
- Starter packs for SaaS, bot, API, landing, CLI, scraper, e-commerce, mini app, and internal automation.
- Machine-readable golden paths for core product categories.
- Automatic starter selection, scaffold expansion, generated CI templates, starter compliance validation, and `PFO_REPORT.md` generation.
- Real starter skeleton files, execution graph generator, static dashboard, local voice-to-text adapter, benchmark suite, packaging helper, marketplace metadata, and GitHub/Linear/Notion export contracts.
- Open-core strategy, commercial boundary, pricing, packs, cloud, governance, security, and code-of-conduct docs.
- Connector-aware PFO routes for `/mcp-docs`, `/browser-check`, `/github-workflow`, and `/tool-sync`.
- Researcher, UX reviewer, release manager, integration engineer, and data reviewer agent roles.
- OpenAI/MCP integration map for Context7, Browser Use, GitHub, Codex Security, Linear, Notion, and Google Drive.
- Google Drive integration export contract.

### Changed

- `/project`, `/blueprint`, `/kickstart`, and `/session-save` now reference PFO runtime contracts and state persistence.
- Validation now checks PFO machine-readable contracts and expanded agent roles.
- CI now runs execution graph semantic validation.
- Workspace policy now documents mandatory voice-first PFO routing for new projects.
- `/task` and `/adopt` now enforce existing-project PFO state and memory checks.
- Strategy, review, test, security, hardening, backend, frontend, and operations roles now use deeper production-grade contracts.
- Kickstart, task routing, review, security audit, and deploy skills now route connector-assisted gates explicitly.

## [0.4.0] - 2026-05-02

### Added

- Workspace default policy docs.
- Root workspace `CODEX.md` and `PFO_WORKSPACE.json` policy files.
- Adoption-check script for first-level workspace projects.

### Changed

- Meta-review now checks workspace policy files.

## [0.3.0] - 2026-05-02

### Added

- GitHub Actions validation workflow.
- Russian README.
- Local install and testing guide.
- Golden-path tutor booking example.
- Optional soft hook scripts for route reminders and preflight context.

### Changed

- Validation now requires CI, install docs, golden-path docs, and hook scripts.
- Fixture runner now smoke-tests the route reminder hook.

## [0.2.0] - 2026-05-02

### Added

- Trigger registry.
- Review, security, dependency, and production readiness rubrics.
- Smoke fixtures for new project, existing bug, and planning-only flows.
- Additional fixtures for deploy, migration, security audit, and adoption.
- Planning document templates.
- Fixture route runner.
- Meta-review script.
- Roadmap.

### Changed

- Expanded key lifecycle skills with gates, mode detection, failure handling, and explicit production confirmation rules.
- Strengthened structure validation to cover templates, rubrics, fixtures, trigger coverage, and rubric references.

## [0.1.0] - 2026-05-02

### Added

- Initial Codex plugin manifest.
- 23 methodology skills.
- 6 agent role descriptions.
- Methodology docs, skill contracts, and call graph.
- Structure validation script.
