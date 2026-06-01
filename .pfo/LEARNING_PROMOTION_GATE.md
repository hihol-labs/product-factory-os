# Learning Promotion Gate

Purpose: convert repeated errors into system changes instead of reminders.

Harness ratchet:

- Treat repeated agent mistakes as signals for harness repair.
- Add a rule only when it traces to observed failure evidence or a hard external constraint.
- Prefer tests, hooks, validators, schemas, templates, routes, or skills over prose reminders.
- Keep `AGENTS.md`, tool registries, and skill prompts short; remove stale rules when stronger controls make them redundant.

Required path:

```text
.codex-memory/LEARNINGS.jsonl
  -> .codex-memory/LEARNING_PROPOSALS.json
  -> promotion target: test, hook, doc, rule, linter, validator, template, or skill
  -> promotion checks
  -> reviewed change
```

Promotion rules:

- A learning without evidence remains a note.
- A proposed rule without a target artifact remains blocked.
- A methodology change must name the check that will catch the issue next time.
- Accepted promotions must update at least one test, hook, validator, linter, doc, template, route, or skill.
- Rejected promotions must keep the reason in `.codex-memory/LEARNING_PROPOSALS.json`.
