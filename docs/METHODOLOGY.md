# Methodology

Product Factory OS is built around small gates instead of one large generation pass. In Product Factory OS mode, those gates are controlled by classifier, template, compiler, state-machine, and memory contracts.

## Control Harness Model

PFO classifies every durable guardrail with two axes:

- Feedforward controls, or guides, shape work before execution: instructions, templates, architecture decisions, examples, task decomposition, permission policy, and verification contracts.
- Feedback controls, or sensors, judge work after output exists: tests, hooks, CI, validators, security review, UX review, human review, and repair gates.
- Computational controls are deterministic: linters, tests, schema validation, contract gates, execution graph validation, permission gates, build checks, and generated-project CI.
- Inferential controls use LLM or human judgment: reviewer, security-reviewer, UX-reviewer, advisor, grill-me, architecture debate, and market synthesis.

The full matrix and inventory live in `docs/CONTROL_HARNESS.md`. PFO prefers computational feedback for blocking invariants, uses inferential controls for semantic judgment, and promotes repeated inferential findings into deterministic checks when possible.

PFO uses agent harness engineering as the operating frame: work backwards from desired behaviour or observed failure, then add the smallest prompt, tool, hook, state, permission, verification, or review control that changes future runs. Controls must also name what they regulate: maintainability, architecture fitness, or behaviour.

PFO keeps quality left by running fast computational sensors locally, repeating them in CI or release gates, and reserving slower inferential or broad sensors for higher-risk decisions. The source integration guide is `docs/AGENT_HARNESS_ENGINEERING.md`.

## Codex Goal Mode

Codex `/goal` mode is default-on inside Product Factory OS. For every non-trivial local project request, Codex creates or continues one goal before implementation. The objective names the user outcome and the active PFO route, for example `/project -> /kickstart` for new products or `/task -> /bugfix` for existing-code work.

The goal stays active through implementation, gates, verification, and state-save. It is marked complete only when the requested outcome and PFO exit gates are satisfied. It is marked blocked only when PFO cannot continue without user input or an external state change.

## Lifecycle

1. Route the request.
2. Parse intent and classify the product type.
3. Score the idea and decide `KILL`, `TEST`, or `BUILD`.
4. Run the evidence quality gate: real conversations, past behavior evidence, contradicting evidence, and BUILD truth conditions.
5. Define validation experiments and customer discovery interview discipline for the riskiest assumptions.
6. Run adversarial discovery when market or competitor risk matters.
7. Select a product template, architecture pattern, and default stack preset.
8. Compile the idea into Product Blueprint, Build Plan, and Execution Graph.
9. Run a phase discussion before planning detailed work.
10. Ask only the clarifying questions that change the build.
11. Produce documents before code.
12. Review the documents before implementation.
13. Build a unit context manifest before executing a node, including context and tool policy for the active unit.
14. Check harnessability for the active unit: clear structure, contracts, golden flows, command availability, and sensor coverage.
15. Write `/handoff` before session transfer, role switch, delegated execution, AFK, compaction, or recovery.
16. Use `/mcp-docs` when library, SDK, or platform behavior could be stale.
17. Implement execution graph nodes in small, isolated units.
18. Run fast local sensors as early as possible: targeted tests, validators, lint, schema checks, route checks.
19. Record dispatches, verification commands, cost or token notes, and recovery decisions.
20. For measurement-driven self-improvement, initialize an experiment loop with one metric, a fixed budget, protected evaluation files, and a results TSV.
21. For behavior changes, record TDD red/green/refactor evidence or an explicit exception.
22. For bugfixes, record root-cause evidence before changing code.
23. Run `/browser-check` for browser-facing critical flows.
24. Capture feedback and iteration outcomes from users, metrics, or validation evidence.
25. Before MVP launch, define activation, retention, PMF signals, and false-positive traction when market risk is material.
26. Use optional launch maturity and scale moat artifacts only when stage and risk justify them.
27. Verify work fail-closed: unclear verification does not pass.
28. Run two-stage review: spec compliance first, code quality second.
29. Review before commit or deploy.
30. Use `/github-workflow` and `/tool-sync` when PR, CI, release, or external planning sync is in scope.
31. Finish branches with an explicit PR, merge, keep, or discard decision.
32. Extract durable learnings after completed milestones or significant repairs, and promote repeated failures through the harness ratchet.
33. Promote repeatable solutions into assets and content candidates.
34. Harden production-facing services.
35. Deploy only after explicit confirmation.
36. Save reloadable session memory.

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

This applies globally after install. The preflight hook reads `PFO_GLOBAL.json`, detects the current project root outside the default workspace, and runs adoption/analysis before implementation.

The default `/goal` rule applies before the `/task` route starts. Existing-project goals should include the requested change, adoption/analysis state if relevant, and the selected daily-work route.

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

## New Project Repository Policy

New projects are local-first. The mandatory bootstrap target is a project directory inside the configured workspace.

- Initialize local Git before implementation when the project is not already a repository, so changes are traceable from the first build step.
- Do not require a GitHub repository to create a PFO project.
- Create or connect a GitHub repository only when the user requests it, when PR/CI/release workflow is in scope, or when workspace policy explicitly enables it.
- When a remote repository exists, track `repositoryUrl` and sync status in project state or architecture notes.
- Use `/github-workflow` for GitHub issues, PRs, CI, releases, and publication; use `/tool-sync` only for export or external planning sync.

## Core Documents

- `DISCOVERY.md`: market, users, customer discovery plan, alternatives, positioning, MVP scope
- `IDEA_SCORECARD.md`: idea score, evidence quality, weaknesses, contradicting evidence, BUILD truth conditions, and KILL/TEST/BUILD decision
- `VALIDATION_PLAN.md`: riskiest assumptions, interview discipline, experiments, expected signals, actual signals, and exit decision
- `MARKET_BRIEF.md`: problem, segment, alternatives, adversarial discovery, differentiation, market entry
- `ICP.md`: primary user, buyer, jobs, pain signals, adoption trigger
- `BUSINESS_MODEL.md`: value capture, pricing or ROI, cost drivers
- `GO_TO_MARKET.md`: channel, offer, activation path, MVP measurement contract, feedback loop, metrics
- `FUNNEL_MODEL.md`: traffic, lead, activation, conversion, retention stages, PMF signals, false-positive traction, and bottleneck
- `FEEDBACK_LOG.md`: feedback sources, evidence, patterns, and triggered decisions
- `ITERATION_REVIEW.md`: iteration inputs, changes, outcomes, and keep/revert/iterate decision
- `PRD.md`: user stories, acceptance criteria, non-goals, launch criteria
- `PRODUCT_BLUEPRINT.md`: product classification, business logic, entities, modules, interfaces, dependencies, infrastructure
- `PROJECT_ARCHITECTURE.md`: stack, data model, APIs, auth, deployment topology
- `THREAT_MODEL.md`: assets, actors, trust boundaries, abuse cases, controls
- `DATA_CLASSIFICATION.md`: data inventory, sensitivity, retention, storage, access
- `TEST_PLAN.md`: test matrix, critical flows, negative cases, smoke path
- `QUALITY_GATES.md`: gate status, evidence, blockers, accepted risk
- `PHASE_CONTEXT.md`: decisions, assumptions, open questions, planning impact
- `HANDOFF.md`: transfer packet for session, role, delegation, AFK, compaction, or recovery handoff
- `ROOT_CAUSE.md`: bug reproduction, evidence, and fix hypothesis for bugfix work
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
- `.pfo/EXECUTION_POLICY.json`: command, write, network, and approval policy
- `.pfo/PERMISSION_MATRIX.json`: machine-readable permission table for local, git, external API, secret, deploy, and migration actions
- `.pfo/PERMISSION_MATRIX.md`: human-readable permission table
- `.pfo/VERIFICATION_CONTRACT.json`: required verification commands, expected output, timeout, pass/fail parser, artifacts, and sensor timing policy
- `.pfo/TOOL_CAPABILITY_REGISTRY.json`: tool and connector read/write/execute capability registry with side effects, auth, external data risk, fallback mode, and approvals
- `.pfo/LEARNING_PROMOTION_GATE.md`: promotion path from repeated errors to tests, hooks, docs, rules, linters, validators, templates, routes, or skills
- `docs/AGENT_HARNESS_ENGINEERING.md`: PFO operating standard for ratcheting observed agent failures into context, tool, hook, verification, and review controls
- `.pfo/EXPERIMENT_PROGRAM.md`: Autoresearch-style fixed-budget experiment contract
- `.pfo/EXPERIMENTS.tsv`: baseline, candidate metrics, and keep/discard/crash decisions
- `.codex-memory/LEARNINGS.md`: durable decisions, lessons, patterns, and surprises
- `.codex-memory/events.jsonl`: structured event log for commands, gates, approvals, verification, errors, state changes, external tools, and learning
- `ASSET_REGISTER.md`: repeatable product, process, template, offer, or automation assets
- `CONTENT_BACKLOG.md`: publishable learnings and case-study candidates tied to evidence
- `LAUNCH_MATURITY_GATE.md`: optional founder bottleneck and ops automation/delegation audit for launch-stage products
- `SCALE_MOAT_REGISTER.md`: optional domain knowledge, edge case, data flywheel, workflow integration, switching-cost, and defensibility register for scale-stage products
- `BRANCH_FINISH.md`: PR, merge, keep, or discard decision when branch cleanup is in scope
- `MASTER_CONTEXT.md`, `ARCHITECTURE.md`, `TASKS.md`, `PROGRESS.md`, `TESTING.md`: thin navigation aliases for humans, agents, and external tools; canonical truth stays in the linked artifacts. New-project aliases may link to Product Compiler docs after `pfo plan`; existing-project aliases must link only to files that already exist.

## Gate Status

Every quality skill returns exactly one status:

- `BLOCKED`: a critical issue prevents the next lifecycle step
- `PASSED_WITH_WARNINGS`: critical checks pass, but important issues remain
- `PASSED`: critical and important checks pass

Scores can be useful as summaries, but they must not replace the status enum.

## Runtime Contracts

- `routing/product-classifier.json`: product classification contract.
- `routing/product-classifier.json`: PFO Default Stack v1 preset and stack deviation policy.
- `templates/product-templates.json`: reusable module template contract.
- `core/product-compiler.md`: idea-to-execution-graph compiler contract.
- `pipelines/execution-pipeline.json`: required stage and artifact contract.
- `execution/state-machine.json`: valid workflow transitions.
- `memory/session-state.schema.json`: reloadable state format.
- `deployment/deployment-targets.json`: deploy-readiness abstraction.
- `integrations/mcp-capabilities.json`: MCP and OpenAI/Codex plugin capability map.
- `scripts/pfo_contract_gate.py`: project-contract gate for scope lock, data authenticity, golden flows, regression contracts, fallback policy, diff risk, no silent substitution, and alias target integrity.
- `scripts/pfo_alias_targets.py`: alias/index target checker for `MASTER_CONTEXT.md`, `ARCHITECTURE.md`, `TASKS.md`, `PROGRESS.md`, and `TESTING.md`.
- `scripts/validate_control_harness.py`: validates the four-quadrant feedforward/feedback and computational/inferential control inventory.

## Autonomous Execution Layer

Product Factory OS adopts the strongest GSD execution ideas without copying its product shape:

- Phase discussion: capture implementation decisions and assumptions before detailed planning.
- Unit context manifest: each execution unit declares inputs, write scope, dependencies, gates, and verification.
- PIV unit handoff: `pfo manifest` writes `plans/<unit>-piv-plan.md`; `pfo verify-work --pass-gate` writes `reports/<unit>-implementation-report.md`.
- Fresh-context dispatch: agents should execute units from the manifest, not from accumulated chat context.
- Atomic progress: every meaningful unit records dispatch, verification, and next action in state.
- Fail-closed verification: missing or ambiguous evidence creates a repair path, not a pass.
- Drift and recovery: stale state, missing artifacts, broken alias targets, unexpected worktree changes, and blocked verification are first-class recovery cases.
- Telemetry: record unit duration, commands, token or cost notes when available, and gate outcomes.
- Autoresearch-style experiments: use one protected metric, fixed budget, baseline-first result logging, and keep/discard/crash decisions for self-improvement loops.
- Learnings: extract reusable decisions, patterns, lessons, and surprises into project memory.
- Assetization: convert proven repeatable solutions into reusable assets and content candidates.

## Engineering Discipline v2 Layer

Product Factory OS adopts the strongest Superpowers engineering discipline while keeping PFO artifacts as the source of truth:

- TDD evidence gate: behavior changes record red evidence before implementation, green evidence after minimal implementation, and post-refactor evidence or an explicit exception.
- Root-cause gate: bugfixes require reproduction, evidence, and a fix hypothesis before code changes.
- Two-stage review: first verify spec compliance against the unit manifest and plan, then review code quality.
- Strict plan granularity: executable tasks name exact files, exact commands, expected output, and exit criteria. Placeholders are plan failures.
- Branch finish workflow: every finished branch records PR, merge, keep, or discard decision with fresh verification evidence.
- Enforcement: `scripts/validate_plan_quality.py` blocks weak executable plans, missing TDD evidence for behavior changes, bugfixes without `ROOT_CAUSE.md`, reversed review order, and branch finish without fresh verification.

## Harness Discipline

Every PFO mechanism must be explainable as one of the four control types from `docs/CONTROL_HARNESS.md`.

- Before implementation, the active feedforward controls must name scope, write boundaries, required artifacts, and expected verification.
- After implementation, feedback controls must produce evidence or a repair path.
- Computational feedback blockers cannot be waived by inferential review.
- Inferential feedback may add blockers for issues deterministic checks cannot see.
- New repeatable findings should be promoted into computational controls through `.pfo/LEARNING_PROMOTION_GATE.md`.

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
- Prefer PFO Default Stack v1 for new products, but allow ADR-style deviations when they improve fit.
- Prefer narrow, verifiable implementation steps.
- Prefer fresh, task-scoped context over long accumulated chat state.
- Keep planning documents and code synchronized.
- Kill weak ideas before they become build scope.
- Treat user behavior evidence as stronger than opinions, compliments, or future-intent answers.
- Require adversarial discovery when confirmation bias could distort strategy.
- Define MVP measurement before launch so early curiosity is not mistaken for PMF.
- Keep launch maturity and scale moat checks optional unless the product stage requires them.
- Treat validation signals and feedback as the source of product iteration.
- Treat content and reusable assets as outputs of evidence, not activity.
- Treat TDD evidence, tests, and two-stage review as part of implementation, not cleanup.
- Treat bugfixes without root-cause evidence as blocked.
- Treat unclear verification as failed until evidence exists.
- Treat self-improvement as an experiment loop: baseline first, fixed budget, protected harness, one metric, and explicit keep/discard/crash.
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
