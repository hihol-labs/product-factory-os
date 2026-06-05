# Call Graph

The workflow is intentionally shallow. Skills can call other skills conceptually, but chains should stay understandable.

```text
/project
  -> Product Factory OS intent capture
  -> product classification
  -> template selection
  -> /brainstorm
       -> /discover
       -> /advisor
       -> /grill-me
       -> /strategy
       -> /blueprint
  -> /kickstart
       -> /discover
       -> /market-scan
       -> /seo
       -> /blueprint
       -> product compiler
       -> execution graph
       -> /mcp-docs
       -> /review
       -> /test
       -> /browser-check
       -> /security-audit
       -> /deps-audit
       -> /harden
       -> /deploy
       -> /handoff
       -> /github-workflow
       -> /tool-sync
       -> /obsidian-export
       -> /session-save
  -> /blueprint
       -> /market-scan
       -> product compiler
       -> execution graph
       -> /review
  -> /guide

/task
  -> /brainstorm
  -> /bugfix
  -> /refactor
  -> /doc
  -> /test
  -> /perf
  -> /seo
  -> /mcp-docs
  -> /caveman
  -> /skill-create
  -> /browser-check
  -> /review
  -> /security-audit
  -> /deps-audit
  -> /migrate
  -> /harden
  -> /infra
  -> /deploy
  -> /handoff
  -> /github-workflow
  -> /tool-sync
  -> /obsidian-export
  -> /session-save
  -> /strategy
  -> /advisor
  -> /grill-me

/strategy
  -> /market-scan
  -> /seo
  -> /caveman
  -> pfo experiment-init / pfo experiment-record
  -> /advisor
  -> /grill-me
  -> /mcp-docs
  -> /handoff
  -> /tool-sync
  -> /review

/adopt
  -> /strategy or /blueprint
```

Rules:

- No skill calls itself.
- Maximum planned depth is 3.
- Production-impacting paths require explicit user confirmation.
- Read-only audits do not apply fixes unless the user explicitly asks for remediation.
- Product Factory OS compiler stages are internal runtime stages, not user-invoked skills.
- Implementation proceeds by execution graph node, with repair paths for failed gates.
- Use `/handoff` before session transfer, role switch, delegation, AFK execution, compaction, or recovery.
- External tools are invoked only through explicit skills such as `/mcp-docs`, `/market-scan`, `/browser-check`, `/github-workflow`, or `/tool-sync`.
