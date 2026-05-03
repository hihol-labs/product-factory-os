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
```

## Executable Runtime

Runtime scripts live in `scripts/`:

- `pfo.py`: unified CLI
- `pfo_runner.py`: execution step runner
- `validate_project.py`: generated-project validator
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
- Security review has no Critical findings.
- Dependency review has no Critical findings or accepted risk.
- Deployment readiness includes env vars, build command, health check, and rollback or recovery notes.
- Strategy, testing, PFO, and security rubrics pass for their applicable scope.
