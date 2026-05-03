# Methodology

Product Factory OS is built around small gates instead of one large generation pass. In Product Factory OS mode, those gates are controlled by classifier, template, compiler, state-machine, and memory contracts.

## Lifecycle

1. Route the request.
2. Parse intent and classify the product type.
3. Select a product template and architecture pattern.
4. Compile the idea into Product Blueprint, Build Plan, and Execution Graph.
5. Ask only the clarifying questions that change the build.
6. Produce documents before code.
7. Review the documents before implementation.
8. Implement execution graph nodes in small steps.
9. Add tests for every behavior change.
10. Review before commit or deploy.
11. Harden production-facing services.
12. Deploy only after explicit confirmation.
13. Save reloadable session memory.

## Existing Project Lifecycle

Existing projects use Product Factory OS too:

```text
Existing project task
  -> /task
  -> PFO adoption check
  -> repository analysis
  -> task classification
  -> task plan or execution graph node
  -> implementation
  -> tests
  -> review
  -> state save
```

Before substantial changes, the project must have:

- `CODEX.md`
- `.codex-memory/MEMORY.md`
- `.codex-memory/STATE.json`

If any are missing, run `/adopt` first.

## Core Documents

- `DISCOVERY.md`: market, users, alternatives, positioning, MVP scope
- `MARKET_BRIEF.md`: problem, segment, alternatives, differentiation, market entry
- `ICP.md`: primary user, buyer, jobs, pain signals, adoption trigger
- `BUSINESS_MODEL.md`: value capture, pricing or ROI, cost drivers
- `GO_TO_MARKET.md`: channel, offer, activation path, feedback loop, metrics
- `PRD.md`: user stories, acceptance criteria, non-goals, launch criteria
- `PRODUCT_BLUEPRINT.md`: product classification, business logic, entities, modules, interfaces, dependencies, infrastructure
- `PROJECT_ARCHITECTURE.md`: stack, data model, APIs, auth, deployment topology
- `THREAT_MODEL.md`: assets, actors, trust boundaries, abuse cases, controls
- `DATA_CLASSIFICATION.md`: data inventory, sensitivity, retention, storage, access
- `TEST_PLAN.md`: test matrix, critical flows, negative cases, smoke path
- `QUALITY_GATES.md`: gate status, evidence, blockers, accepted risk
- `BUILD_PLAN.md`: ordered module build plan with dependencies and verification
- `EXECUTION_GRAPH.md`: execution nodes, transitions, checkpoints, and repair paths
- `IMPLEMENTATION_PLAN.md`: ordered implementation steps with verification
- `README.md`: local setup, scripts, environment variables, deployment notes
- `CODEX_GUIDE.md`: step-by-step prompts and operating rules for Codex
- `CODEX.md`: current project context, decisions, status table, session memory rule

## Gate Status

Every quality skill returns exactly one status:

- `BLOCKED`: a critical issue prevents the next lifecycle step
- `PASSED_WITH_WARNINGS`: critical checks pass, but important issues remain
- `PASSED`: critical and important checks pass

Scores can be useful as summaries, but they must not replace the status enum.

## Runtime Contracts

- `routing/product-classifier.json`: product classification contract.
- `templates/product-templates.json`: reusable module template contract.
- `core/product-compiler.md`: idea-to-execution-graph compiler contract.
- `pipelines/execution-pipeline.json`: required stage and artifact contract.
- `execution/state-machine.json`: valid workflow transitions.
- `memory/session-state.schema.json`: reloadable state format.
- `deployment/deployment-targets.json`: deploy-readiness abstraction.

## Rubrics

Canonical checklists live under `docs/rubrics/`:

- `review.md`: project document and code quality gate
- `pfo.md`: Product Factory OS compiler, state, and gate consistency
- `strategy.md`: product strategy, ICP, value capture, launch readiness
- `testing.md`: test matrix, coverage, smoke, and CI readiness
- `security.md`: read-only security audit
- `deps.md`: dependency, license, and supply-chain audit
- `production.md`: production readiness, hardening, and deploy preflight

## Operating Principles

- Prefer explicit user confirmation at irreversible boundaries.
- Prefer project conventions over generic templates.
- Prefer narrow, verifiable implementation steps.
- Keep planning documents and code synchronized.
- Treat tests and review as part of implementation, not cleanup.
- Preserve session memory so the next session resumes with context.
