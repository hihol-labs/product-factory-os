---
name: handoff
description: Write a compact PFO handoff artifact for session, role, compaction, AFK, delegation, or recovery transfer.
argument-hint: project path plus handoff reason
license: MIT
metadata:
  category: workflow
  tags: [memory, context, delegation, recovery]
---

# Handoff

Transfer actionable context from one PFO agent session to another when there is no return path.

Use `/handoff` when:

- A planning session hands work to implementation.
- A long session is about to compact or restart.
- Work is delegated to another agent, role, or AFK run.
- Recovery work starts after a failed or ambiguous gate.
- Release, PR, CI, or external-tool work needs a bounded context packet.

## Output

Write or refresh:

```text
HANDOFF.md
.codex-memory/STATE.json
```

## Include

- From role and target role
- Reason for transfer
- Current state, node, unit, and next action
- Final decisions only
- Required inputs
- Allowed write areas and forbidden changes
- Verification commands
- Blockers and risks
- Exact first action for the receiving session

## Rules

- Do not store secrets.
- Keep it concise enough for a fresh session to read first.
- Prefer durable artifact references over chat history.
- Use `.pfo/UNIT_CONTEXT_MANIFEST.json` as the execution scope when present.
- Use `/session-save` after the milestone is complete; `/handoff` is for transfer before the next actor starts.
