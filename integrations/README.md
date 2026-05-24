# Integrations

Product Factory OS exports project state into integration payloads for:

- GitHub Issues
- Linear
- Notion
- Google Drive
- Obsidian local knowledge graph
- MCP capability map for Context7, Browser Use, GitHub, Codex Security, Linear, Notion, and Google Drive
- Tool capability registry with read/write/execute, side effects, auth, external data risk, fallback mode, and approval requirements

Generate payloads:

```bash
python3 scripts/export_integrations.py ../my-product --target github
python3 scripts/export_integrations.py ../my-product --target linear
python3 scripts/export_integrations.py ../my-product --target notion
python3 scripts/export_integrations.py ../my-product --target google-drive
python3 scripts/export_integrations.py ../my-product --target obsidian
```

The payloads are written to `.pfo-integrations/`.

Live connector work should route through `/github-workflow` or `/tool-sync`. Export payloads are the fallback when connector access is unavailable or a live write was not approved.

Validate tool capabilities with:

```bash
python3 scripts/validate_tool_registry.py integrations/tool-capability-registry.json
```

Obsidian exports are local generated Markdown under `.pfo-integrations/obsidian/`. Start from `PROJECT_INDEX.md`; it links planning docs, `.codex-memory/`, `HANDOFF.md`, state, gates, decisions, and `KNOWLEDGE_GRAPH.md`.
