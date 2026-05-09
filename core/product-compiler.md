# Product Compiler

The product compiler turns a raw idea into deterministic build artifacts. In the local runtime, `pfo plan <project>` writes missing compiler artifacts while preserving existing user-authored files.

## Compilation Stages

```text
Idea
  -> Intent Model
  -> Product Classification
  -> Architecture Selection
  -> Product Blueprint
  -> Build Plan
  -> Execution Graph
```

## Stage Contracts

### 1. Intent Model

Capture:

- User goal
- Product audience
- Domain
- Must-have flows
- Constraints
- Deployment preference

### 2. Product Classification

Use `routing/product-classifier.json` to produce:

```text
PRODUCT_TYPE:
DOMAIN:
COMPLEXITY:
REQUIRED_MODULES:
INFRASTRUCTURE:
```

### 3. Architecture Selection

Select:

- Monolith for small local MVPs
- Modular monolith for multi-module products
- Microservices only when scale, team, or isolation requirements justify it

### 4. Product Blueprint

Write `PRODUCT_BLUEPRINT.md` with:

- Business logic
- Entities
- Modules
- Interfaces
- Dependencies
- Infrastructure
- Risks

### 5. Build Plan

Write `BUILD_PLAN.md` with:

- Module order
- Dependencies
- Files likely touched
- Verification per module
- Exit criteria

### 6. Execution Graph

Write `EXECUTION_GRAPH.md` with:

- Nodes
- Transitions
- Validation checkpoints
- Rollback or repair action for failed gates

### 7. Test And Gate Plan

Write `TEST_PLAN.md` and `QUALITY_GATES.md` with:

- Product-type test matrix
- Critical smoke path
- Required quality gates
- Evidence slots
- Accepted-risk section
