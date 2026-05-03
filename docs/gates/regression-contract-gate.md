# Regression Contract Gate

Purpose: prevent accidental changes to established behavior.

Universal rule:

- Stable product behavior must be documented as contracts.
- Diffs that alter contract behavior must be classified as intentional product changes, not incidental fixes.
- Contract changes require explicit rationale and updated tests/golden flows.

Project-owned inputs:

- `.pfo/PROJECT_CONTRACT.md`
- `.pfo/GOLDEN_FLOWS.md`
- `.pfo/FORBIDDEN_CHANGES.md`

Gate output:

- `PASS`: behavior contracts remain intact or are intentionally updated with evidence.
- `PASS_WITH_WARNINGS`: contracts exist but coverage is incomplete.
- `BLOCKED`: diff changes contract behavior without scope/rationale.

