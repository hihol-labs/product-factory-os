# Call Graph

The workflow is intentionally shallow. Skills can call other skills conceptually, but chains should stay understandable.

```text
/project
  -> Product Factory OS intent capture
  -> product classification
  -> template selection
  -> /kickstart
       -> /discover
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
       -> /github-workflow
       -> /tool-sync
       -> /session-save
  -> /blueprint
       -> product compiler
       -> execution graph
       -> /review
  -> /guide

/task
  -> /bugfix
  -> /refactor
  -> /doc
  -> /test
  -> /perf
  -> /mcp-docs
  -> /browser-check
  -> /review
  -> /security-audit
  -> /deps-audit
  -> /migrate
  -> /harden
  -> /infra
  -> /deploy
  -> /github-workflow
  -> /tool-sync

/strategy
  -> /advisor
  -> /mcp-docs
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
- External tools are invoked only through explicit skills such as `/mcp-docs`, `/browser-check`, `/github-workflow`, or `/tool-sync`.
