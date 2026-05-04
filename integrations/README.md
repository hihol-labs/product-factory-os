# Integrations

Product Factory OS exports project state into integration payloads for:

- GitHub Issues
- Linear
- Notion
- Google Drive
- MCP capability map for Context7, Browser Use, GitHub, Codex Security, Linear, Notion, and Google Drive

Generate payloads:

```bash
python3 scripts/export_integrations.py ../my-product --target github
python3 scripts/export_integrations.py ../my-product --target linear
python3 scripts/export_integrations.py ../my-product --target notion
python3 scripts/export_integrations.py ../my-product --target google-drive
```

The payloads are written to `.pfo-integrations/`.

Live connector work should route through `/github-workflow` or `/tool-sync`. Export payloads are the fallback when connector access is unavailable or a live write was not approved.
