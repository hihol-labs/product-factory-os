---
name: github-workflow
description: GitHub issue, pull request, CI, release, and code review workflow for Product Factory OS projects. Use when work involves GitHub Issues, PR summaries, review comments, failing GitHub Actions, release branches, changelogs, or publishing project state to GitHub.
argument-hint: issue, pull request, branch, check run, release, or GitHub repo
license: MIT
metadata:
  category: integration
  tags: [github, pull-request, ci, release]
---

# GitHub Workflow

Use this skill when Product Factory OS state needs to connect to GitHub work.

## Capabilities

- Convert `EXECUTION_GRAPH.md` nodes and blockers into GitHub issues.
- Inspect PR metadata, review comments, and check status through the GitHub plugin or `gh` when available.
- Debug failing GitHub Actions before changing code.
- Prepare branch, changelog, release notes, and PR summaries.
- Keep `QUALITY_GATES.md` and `.codex-memory/STATE.json` aligned with PR and CI status.

## Procedure

1. Identify the repository, branch, issue, PR, or check run.
2. Read local git status before mutating anything.
3. Use GitHub connector capabilities first; use `gh` only when connector coverage is insufficient.
4. Map findings back to PFO artifacts:
   - issues -> execution nodes or blockers
   - CI checks -> verification history
   - review comments -> repair actions
   - release notes -> completed modules and accepted risks
5. Before branch completion, record `pfo finish-branch <project> --mode pr|merge|keep|discard --verification ...`.
6. Update integration payloads with `python3 scripts/pfo.py export <project> --target github` when a file export is requested.

## Output

Return:

```text
GITHUB TARGET:
PFO ARTIFACTS UPDATED:
CHECK STATUS:
ACTION TAKEN:
BLOCKERS:
NEXT ACTION:
```

## Rules

- Do not push, merge, close issues, resolve review threads, or create production releases without explicit user intent.
- Do not hide failing CI behind documentation-only status.
- Keep local worktree changes scoped to the active execution node.
- Do not mark branch work finished without fresh verification and `BRANCH_FINISH.md` when branch finish is in scope.
- If GitHub is unavailable, produce `.pfo-integrations/github.json` and state that live sync was not performed.
