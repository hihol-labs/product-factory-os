# Product Factory OS Hooks

Hooks are installed by default by `bash install.sh`. They keep Codex on the Product Factory OS path when prompts are ambiguous, when an existing project needs adoption, or when methodology files are changing.

## Hook Layers

| Layer | Hook | Purpose | Blocks |
|---|---|---|---|
| Routing | `route-reminder.py` | Maps natural language to `/project`, `/task`, and specialized PFO skills. | No |
| Context | `preflight-context.py` | Auto-enforces full PFO runtime for workspace projects and any local project discovered through `PFO_GLOBAL.json`, then prints discovered PFO docs, state, memory, event log, and `.pfo/` contracts. | No |
| Diagnostics | `session-diagnostics.py` | Prints stale state, recovery, handoff, and telemetry warnings from `.codex-memory/STATE.json`. | No |
| Skill completeness | `skill-completeness.py` | Verifies that skills have contracts, trigger entries, fixtures, and route snapshots. | Yes when used as a gate |
| Commit completeness | `commit-completeness.py` | Checks staged methodology diffs for supporting docs, snapshots, and changelog updates. | Yes |
| Review before commit | `review-before-commit.py` | Runs fast validators before methodology changes are committed. | Yes |

## Local Smoke Checks

```bash
python3 hooks/route-reminder.py "plan only, architecture first"
python3 hooks/preflight-context.py
python3 hooks/session-diagnostics.py
python3 hooks/skill-completeness.py
python3 hooks/review-before-commit.py
python3 scripts/validate_hooks.py
```

## Installation

The plugin manifest points to `hooks/hooks.json`. For local development, run:

```bash
bash install.sh
```

The installer copies hook scripts into `${CODEX_HOME:-$HOME/.codex}/hooks/product-factory-os/`, writes workspace policy files, and writes global `PFO_GLOBAL.json` files so Codex can connect PFO for projects outside the default workspace.

## Policy

- Soft hooks may remind or print context, but they must not make product decisions.
- Enforcement hooks block only methodology integrity issues: missing docs, missing snapshots, broken validators, or unsupported staged changes.
- Production-impacting operations still require explicit user confirmation inside the relevant skill or runtime command.
