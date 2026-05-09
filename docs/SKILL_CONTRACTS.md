# Skill Contracts

| Skill | Input | Output | Side Effects | Idempotency |
|---|---|---|---|---|
| `/project` | Product idea | Route decision | None | Safe |
| `/task` | Existing-project task | Route decision | None | Safe |
| `/discover` | Idea or problem | `DISCOVERY.md` | Writes docs | Ask before overwrite |
| `/blueprint` | Idea plus clarifications | Planning documents plus `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md`, `QUALITY_GATES.md` | Writes docs | Ask before overwrite |
| `/guide` | Existing planning docs | `CODEX_GUIDE.md` | Writes docs | Safe if generated from same inputs |
| `/kickstart` | Idea or approved PFO docs | Project docs, scaffold, code, state updates | Writes code/docs/memory | Stateful |
| `/review` | Project path or changed files | Review report | Read-only by default | Safe |
| `/test` | File, module, feature | Test files or test plan | Writes tests | Safe if tests are absent |
| `/bugfix` | Symptom, error, failing test | Root-cause fix | Writes code/tests | Stateful |
| `/refactor` | Area to improve | Behavior-preserving patch | Writes code | Requires tests |
| `/doc` | Module or docs target | Updated docs | Writes docs/comments | Safe |
| `/explain` | File or concept | Explanation | None | Safe |
| `/security-audit` | Project or path | Security report | Read-only | Safe |
| `/deps-audit` | Manifests or lockfiles | Supply-chain report | Read-only | Safe |
| `/mcp-docs` | Library, framework, SDK, or API question | Documentation decision and implementation impact | External MCP or official-doc lookup | Safe |
| `/perf` | Slow path or complaint | Bottleneck report and patch | Writes code optionally | Measure between runs |
| `/browser-check` | Local URL or user flow | Browser smoke result and evidence | Opens local browser target | Safe |
| `/harden` | Service or project | Hardening report/artifacts | Writes only with approval | Stateful |
| `/infra` | Target platform | IaC files | Writes `infra/` | Deterministic per input |
| `/deploy` | Service and target | Deployment result | Production impact | Requires confirmation |
| `/migrate` | Migration target | Applied migration/report | DB impact | Requires confirmation for prod |
| `/github-workflow` | Issue, PR, check run, branch, or release | GitHub status, CI/PR actions, export payload | External GitHub reads/writes with approval | Stateful |
| `/tool-sync` | PFO artifacts and target tool | Connector sync result or `.pfo-integrations/` payload | External writes only with approval | Reconcile by source artifact |
| `/session-save` | Session summary and PFO state | Memory files and `.codex-memory/STATE.json` | Writes memory docs/state | Creates or updates state |
| `/advisor` | Decision or question | Analysis report | None | Safe |
| `/strategy` | Existing project context | Strategy docs/backlog | Writes docs | Safe with review |
| `/adopt` | Existing repository | `AGENTS.md`, `CODEX.md`, `.codex-memory/`, `.pfo/` contracts when required | Writes project metadata | Marker-based |
