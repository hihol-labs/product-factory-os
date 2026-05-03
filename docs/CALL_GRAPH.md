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
       -> /review
       -> /test
       -> /security-audit
       -> /deps-audit
       -> /harden
       -> /deploy
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
  -> /review
  -> /security-audit
  -> /deps-audit
  -> /migrate
  -> /harden
  -> /infra
  -> /deploy

/strategy
  -> /advisor
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
