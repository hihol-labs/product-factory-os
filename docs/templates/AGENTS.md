# AGENTS

This project is governed by Product Factory OS.

## Runtime Rule

- New product work routes through `/project -> /kickstart`.
- Existing project work routes through `/task`.
- Significant work updates `.codex-memory/STATE.json`.
- Scope, data, fallback, and golden-flow rules live in `.pfo/`.

## Before Substantial Work

Run or confirm:

```bash
pfo adopt . --analyze
```

Then use the smallest relevant PFO gate before finishing.
