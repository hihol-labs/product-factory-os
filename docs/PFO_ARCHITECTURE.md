# Product Factory OS Architecture

Product Factory OS turns Product Factory OS into a reusable execution engine for generating digital products.

It keeps the existing Codex skill-routing model, but adds deterministic runtime contracts:

```text
IDEA
  -> Intent Parsing
  -> Product Classification
  -> Architecture Selection
  -> Product Blueprint
  -> Build Plan
  -> Execution Graph
  -> Modular Build
  -> Tests
  -> Quality Gates
  -> Deploy Ready
  -> Session State
```

## Logical Architecture

```text
interface/
  -> routing/
     -> core/product-compiler
        -> templates/
        -> pipelines/
        -> execution/state-machine
           -> agents/
           -> deployment/
           -> memory/
           -> integrations/
```

## Executable Runtime

Runtime scripts live in `scripts/`:

- `pfo.py`: unified CLI
- `pfo_runner.py`: execution step runner
- `existing_project_analyzer.py`: existing-project stack, command, gate, security, and state analyzer
- `validate_project.py`: generated-project validator
- `validate_hooks.py`: hook contract validator
- `voice_intent.py`: voice/text intent normalizer
- `pfo_metrics.py`: workspace metrics
- `release_check.py`: release validation

Starter packs live in `starters/`.

Golden paths live in `golden-paths/`.

## Layers

### 1. Intent Layer

Normalizes natural language, voice transcripts, and short commands into a product intent.

### 2. Product Classification Engine

Uses `routing/product-classifier.json` to classify:

- Product type
- Domain
- Complexity
- Required modules
- Infrastructure
- Confidence
- Ambiguity
- Data sensitivity
- Monetization or value-capture model
- Recommended stack

### 3. Architecture Selector

Chooses:

- Monolith
- Modular monolith
- Microservices

Default rule:

- Small products use monolith.
- Medium products use modular monolith.
- Large products use microservices only when isolation or scale requires it.

### 4. Template Library

Uses `templates/product-templates.json` to select reusable module sets for SaaS, bots, APIs, web apps, landing pages, CLI tools, mini apps, e-commerce, scrapers, and internal automation.

Each template defines modules, default folders, test minimums, security minimums, and deployment minimums.

### 5. Product Compiler

Compiles:

```text
Idea -> Product Blueprint -> Build Plan -> Execution Graph
```

### 6. Execution Engine

Uses `execution/state-machine.json` and `pipelines/execution-pipeline.json` to move through controlled states. Failed gates block forward movement and create a repair path.

### 7. Memory System

Uses `memory/session-state.schema.json` as the canonical reloadable state contract.

### 8. Deployment Abstraction Layer

Uses `deployment/deployment-targets.json` to prepare deploy-ready artifacts for Docker, VPS, Vercel, Netlify, AWS, GCP, and Azure.

### 9. Connector And MCP Layer

Uses `integrations/mcp-capabilities.json` and `docs/OPENAI_MCP_INTEGRATIONS.md` to bind external tools to named PFO skills:

- `/mcp-docs` for Context7 and current documentation lookup.
- `/browser-check` for Browser Use smoke testing.
- `/github-workflow` for issues, PRs, CI, and release workflow.
- `/tool-sync` for Linear, Notion, Google Drive, and export-only payloads.

## Required PFO Artifacts

Every full-cycle PFO project should maintain:

- `DISCOVERY.md`
- `MARKET_BRIEF.md` when strategy risk is non-trivial
- `ICP.md` when users or customers matter
- `BUSINESS_MODEL.md` when value capture matters
- `GO_TO_MARKET.md` when launch or acquisition matters
- `PRD.md`
- `PRODUCT_BLUEPRINT.md`
- `PROJECT_ARCHITECTURE.md`
- `THREAT_MODEL.md` when sensitive data, auth, integrations, admin, or payments exist
- `DATA_CLASSIFICATION.md` when data is stored or logged
- `TEST_PLAN.md`
- `QUALITY_GATES.md`
- `BUILD_PLAN.md`
- `EXECUTION_GRAPH.md`
- `IMPLEMENTATION_PLAN.md`
- `CODEX.md`
- `.codex-memory/STATE.json`
- `.codex-memory/MEMORY.md`

## Quality Gates

Deployment is blocked unless:

- Architecture matches implementation.
- Changed behavior has tests or a documented non-production limitation.
- Project `.pfo/` contracts pass: scope lock, data authenticity, golden flows, regression contract, fallback policy, diff risk, and no silent substitution.
- Security review has no Critical findings.
- Dependency review has no Critical findings or accepted risk.
- Deployment readiness includes env vars, build command, health check, and rollback or recovery notes.
- Browser-facing products have no blocking `/browser-check` findings before deploy readiness.
- GitHub, Linear, Notion, or Google Drive sync status is explicit when external tracking is in scope.
- Strategy, testing, PFO, and security rubrics pass for their applicable scope.

## Hook And Snapshot Layer

PFO uses `hooks/hooks.json` and `tests/snapshots/route-snapshots.json` to keep natural-language routing, skill docs, fixtures, and runtime behavior aligned.

- `route-reminder.py` suggests routes before Codex drifts into ad hoc work.
- `preflight-context.py` surfaces PFO docs, state, memory, and `.pfo/` contracts.
- `skill-completeness.py` verifies every skill has docs, triggers, fixtures, and route snapshots.
- `commit-completeness.py` checks methodology diffs for supporting artifacts.
- `review-before-commit.py` runs fast validators before methodology commits.

The release bar for PFO is: every skill has a route snapshot, every route snapshot has a fixture, and CI validates both.

## Project Contract Layer

Product Factory OS owns the universal mechanism, not project-specific truth.

Every generated or adopted project receives a `.pfo/` directory:

- `PROJECT_CONTRACT.md`
- `DATA_POLICY.md`
- `GOLDEN_FLOWS.md`
- `FORBIDDEN_CHANGES.md`
- `FALLBACK_POLICY.md`
- `SCOPE_LOCK.md`

The runtime gate `scripts/pfo_contract_gate.py` reads those files, classifies the current diff, and blocks unsafe silent substitutions. This keeps PFO reusable for any product while letting each product define its own invariants.
