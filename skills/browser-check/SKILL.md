---
name: browser-check
description: Local browser smoke testing for frontend, full-stack, and visual workflows using Playwright, Browser Use, or equivalent browser automation. Use when a UI, route, form, dashboard, landing page, generated app, or frontend regression needs interactive verification.
argument-hint: local URL, app path, route, user flow, or visual check target
license: MIT
metadata:
  category: quality
  tags: [browser, frontend, smoke-test, ux]
---

# Browser Check

Use this skill to verify user-facing browser behavior after frontend or full-stack changes.

Default to the local Playwright harness in `playwright/` for repeatable checks. Use the in-app browser or Browser Use when Playwright is unavailable, when a visual/manual judgment is required, or when the user explicitly asks for interactive inspection.

When running commands, resolve `$SKILL_DIR` to the directory that contains this `SKILL.md`.

## Preconditions

- Identify the local URL or file URL.
- Start the dev server when the project requires one.
- Confirm the expected critical flow from `PRD.md`, `GOLDEN_FLOWS.md`, `TEST_PLAN.md`, or the current task.
- For localhost checks, detect running dev servers before writing a script.

## Procedure

1. Resolve the browser target:
   - If a URL is supplied, use it.
   - If testing localhost and no URL is supplied, run `node $SKILL_DIR/playwright/run.js --detect`.
   - If multiple servers are detected, ask which target to verify.
2. Write task-specific Playwright checks to a temporary script outside the project, such as `/tmp/pfo-browser-check-<flow>.js`.
3. Execute the script through `node $SKILL_DIR/playwright/run.js /tmp/pfo-browser-check-<flow>.js`.
4. Check the initial render for blank screens, layout breakage, overlapping text, missing assets, and console-visible failures when available.
5. Exercise the critical path: navigation, forms, auth placeholder behavior, loading states, error states, and primary calls to action.
6. Capture screenshots for desktop and mobile when visual evidence is useful.
7. Record whether the check blocks release or is advisory.

## Output

Return:

```text
BROWSER TARGET:
ENGINE: Playwright | Browser Use | in-app browser | manual
FLOW CHECKED:
RESULT: PASSED | PASSED_WITH_WARNINGS | BLOCKED
EVIDENCE:
SCREENSHOTS:
CONSOLE OR NETWORK ISSUES:
ISSUES:
NEXT ACTION:
```

## Rules

- Prefer real interaction over static inspection for user-facing changes.
- Treat broken first render, blank app shell, unusable navigation, or inaccessible primary flow as `BLOCKED` before deploy.
- Do not rely on screenshots alone when forms or navigation can be clicked.
- Do not commit temporary Playwright scripts generated only for smoke checks.
- Parameterize target URLs in generated scripts.
- Prefer stable role/text/test-id locators over brittle CSS selectors.
- Run headless only when requested or when CI requires it.
- If the harness dependency is missing, run `npm run setup` from `$SKILL_DIR/playwright` after user approval when network access is required.
- Do not make production-impacting changes from the browser check; route fixes through `/bugfix`, `/frontend-builder`, or the active execution node.
- Save browser evidence in the final report or `QUALITY_GATES.md` when deploy readiness is in scope.
