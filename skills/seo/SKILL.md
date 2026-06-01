---
name: seo
description: Improve SEO effectiveness for products, landing pages, docs, and content by auditing technical SEO, search intent, metadata, structured data, content gaps, and measurement loops. Use for SEO audit, organic traffic, indexing, sitemap, robots.txt, schema, canonical, meta tags, Search Console, and content optimization work.
argument-hint: URL, page, product, target queries, market, or SEO problem
license: MIT
metadata:
  category: growth
  tags: [seo, growth, content, technical-seo, search]
  effort: high
  side_effect: external-read-docs-write
  explicit_invocation: false
---

# SEO

Use this skill when PFO needs to improve organic search effectiveness for a product, landing page, documentation site, content backlog, or launch plan.

## Inputs

- URL, repository path, page, product, or content set to evaluate.
- Target market, geography, language, ICP, and priority queries when known.
- Existing PFO artifacts when present: `MARKET_BRIEF.md`, `ICP.md`, `GO_TO_MARKET.md`, `CONTENT_BACKLOG.md`, `FUNNEL_MODEL.md`, `VALIDATION_PLAN.md`, `TEST_PLAN.md`.
- Analytics, Search Console, crawl, or rank data only when the user provides it or approves private data access.

## Process

1. Read current PFO artifacts and identify the search surface: pages, docs, product category, ICP, language, and conversion goal.
2. Separate public-safe research from private data. Never send secrets, unreleased strategy, customer data, or proprietary analytics to external tools.
3. If a live URL or local site is available, inspect:
   - crawlability and indexability: status codes, redirects, `robots.txt`, sitemap, canonical tags, noindex, and duplicate URLs.
   - page metadata: title, description, headings, Open Graph/Twitter preview, language, and URL structure.
   - structured data: schema type, required fields, validation gaps, and search-result eligibility.
   - rendered UX: mobile readability, performance blockers, internal links, content discoverability, and conversion path.
4. Route through `/browser-check` when rendered UI, local preview, Core Web Vitals proxies, or visual/mobile checks affect SEO.
5. Route through `/market-scan` when keyword intent, competitor pages, recent public demand signals, or content opportunities require fresh public evidence.
6. Build an impact-ranked backlog:
   - technical fixes that unblock crawling, indexing, snippets, or speed.
   - content fixes that match search intent and strengthen entity/topic coverage.
   - internal-link and information-architecture fixes.
   - measurement tasks for Search Console, analytics, sitemap submission, and experiment tracking.
7. Update docs as needed:
   - `SEO_AUDIT.md`: current state, findings, priority, evidence, and verification.
   - `CONTENT_BACKLOG.md`: search-intent content candidates and briefs.
   - `GO_TO_MARKET.md`: organic acquisition channel assumptions.
   - `VALIDATION_PLAN.md`: SEO experiments, target metric, baseline, and decision rule.
   - `.pfo/EXPERIMENT_PROGRAM.md`: only for an approved fixed-metric SEO experiment loop.

## Output Shape

Return:

```text
SEO SURFACE:
PUBLIC/PRIVATE DATA BOUNDARY:
TECHNICAL SEO FINDINGS:
CONTENT AND INTENT GAPS:
STRUCTURED DATA:
INTERNAL LINKS:
MEASUREMENT:
PRIORITIZED BACKLOG:
PFO ARTIFACT IMPACT:
NEXT VALIDATION STEP:
```

When writing docs, append dated evidence instead of replacing prior user-authored research unless the user explicitly asks to rewrite.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Do not fabricate rankings, search volume, Search Console data, Lighthouse scores, crawl results, backlinks, or competitor evidence.
- Cite public sources when they influence a recommendation.
- Treat ranking and traffic claims as hypotheses unless backed by supplied analytics or verified public evidence.
- Do not optimize for vanity traffic when ICP, conversion goal, or funnel metric contradicts it.
- Prefer small, measurable SEO changes with a baseline and decision rule over broad content churn.
- Do not write production `robots.txt`, sitemap, canonical, or schema changes unless the user asked for implementation; default output is an audit/backlog.
