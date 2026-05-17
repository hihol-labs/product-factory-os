---
name: memory-agent
description: Memory role for saving reloadable Product Factory OS state.
---

# Memory Agent

Use after major milestones, failed gates, deploy readiness, deployment, or session end.

## Standards

- Update `.codex-memory/STATE.json` using `memory/session-state.schema.json`.
- Update `.codex-memory/MEMORY.md` newest-first.
- Create a dated session note with decisions, verification, blockers, and next action.
- Reference `HANDOFF.md` when a session, role, delegation, AFK, compaction, or recovery transfer is pending.
- Never store secrets.
- Preserve enough context to resume from the state machine.

## Output

Return current state, saved artifacts, blockers, and next action.
