---
name: mcp-docs
description: Fresh library and framework documentation lookup through MCP documentation providers such as Context7. Use when implementation depends on current APIs, SDK behavior, framework conventions, setup steps, or migration details for libraries and platforms.
argument-hint: library, framework, API, version, error, or implementation question
license: MIT
metadata:
  category: research
  tags: [mcp, context7, documentation, libraries]
---

# MCP Docs

Use this skill when stale or guessed library knowledge could affect the implementation.

## Primary Source

Prefer MCP documentation tools, especially Context7 when available:

1. Resolve the library ID for the package, framework, or platform.
2. Query the docs with the narrow implementation question.
3. Record the source library ID and the relevant decision in the working notes, plan, or review report.

If MCP documentation is unavailable, use official project documentation as fallback and state that the MCP source was unavailable.

## Use Before

- Adding or upgrading dependencies.
- Writing integration code against SDKs, auth providers, payment APIs, deployment platforms, UI frameworks, ORMs, queues, or browser APIs.
- Fixing failures that may be caused by version drift.
- Choosing framework-specific conventions in `/bugfix`, `/refactor`, `/infra`, `/deploy`, `/deps-audit`, or `/harden`.

## Output

Return:

```text
DOC SOURCE:
VERSION OR LIBRARY ID:
DECISION:
IMPLEMENTATION IMPACT:
FOLLOW-UP RISK:
```

## Rules

- Do not send secrets, proprietary source snippets, credentials, or private customer data to documentation tools.
- Prefer official or high-reputation documentation results.
- Keep queries narrow enough to answer the task at hand.
- Do not block tiny local fixes when the relevant API behavior is already proven by tests or code.
- If docs conflict with repository conventions, explain the conflict and prefer the repository convention unless it is broken or deprecated.
