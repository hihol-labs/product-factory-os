# Starter Packs

Starter packs are machine-readable runtime templates used by Product Factory OS.

Each `STARTER.json` declares:

- product type
- stack
- folders
- commands
- required artifacts

The starter layer keeps product generation repeatable: PFO chooses a starter pack instead of inventing a scaffold from scratch.

Starter stacks follow `PFO Default Stack v1` as a golden path, not a hard lock. Product-specific deviations are valid when `PROJECT_ARCHITECTURE.md` records the reason, risk, support cost, and verification impact.

`pfo plan` uses the selected starter to generate missing planning artifacts:

- `PRODUCT_BLUEPRINT.md`
- `PROJECT_ARCHITECTURE.md`
- `BUILD_PLAN.md`
- `EXECUTION_GRAPH.md`
- `TEST_PLAN.md`
- `QUALITY_GATES.md`

Starter files must remain compatible with `scripts/validate_runtime.py`, `scripts/validate_project.py`, and the generated-project CI templates.
