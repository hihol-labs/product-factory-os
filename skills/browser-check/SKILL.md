---
name: browser-check
description: Local browser smoke testing for frontend, full-stack, and visual workflows using Browser Use or equivalent browser automation. Use when a UI, route, form, dashboard, landing page, generated app, or frontend regression needs interactive verification.
argument-hint: local URL, app path, route, user flow, or visual check target
license: MIT
metadata:
  category: quality
  tags: [browser, frontend, smoke-test, ux]
---

# Browser Check

Use this skill to verify user-facing browser behavior after frontend or full-stack changes.

## Preconditions

- Identify the local URL or file URL.
- Start the dev server when the project requires one.
- Confirm the expected critical flow from `PRD.md`, `GOLDEN_FLOWS.md`, `TEST_PLAN.md`, or the current task.

## Procedure

1. Open the target in the in-app browser or Browser Use.
2. Check the initial render for blank screens, layout breakage, overlapping text, missing assets, and console-visible failures when available.
3. Exercise the critical path: navigation, forms, auth placeholder behavior, loading states, error states, and primary calls to action.
4. Capture screenshots when visual evidence is useful.
5. Record whether the check blocks release or is advisory.

## Output

Return:

```text
BROWSER TARGET:
FLOW CHECKED:
RESULT: PASSED | PASSED_WITH_WARNINGS | BLOCKED
EVIDENCE:
ISSUES:
NEXT ACTION:
```

## Rules

- Prefer real interaction over static inspection for user-facing changes.
- Treat broken first render, blank app shell, unusable navigation, or inaccessible primary flow as `BLOCKED` before deploy.
- Do not rely on screenshots alone when forms or navigation can be clicked.
- Do not make production-impacting changes from the browser check; route fixes through `/bugfix`, `/frontend-builder`, or the active execution node.
- Save browser evidence in the final report or `QUALITY_GATES.md` when deploy readiness is in scope.
