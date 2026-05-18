# Notes

This fixture checks idempotent onboarding and no application behavior changes.

## Scenario 1: Happy Path

An existing repository without PFO files is adopted. The output creates `AGENTS.md`, `CODEX.md`, `.codex-memory/STATE.json`, and `.pfo/` contracts.

## Scenario 2: Idempotent Re-run

Running adoption again updates marked PFO blocks only and does not duplicate managed sections.

## Scenario 3: self-reference refusal

Running adoption inside the Product Factory OS methodology repository itself is refused or skipped.

## Scenario 4: Guard Rails

Application source files are not rewritten, existing local instructions are preserved, and behavior remains unchanged.
