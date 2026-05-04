# Product Factory Core

This directory defines the Product Factory OS runtime layer.

PFO extends Product Factory OS from a methodology scaffold into a deterministic product generation runtime:

```text
IDEA -> PRODUCT_BLUEPRINT -> BUILD_PLAN -> EXECUTION_GRAPH -> BUILD -> TEST -> VALIDATE -> DEPLOY_READY -> SAVE_STATE
```

## Runtime Responsibilities

- Parse natural-language product intent.
- Classify the product type and complexity.
- Select a reusable product template.
- Compile product intent into build artifacts.
- Execute modules through a state machine.
- Block unsafe transitions through quality gates.
- Use MCP and OpenAI/Codex plugin routes for current documentation, browser smoke checks, GitHub workflow, security scans, and external tool sync.
- Save reloadable project state after every major milestone.

## Core Artifacts

- `PRODUCT_BLUEPRINT.md`: product type, domain, entities, modules, interfaces, dependencies, infrastructure.
- `BUILD_PLAN.md`: ordered module build plan with dependencies and verification.
- `EXECUTION_GRAPH.md`: build nodes, transitions, checkpoints, and gate rules.
- `.codex-memory/STATE.json`: reloadable machine-readable session state.
