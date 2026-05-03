# Data Authenticity Gate

Purpose: protect products from fake, synthetic, or mislabeled data in production paths.

Universal rule:

- Data shown as real must come from an approved real source.
- Synthetic, fixture, seed, demo, mock, or fallback data must never be labeled as production truth.
- If a real data source is unavailable, the system must return an explicit unavailable/degraded status instead of inventing data.

Project-owned inputs:

- `.pfo/DATA_POLICY.md`
- `.pfo/PROJECT_CONTRACT.md`
- `.pfo/FALLBACK_POLICY.md`

Gate output:

- `PASS`: real/synthetic boundaries are explicit and respected.
- `PASS_WITH_WARNINGS`: project has a data policy but diff touches data paths without enough evidence.
- `BLOCKED`: production code introduces fake/mock/fallback data as real output.

