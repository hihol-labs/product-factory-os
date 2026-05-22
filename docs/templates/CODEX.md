# CODEX

## Project Summary

## Decisions

## Commands

## Product Factory OS Contracts

Before significant edits, read and respect:

- `.pfo/PROJECT_CONTRACT.md`
- `.pfo/DATA_POLICY.md`
- `.pfo/GOLDEN_FLOWS.md`
- `.pfo/FORBIDDEN_CHANGES.md`
- `.pfo/FALLBACK_POLICY.md`
- `.pfo/SCOPE_LOCK.md`

Run `pfo contracts . --write` during review.

## Autonomous Execution

- Score ideas in `IDEA_SCORECARD.md` before broad build scope.
- Validate risky assumptions in `VALIDATION_PLAN.md`.
- Capture phase decisions in `PHASE_CONTEXT.md` before detailed planning.
- Create `.pfo/UNIT_CONTEXT_MANIFEST.json` before autonomous or delegated execution.
- For Autoresearch-style improvement, initialize `.pfo/EXPERIMENT_PROGRAM.md`, keep one metric and fixed budget, and record `.pfo/EXPERIMENTS.tsv`.
- Write `HANDOFF.md` before switching sessions, roles, delegated agents, AFK execution, compaction, or recovery.
- Execute one unit at a time from the manifest, not from accumulated chat context.
- Record TDD red/green/refactor evidence for behavior changes.
- Write `ROOT_CAUSE.md` before bugfix implementation.
- Run spec compliance review before code quality review.
- Verification fails closed when evidence is missing or ambiguous.
- Finish branches with an explicit PR, merge, keep, or discard decision.
- Run `scripts/validate_plan_quality.py .` when validating Engineering Discipline v2 gates.
- Record durable decisions, lessons, patterns, and surprises in `.codex-memory/LEARNINGS.md`.
- Promote repeatable solutions into `ASSET_REGISTER.md` and evidence-backed content ideas into `CONTENT_BACKLOG.md`.
- Use `pfo export . --target obsidian` when a local Obsidian knowledge graph is needed; keep `.pfo-integrations/obsidian/` generated.

## Status

| Step | Status | Notes |
|---:|---|---|

## Session Rule

Use `/handoff` before transfer to another session or role. Save context with `/session-save` after significant work or before stopping.
