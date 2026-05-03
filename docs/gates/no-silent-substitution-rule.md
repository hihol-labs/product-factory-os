# No Silent Substitution Rule

Purpose: prevent hidden replacement of real behavior with synthetic behavior.

Universal rule:

- When a dependency, provider, database, API, or external source fails, the product must not silently substitute invented production results.
- Acceptable responses include retry, queue, cached result with clear freshness metadata, degraded/unavailable status, or explicit error.
- Unacceptable responses include fabricated provider answers, fake demand, fake prices, fake analytics, fake compliance output, or mock business entities presented as real.

Project-owned inputs:

- `.pfo/DATA_POLICY.md`
- `.pfo/FALLBACK_POLICY.md`
- `.pfo/FORBIDDEN_CHANGES.md`

Gate output:

- `PASS`: failures are handled transparently.
- `PASS_WITH_WARNINGS`: substitution risk exists only in tests/dev fixtures.
- `BLOCKED`: production path contains silent synthetic substitution.

