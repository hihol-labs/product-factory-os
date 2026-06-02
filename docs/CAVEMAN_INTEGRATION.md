# Caveman Integration

Product Factory OS includes a PFO-native `/caveman` route for token-efficient communication.

## Source

- Upstream plugin: `https://github.com/JuliusBrussee/caveman`
- Public claim: Caveman-style output compression reduces output tokens while preserving technical accuracy.
- PFO integration: use the principle as a communication control, not as an unmanaged global install.

## PFO Contract

`/caveman` is read-only by default. It changes response style, not project behavior.

Allowed:

- Compress status updates, summaries, reviews, and routine implementation notes.
- Keep exact commands, paths, code, errors, dates, gate names, and verification evidence.
- Switch between `lite`, `full`, `ultra`, and `normal mode`.

Forbidden:

- Hiding failed gates, blockers, uncertainty, warnings, or user approvals.
- Rewriting code blocks, URLs, shell commands, stack traces, or quoted errors.
- Performing global plugin install, network install, shell profile edits, or agent config writes without explicit approval.

## External Install Boundary

When a user asks to install the upstream plugin, verify current upstream docs and request approval for side effects. For Codex CLI, upstream documents:

```bash
npx skills add JuliusBrussee/caveman -a codex
```

Project-scoped Codex Desktop packaging should be treated as a separate `/github-workflow` or `/tool-sync` style publish/install task only after the target project and write scope are explicit.

## Verification

Use these local gates after changing the PFO integration:

```bash
python3 hooks/skill-completeness.py --skill caveman
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/verify_triggers.py
python3 scripts/verify_fixture_contracts.py
python3 scripts/verify_skill_profiles.py
```
