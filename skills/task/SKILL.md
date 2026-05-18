---
name: task
description: Route existing-code work through Product Factory OS to the correct daily-work skill.
argument-hint: bug, feature, refactor, docs, tests, review, deploy, or audit request
license: MIT
metadata:
  category: router
  tags: [task, router, existing-code]
---

# Task Router

Use this skill for work on an existing repository.

## Product Factory OS Preflight

Before routing substantial work, ensure the repository is PFO-managed:

```text
AGENTS.md
CODEX.md
.codex-memory/MEMORY.md
.codex-memory/STATE.json
.pfo/
```

If any are missing, route to `/adopt` first.

Then inspect:

- repository structure
- stack and package manifests
- available scripts/commands
- existing docs
- tests
- current memory state

Update `.codex-memory/STATE.json` with:

- `existingProject.isExistingProject = true`
- detected stack
- available commands
- selected task route
- short analysis summary

State path:

```text
EXISTING_PROJECT_DETECTED
  -> EXISTING_PROJECT_ANALYZED
  -> TASK_CLASSIFIED
  -> PLAN_READY
```

## Routing

- Bug, stack trace, failing behavior -> `/bugfix`
- Test coverage, missing tests, test failures -> `/test`
- Cleanup without behavior change -> `/refactor`
- Documentation, README, API docs -> `/doc`
- Explain code or architecture -> `/explain`
- Slow behavior or resource use -> `/perf`
- Current framework, SDK, or API documentation needed -> `/mcp-docs`
- Browser UI smoke test, Playwright smoke, or visual QA -> `/browser-check`
- General quality review -> `/review`
- Security concerns -> `/security-audit`
- Dependency, license, CVE concerns -> `/deps-audit`
- Infrastructure generation -> `/infra`
- Production readiness -> `/harden`
- Database schema/data change -> `/migrate`
- Deploy/release -> `/deploy`
- GitHub issue, PR, CI, or release workflow -> `/github-workflow`
- Linear, Notion, Google Drive, or integration export -> `/tool-sync`
- Session transfer, role switch, delegation, AFK, compaction, or recovery transfer -> `/handoff`
- Product/strategy decision -> `/advisor` or `/strategy`

## Rules

- If the task is ambiguous, inspect the repository briefly before routing.
- If the project is not adopted into PFO, route to `/adopt` first.
- For non-trivial changes, create or update the relevant execution node in `EXECUTION_GRAPH.md` or document why the task is small enough for direct daily-work routing.
- Do not perform the work directly unless it is tiny and clearly belongs to the selected route.
- For production-impacting tasks, require explicit confirmation.

## Self-Check

- Existing project signals were considered.
- PFO adoption status was checked.
- `.codex-memory/STATE.json` was considered or created via `/adopt`.
- A single route was selected.
- Safety boundaries were respected.
