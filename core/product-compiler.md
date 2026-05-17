# Product Compiler

The product compiler turns a raw idea into deterministic build artifacts. In the local runtime, `pfo plan <project>` writes missing compiler artifacts while preserving existing user-authored files.

## Compilation Stages

```text
Idea
  -> Intent Model
  -> Product Classification
  -> Idea Scorecard
  -> Validation Plan
  -> Architecture Selection
  -> Product Blueprint
  -> Phase Context
  -> Build Plan
  -> Execution Graph
  -> Unit Context Manifest
  -> TDD And Review Gates
  -> Feedback, Assets, And Content
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

### 3. Idea Scorecard

Write `IDEA_SCORECARD.md` with:

- evidence-backed score
- weak assumptions
- KILL, TEST, or BUILD decision
- kill criteria

### 4. Validation Plan

Write `VALIDATION_PLAN.md` with:

- riskiest assumptions
- validation experiments
- expected and actual signals
- continue, pivot, or stop decision

### 5. Architecture Selection

Select:

- Monolith for small local MVPs
- Modular monolith for multi-module products
- Microservices only when scale, team, or isolation requirements justify it

### 6. Product Blueprint

Write `PRODUCT_BLUEPRINT.md` with:

- Business logic
- Entities
- Modules
- Interfaces
- Dependencies
- Infrastructure
- Risks

### 7. Phase Context

Write `PHASE_CONTEXT.md` with:

- implementation decisions
- assumptions
- open questions
- planning impact

### 8. Build Plan

Write `BUILD_PLAN.md` with:

- Module order
- Dependencies
- Files likely touched
- Verification per module
- Exit criteria

### 9. Execution Graph

Write `EXECUTION_GRAPH.md` with:

- Nodes
- Transitions
- Validation checkpoints
- Rollback or repair action for failed gates

### 10. Unit Context Manifest

Write `.pfo/UNIT_CONTEXT_MANIFEST.json` before autonomous or delegated execution with:

- unit id and goal
- required inputs
- allowed write areas
- forbidden changes
- verification commands
- gates and recovery behavior

### 11. Test And Gate Plan

Write `TEST_PLAN.md` and `QUALITY_GATES.md` with:

- Product-type test matrix
- Critical smoke path
- TDD red/green/refactor evidence fields
- Root-cause evidence for bugfixes
- Spec compliance and code quality review stages
- Branch finish decision and cleanup evidence
- Required quality gates
- Evidence slots
- Accepted-risk section

### 12. Feedback, Assets, And Content

Write or update:

- `FEEDBACK_LOG.md`
- `ITERATION_REVIEW.md`
- `FUNNEL_MODEL.md`
- `ASSET_REGISTER.md`
- `CONTENT_BACKLOG.md`

These artifacts keep iteration tied to evidence and turn repeatable outcomes into reusable assets.
