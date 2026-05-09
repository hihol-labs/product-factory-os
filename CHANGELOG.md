# Changelog

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
