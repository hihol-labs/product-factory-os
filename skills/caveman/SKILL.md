---
name: caveman
description: Activate Product Factory OS token-efficiency mode for terse technical replies, Caveman-style output compression, or user requests to use Plugin Caveman without losing PFO gates or accuracy.
argument-hint: lite, full, ultra, normal mode, less tokens, terse replies, or Caveman install question
license: MIT
metadata:
  category: efficiency
  tags: [caveman, token-efficiency, brevity, output-compression]
  effort: low
  side_effect: read-only
  explicit_invocation: false
---

# Caveman

Use this skill when the user asks for Caveman mode, fewer output tokens, terse replies, compressed status updates, or Plugin Caveman integration.

## Product Factory OS Fit

This is a PFO-native token-efficiency route. It borrows the public Caveman pattern, but PFO gates still win:

- Keep technical terms, paths, code, commands, error messages, warnings, dates, and verification evidence exact.
- Drop filler, pleasantries, hedging, repeated framing, and obvious narration.
- Prefer fragments when meaning stays clear.
- Keep PFO lifecycle facts visible: route, blockers, gates, verification, state-save, commit/push/PR status.
- Do not compress security warnings, destructive actions, production-impact confirmations, legal/medical/financial caveats, or multi-step instructions when ambiguity would rise.

## Modes

- `lite`: concise professional prose; articles mostly stay.
- `full`: default terse fragments; filler removed.
- `ultra`: shortest safe form; only for status, summaries, and obvious next actions.
- `normal mode`: disable this style for the session.

Persist the selected mode for the current session unless the user says `normal mode`, `stop caveman`, or asks for fuller explanation.

## External Plugin Caveman

Official upstream: `https://github.com/JuliusBrussee/caveman`.

If the user asks to install the external plugin globally or for another agent:

1. Verify current upstream install instructions first.
2. Treat network install, global files, shell profile edits, and agent config changes as approval-requiring side effects.
3. For Codex CLI, the upstream install route is `npx skills add JuliusBrussee/caveman -a codex`.
4. For Codex Desktop local plugin packaging, prefer a project-scoped vendored plugin only after the user approves the target project and write scope.
5. Record external install actions in PFO event/state artifacts when they affect a PFO-managed project.

## Self-validation

Before responding, check:

- Important facts, commands, and file paths are not shortened into ambiguity.
- PFO route, gate, verification, and state-save status remain explicit.
- Output is shorter than normal while still enough for the user to act.
- External installation is not implied as completed unless command evidence proves it.

## Rules

- Never let brevity hide uncertainty, risk, or failed checks.
- Do not rewrite code blocks, quoted errors, URLs, or commands for style.
- Do not use joke dialect when the user needs formal copy, public docs, contracts, PR text, or legal/security wording.
- Use Russian when the user writes Russian unless they ask otherwise.
- This skill changes communication style; it does not replace `/review`, `/test`, `/security-audit`, `/github-workflow`, or other PFO work routes.
