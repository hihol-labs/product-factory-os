# CODEX

## Project Summary

Tutor booking MVP with FastAPI, SQLite, auth, availability slots, and booking flow.

## Decisions

- Use SQLite for local MVP.
- Defer payments and calendar sync.
- Prevent double-booking with a unique booking per slot.

## Commands

```bash
pytest
uvicorn app.main:app --reload
```

## Status

| Step | Status | Notes |
|---:|---|---|
| 1 | pending | Scaffold |
| 2 | pending | Data model |
| 3 | pending | Auth |
| 4 | pending | Slots |
| 5 | pending | Bookings |
| 6 | pending | Docs and Docker |

## Session Rule

Save context with `/session-save` after significant work or before stopping.

