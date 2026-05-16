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

- Capture phase decisions in `PHASE_CONTEXT.md` before detailed planning.
- Create `.pfo/UNIT_CONTEXT_MANIFEST.json` before autonomous or delegated execution.
- Execute one unit at a time from the manifest, not from accumulated chat context.
- Verification fails closed when evidence is missing or ambiguous.
- Record durable decisions, lessons, patterns, and surprises in `.codex-memory/LEARNINGS.md`.

## Status

| Step | Status | Notes |
|---:|---|---|

## Session Rule

Save context with `/session-save` after significant work or before stopping.
