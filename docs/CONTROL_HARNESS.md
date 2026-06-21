# Control Harness

Product Factory OS uses a four-quadrant control harness to keep agent work bounded, testable, and reviewable. This implements the agent harness engineering stance described by Addy Osmani and the coding-agent user harness model described on martinfowler.com: improve the model-plus-harness system by turning observed failures into durable controls, and make correct output more likely before human review.

The model separates controls by timing and evaluator:

| Axis | Meaning | PFO Rule |
|---|---|---|
| Feedforward | Controls that shape work before execution starts. | They must define scope, inputs, allowed writes, examples, architecture, and verification expectations before implementation. |
| Feedback | Controls that judge work after output exists. | They must produce evidence, a gate status, or a repair path. Missing evidence fails closed. |
| Computational | Deterministic or scriptable controls. | They are preferred for blocking gates because they are cheap, repeatable, and auditable. |
| Inferential | LLM or human judgment controls. | They are used for semantic review, ambiguity, product judgment, security reasoning, UX judgment, and adversarial critique. |

In Fowler's terminology, feedforward controls are guides and feedback controls are sensors. PFO should pair guides with sensors whenever practical, and sensor output should be written so an agent can self-correct from it.

## Quadrant Matrix

| Quadrant | Primary Use | Examples | Blocking Rule |
|---|---|---|---|
| Computational feedforward | Define machine-checkable boundaries before work starts. | Schemas, templates, execution policies, permission matrices, verification contracts, route fixtures. | Missing required contracts blocks autonomous or delegated execution. |
| Computational feedback | Check output with repeatable commands. | Tests, CI, validators, contract gates, schema checks, build checks, route snapshots, Playwright smoke checks. | Failing commands block the next lifecycle step. |
| Inferential feedforward | Improve plans before code exists. | Blueprint reasoning, architecture debate, market scan synthesis, advisor/grill-me stress tests, role prompts. | Findings become scope, plan, risk, or verification requirements. |
| Inferential feedback | Judge meaning and risk after output exists. | Reviewer, security-reviewer, UX-reviewer, tester, human review. | Critical findings block until fixed, accepted, or downgraded with evidence. |

## Control Inventory

Every durable PFO control should be classified by quadrant. A single mechanism may appear in more than one quadrant only when it has separate before/after responsibilities.

| ID | Control | Timing | Evaluator | Primary Artifacts |
|---|---|---|---|---|
| intent-routing | Natural-language route shaping | Feedforward | Computational | `hooks/route-reminder.py`, `docs/TRIGGERS.md`, `tests/snapshots/route-snapshots.json` |
| product-classification | Product type, risk, stack, and module selection | Feedforward | Computational | `routing/product-classifier.json`, `templates/product-templates.json`, `core/product-compiler.md` |
| planning-documents | Product, PRD, architecture, build, and execution docs | Feedforward | Inferential | `docs/templates/PRODUCT_BLUEPRINT.md`, `docs/templates/PROJECT_ARCHITECTURE.md`, `docs/templates/BUILD_PLAN.md`, `skills/blueprint/SKILL.md` |
| ideation-routing | Structured option generation before discovery or planning | Feedforward | Inferential | `skills/brainstorm/SKILL.md`, `docs/TRIGGERS.md`, `tests/fixtures/brainstorm-product/idea.md` |
| adversarial-planning | Plan, architecture, and decision stress testing | Feedforward | Inferential | `skills/grill-me/SKILL.md`, `skills/advisor/SKILL.md`, `agents/architect.md` |
| unit-context | Task-scoped execution inputs and write scope | Feedforward | Computational | `docs/templates/pfo/EXECUTION_POLICY.json`, `docs/templates/pfo/PERMISSION_MATRIX.json`, `docs/templates/UNIT_CONTEXT_MANIFEST.json` |
| verification-contract | Expected checks before execution starts | Feedforward | Computational | `docs/templates/pfo/VERIFICATION_CONTRACT.json`, `docs/templates/TEST_PLAN.md`, `docs/templates/QUALITY_GATES.md` |
| acceptance-contract | Original request criteria and evidence closure before a unit can pass | Feedback | Computational | `scripts/validate_acceptance_contract.py`, `docs/templates/pfo/ACCEPTANCE_CONTRACT.json`, `docs/gates/acceptance-contract-gate.md` |
| defensive-layer-diagnostics | Five-layer diagnostic gate for task spec, context, execution environment, verification feedback, and state continuity | Feedback | Computational | `docs/DEFENSIVE_LAYERS.md`, `scripts/validate_defensive_layers.py`, `scripts/production_readiness.py` |
| session-security-guard | Pre-tool safety boundary for secrets and destructive operations | Feedforward | Computational | `hooks/security-guard.py`, `hooks/hooks.json`, `docs/templates/pfo/EXECUTION_POLICY.json` |
| context-economy | Progressive context loading, output offloading, and reset handoff policy | Feedforward | Computational | `docs/AGENT_HARNESS_ENGINEERING.md`, `skills/handoff/SKILL.md`, `docs/templates/HANDOFF.md` |
| context-budget-runtime | Numeric context budget checks for tool/read/log/web output and raw HTTP routing | Feedback | Computational | `hooks/context-budget.py`, `scripts/pfo_context_runtime.py`, `scripts/validate_context_runtime.py` |
| session-memory-search | Searchable event memory and compact resume snapshots for session continuity | Feedback | Computational | `scripts/pfo_context_runtime.py`, `memory/events.schema.json`, `hooks/session-diagnostics.py` |
| token-efficiency | Caveman-style terse communication that preserves exact technical evidence and gate status | Feedforward | Computational | `skills/caveman/SKILL.md`, `docs/CAVEMAN_INTEGRATION.md`, `hooks/route-reminder.py` |
| tool-surface-discipline | Minimal trusted tool and connector menu with side effects and explicit degraded modes | Feedforward | Computational | `docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json`, `integrations/tool-capability-registry.json`, `docs/AGENT_HARNESS_ENGINEERING.md` |
| harness-templates | Product topology templates that bundle structure, guides, sensors, and regulation targets | Feedforward | Computational | `templates/product-templates.json`, `starters/README.md`, `golden-paths/README.md` |
| market-validation | Evidence before broad product scope, including evidence quality, customer discovery discipline, adversarial discovery, and MVP measurement | Feedforward | Inferential | `skills/discover/SKILL.md`, `skills/market-scan/SKILL.md`, `docs/templates/IDEA_SCORECARD.md`, `docs/templates/VALIDATION_PLAN.md`, `docs/templates/MARKET_BRIEF.md`, `docs/templates/FUNNEL_MODEL.md`, `docs/templates/GO_TO_MARKET.md` |
| seo-growth | Search-intent, technical SEO, content, and organic acquisition shaping before broad growth work | Feedforward | Inferential | `skills/seo/SKILL.md`, `docs/templates/SEO_GROWTH_GUARANTEE_GATE.md`, `docs/templates/CONTENT_BACKLOG.md`, `docs/templates/GO_TO_MARKET.md`, `docs/templates/VALIDATION_PLAN.md` |
| maturity-stage-gates | Optional launch and scale maturity checks | Feedforward | Inferential | `skills/strategy/SKILL.md`, `docs/templates/LAUNCH_MATURITY_GATE.md`, `docs/templates/SCALE_MOAT_REGISTER.md` |
| harnessability-assessment | Project structure and topology judgment that determines how cheaply PFO can guide and sensor work | Feedforward | Inferential | `docs/DESIGN_SPACE.md`, `docs/PFO_ARCHITECTURE.md`, `docs/AGENT_HARNESS_ENGINEERING.md` |
| route-regression | Route, fixture, trigger, and skill drift checks | Feedback | Computational | `scripts/run_fixtures.py`, `scripts/verify_triggers.py`, `scripts/verify_fixture_contracts.py` |
| release-live-eval | Release-critical live headless proof, quality graders, high-risk skill datasets, and adversarial fixtures | Feedback | Computational | `scripts/validate_release_live_headless.py`, `scripts/validate_eval_layer.py`, `tests/eval-datasets/deploy.json` |
| seo-growth-guarantee | Measured SEO growth claim validation with baseline, target, source, attribution window, changes, exclusions, decision, and next iteration | Feedback | Computational | `scripts/validate_seo_growth_gate.py`, `docs/templates/SEO_GROWTH_GUARANTEE_GATE.md`, `docs/templates/VALIDATION_PLAN.md` |
| alias-integrity | Navigation alias target existence | Feedback | Computational | `scripts/pfo_alias_targets.py`, `scripts/pfo_contract_gate.py`, `docs/templates/existing/MASTER_CONTEXT.md` |
| methodology-ci | Repository-level deterministic validation | Feedback | Computational | `.github/workflows/validate.yml`, `scripts/validate_structure.py`, `scripts/validate_runtime.py`, `scripts/meta_review.py` |
| quality-left-scheduling | Sensor placement by cost, speed, and criticality before commit, in CI, and at release gates | Feedback | Computational | `hooks/review-before-commit.py`, `.github/workflows/validate.yml`, `scripts/production_readiness.py` |
| continuous-health-sensors | Drift, benchmark, state, and runtime-health checks outside one change lifecycle | Feedback | Computational | `scripts/production_readiness.py`, `scripts/pfo_metrics.py`, `scripts/validate_runtime.py` |
| project-ci | Generated-project validation | Feedback | Computational | `templates/generated-ci/validate.yml`, `scripts/validate_project.py`, `scripts/pfo_contract_gate.py` |
| engineering-discipline | TDD, root-cause, two-stage review, branch finish | Feedback | Computational | `scripts/validate_plan_quality.py`, `docs/templates/ROOT_CAUSE.md`, `docs/templates/BRANCH_FINISH.md` |
| browser-smoke | Browser-facing critical-flow verification | Feedback | Computational | `skills/browser-check/SKILL.md`, `skills/browser-check/playwright/run.js`, `docs/templates/TEST_PLAN.md` |
| review-agent | Spec and code quality review | Feedback | Inferential | `skills/review/SKILL.md`, `agents/reviewer.md`, `docs/rubrics/review.md` |
| security-review-agent | Security reasoning and audit findings | Feedback | Inferential | `skills/security-audit/SKILL.md`, `agents/security-reviewer.md`, `docs/rubrics/security.md` |
| security-evidence-gate | Security report shape, coverage artifacts, and `security_change` evidence validation | Feedback | Computational | `scripts/validate_security_report.py`, `docs/templates/SECURITY_AUDIT_REPORT.md`, `docs/gates/security-review-evidence.md` |
| ux-review-agent | UX, visual, accessibility, and interaction judgment | Feedback | Inferential | `agents/ux-reviewer.md`, `skills/browser-check/SKILL.md`, `docs/templates/QUALITY_GATES.md` |
| human-approval | Irreversible or production-impacting boundary approval | Feedback | Inferential | `docs/METHODOLOGY.md`, `docs/templates/pfo/PERMISSION_MATRIX.md`, `skills/deploy/SKILL.md` |
| human-steering | Human attention routed to unclear intent, accepted risk, load-bearing convention, and harness gaps | Feedback | Inferential | `docs/METHODOLOGY.md`, `.codex-memory/STATE.json`, `NEXT_STEP.md` |
| learning-promotion | Turn repeated failures into stronger controls | Feedback | Computational | `docs/templates/pfo/LEARNING_PROMOTION_GATE.md`, `scripts/pfo_learn.py`, `memory/LEARNING_REGISTRY.json` |
| platform-readiness | Measure whether a project can support autonomous PFO work before raising autonomy | Feedback | Computational | `pfo readiness`, `PFO_READINESS_REPORT.md`, `.codex-memory/STATE.json` |
| readiness-remediation | Convert readiness gaps into deterministic local artifact repair | Feedback | Computational | `pfo readiness-fix`, `.codex-memory/context-index.json`, `.codex-memory/resume-snapshot.md`, `.codex-memory/LEARNING_PROPOSALS.json` |
| autonomy-policy | Explain and check risk-tier permissions before headless or delegated work | Feedforward | Computational | `pfo policy`, `pfo autonomy`, `.pfo/PERMISSION_MATRIX.json`, `.pfo/EXECUTION_POLICY.json` |
| agent-spec-runtime | Declare runnable PFO roles with harness, tools, policies, and sandbox boundaries | Feedforward | Computational | `docs/templates/PFO_AGENT_SPEC.yaml`, `agents/orchestrator.yaml`, `scripts/validate_omnigent_runtime.py` |
| policy-verdict-runtime | Evaluate runtime events into `ALLOW`, `DENY`, or `ASK` before or after tool activity | Feedback | Computational | `scripts/pfo.py`, `docs/templates/pfo/PERMISSION_MATRIX.json`, `docs/PFO_OMNIGENT_RUNTIME.md` |
| runner-server-separation | Separate local runner execution from coordination server/dashboard state | Feedforward | Computational | `scripts/pfo.py`, `.pfo/runner/runner-host.json`, `.pfo/server/control-plane.json` |
| dispatch-runtime | Create bounded sub-agent dispatch envelopes with purpose, harness, model, inbox, and worktree metadata | Feedforward | Computational | `scripts/pfo.py`, `docs/PFO_OMNIGENT_RUNTIME.md`, `.pfo/UNIT_CONTEXT_MANIFEST.json` |
| cross-harness-review | Require an independent different-harness reviewer for high-risk diffs when available | Feedback | Inferential | `scripts/pfo.py`, `agents/reviewer.yaml`, `docs/PFO_OMNIGENT_RUNTIME.md` |
| cost-risk-routing | Route model tier and autonomy from risk score, cost estimate, and triviality before spending budget | Feedforward | Computational | `scripts/pfo.py`, `docs/templates/pfo/PERMISSION_MATRIX.json`, `docs/PFO_OMNIGENT_RUNTIME.md` |
| live-session-observability | Expose live gates, artifacts, policy, dispatch, review, telemetry, and next action for dashboards or team supervision | Feedback | Computational | `scripts/pfo.py`, `dashboard/index.html`, `docs/PFO_OMNIGENT_RUNTIME.md` |
| forkable-session-context | Export/import compact session packets for attach, fork, handoff, and recovery workflows | Feedforward | Computational | `scripts/pfo.py`, `docs/templates/HANDOFF.md`, `docs/PFO_OMNIGENT_RUNTIME.md` |
| sandbox-spec-runtime | Keep filesystem, network, and environment boundaries in agent and unit specs before execution | Feedforward | Computational | `docs/templates/PFO_AGENT_SPEC.yaml`, `docs/templates/UNIT_CONTEXT_MANIFEST.json`, `docs/templates/pfo/UNIT_CONTEXT_MANIFEST.json` |
| headless-exec-envelope | Run deterministic PFO routes as machine-readable one-shot automation | Feedforward | Computational | `pfo exec`, route profile, JSON result envelope |
| mission-control | Plan and validate milestone-based agent work without relying on chat history | Feedforward | Computational | `pfo mission`, `.pfo/mission.json`, `PFO_MISSION.md` |
| project-wiki | Keep navigable architecture, module, command, gate, and state context close to the repo | Feedforward | Computational | `pfo wiki`, `.pfo/wiki/index.md` |
| diff-scoped-qa | Test only relevant app/project surfaces and record evidence after changes | Feedback | Computational | `pfo qa`, `.pfo/qa/config.yaml`, `.pfo/qa/PFO_QA_REPORT.md` |
| telemetry-export | Export local event, artifact, gate, and verification metrics for observability | Feedback | Computational | `pfo telemetry`, `.pfo/telemetry/pfo-telemetry.jsonl`, `pfo metrics` |

Platform surface canonical artifacts: `scripts/pfo.py`, `scripts/pfo_metrics.py`, `routing/route-profiles.json`, `docs/HEADLESS_EXECUTION.md`, `docs/DROID_INSPIRED_RUNTIME.md`, `docs/PFO_OMNIGENT_RUNTIME.md`, `docs/templates/PFO_AGENT_SPEC.yaml`, `agents/orchestrator.yaml`, `PFO_READINESS_REPORT.md`, `PFO_MISSION.md`, `.pfo/mission.json`, `.pfo/dispatch/`, `.pfo/cross-review/`, `.pfo/session/live-status.json`, `.pfo/session/session-export.json`, `.pfo/wiki/index.md`, `.pfo/qa/config.yaml`, `.pfo/qa/PFO_QA_REPORT.md`, `.pfo/telemetry/pfo-telemetry.jsonl`, `.codex-memory/STATE.json`, `.codex-memory/context-index.json`, `.codex-memory/resume-snapshot.md`, `.codex-memory/LEARNING_PROPOSALS.json`, `docs/templates/pfo/PERMISSION_MATRIX.json`, and `docs/templates/pfo/EXECUTION_POLICY.json`.

## Precedence

1. Computational feedback blockers win first. A failing test, schema check, CI job, contract gate, or permission gate cannot be overruled by an LLM review.
2. Computational feedforward blockers stop execution before work starts when required contracts, permissions, or verification commands are missing.
3. Inferential feedback can add blockers for semantic issues that scripts cannot see, especially security, UX, architecture, and product-fit risks.
4. Inferential feedforward can create plan requirements, but those requirements should be converted into computational controls when they become repeatable.
5. Human approval is required at irreversible boundaries: production deploy, migration, external writes, secret access, billing changes, or destructive operations.

## Operating Rules

- Prefer computational controls for invariants, schemas, commands, permissions, and known failure modes.
- Use inferential controls for ambiguity, threat reasoning, architecture tradeoffs, product judgment, and UX quality.
- Do not ship a high-risk workflow with only inferential controls when a deterministic check can be added.
- Do not cut a release without command-mode live headless proof for the critical fixture set defined by `scripts/validate_release_live_headless.py`.
- Do not add a new skill, hook, gate, or CI command without assigning it to a quadrant.
- Do not add a guide without naming the sensor that will prove it worked, unless the guide is explicitly advisory.
- Do not add a new rule unless it traces to observed failure evidence or a hard external constraint.
- Keep project `AGENTS.md`, skill prompts, and tool registries concise; remove controls that no longer encode a real model or workflow limitation.
- Every blocking feedback control must return evidence and one of `BLOCKED`, `PASSED_WITH_WARNINGS`, or `PASSED`, or a script exit code.
- Sensor output should be optimized for self-correction: exact failure, expected condition, relevant file or command, and recovery hint.
- Feedforward controls must name the expected feedback controls before implementation starts.
- Repeated inferential findings should be promoted into scripts, tests, schemas, templates, or hooks through the learning promotion gate.
- Runtime-only memory artifacts, such as `.codex-memory/STATE.json`, may be required during local PFO execution but are not required to exist in CI checkout.

## Lifecycle Mapping

| PFO Stage | Required Feedforward Controls | Required Feedback Controls |
|---|---|---|
| Route request | `intent-routing`, `product-classification` | `route-regression` |
| Plan product | `ideation-routing`, `planning-documents`, `market-validation`, `adversarial-planning`, `harnessability-assessment` | `review-agent` |
| Dispatch unit | `unit-context`, `verification-contract`, `harness-templates` when topology is selected | `engineering-discipline` |
| Build behavior | `verification-contract`, `.pfo/ACCEPTANCE_CONTRACT.json`, `docs/templates/TEST_PLAN.md` | tests, `acceptance-contract`, `engineering-discipline`, `project-ci`, `alias-integrity`, `quality-left-scheduling`, `context-budget-runtime` |
| Review work | rubrics and quality gate expectations | `review-agent`, `security-review-agent`, `ux-review-agent` when applicable |
| Deploy readiness | permission matrix, deployment target, rollback expectations | `methodology-ci`, `project-ci`, security/deps/hardening/browser gates |
| Learn and improve | learning promotion policy | `learning-promotion`, `continuous-health-sensors`, `defensive-layer-diagnostics`, fixture and validator updates |
| Operate agent platform | `autonomy-policy`, `mission-control`, `headless-exec-envelope`, `project-wiki` | `platform-readiness`, `readiness-remediation`, `diff-scoped-qa`, `telemetry-export` |
| Supervise live agents | `agent-spec-runtime`, `runner-server-separation`, `dispatch-runtime`, `cost-risk-routing`, `forkable-session-context`, `sandbox-spec-runtime` | `policy-verdict-runtime`, `cross-harness-review`, `live-session-observability`, `telemetry-export` |
| Resume or compact | `context-economy`, `unit-context` | `session-memory-search`, `handoff` |

## Addition Checklist

When adding or changing a PFO control:

1. Classify it by timing: feedforward or feedback.
2. Classify it by evaluator: computational or inferential.
3. Classify what it regulates: maintainability, architecture fitness, or behaviour.
4. Name the behaviour it exists to produce or the failure it prevents.
5. Name the artifact that stores the guide or sensor.
6. Name the command, reviewer, or evidence that proves it ran.
7. Define whether it blocks, warns, or only advises.
8. Place sensors as far left as cost, speed, and criticality allow.
9. Add or update CI/validator coverage when the control is deterministic.
10. Update `docs/CONTROL_HARNESS.md` and run `python3 scripts/validate_control_harness.py`.
