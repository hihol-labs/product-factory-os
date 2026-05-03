# Golden Path: Tutor Booking App

This example shows the expected Route A flow for a small booking product.

## User Prompt

```text
I want to build a booking app for private tutors. Tutors can publish available slots, students can book a slot, and the MVP should run locally first.
```

## Expected Route

```text
/project -> /kickstart
  -> /blueprint
  -> /review
  -> implementation step loop
  -> /test
  -> /security-audit
  -> /deps-audit
  -> /harden
  -> /session-save
```

## Clarifying Answers

| Question | Answer |
|---|---|
| Primary users | Independent tutors and students |
| Auth | Email/password for MVP |
| Payments | Deferred |
| Calendar sync | Deferred |
| Database | SQLite for local MVP, PostgreSQL-ready schema |
| Deployment | Local Docker first |

## Expected Documents

- `DISCOVERY.md`
- `PRD.md`
- `PRODUCT_BLUEPRINT.md`
- `PROJECT_ARCHITECTURE.md`
- `BUILD_PLAN.md`
- `EXECUTION_GRAPH.md`
- `IMPLEMENTATION_PLAN.md`
- `README.md`
- `CODEX.md`
- `CODEX_GUIDE.md`

## Quality Gates

- `/review` must not return `BLOCKED` before code.
- `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md`, and `EXECUTION_GRAPH.md` must agree.
- Each implementation step must define verification.
- Booking creation must have a regression-capable test.
- Deploy is out of scope until the user confirms a target environment.
