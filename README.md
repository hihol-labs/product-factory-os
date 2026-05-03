# Product Factory OS

Product Factory OS is a methodology plugin and runtime framework for Codex: a deterministic workflow for moving from a rough product idea to a working, reviewed, deployable project.

It is inspired by the same discipline as `idea-to-deploy`, but this repository is shaped for Codex plugin conventions:

```text
IDEA -> PRODUCT_BLUEPRINT -> BUILD_PLAN -> EXECUTION_GRAPH -> BUILD -> TEST -> VALIDATE -> DEPLOY_READY -> SAVE_STATE
```

## Status

This is an initial methodology scaffold. It contains:

- 23 skills for creation, daily work, quality, operations, strategy, and memory
- Agent role descriptions for heavy review, architecture, test, analysis, and security work
- Skill contracts with inputs, outputs, side effects, and idempotency notes
- A call graph that keeps workflow chaining bounded
- Trigger registry and quality rubrics for review, security, dependency, and production checks
- Smoke fixtures for the main routing scenarios
- Golden-path example for a tutor booking app
- Optional soft hooks for route reminders and preflight context
- GitHub Actions workflow for validation
- Workspace-default policy for `/home/hihol/projects`
- A structure validator for repository health checks
- Product Factory OS runtime contracts for classification, templates, state machine, execution pipeline, memory, deployment, and voice-first interface

## Quick Start

Use natural language first:

```text
I want to build a booking app for private tutors.
```

The `/project` skill routes the request:

- `A` Full cycle: plan, build, test, review, deploy
- `B` Planning only: produce project documents, no code
- `C` Existing docs: convert docs into an executable Codex guide

For existing codebases, start with:

```text
Fix this bug in the current project.
```

The `/task` skill routes daily work to bugfix, refactor, docs, tests, review, security audit, dependency audit, performance, infra, migration, hardening, or deploy workflows.

## Product Factory OS Runtime

PFO adds deterministic execution contracts:

- `routing/product-classifier.json`: classifies SaaS, bots, APIs, web apps, landing pages, CLI tools, mini apps, e-commerce, scrapers, and internal automation.
- `templates/product-templates.json`: maps product types to reusable module sets.
- `core/product-compiler.md`: compiles idea -> Product Blueprint -> Build Plan -> Execution Graph.
- `execution/state-machine.json`: controls valid workflow transitions.
- `pipelines/execution-pipeline.json`: defines required stages and artifacts.
- `memory/session-state.schema.json`: defines reloadable state.
- `deployment/deployment-targets.json`: defines deploy-readiness checks.

## Runtime CLI

Product Factory OS includes an executable runtime CLI:

```bash
python3 scripts/pfo.py new my-product --idea "SaaS for subscription tracking"
python3 scripts/pfo.py adopt
python3 scripts/pfo.py plan ../my-product
python3 scripts/pfo.py build ../my-product
python3 scripts/pfo.py test ../my-product
python3 scripts/pfo.py review ../my-product
python3 scripts/pfo.py validate ../my-product
python3 scripts/pfo.py status ../my-product
python3 scripts/pfo.py resume ../my-product
python3 scripts/pfo.py report ../my-product
python3 scripts/pfo.py voice "создай Telegram бот для продаж"
python3 scripts/pfo.py metrics
python3 scripts/pfo.py export ../my-product --target github
```

Starter packs live in `starters/`. Golden paths live in `golden-paths/`.

Generated projects receive `.pfo-starter.json`, `.env.example`, `.github/workflows/validate.yml`, `justfile`, and `PFO_REPORT.md`.

Additional platform extensions:

- `dashboard/`: static PFO dashboard shell.
- `benchmarks/`: prompt benchmark suite.
- `packaging/`: install/update helper.
- `marketplace/`: local marketplace metadata.
- `integrations/`: GitHub, Linear, and Notion payload contracts.

## Open Core And Commercial Extensions

Product Factory OS uses an open-core model:

- The local runtime, basic starters, validators, skills, agents, and methodology are open source.
- Premium starter packs, hosted dashboard, team workspaces, managed execution, enterprise policy, and implementation services can be commercial extensions.

Products generated with PFO belong to their authors. Using PFO does not require generated products to be open source.

See:

- [Open Core Strategy](docs/OPEN_CORE.md)
- [Commercial Strategy](docs/COMMERCIAL.md)
- [Pricing Model](docs/PRICING.md)
- [Starter Pack Strategy](docs/PACKS.md)
- [PFO Cloud](docs/CLOUD.md)
- [GitHub Launch Checklist](docs/GITHUB_LAUNCH.md)
- [Initial Roadmap Issues](docs/GITHUB_ISSUES.md)
- [v0.5.0 Release Notes](docs/RELEASE_NOTES_v0.5.0.md)

## Repository Layout

```text
.codex-plugin/plugin.json   Plugin manifest
skills/                     Methodology skills
agents/                     Role prompts for delegated work
docs/                       Methodology docs and contracts
commercial/                 Commercial boundary docs
core/                       Product compiler and runtime responsibilities
routing/                    Product classification engine
templates/                  Product template library
pipelines/                  Execution pipeline contract
execution/                  State machine contract
memory/                     Reloadable session-state schema
deployment/                 Deployment abstraction layer
interface/                  Voice-first input/output contract
hooks/                      Hook configuration placeholder
scripts/                    Validation scripts
tests/fixtures/             Methodology smoke fixtures
.github/workflows/          CI validation workflow
```

## Quality Rule

Every major project step should pass:

1. Requirements are documented.
2. Product classification and architecture template are explicit.
3. `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, and `EXECUTION_GRAPH.md` agree.
4. Tests exist for changed behavior.
5. Review status is not `BLOCKED`.
6. Session state is saved before stopping.

## Validation

```bash
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/validate_execution_graph.py
python3 scripts/validate_state.py /path/to/project/.codex-memory/STATE.json
python3 scripts/validate_runtime.py
python3 scripts/run_benchmarks.py
python3 scripts/meta_review.py
```

The validator checks manifest metadata, required skills, agent role files, trigger coverage, contract coverage, call-graph references, rubrics, fixture shape, PFO runtime contracts, and execution graph semantics.

## Local Testing

See [docs/INSTALL.md](docs/INSTALL.md).

## Master Prompt

See [docs/MASTER_PROMPT.ru.md](docs/MASTER_PROMPT.ru.md) for the Russian Product Factory OS master prompt.

## Workspace Defaults

See [docs/WORKSPACE_DEFAULTS.md](docs/WORKSPACE_DEFAULTS.md). In this workspace, `/home/hihol/projects/CODEX.md` makes Product Factory OS the default methodology for new work and adoption checks.

New projects in `/home/hihol/projects` are bootstrapped and executed through Product Factory OS automatically. Voice or natural-language commands route to `/project -> /kickstart` by default.

Bootstrap helper:

```bash
python3 /home/hihol/projects/product-factory-os/scripts/pfo_new_project.py my-product --idea "voice transcript or product idea"
```

Existing projects in `/home/hihol/projects` also use Product Factory OS:

```text
/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save
```

Use `/adopt` first when `CODEX.md`, `.codex-memory/MEMORY.md`, or `.codex-memory/STATE.json` is missing.

## Golden Path

See [docs/examples/golden-path-booking-app](docs/examples/golden-path-booking-app) for a complete expected planning output.

## Russian

See [README.ru.md](README.ru.md).
