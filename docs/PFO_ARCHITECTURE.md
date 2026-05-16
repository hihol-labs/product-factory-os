# Product Factory OS Architecture

Product Factory OS turns Product Factory OS into a reusable execution engine for generating digital products.

It keeps the existing Codex skill-routing model, but adds deterministic runtime contracts:

```text
IDEA
  -> Intent Parsing
  -> Product Classification
  -> Architecture Selection
  -> Product Blueprint
  -> Phase Discussion
  -> Build Plan
  -> Execution Graph
  -> Unit Context Manifest
  -> TDD Evidence
  -> Modular Build
  -> Work Verification
  -> Two-Stage Review
  -> Drift And Recovery Check
  -> Tests
  -> Quality Gates
  -> Deploy Ready
  -> Learning Extraction
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
- `install_workspace.py`: one-command workspace installer for policy files, hooks, command wrapper, and existing-project adoption
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

### 6. Phase Discussion Layer

Captures the implementation decisions that usually get lost between high-level planning and code:

- product behavior choices
- UI and API shape decisions
- data model assumptions
- integrations and fallback boundaries
- open questions that block planning

The canonical artifact is `PHASE_CONTEXT.md`.

### 7. Unit Context Manifest

Before execution, each node gets a task-scoped manifest:

- unit id and goal
- required inputs and source artifacts
- allowed write areas
- forbidden changes
- dependencies
- verification commands
- gates that must pass
- recovery behavior

The canonical artifact is `.pfo/UNIT_CONTEXT_MANIFEST.json`.

### 8. Execution Engine

Uses `execution/state-machine.json` and `pipelines/execution-pipeline.json` to move through controlled states. Failed gates block forward movement and create a repair path.

Execution should use fresh, task-scoped context per unit. Long chat history is not the execution source of truth.

### 9. Verification, Drift, And Recovery

Post-unit verification fails closed. PFO records unclear evidence as recovery work, not success.

Recovery covers:

- stale or missing state
- missing required artifacts
- worktree or branch mismatch
- unsafe verification commands
- changed golden flows without evidence
- repeated unit failure or stuck progress

### 10. Engineering Discipline Gates

PFO keeps product strategy and project contracts as the outer lifecycle, then applies disciplined engineering gates inside each execution unit:

- TDD evidence: red, green, and refactor verification for behavior changes.
- Root cause: bugfixes require evidence and a fix hypothesis before code changes.
- Two-stage review: spec compliance first, code quality second.
- Strict task granularity: exact files, commands, expected output, and exit criteria.
- Branch finish: PR, merge, keep, or discard decision with fresh verification.

### 11. Memory System

Uses `memory/session-state.schema.json` as the canonical reloadable state contract.

It stores dispatch history, telemetry, recovery state, captured notes, and durable learnings in addition to basic stage and gate state.

Structured learnings are recorded in `.codex-memory/LEARNINGS.jsonl`. Candidate runtime improvements are proposed into `.codex-memory/LEARNING_PROPOSALS.json` and the repository-level `memory/LEARNING_REGISTRY.json`; they must pass promotion gates before changing templates, routes, gates, or skills.

### 12. Deployment Abstraction Layer

Uses `deployment/deployment-targets.json` to prepare deploy-ready artifacts for Docker, VPS, Vercel, Netlify, AWS, GCP, and Azure.

### 13. Connector And MCP Layer

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
- `PHASE_CONTEXT.md` when detailed implementation decisions exist
- `ROOT_CAUSE.md` for bugfix work
- `.pfo/UNIT_CONTEXT_MANIFEST.json` before autonomous or delegated execution
- `PFO_RECOVERY.md` when verification or state reconciliation blocks progress
- `BRANCH_FINISH.md` when branch cleanup or PR/merge decisions are in scope
- `PFO_BRIEF.html` when visual status, plan, diff, or recap review is useful
- `.codex-memory/LEARNINGS.md` after significant milestones or repairs
- `CODEX.md`
- `.codex-memory/STATE.json`
- `.codex-memory/MEMORY.md`

## Quality Gates

Deployment is blocked unless:

- Architecture matches implementation.
- Changed behavior has tests or a documented non-production limitation.
- TDD red/green/refactor evidence is recorded for behavior changes, or an explicit exception exists.
- Bugfixes have root-cause evidence before the fix is accepted.
- Implementation units pass spec compliance review before code quality review.
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
