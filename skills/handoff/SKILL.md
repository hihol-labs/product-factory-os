---
name: handoff
description: Write a compact PFO handoff artifact for session, role, compaction, AFK, delegation, or recovery transfer.
argument-hint: project path plus handoff reason
license: MIT
metadata:
  category: workflow
  tags: [memory, context, delegation, recovery]
  effort: low
  side_effect: memory-write
  explicit_invocation: false
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

`HANDOFF.md` should remain regular Markdown while also being Obsidian-compatible: frontmatter for project/stage/roles, wikilinks to PFO artifacts, and callouts for first action, blockers, and risks.

## Include

- From role and target role
- Reason for transfer
- Current state, node, unit, and next action
- Done condition for the receiving agent
- Final decisions only
- Required inputs
- Context budget: read-first files, do-not-reload material, and large output paths
- Allowed write areas and forbidden changes
- Verification commands
- Blockers and risks
- Exact first action for the receiving session

## Obsidian Layer

- Link core artifacts with wikilinks: `[[STATE]]`, `[[BUILD_PLAN]]`, `[[EXECUTION_GRAPH]]`, `[[QUALITY_GATES]]`.
- Highlight the first action with `> [!todo]`.
- Highlight risks and blockers with `> [!warning]`.
- After a handoff that should be searchable in a vault, run:

```bash
python3 scripts/pfo.py export <project> --target obsidian
```

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Do not store secrets.
- Keep it concise enough for a fresh session to read first.
- Prefer durable artifact references over chat history.
- Offload long logs or traces to files and include only path plus decision-relevant summary.
- Use `.pfo/UNIT_CONTEXT_MANIFEST.json` as the execution scope when present.
- Use `/session-save` after the milestone is complete; `/handoff` is for transfer before the next actor starts.
