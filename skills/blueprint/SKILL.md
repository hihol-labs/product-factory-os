---
name: blueprint
description: Planning-only workflow that compiles an idea into PFO product documents without implementation.
argument-hint: product idea plus constraints
license: MIT
metadata:
  category: planning
  tags: [blueprint, architecture, prd, planning]
  effort: high
  side_effect: docs-write
  explicit_invocation: false
---

# Blueprint

Create Product Factory OS planning documents and stop before code.

## Inputs To Collect

Ask only for details that change the plan:

- Product goal and primary user
- Idea score, target segment, and riskiest assumption
- Evidence quality: real user conversations, past behavior evidence, contradicting evidence, and BUILD truth conditions
- Must-have user flows
- Data that must be stored
- Authentication and roles
- External integrations
- Deployment target and budget
- Deadline or first milestone
- Fresh market or community signal need when public demand, competitors, launch, ICP, or roadmap risk matters
- First channel, offer, funnel, or feedback source when launch matters
- Launch maturity or scale defensibility context when the product is beyond MVP
- Non-goals and constraints

If the user says "you decide", choose a conservative default and record it as `Assumption: user deferred`.
If the user gives only a generic creation request, ask product-steering questions before selecting a starter or implementation path.

## Process

1. Read existing docs if present.
2. Load PFO runtime contracts when present:
   - `routing/product-classifier.json`
   - `templates/product-templates.json`
   - `core/product-compiler.md`
   - `pipelines/execution-pipeline.json`
   - `execution/state-machine.json`
   - `memory/session-state.schema.json`
   - `docs/rubrics/strategy.md`
   - `docs/rubrics/testing.md`
3. Run `/market-scan` before strategy documents when fresh public market, competitor, ICP, launch, or user/community signals can change the plan.
4. Ask only clarifying questions that affect architecture, scope, data, auth, deployment, budget, or deadline.
5. Confirm the captured understanding.
6. Generate 2 or 3 architecture variants before selecting one:
   - candidate architecture name
   - rationale
   - complexity
   - operational burden
   - failure modes
   - when to reject it
7. Run an adversarial architecture debate:
   - challenge the selected option against simpler and safer alternatives
   - record accepted challenges and rejected challenges
   - capture the final decision as an ADR section in `PROJECT_ARCHITECTURE.md`
8. Generate documents in this order:
   - `DISCOVERY.md`
   - `IDEA_SCORECARD.md`
   - `VALIDATION_PLAN.md`
   - `MARKET_BRIEF.md` when strategy risk is non-trivial
   - `ICP.md` when users/customers matter
   - `BUSINESS_MODEL.md` when revenue, cost saving, or value capture matters
   - `GO_TO_MARKET.md` when launch or user acquisition matters
   - `FUNNEL_MODEL.md` when acquisition, activation, conversion, or retention matters
   - `LAUNCH_MATURITY_GATE.md` when launch-stage founder bottleneck or ops readiness is in scope
   - `SCALE_MOAT_REGISTER.md` when scale, enterprise, vertical depth, or defensibility is in scope
   - `FEEDBACK_LOG.md` when feedback collection is in scope
   - `ITERATION_REVIEW.md` when improving an existing product or MVP
   - `ASSET_REGISTER.md` when reusable assets may be produced
   - `CONTENT_BACKLOG.md` when learnings may become content
   - `PRD.md`
   - `PRODUCT_BLUEPRINT.md`
   - `PROJECT_ARCHITECTURE.md`
   - `THREAT_MODEL.md` when sensitive data, auth, integrations, admin, or payments exist
   - `DATA_CLASSIFICATION.md` when user, business, scraped, or platform data is stored
   - `TEST_PLAN.md`
   - `QUALITY_GATES.md`
   - `BUILD_PLAN.md`
   - `EXECUTION_GRAPH.md`
   - `IMPLEMENTATION_PLAN.md`
   - `NEXT_STEP.md`
   - `HANDOFF.md` when implementation will start in another session or role
   - `README.md`
   - `CODEX.md`
9. Run `/review` on the documents.

## Overwrite Policy

Before changing an existing planning document, list found files and ask:

```text
I found existing planning docs. Should I supplement missing docs or replace the set?
```

Default to supplement. Do not silently replace user-authored documents.

## Document Requirements

- `PRD.md`: user stories, acceptance criteria, non-goals, launch criteria.
- `IDEA_SCORECARD.md`: evidence-backed KILL, TEST, or BUILD decision, real conversation count, past behavior evidence, contradicting evidence, and BUILD truth conditions.
- `VALIDATION_PLAN.md`: riskiest assumptions, customer discovery interview discipline, five-interview debrief, experiments, expected signals, and exit decision.
- `MARKET_BRIEF.md`: problem, segment, alternatives, differentiation, adversarial discovery, recent community signals, top complaints, and evidence links.
- `FUNNEL_MODEL.md`: traffic, lead, activation, conversion, retention stages, MVP measurement contract, false-positive traction, PMF signals, and bottleneck.
- `GO_TO_MARKET.md`: launch goal, channel, offer, activation path, MVP measurement contract, funnel summary, feedback loop, and success metrics.
- `LAUNCH_MATURITY_GATE.md`: optional founder bottleneck audit and ops automation/delegation map for launch-stage products.
- `SCALE_MOAT_REGISTER.md`: optional domain knowledge, edge-case, data flywheel, workflow integration, switching-cost, and defensibility register.
- `FEEDBACK_LOG.md`: feedback sources, evidence, patterns, and triggered decisions.
- `ITERATION_REVIEW.md`: inputs, changes, outcome, and keep/revert/iterate/pivot/stop decision.
- `ASSET_REGISTER.md`: reusable product, process, template, offer, or automation assets.
- `CONTENT_BACKLOG.md`: evidence-backed content candidates with audience and offer tie-in.
- `PRODUCT_BLUEPRINT.md`: product classification, business logic, entities, modules, interfaces, dependencies, infrastructure.
- `PROJECT_ARCHITECTURE.md`: stack, data model, APIs, auth, integrations, deployment.
- `THREAT_MODEL.md`: assets, actors, trust boundaries, abuse cases, controls.
- `DATA_CLASSIFICATION.md`: data inventory, sensitivity, retention, storage, access.
- `TEST_PLAN.md`: product-type test matrix, critical flows, negative cases, CI.
- `QUALITY_GATES.md`: gate results, evidence, blockers, accepted risk.
- `BUILD_PLAN.md`: module order, dependencies, verification, exit criteria.
- `EXECUTION_GRAPH.md`: nodes, transitions, validation checkpoints, repair paths.
- `IMPLEMENTATION_PLAN.md`: ordered steps, touched files, verification per step.
- `NEXT_STEP.md`: user-facing roadmap, recommended next step, alternatives, and explicit decision needed before implementation.
- `HANDOFF.md`: compact transfer packet for session, role, delegation, AFK, compaction, or recovery handoff.
- `CODEX.md`: project context, decisions, status table, handoff and session-save rules.

## Required Document Shape

`DISCOVERY.md`:

- Problem
- Users
- Alternatives
- Customer discovery plan and interview discipline
- Positioning
- Hypotheses
- MVP scope
- Kill criteria
- Risks

`PRD.md`:

- Goals
- Non-goals
- Personas
- User stories grouped by priority
- Acceptance criteria
- Launch criteria

`PROJECT_ARCHITECTURE.md`:

- Stack and rationale
- Architecture variants considered
- ADR for the selected architecture
- Adversarial challenges and resolutions
- Data model or no-DB rationale
- API, pages, commands, or handlers
- Auth and permissions
- Integrations
- Deployment topology
- Risks and tradeoffs

`PRODUCT_BLUEPRINT.md`:

- Product classification output
- Business logic
- Users and roles
- Core entities
- Modules selected from the template library
- Interfaces
- Infrastructure
- Risks and assumptions

`BUILD_PLAN.md`:

- Ordered module build steps
- Module dependencies
- Files likely touched
- Verification per module
- Exit criteria

`EXECUTION_GRAPH.md`:

- Current state and next state
- Nodes
- Transitions
- Validation checkpoints
- Repair paths for failed gates

`IMPLEMENTATION_PLAN.md`:

- 5 to 12 ordered steps
- Files likely touched
- Tests or verification command for each step
- Exit criteria for each step

`NEXT_STEP.md`:

- Current product-owner-readable state
- Visible roadmap
- One recommended next step
- Alternatives
- Decision needed: confirm, change, or stop

`CODEX.md`:

- Project summary
- Current decisions
- Development commands
- Status table
- Rule: use `/handoff` before session or role transfer; save context with `/session-save` after significant work

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, visible roadmap, recommended next step, alternatives, and required user decision are stated.

## Rules

- Do not scaffold or write application code.
- Ask before overwriting existing documents.
- Keep names and entities consistent across all documents.
- Treat `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, and `EXECUTION_GRAPH.md` as the Product Compiler outputs.
- Treat `IDEA_SCORECARD.md` and `VALIDATION_PLAN.md` as gates before broad build scope.
- Treat evidence quality and adversarial discovery as blockers for broad build scope when market risk is material.
- Treat `/market-scan` output as evidence for strategy artifacts, not as permission to skip validation experiments.
- Do not move to implementation until the execution graph can reach `PLAN_READY`.
- Do not move to implementation until `NEXT_STEP.md` has a user-approved or user-changed next step.
- Translate PFO internal states into plain product-owner language in user-facing summaries.
- Stop with `BLOCKED` if the user refuses to answer a question that determines architecture or data safety.
- If `/review` returns `BLOCKED`, offer doc fixes before implementation.

## Done Criteria

- All required documents exist.
- `/review` status is `PASSED` or `PASSED_WITH_WARNINGS`.
- Idea gate, validation plan, funnel, feedback, and asset/content assumptions are explicit when applicable.
- Evidence quality, contradicting evidence, customer discovery discipline, and false-positive traction are explicit when market risk is material.
- Launch maturity and scale moat artifacts are present only when the stage requires them.
- Fresh market or community signal gaps are explicit when they affect product or launch risk.
- Product type, template modules, architecture pattern, and execution graph are explicit.
- Remaining assumptions are explicitly listed.
- The user has a clear visible roadmap and a decision point: approve the recommended step, change it, or stop for review.
