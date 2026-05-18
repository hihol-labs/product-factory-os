# Notes

This fixture verifies that a voice-first PFO product request for a Telegram bot enters the full Product Factory OS route.

The expected compiler path is:

```text
Intent -> Messaging Bot classification -> Bot template -> Product Blueprint -> Build Plan -> Execution Graph
```

## Scenario 1: Voice-first Product Request

The user can describe a Telegram bot in natural language and enter the full Product Factory OS route.

## Scenario 2: Runtime Contracts

The generated project receives `.pfo/` contracts and `.codex-memory/STATE.json`.

## Scenario 3: Gate Path

The execution graph includes validation checkpoints, repair paths, and review gates before deploy readiness.
