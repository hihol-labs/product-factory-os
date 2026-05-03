---
name: deps-audit
description: Read-only dependency, CVE, license, and maintenance audit.
argument-hint: package manifests, lockfiles, or project root
license: MIT
metadata:
  category: quality
  tags: [dependencies, supply-chain, licenses]
---

# Dependency Audit

Audit dependency manifests and lockfiles.

The canonical rubric lives in `docs/rubrics/deps.md`. Use it as the source of truth.

## Process

1. Detect package managers and lockfiles.
2. Use local audit tools when available.
3. Check for known vulnerable packages, abandoned packages, risky licenses, duplicate frameworks, unpinned Docker base images, and missing lockfiles.
4. Identify whether dependency audit can run in CI.
5. Report actionable upgrades and accepted-risk options.

## Rules

- Read-only by default.
- Do not mutate lockfiles unless remediation is explicitly requested.
- If network access is unavailable, report the local-only limitation.
- If the rubric and this skill conflict, follow the rubric and update this skill later.
- For deployable products, dependency gate cannot pass unless lockfiles or an explicit no-lockfile rationale exist.
