# Agent Harness Engineering

Source: https://addyosmani.com/blog/agent-harness-engineering/

PFO treats an agent as model plus harness. The model supplies reasoning and generation; the harness supplies state, tools, context, permissions, hooks, verification, memory, recovery, and review. Improving PFO means tightening that harness whenever a real failure exposes a missing control.

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

## Operating Standard

- Derive harness controls from desired behaviour or observed failure.
- Prefer deterministic feedback for repeatable failures.
- Reserve inferential review for semantics, ambiguity, product judgment, and adversarial critique.
- Keep `AGENTS.md`, `CODEX.md`, skill prompts, and tool registries concise; each line competes for attention.
- Treat PFO harness assumptions as living system design. Promote what works, prune what no longer carries weight.
