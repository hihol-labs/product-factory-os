# Methodology

Product Factory OS is built around small gates instead of one large generation pass. In Product Factory OS mode, those gates are controlled by classifier, template, compiler, state-machine, and memory contracts.

## Lifecycle

1. Route the request.
2. Parse intent and classify the product type.
3. Select a product template and architecture pattern.
4. Compile the idea into Product Blueprint, Build Plan, and Execution Graph.
5. Run a phase discussion before planning detailed work.
6. Ask only the clarifying questions that change the build.
7. Produce documents before code.
8. Review the documents before implementation.
9. Build a unit context manifest before executing a node.
10. Use `/mcp-docs` when library, SDK, or platform behavior could be stale.
11. Implement execution graph nodes in small, isolated units.
12. Record dispatches, verification commands, cost or token notes, and recovery decisions.
13. Add tests for every behavior change.
14. Run `/browser-check` for browser-facing critical flows.
15. Verify work fail-closed: unclear verification does not pass.
16. Review before commit or deploy.
17. Use `/github-workflow` and `/tool-sync` when PR, CI, release, or external planning sync is in scope.
18. Extract durable learnings after completed milestones or significant repairs.
19. Harden production-facing services.
20. Deploy only after explicit confirmation.
21. Save reloadable session memory.

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
- `.pfo/PROJECT_CONTRACT.md`
- `.pfo/DATA_POLICY.md`
- `.pfo/GOLDEN_FLOWS.md`
- `.pfo/FORBIDDEN_CHANGES.md`
- `.pfo/FALLBACK_POLICY.md`
- `.pfo/SCOPE_LOCK.md`
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
- `PHASE_CONTEXT.md`: decisions, assumptions, open questions, planning impact
- `BUILD_PLAN.md`: ordered module build plan with dependencies and verification
- `EXECUTION_GRAPH.md`: execution nodes, transitions, checkpoints, and repair paths
- `IMPLEMENTATION_PLAN.md`: ordered implementation steps with verification
- `README.md`: local setup, scripts, environment variables, deployment notes
- `CODEX_GUIDE.md`: step-by-step prompts and operating rules for Codex
- `CODEX.md`: current project context, decisions, status table, session memory rule
- `.pfo/PROJECT_CONTRACT.md`: project-owned product invariants and behavior contracts
- `.pfo/DATA_POLICY.md`: real-vs-synthetic data rules and required evidence
- `.pfo/GOLDEN_FLOWS.md`: critical user journeys that block deploy when touched and unverified
- `.pfo/FORBIDDEN_CHANGES.md`: changes that require explicit scope approval
- `.pfo/FALLBACK_POLICY.md`: allowed/forbidden degraded-mode behavior
- `.pfo/SCOPE_LOCK.md`: current task boundaries and forbidden change areas
- `.pfo/UNIT_CONTEXT_MANIFEST.json`: execution-unit input, write-scope, gate, and recovery contract
- `.codex-memory/LEARNINGS.md`: durable decisions, lessons, patterns, and surprises

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
- `integrations/mcp-capabilities.json`: MCP and OpenAI/Codex plugin capability map.
- `scripts/pfo_contract_gate.py`: project-contract gate for scope lock, data authenticity, golden flows, regression contracts, fallback policy, diff risk, and no silent substitution.

## Autonomous Execution Layer

Product Factory OS adopts the strongest GSD execution ideas without copying its product shape:

- Phase discussion: capture implementation decisions and assumptions before detailed planning.
- Unit context manifest: each execution unit declares inputs, write scope, dependencies, gates, and verification.
- Fresh-context dispatch: agents should execute units from the manifest, not from accumulated chat context.
- Atomic progress: every meaningful unit records dispatch, verification, and next action in state.
- Fail-closed verification: missing or ambiguous evidence creates a repair path, not a pass.
- Drift and recovery: stale state, missing artifacts, unexpected worktree changes, and blocked verification are first-class recovery cases.
- Telemetry: record unit duration, commands, token or cost notes when available, and gate outcomes.
- Learnings: extract reusable decisions, patterns, lessons, and surprises into project memory.

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
- Prefer fresh, task-scoped context over long accumulated chat state.
- Keep planning documents and code synchronized.
- Treat tests and review as part of implementation, not cleanup.
- Treat unclear verification as failed until evidence exists.
- Treat project-owned `.pfo/` contracts as runtime guardrails, not documentation decoration.
- If a real source or provider is unavailable, fail transparently or use an approved degraded mode; never silently invent production output.
- Preserve session memory so the next session resumes with context.

## Non-Goals

Product Factory OS is an execution framework, not magic product liability insurance.

- It does not replace expert review for regulated, safety-critical, financial, medical, legal, or security-sensitive systems.
- It does not silently call cloud APIs, deploy, migrate databases, rotate DNS, or mutate production.
- It does not treat generated starter code as production-ready until tests, review, security, dependency, hardening, deployment, and `.pfo/` gates are explicit.
- It does not invent production data or provider behavior when a real source is unavailable.
- It does not remove human ownership of product strategy, compliance posture, pricing, or launch risk.
