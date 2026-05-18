---
name: tool-sync
description: Synchronize Product Factory OS state with external tools and OpenAI/Codex connectors such as Linear, Notion, Google Drive Docs/Sheets/Slides, GitHub export payloads, and local Obsidian exports. Use when roadmaps, PRDs, execution graphs, decisions, blockers, or status reports need to be mirrored outside the repository or into a local knowledge graph.
argument-hint: target tool, project path, roadmap, PRD, execution graph, or status sync
license: MIT
metadata:
  category: integration
  tags: [linear, notion, google-drive, obsidian, sync, connectors]
  effort: medium
  side_effect: external-write
  explicit_invocation: true
---

# Tool Sync

Use this skill when PFO artifacts need to be synchronized with an external planning or documentation tool.

## Targets

- GitHub: issues, labels, milestones, PR context.
- Linear: projects, issues, workflow states, blockers.
- Notion: project pages, task databases, decision logs.
- Google Drive: Docs, Sheets, Slides, project briefs, stakeholder summaries.
- Obsidian: local vault-ready Markdown notes, wikilinks, callouts, and project knowledge graph.

## Procedure

1. Identify the source artifacts: `.codex-memory/STATE.json`, `.codex-memory/MEMORY.md`, `.codex-memory/session_YYYY-MM-DD.md`, `HANDOFF.md`, `PFO_REPORT.md`, `EXECUTION_GRAPH.md`, `QUALITY_GATES.md`, `PRD.md`, or planning docs.
2. Identify the target connector and whether live write access is available.
3. Prefer connector-native reads before writes so existing external state is not overwritten blindly.
4. When live sync is unavailable or not approved, export payloads with:

```bash
python3 scripts/pfo.py export <project> --target github
python3 scripts/pfo.py export <project> --target linear
python3 scripts/pfo.py export <project> --target notion
python3 scripts/pfo.py export <project> --target google-drive
python3 scripts/pfo.py export <project> --target obsidian
```

5. Record sync results in `.codex-memory/STATE.json` or the final report when the sync affects project status.

## Output

Return:

```text
SYNC TARGET:
SOURCE ARTIFACTS:
MODE: live | export-only | read-only
CHANGES:
UNSYNCED ITEMS:
NEXT ACTION:
```

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Ask before modifying live external systems unless the user explicitly requested the change.
- Preserve external user edits; reconcile rather than overwrite.
- Do not sync secrets, private customer data, or credentials into planning tools.
- Keep exported payloads under `.pfo-integrations/`.
- Treat `.pfo-integrations/obsidian/` as generated output; canonical edits belong in source PFO docs.
- Treat `EXECUTION_GRAPH.md` as the canonical execution source unless the user explicitly makes an external tool authoritative.
