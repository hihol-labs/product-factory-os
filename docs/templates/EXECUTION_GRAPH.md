# Execution Graph

## State

```text
CURRENT_STATE:
NEXT_STATE:
```

## Nodes

| Node | Module Or Stage | Inputs | Outputs | Validation | Dependencies |
|---|---|---|---|---|---|

## Transitions

| From | To | Requires | On Failure |
|---|---|---|---|

## Validation Checkpoints

- Unit Context Manifest:
- Architecture Validation:
- Dependency Check:
- Test Coverage Check:
- Security Review:
- Deployment Validation:

## Repair Paths

- Missing or ambiguous verification evidence -> `RECOVERY_REQUIRED` -> `PFO_RECOVERY.md`.
- Scope, data, fallback, or golden-flow contract failure -> repair before next unit.
