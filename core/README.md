# Product Factory Core

This directory defines the Product Factory OS runtime layer.

PFO is a deterministic product generation runtime for Codex:

```text
IDEA -> PRODUCT_BLUEPRINT -> BUILD_PLAN -> EXECUTION_GRAPH -> BUILD -> TEST -> VALIDATE -> DEPLOY_READY -> SAVE_STATE
```

## Runtime Responsibilities

- Parse natural-language product intent.
- Classify the product type and complexity.
- Select a reusable product template.
- Compile product intent into build artifacts.
- Generate missing planning artifacts through `pfo plan` while preserving existing files.
- Execute modules through a state machine.
- Block unsafe transitions through quality gates.
- Keep route snapshots, hook contracts, and fixtures aligned.
- Use MCP and OpenAI/Codex plugin routes for current documentation, browser smoke checks, GitHub workflow, security scans, and external tool sync.
- Save reloadable project state after every major milestone.

## Core Artifacts

- `PRODUCT_BLUEPRINT.md`: product type, domain, entities, modules, interfaces, dependencies, infrastructure.
- `BUILD_PLAN.md`: ordered module build plan with dependencies and verification.
- `EXECUTION_GRAPH.md`: build nodes, transitions, checkpoints, and gate rules.
- `TEST_PLAN.md`: product-specific test matrix and smoke path.
- `QUALITY_GATES.md`: gate status, evidence, blockers, and accepted risks.
- `.codex-memory/STATE.json`: reloadable machine-readable session state.
- `.pfo/*`: project-owned scope, data, fallback, golden-flow, and regression contracts.
