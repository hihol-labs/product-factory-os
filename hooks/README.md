# Product Factory OS Hooks

Hooks are optional, but they are the recommended way to keep Codex on the Product Factory OS path when prompts are ambiguous or when methodology files are changing.

## Hook Layers

| Layer | Hook | Purpose | Blocks |
|---|---|---|---|
| Routing | `route-reminder.py` | Maps natural language to `/project`, `/task`, and specialized PFO skills. | No |
| Context | `preflight-context.py` | Prints discovered PFO docs, state, memory, and `.pfo/` contracts. | No |
| Skill completeness | `skill-completeness.py` | Verifies that skills have contracts, trigger entries, fixtures, and route snapshots. | Yes when used as a gate |
| Commit completeness | `commit-completeness.py` | Checks staged methodology diffs for supporting docs, snapshots, and changelog updates. | Yes |
| Review before commit | `review-before-commit.py` | Runs fast validators before methodology changes are committed. | Yes |

## Local Smoke Checks

```bash
python3 hooks/route-reminder.py "plan only, architecture first"
python3 hooks/preflight-context.py
python3 hooks/skill-completeness.py
python3 hooks/review-before-commit.py
python3 scripts/validate_hooks.py
```

## Installation

The plugin manifest points to `hooks/hooks.json`. For local development, run:

```bash
bash packaging/install.sh --install-hooks
```

The installer copies the hook scripts into `${CODEX_HOME:-$HOME/.codex}/hooks/product-factory-os/` and leaves registration explicit. This avoids silently changing global Codex behavior on a user's machine.

## Policy

- Soft hooks may remind or print context, but they must not make product decisions.
- Enforcement hooks block only methodology integrity issues: missing docs, missing snapshots, broken validators, or unsupported staged changes.
- Production-impacting operations still require explicit user confirmation inside the relevant skill or runtime command.
