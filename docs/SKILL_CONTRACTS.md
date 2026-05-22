# Skill Contracts

Every skill frontmatter must declare:

- `effort`: `low`, `medium`, or `high`.
- `side_effect`: the highest expected mutation or external interaction class.
- `explicit_invocation`: `true` for production, migration, infrastructure, external-write, or other high-impact routes.

`scripts/verify_skill_profiles.py` enforces these fields and checks that every skill has a `## Self-validation` section.

| Skill | Input | Output | Side Effects | Idempotency |
|---|---|---|---|---|
| `/project` | Product idea | Route decision | None | Safe |
| `/task` | Existing-project task | Route decision | None | Safe |
| `/discover` | Idea or problem | `DISCOVERY.md`, `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md` | Writes docs | Ask before overwrite |
| `/market-scan` | Idea, problem, segment, competitor, or launch question | Fresh public market/community signals normalized into `MARKET_BRIEF.md`, `VALIDATION_PLAN.md`, `FEEDBACK_LOG.md`, or `CONTENT_BACKLOG.md` | External public research, writes docs when approved | Append dated evidence |
| `/blueprint` | Idea plus clarifications | Planning documents plus `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md`, `FUNNEL_MODEL.md`, `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `PHASE_CONTEXT.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md`, `QUALITY_GATES.md`, optional `HANDOFF.md` | Writes docs | Ask before overwrite |
| `/guide` | Existing planning docs | `CODEX_GUIDE.md` | Writes docs | Safe if generated from same inputs |
| `/kickstart` | Idea or approved PFO docs | Project docs, scaffold, `.pfo/UNIT_CONTEXT_MANIFEST.json`, code, state updates | Writes code/docs/memory | Stateful |
| `/review` | Project path or changed files | Spec compliance review, code quality review, review report | Read-only by default | Safe |
| `/test` | File, module, feature | Test files, test plan, TDD red/green/refactor evidence | Writes tests/state | Safe if tests are absent |
| `/bugfix` | Symptom, error, failing test | `ROOT_CAUSE.md`, regression test, root-cause fix | Writes code/tests/docs | Stateful |
| `/refactor` | Area to improve | Behavior-preserving patch | Writes code | Requires tests |
| `/doc` | Module or docs target | Updated docs | Writes docs/comments | Safe |
| `/explain` | File or concept | Explanation | None | Safe |
| `/security-audit` | Project or path | Security report | Read-only | Safe |
| `/deps-audit` | Manifests or lockfiles | Supply-chain report | Read-only | Safe |
| `/mcp-docs` | Library, framework, SDK, or API question | Documentation decision and implementation impact | External MCP or official-doc lookup | Safe |
| `/skill-create` | Skill idea, workflow examples, or existing skill path | New or updated PFO skill plus contract, trigger, fixture, and route snapshot updates | Writes methodology files | Ask before overwrite |
| `/perf` | Slow path or complaint | Bottleneck report and patch | Writes code optionally | Measure between runs |
| `/browser-check` | Local URL or user flow | Browser smoke result, engine, screenshots/log evidence | Opens local browser target or runs local Playwright harness | Safe |
| `/harden` | Service or project | Hardening report/artifacts | Writes only with approval | Stateful |
| `/infra` | Target platform | IaC files | Writes `infra/` | Deterministic per input |
| `/deploy` | Service and target | Deployment result | Production impact | Requires confirmation |
| `/migrate` | Migration target | Applied migration/report | DB impact | Requires confirmation for prod |
| `/github-workflow` | Issue, PR, check run, branch, or release | GitHub status, CI/PR actions, branch finish evidence, export payload | External GitHub reads/writes with approval | Stateful |
| `/tool-sync` | PFO artifacts and target tool | Connector sync result or `.pfo-integrations/` payload | External writes only with approval | Reconcile by source artifact |
| `/obsidian-export` | PFO project docs, memory, handoff, state, decisions, and gates | `.pfo-integrations/obsidian/PROJECT_INDEX.md`, `KNOWLEDGE_GRAPH.md`, and linked notes | Writes generated local export docs and updates knowledge log | Rebuildable from canonical PFO artifacts |
| `/handoff` | Session, role, delegation, compaction, AFK, or recovery transfer context | `HANDOFF.md`, `.codex-memory/STATE.json` handoff state | Writes current transfer artifact/state | Overwrites current handoff |
| `/session-save` | Session summary and PFO state | Memory files, `.codex-memory/STATE.json`, optional `.codex-memory/LEARNINGS.md` | Writes memory docs/state | Creates or updates state |
| `/advisor` | Decision or question | Analysis report | None | Safe |
| `/grill-me` | Plan, design, strategy, architecture, migration, deploy, or decision | One-question-at-a-time decision stress test with recommended answers | None | Safe |
| `/strategy` | Existing project context | Strategy, validation, funnel, feedback, experiment loop, asset, and backlog docs | Writes docs | Safe with review |
| `/adopt` | Existing repository | `AGENTS.md`, `CODEX.md`, `.codex-memory/`, `.pfo/` contracts when required | Writes project metadata | Marker-based |
