# Project Contract

This file is owned by the project. Product Factory OS reads it before planning, editing, reviewing, and deploying.

## Product Invariants

- Product Factory OS remains a local-first Codex methodology and runtime for creating, adopting, planning, validating, reviewing, and saving project work through `/project` and `/task` routes.
- `scripts/pfo.py` is the canonical CLI entrypoint, and the `pfo` wrapper must execute that script without requiring per-project manual setup.
- Existing-project adoption must preserve project-owned instructions and files while adding or refreshing only managed PFO runtime artifacts.
- PFO gates must fail closed on missing contracts, invalid runtime JSON, unsafe substitutions, broken alias targets, and unsupported deployment readiness claims.

## Real Data Sources

- Repository files under `/home/hihol/projects/product-factory-os` are the source of truth for methodology, scripts, skills, templates, docs, tests, and runtime contracts.
- `.codex-memory/STATE.json`, `.codex-memory/events.jsonl`, `PFO_CONTRACT_GATE.json`, `PFO_EXISTING_PROJECT_ANALYSIS.json`, and `PFO_REPORT.md` are generated state/report artifacts and must be regenerated through PFO commands or validators.
- Fixture expectations live in `tests/fixtures/`, `tests/fixture-contracts.json`, and `tests/snapshots/route-snapshots.json`; validators must read these files directly.

## Provider/Integration Contracts

- GitHub, Vercel, Google, Linear, Notion, and other external integrations are optional capability layers; local validators must remain usable without those credentials.
- Plugin metadata in `.codex-plugin/plugin.json`, skill files, hooks, and generated install policies must stay synchronized through repository validators.
- Network-backed or credential-backed evidence must be recorded explicitly; local-only verification cannot be described as live external validation.

## User-Facing Output Contracts

- CLI commands must print actionable statuses, blockers, warnings, and next steps without hiding degraded or skipped work.
- Generated reports must distinguish product changes from runtime/status artifacts so users are not blocked by stale or unrelated report text.
- Documentation, templates, and reports must describe current behavior and runnable commands rather than future intent.

## Deployment Contracts

- `python3 scripts/production_readiness.py` is the repository-wide release gate.
- `.github/workflows/validate.yml` must run the same core validators used locally.
- Installers must keep the `pfo` command available in normal WSL shell usage and direct WSL command execution when permissions allow.
