# Product Factory OS Architecture

Product Factory OS turns Product Factory OS into a reusable execution engine for generating digital products.

It keeps the existing Codex skill-routing model, but adds deterministic runtime contracts:

```text
IDEA
  -> Intent Parsing
  -> Product Classification
  -> Idea Scorecard
  -> Market Validation Plan
  -> Architecture Selection
  -> Product Blueprint
  -> Phase Discussion
  -> Build Plan
  -> Execution Graph
  -> Unit Context Manifest
  -> TDD Evidence
  -> Modular Build
  -> Work Verification
  -> Experiment Loop
  -> Two-Stage Review
  -> Drift And Recovery Check
  -> Tests
  -> Quality Gates
  -> Deploy Ready
  -> Feedback And Iteration Review
  -> Asset And Content Extraction
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
Idea -> Idea Scorecard -> Validation Plan -> Product Blueprint -> Build Plan -> Execution Graph
```

### 6. Validation Layer

Prevents broad build scope from hiding weak demand. It records:

- idea score and KILL/TEST/BUILD decision
- riskiest assumptions
- validation experiments
- expected and actual market signals
- feedback sources
- funnel bottlenecks

When product, ICP, competitor, launch, or roadmap risk depends on current public demand, PFO routes through `/market-scan` before scoring or replanning. `/market-scan` uses Last30Days when available and normalizes recent community signals into `MARKET_BRIEF.md`, `VALIDATION_PLAN.md`, and related strategy artifacts.

Canonical artifacts are `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md`, `FEEDBACK_LOG.md`, `ITERATION_REVIEW.md`, and `FUNNEL_MODEL.md`.

### 7. Phase Discussion Layer

Captures the implementation decisions that usually get lost between high-level planning and code:

- product behavior choices
- UI and API shape decisions
- data model assumptions
- integrations and fallback boundaries
- open questions that block planning

The canonical artifact is `PHASE_CONTEXT.md`.

### 8. Unit Context Manifest

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

### 9. Handoff Layer

Before session transfer, role switch, delegated execution, AFK work, compaction, or recovery, PFO writes a compact transfer packet:

- current state, node, unit, and next action
- final decisions only
- required inputs
- allowed and forbidden scope
- verification commands
- blockers and first action

The canonical artifact is `HANDOFF.md`.

### 10. Execution Engine

Uses `execution/state-machine.json` and `pipelines/execution-pipeline.json` to move through controlled states. Failed gates block forward movement and create a repair path.

Execution should use fresh, task-scoped context per unit. Long chat history is not the execution source of truth.

### 11. Verification, Drift, And Recovery

Post-unit verification fails closed. PFO records unclear evidence as recovery work, not success.

Recovery covers:

- stale or missing state
- missing required artifacts
- worktree or branch mismatch
- unsafe verification commands
- changed golden flows without evidence
- repeated unit failure or stuck progress

### 11a. Autoresearch-Style Experiment Loop

For measurement-driven self-improvement, PFO adds a small Autoresearch-style loop:

- `.pfo/EXPERIMENT_PROGRAM.md` is the local "program" for autonomous iteration.
- `.pfo/UNIT_CONTEXT_MANIFEST.json` defines the only allowed write areas.
- Protected evaluation/data/contract files stay immutable during the loop.
- Each run has one metric, one direction, and a fixed budget.
- `.pfo/EXPERIMENTS.tsv` records baseline and candidate results.
- Candidate changes end in `keep`, `discard`, or `crash`.
- Equal metric quality prefers the simpler implementation.

CLI entrypoints are `pfo experiment-init` and `pfo experiment-record`. Details live in `docs/AUTORESEARCH_INTEGRATION.md`.

### 12. Engineering Discipline v2 Gates

PFO keeps product strategy and project contracts as the outer lifecycle, then applies disciplined engineering gates inside each execution unit:

- TDD evidence: red, green, and refactor verification for behavior changes.
- Root cause: bugfixes require evidence and a fix hypothesis before code changes.
- Two-stage review: spec compliance first, code quality second.
- Strict task granularity: exact files, commands, expected output, and exit criteria.
- Branch finish: PR, merge, keep, or discard decision with fresh verification.
- Enforcement: `scripts/validate_plan_quality.py` runs directly and through `scripts/validate_project.py`.

### 12a. Design-Space And Drift Gates

PFO tracks methodology coverage in `docs/DESIGN_SPACE.md`. The drift layer now checks:

- trigger registry to route-reminder parity
- behavioural fixture contracts for high-risk skills
- skill effort, side-effect, explicit-invocation, and self-validation profiles
- plugin, marketplace, public count, and install/hook sync consistency
- dangerous-route warnings for production, migration, infrastructure, GitHub, and external tool writes

### 13. Memory System

Uses `memory/session-state.schema.json` as the canonical reloadable state contract.

It stores dispatch history, telemetry, recovery state, captured notes, and durable learnings in addition to basic stage and gate state.

Structured learnings are recorded in `.codex-memory/LEARNINGS.jsonl`. Candidate runtime improvements are proposed into `.codex-memory/LEARNING_PROPOSALS.json` and the repository-level `memory/LEARNING_REGISTRY.json`; they must pass promotion gates before changing templates, routes, gates, or skills.

Reusable assets are recorded in `ASSET_REGISTER.md`. Publishable lessons, case studies, and checklists are recorded in `CONTENT_BACKLOG.md` only when they are tied to evidence and approved data boundaries.

### 14. Deployment Abstraction Layer

Uses `deployment/deployment-targets.json` to prepare deploy-ready artifacts for Docker, VPS, Vercel, Netlify, AWS, GCP, and Azure.

### 15. Connector And MCP Layer

Uses `integrations/mcp-capabilities.json` and `docs/OPENAI_MCP_INTEGRATIONS.md` to bind external tools to named PFO skills:

- `/mcp-docs` for Context7 and current documentation lookup.
- `/market-scan` for Last30Days-backed public market and community signal research.
- `/browser-check` for Playwright or Browser Use smoke testing.
- `/github-workflow` for issues, PRs, CI, and release workflow.
- `/tool-sync` for Linear, Notion, Google Drive, and export-only payloads.

## Required PFO Artifacts

Every full-cycle PFO project should maintain:

- `DISCOVERY.md`
- `IDEA_SCORECARD.md`
- `VALIDATION_PLAN.md`
- `MARKET_BRIEF.md` when strategy risk is non-trivial
- `ICP.md` when users or customers matter
- `BUSINESS_MODEL.md` when value capture matters
- `GO_TO_MARKET.md` when launch or acquisition matters
- `FUNNEL_MODEL.md` when acquisition, activation, conversion, or retention matters
- `FEEDBACK_LOG.md` when user or market feedback exists
- `ITERATION_REVIEW.md` after feedback-driven product changes
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
- `HANDOFF.md` before session transfer, role switch, delegated execution, AFK, compaction, or recovery
- `ROOT_CAUSE.md` for bugfix work
- `.pfo/UNIT_CONTEXT_MANIFEST.json` before autonomous or delegated execution
- `.pfo/EXPERIMENT_PROGRAM.md` and `.pfo/EXPERIMENTS.tsv` when autonomous measurement-driven iteration is in scope
- `PFO_RECOVERY.md` when verification or state reconciliation blocks progress
- `BRANCH_FINISH.md` when branch cleanup or PR/merge decisions are in scope
- `PFO_BRIEF.html` when visual status, plan, diff, or recap review is useful
- `.codex-memory/LEARNINGS.md` after significant milestones or repairs
- `ASSET_REGISTER.md` after reusable solutions or patterns appear
- `CONTENT_BACKLOG.md` when evidence-backed learnings can become public content
- `CODEX.md`
- `.codex-memory/STATE.json`
- `.codex-memory/MEMORY.md`

## Quality Gates

Deployment is blocked unless:

- The idea gate is not `KILL` for the current build scope.
- Validation, feedback, and funnel evidence are explicit when market risk is material.
- Architecture matches implementation.
- Changed behavior has tests or a documented non-production limitation.
- TDD red/green/refactor evidence is recorded for behavior changes, or an explicit exception exists.
- Bugfixes have root-cause evidence before the fix is accepted.
- Implementation units pass spec compliance review before code quality review.
- Project `.pfo/` contracts pass: scope lock, data authenticity, golden flows, regression contract, fallback policy, diff risk, and no silent substitution.
- Security review has no Critical findings.
- Dependency review has no Critical findings or accepted risk.
- Deployment readiness includes env vars, build command, health check, and rollback or recovery notes.
- Browser-facing products have no blocking `/browser-check` findings and include target, engine, flow, screenshot/log evidence before deploy readiness.
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
