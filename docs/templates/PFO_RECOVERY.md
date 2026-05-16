# PFO Recovery

Created:

## Reason

## Current State

- Stage:
- Node:
- Unit:

## Repair Plan

1. Re-read required inputs from `.pfo/UNIT_CONTEXT_MANIFEST.json`.
2. Identify the smallest failing gate or missing artifact.
3. If this is a bugfix, write or update `ROOT_CAUSE.md` before changing code.
4. Repair only the affected files.
5. Re-run the declared red/green/refactor and verification commands.
6. Run spec compliance review, then code quality review.
7. Update `.codex-memory/STATE.json` and `PFO_REPORT.md`.
