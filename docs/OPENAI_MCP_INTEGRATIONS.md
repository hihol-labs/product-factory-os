# OpenAI And MCP Integrations

Product Factory OS uses external tools only when they strengthen a specific PFO stage, skill, or quality gate.

## Integration Rules

- Bind every connector to a named PFO skill, agent role, or gate.
- Prefer read-only inspection before live writes.
- Ask before mutating external systems unless the user explicitly requested the mutation.
- Fall back to `.pfo-integrations/` export payloads when live connector access is unavailable.
- Do not send secrets, credentials, private customer data, or proprietary snippets to external research tools.

## Recommended Tool Map

| Tool | PFO Skill | Stage |
|---|---|---|
| Context7 MCP | `/mcp-docs` | planning, implementation, dependency, infra |
| Last30Days skill | `/market-scan` | discovery, validation, strategy, launch, iteration |
| Playwright / Browser Use | `/browser-check` | frontend QA, hardening, deploy readiness |
| GitHub | `/github-workflow` | issues, PR, CI, release |
| Codex Security | `/security-audit` | security gate and attack-path analysis |
| Linear | `/tool-sync` | roadmap and execution tracking |
| Notion | `/tool-sync` | project pages and decision logs |
| Google Drive | `/tool-sync` | Docs, Sheets, Slides, stakeholder artifacts |
| Obsidian local export | `/obsidian-export` | local memory, handoff, planning graph |

## Agent Map

| Agent | Primary Skills |
|---|---|
| `researcher` | `/mcp-docs`, `/market-scan`, `/advisor`, `/strategy` |
| `ux-reviewer` | `/browser-check`, `/review`, `/test` |
| `release-manager` | `/github-workflow`, `/review`, `/deploy` |
| `integration-engineer` | `/tool-sync`, `/github-workflow` |
| `data-reviewer` | `/migrate`, `/security-audit`, `/harden` |

## Fallback Payloads

Use export payloads when live connector access is missing or write approval is not granted:

```bash
python3 scripts/pfo.py export <project> --target github
python3 scripts/pfo.py export <project> --target linear
python3 scripts/pfo.py export <project> --target notion
python3 scripts/pfo.py export <project> --target google-drive
python3 scripts/pfo.py export <project> --target obsidian
```
