# Testing Rubric

Use this rubric from `/test`, `/review`, and `/kickstart`.

## Critical

| ID | Check | Pass Criteria |
|---|---|---|
| T1 | Behavior coverage | Changed user-visible or API behavior has tests or a documented non-production limitation. |
| T2 | Regression coverage | Bugs include a regression test that fails before the fix or clearly reproduces the risk. |
| T3 | Boundary coverage | External services, databases, queues, file systems, and network calls are tested at boundaries or mocked safely. |
| T4 | Verification command | Every execution graph node has a concrete verification command or manual check. |
| T5 | Smoke path | Deployable products have a smoke test path for startup and primary flow; browser-facing products include `/browser-check` Playwright/browser evidence or an explicit accepted limitation. |
| T6 | Data safety | Migrations, destructive operations, and scrapers have rollback, dry-run, or fixture-based verification. |
| T7 | TDD evidence | Behavior changes record red evidence before implementation and green evidence after minimal implementation, or an explicit owner-approved exception. |

## Important

| ID | Check | Pass Criteria |
|---|---|---|
| I1 | Test pyramid | Unit, integration, and E2E coverage are balanced for the product type. |
| I2 | Contract tests | API, bot, CLI, and integration boundaries have request/response or command contract checks. |
| I3 | Accessibility checks | UI products include accessibility and responsive checks where practical. |
| I4 | Security tests | Auth, permission, rate-limit, upload, and injection-sensitive flows include negative tests. |
| I5 | CI readiness | Build and tests are runnable in CI with documented commands. |
| I6 | Refactor evidence | Refactor steps preserve green tests or document why refactor was not applicable. |

## Product-Type Minimums

| Product Type | Minimum Test Set |
|---|---|
| SaaS | Auth, core CRUD, billing/subscription webhooks if present, permission boundaries, smoke flow |
| Messaging Bot | Command routing, handler flows, state transitions, integration mocks |
| API Service | Route contracts, validation errors, auth/authorization, service logic |
| Web App | Component/form behavior, core user flow, Playwright/browser responsive and accessibility smoke |
| Landing Page | Form submit, analytics hook or lead capture, Playwright/browser responsive smoke |
| CLI Tool | Command parsing, file/stdio behavior, error codes |
| Mini App | Platform auth/init, core UI flow with browser evidence, backend contract |
| E-commerce | Catalog, cart, checkout browser smoke, order state, payment webhook mocks |
| Data Scraper | Fetch retry/rate limit, parser fixtures, storage, scheduler dry run |
| Internal Automation | Workflow state, integration mocks, audit log |
