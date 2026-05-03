# Build Plan

## Module Order

| Step | Module | Dependencies | Files Likely Touched | Verification | Exit Criteria |
|---:|---|---|---|---|---|
| 1 | scaffold | none | manifests, src/, tests/, README.md | run install/build command | project starts locally |
| 2 | database | scaffold | schema, models, migrations | migration or schema test | entities exist |
| 3 | auth | database | auth routes, session code, tests | auth tests | users can sign up and log in |
| 4 | tutor-profile | auth | profile routes/pages/tests | profile tests | tutor profile CRUD works |
| 5 | availability | auth, profile | slot routes/pages/tests | availability tests | tutors can publish slots |
| 6 | booking | auth, availability | booking routes/pages/tests | booking tests | students can book available slots |
| 7 | dashboard | auth, modules | UI pages/components/tests | smoke or UI tests | core flows are reachable |
| 8 | deploy-ready | all modules | Dockerfile, .env.example, README.md | build and health check | local Docker path documented |

## Cross-Module Dependencies

Auth and database are base modules. Booking depends on availability conflict checks.

## Test Strategy

Use regression-capable tests for auth, slot creation, and booking conflict prevention.

## Gate Strategy

Run review before implementation, tests after each behavior module, and production hardening before deployment.

## Deferred Work

- Payments
- Calendar sync
- Admin moderation

