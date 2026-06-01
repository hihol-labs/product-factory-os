# Execution Graph

## State

```text
CURRENT_STATE: PLAN_READY
NEXT_STATE: BUILDING
```

## Nodes

| Node | Module Or Stage | Inputs | Outputs | Validation |
|---|---|---|---|---|
| N1 | scaffold | architecture docs | project skeleton | build command exists |
| N2 | database | blueprint entities | schema/models | schema verification |
| N3 | auth | user entity | auth flow | auth tests |
| N4 | tutor-profile | auth | profile CRUD | profile tests |
| N5 | availability | profile | slot management | availability tests |
| N6 | booking | availability | booking flow | booking conflict tests |
| N7 | dashboard | API modules | UI flows | smoke test |
| N8 | deploy-ready | complete build | Docker/env docs | readiness gate |

## Transitions

| From | To | Requires | On Failure |
|---|---|---|---|
| PLAN_READY | BUILDING | review not blocked and next step approved | fix planning docs or NEXT_STEP.md |
| N1 | N2 | scaffold verified | repair scaffold |
| N2 | N3 | schema verified | fix schema |
| N3 | N4 | auth tests pass | fix auth |
| N4 | N5 | profile tests pass | fix profile |
| N5 | N6 | availability tests pass | fix slots |
| N6 | N7 | booking tests pass | fix booking |
| N7 | N8 | smoke test passes | fix UI flow |
| N8 | READY_FOR_DEPLOY | quality gates pass | DEPLOY_BLOCKED |

## Validation Checkpoints

- Architecture Validation: required before N1.
- Next Step Approval: required before each major implementation node starts.
- Dependency Check: required before N8.
- Test Coverage Check: required after N3-N7.
- Security Review: required before deploy-ready.
- Deployment Validation: required at N8.

## Repair Paths

Failed module validation returns to the same node. Failed deployment readiness returns to N8. Failed architecture validation returns to planning docs.
