# Product Factory OS v0.6.1

This release turns PFO installation from a manual onboarding checklist into a workspace runtime install.

## Highlights

- `bash install.sh` is now the default installer.
- The installer writes workspace `AGENTS.md`, `CODEX.md`, and `PFO_WORKSPACE.json`.
- Existing first-level projects in the workspace are adopted automatically.
- Adopted projects receive `AGENTS.md`, `CODEX.md`, `.codex-memory/`, and `.pfo/` contracts without overwriting local instructions.
- `~/.local/bin/pfo` is installed as the short runtime command.
- Hooks are installed by default.
- `preflight-context.py` can auto-adopt a first-level workspace project before printing context.

## Verification

```text
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/validate_runtime.py
python3 scripts/validate_hooks.py
python3 scripts/release_check.py
```
