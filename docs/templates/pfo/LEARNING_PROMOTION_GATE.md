# Learning Promotion Gate

Purpose: convert repeated errors into system changes instead of reminders.

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
