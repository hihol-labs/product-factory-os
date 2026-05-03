# Fallback Policy Gate

Purpose: make fallback behavior explicit and safe.

Universal rule:

- Fallbacks are allowed for resilience, retries, graceful errors, degraded modes, and development fixtures.
- Production fallbacks must not fabricate business results, provider responses, prices, legal/medical facts, user demand, analytics, or other real-world data.
- User-facing fallback output must be clearly labeled as degraded/unavailable unless the project contract says otherwise.

Project-owned inputs:

- `.pfo/FALLBACK_POLICY.md`
- `.pfo/DATA_POLICY.md`

Gate output:

- `PASS`: fallback behavior follows policy.
- `PASS_WITH_WARNINGS`: fallback appears only in non-production/test context.
- `BLOCKED`: fallback silently substitutes real production output.

