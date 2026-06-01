# Agent Harness Engineering

Sources:

- https://addyosmani.com/blog/agent-harness-engineering/
- https://martinfowler.com/articles/harness-engineering.html

PFO treats an agent as model plus harness. The model supplies reasoning and generation; the harness supplies state, tools, context, permissions, hooks, verification, memory, recovery, and review. Improving PFO means tightening that harness whenever a real failure exposes a missing control.

In the Martin Fowler article's coding-agent frame, PFO is the user's outer harness around a coding agent. It should make correct output more likely before work starts and make the agent self-correct before human review.

## Outer Harness Goals

PFO harness changes should serve at least one of these goals:

| Goal | PFO Mechanism |
|---|---|
| Improve first-pass correctness | guides: route selection, specs, templates, architecture docs, skill instructions, examples |
| Self-correct before human review | sensors: tests, validators, hooks, CI, browser checks, review agents, contract gates |
| Reduce review toil | cheap sensors run before expensive review; review sees evidence and residual risk, not raw uncertainty |
| Spend fewer tokens | progressive context loading, small unit manifests, short failure messages with repair instructions |

## Behaviour Backwards

Start with the behaviour PFO wants, then choose the smallest harness component that makes it more likely:

| Wanted behaviour | PFO harness component |
|---|---|
| Work survives long sessions | filesystem state, Git, `.codex-memory/STATE.json`, `HANDOFF.md` |
| Execution stays inside scope | `.pfo/SCOPE_LOCK.md`, `UNIT_CONTEXT_MANIFEST.json`, permission matrix |
| Tools are chosen safely | `.pfo/TOOL_CAPABILITY_REGISTRY.json`, explicit side effects and approvals |
| Broken output is repaired before finish | verification contracts, hooks, validators, CI |
| Semantic risk is caught | spec review, code review, security review, UX review |
| Repeated mistakes disappear | learning promotion gate, tests, hooks, validators, templates |

If a harness element cannot name the behaviour it exists to produce or prevent, it is a removal candidate.

## Guides And Sensors

Use Fowler's vocabulary when designing new controls:

- Guides are feedforward controls. They steer the agent before it acts: `AGENTS.md`, skills, reference docs, templates, codemods, architecture constraints, and tool registries.
- Sensors are feedback controls. They observe output after action: tests, linters, logs, static analysis, browser checks, code review, security review, and human review.
- Sensors should return output that is easy for an agent to repair from: exact file, exact rule, observed evidence, expected condition, and next command.
- A guide without a sensor can become wishful thinking. A sensor without a guide can create repeated repair churn. Prefer paired guide/sensor design.

## Ratchet

Every repeated agent mistake is a candidate system change, not just a reminder. PFO uses this path:

```text
failure evidence
  -> structured learning
  -> candidate rule
  -> target artifact
  -> deterministic or reviewed check
  -> promoted harness change
```

Rules are earned. Add a rule when it traces to a real failure or hard external constraint. Remove or simplify a rule when a better model, tool, hook, or validator makes it redundant.

## Quality Left

Distribute sensors by cost, speed, and criticality:

| Timing | PFO Default |
|---|---|
| Before editing | Load only relevant guides, unit manifest, permission policy, and verification contract. |
| During local work | Run fast computational sensors: targeted tests, validators, lint, schema checks, route checks. |
| Before commit or handoff | Re-run local blockers and two-stage review; record evidence in state or report. |
| CI or release gate | Repeat local sensors and add broader expensive sensors: fixture suites, production readiness, dependency/security checks. |
| Continuous health | Run drift, stale-state, dependency, benchmark, and runtime health sensors outside a single change when available. |

Fast computational sensors should move as far left as practical. Expensive or inferential sensors should be reserved for broader scope, higher risk, or release gates.

## Regulation Categories

Name what the harness is regulating:

| Category | What PFO Regulates | Typical Guides | Typical Sensors |
|---|---|---|---|
| Maintainability | simplicity, duplication, style, test quality, dependency hygiene | coding rules, templates, refactor guidance | linters, tests, plan-quality checks, review |
| Architecture fitness | module boundaries, performance, observability, data flow, deployment shape | architecture docs, stack policy, topology templates | architecture review, structural tests, benchmarks, contract gates |
| Behaviour | functional correctness and user-visible workflows | PRD, golden flows, acceptance criteria, fixtures | tests, browser checks, approved fixtures, manual review |

Behaviour is the hardest category to fully sensor. Do not treat AI-generated tests as enough when the specification, fixtures, golden flows, or manual checks are weak.

## Context Economy

Context is scarce. PFO keeps long work coherent by moving durable state out of chat and loading only what the active route needs.

- Use progressive disclosure: load the skill, registry, template, or connector instructions only when the route requires them.
- Offload long logs and tool output to files under `reports/`, `plans/`, or `.codex-memory/`; keep the active context to the decision, head/tail signal, and file path.
- Write `HANDOFF.md` before compaction, role transfer, AFK execution, delegation, or recovery; the receiving session reads artifacts, not chat history.
- Use `session-diagnostics.py` and `.codex-memory/STATE.json` as the current truth for stage, blockers, and next action.

## Tool Surface Discipline

Tool descriptions and MCP metadata are prompt input. PFO treats the tool menu as trusted configuration, not neutral plumbing.

- Prefer a small set of non-overlapping tools over broad menus with similar capabilities.
- Every tool entry must declare read/write/execute capability, side effects, auth, external data risk, fallback mode, and approval boundaries.
- Do not use a connector or MCP server unless it is declared in the project tool registry or explicitly approved for the active task.
- If a tool is unavailable, record the fallback or blocker instead of silently substituting behaviour.

## Harnessability

A project is more harnessable when agents can cheaply see structure and sensors can cheaply detect drift. PFO should prefer:

- clear module boundaries and stable folder conventions
- typed interfaces, schemas, contracts, and explicit data policies
- small generated starters with known commands
- golden flows and fixtures that represent user-visible behaviour
- logs, health checks, and benchmark hooks that make runtime problems observable

For legacy projects, first improve harnessability around the current task rather than demanding a whole-repo rewrite.

## Harness Templates

PFO product templates should behave like harness templates: topology plus guides plus sensors. Each product topology should declare:

- structure and stack defaults
- maintainability, architecture, and behaviour regulation targets
- fast local sensors
- broader pipeline sensors
- continuous drift or health sensors where meaningful

This reduces the agent's solution space and makes repeatable generation cheaper to verify.

## Long-Horizon Loop

PFO long-running work is split into plan, implement, validate, and review:

1. Build a unit manifest and PIV plan before editing.
2. Implement one small unit at a time.
3. Run narrow validation immediately, then the full verification contract.
4. Separate spec compliance review from code quality review.
5. Save state and, when context is about to reset, write a compact handoff.

Success should be quiet and failures should be useful: passing hooks do not add noise, while failing hooks surface exact evidence and recovery actions.

## Evaluator Split

Self-review is useful but optimistic. PFO separates generation from evaluation where risk justifies it:

- Builder follows the unit manifest and verification contract.
- Reviewer checks spec compliance first.
- Tester or validator checks executable evidence.
- Security, UX, architecture, or human review blocks only with evidence or accepted-risk notes.

## Human Steering

Humans remain part of the harness. PFO should direct human attention to high-leverage decisions:

- unclear intent, product tradeoffs, and accepted risk
- load-bearing conventions that are hard to infer from code
- weak behaviour specs or missing golden flows
- conflicts between sensors, or sensors that never fire despite known risk
- deciding when a repeated failure deserves a new durable control

## Operating Standard

- Derive harness controls from desired behaviour or observed failure.
- Prefer deterministic feedback for repeatable failures.
- Reserve inferential review for semantics, ambiguity, product judgment, and adversarial critique.
- Pair guides with sensors where possible.
- Move fast computational sensors left; keep expensive sensors for broader or higher-risk gates.
- Classify controls by regulation category: maintainability, architecture fitness, or behaviour.
- Improve harnessability through structure, contracts, fixtures, observability, and starter topology.
- Keep `AGENTS.md`, `CODEX.md`, skill prompts, and tool registries concise; each line competes for attention.
- Treat PFO harness assumptions as living system design. Promote what works, prune what no longer carries weight.
