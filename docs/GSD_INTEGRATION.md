# GSD Integration Notes

Product Factory OS and GSD overlap on spec-driven development, stateful planning, agents, gates, and context engineering. PFO keeps its product-factory scope and adopts only the execution mechanics that improve reliability.

## Adopted From GSD

- Phase discussion before planning detailed work.
- Fresh, unit-scoped execution context.
- Unit manifest with inputs, write scope, dependencies, gates, and verification commands.
- Dispatch journal for resumability.
- Fail-closed verification with explicit recovery path.
- Drift and state reconciliation as first-class runtime concerns.
- Token, cost, command, and verification telemetry when available.
- Durable learnings extraction after milestones and repairs.
- Visual HTML briefs for recap, plans, diffs, tables, and status.

## Already Covered By PFO

- Product classification and starter selection.
- Product strategy artifacts: discovery, ICP, market brief, business model, GTM.
- Project-owned `.pfo/` guardrails for scope, data, fallbacks, golden flows, and regression contracts.
- Connector-aware workflow through GitHub, Linear, Notion, Google Drive, Context7, Browser Use, and Codex Security.
- Starter packs and golden paths across product types.

## Not Adopted

- GSD's full standalone agent harness.
- Always-on autonomous milestone execution.
- Database-authoritative state as the only source of truth.
- Permission bypass defaults.

PFO keeps human confirmation at irreversible boundaries and uses file-backed state as the portable default.

## PFO Runtime Mapping

| GSD Pattern | PFO Surface |
|---|---|
| discuss phase | `pfo discuss`, `PHASE_CONTEXT.md` |
| task-ready context | `pfo manifest`, `.pfo/UNIT_CONTEXT_MANIFEST.json` |
| execute and verify loop | `pfo build`, `pfo verify-work` |
| recovery and stuck handling | `RECOVERY_REQUIRED`, `PFO_RECOVERY.md` |
| history and metrics | `dispatchJournal`, `telemetry`, `pfo report` |
| visual recap | `pfo brief --mode recap` |
| knowledge extraction | `pfo learnings`, `.codex-memory/LEARNINGS.md` |
