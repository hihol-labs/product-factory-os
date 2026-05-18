---
name: obsidian-export
description: Export Product Factory OS planning docs, handoff, memory, state, decisions, and gates into an Obsidian-compatible local knowledge graph. Use when the user mentions Obsidian, vault, wikilinks, knowledge graph, linked notes, or wants PFO project memory exported for local knowledge work.
argument-hint: project path, Obsidian vault/export request, knowledge graph, linked notes
license: MIT
metadata:
  category: integration
  tags: [obsidian, markdown, knowledge-graph, memory, export]
---

# Obsidian Export

Create an optional Obsidian knowledge/export layer from canonical Product Factory OS artifacts.

## Purpose

PFO source artifacts stay canonical in the project root and `.codex-memory/`. The Obsidian layer is derived, local, and safe to regenerate.

## Source Artifacts

- Planning docs: `DISCOVERY.md`, `PRD.md`, `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md`, `QUALITY_GATES.md`, and related strategy docs.
- Memory: `.codex-memory/MEMORY.md`, `.codex-memory/session_YYYY-MM-DD.md`, `.codex-memory/STATE.json`, `.codex-memory/LEARNINGS.md`.
- Transfer: `HANDOFF.md`.
- Reports: `PFO_REPORT.md` when present.

## Procedure

1. Confirm the project has PFO adoption: `CODEX.md`, `.codex-memory/STATE.json`, and relevant planning docs.
2. Export the vault-ready note set:

```bash
python3 scripts/pfo.py export <project> --target obsidian
```

3. Use `.pfo-integrations/obsidian/PROJECT_INDEX.md` as the entrypoint.
4. Verify the export contains:
   - `PROJECT_INDEX.md`
   - `KNOWLEDGE_GRAPH.md`
   - `STATE.md`
   - `DECISIONS.md`
   - `GATES.md`
   - copied planning and memory notes for existing source artifacts
5. Keep canonical edits in source PFO docs, then regenerate the Obsidian export.

## Obsidian Markdown Rules

- Use `[[wikilinks]]` for generated local note links.
- Use `![[KNOWLEDGE_GRAPH]]` to embed the graph in `PROJECT_INDEX.md`.
- Use callouts for next action, blockers, risks, and source notes.
- Use frontmatter tags such as `pfo/project`, `pfo/planning`, `pfo/memory`, and `pfo/graph`.
- Do not sync secrets, credentials, private customer data, or production dumps into the export.

## Output

Return:

```text
OBSIDIAN EXPORT:
ENTRYPOINT:
NOTES:
SOURCE ARTIFACTS:
REGENERATE COMMAND:
NEXT ACTION:
```

## Rules

- Treat `.pfo-integrations/obsidian/` as generated output.
- Do not make Obsidian syntax mandatory for canonical PFO docs.
- Preserve user edits in canonical docs; regenerate export instead of editing generated notes by hand.
- If the user provides a real vault path, ask before writing outside the project.
