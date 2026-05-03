# Golden Flow Tests Gate

Purpose: preserve the product's most important user journeys.

Universal rule:

- Each project must define the minimum flows that prove the product still works.
- When a task touches a golden flow, the flow must be tested or explicitly marked blocked.
- Golden flow failures block deployment.

Project-owned inputs:

- `.pfo/GOLDEN_FLOWS.md`
- project test commands
- manual verification notes when automation is not available

Gate output:

- `PASS`: golden flows were verified.
- `PASS_WITH_WARNINGS`: flows exist but only partial evidence is available.
- `BLOCKED`: a touched golden flow is not verified or is failing.

