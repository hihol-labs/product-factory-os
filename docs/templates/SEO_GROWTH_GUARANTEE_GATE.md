# SEO Growth Guarantee Gate

Use this gate when SEO work claims or targets measurable growth for a concrete product, page set, market, or content surface.

This gate does not guarantee ranking or traffic outcomes. It guarantees that SEO growth work has a baseline, a target, a measurement source, an attribution window, implemented changes, exclusion factors, a result decision, and a next iteration before PFO treats the growth claim as verified.

## Gate Status

```text
PENDING | BLOCKED | PASSED_WITH_WARNINGS | PASSED
```

## Gate Fields

| Field | Value | Evidence |
|---|---|---|
| Baseline Metric |  | Search Console, Analytics, rank tracker, crawl, or approved export before changes |
| Target Metric |  | numeric target and direction, for example clicks +15%, CTR +2pp, indexed pages +20 |
| Measurement Source |  | Search Console, Analytics, logs, crawl report, rank tracker, or approved dataset |
| Attribution Window |  | start date, end date, and reason the window fits crawl/indexing lag |
| Implemented Changes |  | shipped SEO changes, commit/PR/deploy links, sitemap submission, or content updates |
| Exclusion Factors |  | algorithm updates, seasonality, campaigns, tracking changes, outages, competitor shocks, or none |
| Result Decision |  | PENDING, KEEP, DISCARD, ITERATE, BLOCKED, or STOP |
| Next Iteration |  | smallest next SEO experiment or explicit stop reason |

## Decision Rules

- `PASSED`: baseline, target, measurement source, attribution window, implemented changes, exclusion factors, result decision, and next iteration are all backed by evidence.
- `PASSED_WITH_WARNINGS`: evidence is mostly complete, but attribution is noisy or the measurement window is weak.
- `BLOCKED`: required data access, baseline, implementation evidence, or measurement evidence is missing.
- `PENDING`: SEO changes are planned or running, but the attribution window has not completed.

## Rules

- Do not claim growth from impressions, clicks, CTR, position, indexed pages, conversions, or revenue without an explicit baseline and measurement source.
- Do not compare periods when tracking, indexing, product scope, or paid/owned campaigns changed without recording exclusion factors.
- Do not treat rankings as verified if only manual spot checks exist.
- Prefer Search Console and Analytics exports over screenshots when exact values matter.
- Tie the result decision to one of `KEEP`, `DISCARD`, `ITERATE`, `BLOCKED`, or `STOP`.
