# Control Harness

Product Factory OS uses a four-quadrant control harness to keep agent work bounded, testable, and reviewable. This implements the agent harness engineering stance described by Addy Osmani: improve the model-plus-harness system by turning observed failures into durable controls.

The model separates controls by timing and evaluator:

| Axis | Meaning | PFO Rule |
|---|---|---|
| Feedforward | Controls that shape work before execution starts. | They must define scope, inputs, allowed writes, examples, architecture, and verification expectations before implementation. |
| Feedback | Controls that judge work after output exists. | They must produce evidence, a gate status, or a repair path. Missing evidence fails closed. |
| Computational | Deterministic or scriptable controls. | They are preferred for blocking gates because they are cheap, repeatable, and auditable. |
| Inferential | LLM or human judgment controls. | They are used for semantic review, ambiguity, product judgment, security reasoning, UX judgment, and adversarial critique. |

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
| adversarial-planning | Plan, architecture, and decision stress testing | Feedforward | Inferential | `skills/grill-me/SKILL.md`, `skills/advisor/SKILL.md`, `agents/architect.md` |
| unit-context | Task-scoped execution inputs and write scope | Feedforward | Computational | `docs/templates/pfo/EXECUTION_POLICY.json`, `docs/templates/pfo/PERMISSION_MATRIX.json`, `docs/templates/UNIT_CONTEXT_MANIFEST.json` |
| verification-contract | Expected checks before execution starts | Feedforward | Computational | `docs/templates/pfo/VERIFICATION_CONTRACT.json`, `docs/templates/TEST_PLAN.md`, `docs/templates/QUALITY_GATES.md` |
| session-security-guard | Pre-tool safety boundary for secrets and destructive operations | Feedforward | Computational | `hooks/security-guard.py`, `hooks/hooks.json`, `docs/templates/pfo/EXECUTION_POLICY.json` |
| context-economy | Progressive context loading, output offloading, and reset handoff policy | Feedforward | Computational | `docs/AGENT_HARNESS_ENGINEERING.md`, `skills/handoff/SKILL.md`, `docs/templates/HANDOFF.md` |
| tool-surface-discipline | Minimal trusted tool and connector menu with side effects and explicit degraded modes | Feedforward | Computational | `docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json`, `integrations/tool-capability-registry.json`, `docs/AGENT_HARNESS_ENGINEERING.md` |
| market-validation | Evidence before broad product scope, including evidence quality, customer discovery discipline, adversarial discovery, and MVP measurement | Feedforward | Inferential | `skills/discover/SKILL.md`, `skills/market-scan/SKILL.md`, `docs/templates/IDEA_SCORECARD.md`, `docs/templates/VALIDATION_PLAN.md`, `docs/templates/MARKET_BRIEF.md`, `docs/templates/FUNNEL_MODEL.md`, `docs/templates/GO_TO_MARKET.md` |
| maturity-stage-gates | Optional launch and scale maturity checks | Feedforward | Inferential | `skills/strategy/SKILL.md`, `docs/templates/LAUNCH_MATURITY_GATE.md`, `docs/templates/SCALE_MOAT_REGISTER.md` |
| route-regression | Route, fixture, trigger, and skill drift checks | Feedback | Computational | `scripts/run_fixtures.py`, `scripts/verify_triggers.py`, `scripts/verify_fixture_contracts.py` |
| alias-integrity | Navigation alias target existence | Feedback | Computational | `scripts/pfo_alias_targets.py`, `scripts/pfo_contract_gate.py`, `docs/templates/existing/MASTER_CONTEXT.md` |
| methodology-ci | Repository-level deterministic validation | Feedback | Computational | `.github/workflows/validate.yml`, `scripts/validate_structure.py`, `scripts/validate_runtime.py`, `scripts/meta_review.py` |
| project-ci | Generated-project validation | Feedback | Computational | `templates/generated-ci/validate.yml`, `scripts/validate_project.py`, `scripts/pfo_contract_gate.py` |
| engineering-discipline | TDD, root-cause, two-stage review, branch finish | Feedback | Computational | `scripts/validate_plan_quality.py`, `docs/templates/ROOT_CAUSE.md`, `docs/templates/BRANCH_FINISH.md` |
| browser-smoke | Browser-facing critical-flow verification | Feedback | Computational | `skills/browser-check/SKILL.md`, `skills/browser-check/playwright/run.js`, `docs/templates/TEST_PLAN.md` |
| review-agent | Spec and code quality review | Feedback | Inferential | `skills/review/SKILL.md`, `agents/reviewer.md`, `docs/rubrics/review.md` |
| security-review-agent | Security reasoning and audit findings | Feedback | Inferential | `skills/security-audit/SKILL.md`, `agents/security-reviewer.md`, `docs/rubrics/security.md` |
| ux-review-agent | UX, visual, accessibility, and interaction judgment | Feedback | Inferential | `agents/ux-reviewer.md`, `skills/browser-check/SKILL.md`, `docs/templates/QUALITY_GATES.md` |
| human-approval | Irreversible or production-impacting boundary approval | Feedback | Inferential | `docs/METHODOLOGY.md`, `docs/templates/pfo/PERMISSION_MATRIX.md`, `skills/deploy/SKILL.md` |
| learning-promotion | Turn repeated failures into stronger controls | Feedback | Computational | `docs/templates/pfo/LEARNING_PROMOTION_GATE.md`, `scripts/pfo_learn.py`, `memory/LEARNING_REGISTRY.json` |

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
- Do not add a new skill, hook, gate, or CI command without assigning it to a quadrant.
- Do not add a new rule unless it traces to observed failure evidence or a hard external constraint.
- Keep project `AGENTS.md`, skill prompts, and tool registries concise; remove controls that no longer encode a real model or workflow limitation.
- Every blocking feedback control must return evidence and one of `BLOCKED`, `PASSED_WITH_WARNINGS`, or `PASSED`, or a script exit code.
- Feedforward controls must name the expected feedback controls before implementation starts.
- Repeated inferential findings should be promoted into scripts, tests, schemas, templates, or hooks through the learning promotion gate.

## Lifecycle Mapping

| PFO Stage | Required Feedforward Controls | Required Feedback Controls |
|---|---|---|
| Route request | `intent-routing`, `product-classification` | `route-regression` |
| Plan product | `planning-documents`, `market-validation`, `adversarial-planning` | `review-agent` |
| Dispatch unit | `unit-context`, `verification-contract` | `engineering-discipline` |
| Build behavior | `verification-contract`, `docs/templates/TEST_PLAN.md` | tests, `engineering-discipline`, `project-ci`, `alias-integrity` |
| Review work | rubrics and quality gate expectations | `review-agent`, `security-review-agent`, `ux-review-agent` when applicable |
| Deploy readiness | permission matrix, deployment target, rollback expectations | `methodology-ci`, `project-ci`, security/deps/hardening/browser gates |
| Learn and improve | learning promotion policy | `learning-promotion`, fixture and validator updates |

## Addition Checklist

When adding or changing a PFO control:

1. Classify it by timing: feedforward or feedback.
2. Classify it by evaluator: computational or inferential.
3. Name the behaviour it exists to produce or the failure it prevents.
4. Name the artifact that stores the rule.
5. Name the command, reviewer, or evidence that proves it ran.
6. Define whether it blocks, warns, or only advises.
7. Add or update CI/validator coverage when the control is deterministic.
8. Update `docs/CONTROL_HARNESS.md` and run `python3 scripts/validate_control_harness.py`.
