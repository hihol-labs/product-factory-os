# Workspace Defaults

This document describes the mandatory Product Factory OS workspace behavior and the global auto-connect behavior.

## Files

At workspace root:

```text
AGENTS.md
CODEX.md
PFO_WORKSPACE.json
```

`AGENTS.md` and `CODEX.md` are the human-readable operating rule files. `AGENTS.md` is included so Codex sessions opened directly inside a project or workspace receive the PFO rule without extra prompting.

`PFO_WORKSPACE.json` is the machine-readable policy file for scripts and future tooling.

The installer also writes global policy files:

```text
$CODEX_HOME/PFO_GLOBAL.json
~/.pfo/PFO_GLOBAL.json
```

These files let the preflight hook find the Product Factory OS methodology from any local project folder, even when the project is outside the default workspace.

`PFO_WORKSPACE.json` and `PFO_GLOBAL.json` also carry `codexGoalMode`. This makes Codex `/goal` mode part of the PFO runtime rather than a manual per-session habit.

## Behavior

For every new project request in any local folder where Codex is working, Codex must automatically use:

```text
/project -> /kickstart
```

For every non-trivial PFO project request, Codex must create or continue a `/goal` objective that names the user outcome and the active PFO route. The goal stays active through implementation, gates, verification, and state-save. It is complete only when both the requested outcome and the PFO exit gates are satisfied.

Planning-only and guide-only routes are secondary routes. They are used only when the user explicitly says not to build code or explicitly asks to convert existing docs into a guide.

Voice and natural-language commands are first-class input. The user does not need to manually choose skills, agents, or workflow stages.

After install, the user only needs to describe the product. Codex runs the bootstrap automatically. CLI equivalent:

```bash
bash install.sh
pfo new <project-name> --idea "<voice transcript or product idea>"
```

The bootstrap creates runtime files, starter files, planning artifacts, execution graph, and report:

```text
CODEX.md
AGENTS.md
.codex-memory/MEMORY.md
.codex-memory/STATE.json
.pfo/
.pfo-starter.json
.env.example
.github/workflows/validate.yml
justfile
PFO_REPORT.md
MASTER_CONTEXT.md
ARCHITECTURE.md
TASKS.md
PROGRESS.md
TESTING.md
IDEA_SCORECARD.md
VALIDATION_PLAN.md
PRODUCT_BLUEPRINT.md
PROJECT_ARCHITECTURE.md
BUILD_PLAN.md
EXECUTION_GRAPH.md
TEST_PLAN.md
QUALITY_GATES.md
```

The five uppercase files above are navigation aliases only. For new projects, the canonical sources remain the PFO artifacts created by `pfo plan`.

Repository policy for new projects:

- The local project folder is the canonical starting point.
- If the folder is not already a repository, initialize local Git before implementation so changes are traceable.
- GitHub repository creation is optional. It must not block project bootstrap.
- Publish or connect GitHub only after explicit user request, explicit workspace policy, or `/github-workflow` scope.
- When GitHub is connected, record the remote URL and sync status in PFO state or architecture notes.

`pfo plan` creates the core planning artifacts while preserving files that already exist:

```text
IDEA_SCORECARD.md
VALIDATION_PLAN.md
FEEDBACK_LOG.md
ITERATION_REVIEW.md
FUNNEL_MODEL.md
ASSET_REGISTER.md
CONTENT_BACKLOG.md
PRODUCT_BLUEPRINT.md
PROJECT_ARCHITECTURE.md
BUILD_PLAN.md
EXECUTION_GRAPH.md
TEST_PLAN.md
QUALITY_GATES.md
MASTER_CONTEXT.md
ARCHITECTURE.md
TASKS.md
PROGRESS.md
TESTING.md
```

For non-trivial products, Product Factory OS may also create strategy and security artifacts:

```text
MARKET_BRIEF.md
ICP.md
BUSINESS_MODEL.md
GO_TO_MARKET.md
THREAT_MODEL.md
DATA_CLASSIFICATION.md
```

For every existing project, including projects outside the default workspace, Product Factory OS is also mandatory:

```text
/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save
```

The same default `/goal` rule applies to existing projects before the `/task` route starts. The goal objective should include the requested change and the selected daily-work route.

Before any work in an existing project, full PFO adoption must already be present. The installer and preflight hook create missing `AGENTS.md`, `CODEX.md`, `.codex-memory/`, `.pfo/` contracts, existing-project-safe alias indexes, analysis, contract gate output, `NEXT_STEP.md`, and `PFO_REPORT.md`. If a project was added after install, run `pfo adopt <project>` or rely on the preflight hook to auto-enforce full runtime for the detected project root.

Existing-project alias indexes must link only to files that exist. Missing Product Compiler docs such as `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md`, or `QUALITY_GATES.md` are not linked until intentionally created.

Existing-project work must select the smallest route profile that fits the risk:

| Profile | Default Use | Gates |
|---|---|---|
| `minimal` | Small, no-risk tasks | adoption, scope, targeted verification, review, state-save |
| `standard` | Normal existing-code work | adoption, analysis, classification, scoped manifest, targeted verification, review, state-save |
| `full` | Product, release, deploy, migration, security, hardening, or broad architecture work | planning, full verification, release-grade review, branch finish, state-save |

The minimal profile must not require Product Compiler planning documents. `pfo next-best-action` and `pfo manifest --profile minimal` keep small tasks limited to adoption, scope, targeted verification, review, and state-save. `pfo metrics` reports `artifactDebt` so the active route shows which documents are really required and which tracked artifacts are outside the current route.

Hooks are installed by default. They provide global/workspace auto-adoption, route reminders, preflight context, pre-tool security guardrails, pre/post context-budget routing for large outputs and raw HTTP, skill completeness checks, commit completeness checks, and review-before-commit validation. Install or refresh them from the methodology repo with:

```bash
bash install.sh
```

Existing-project state path:

```text
EXISTING_PROJECT_DETECTED
  -> ADOPTION_REQUIRED
  -> ADOPTED
  -> EXISTING_PROJECT_ANALYZED
  -> TASK_CLASSIFIED
  -> PLAN_READY
```

For non-trivial existing-project changes, create or update the relevant `EXECUTION_GRAPH.md` node. Tiny direct fixes use the `minimal` route profile after PFO adoption status and memory state are checked.

Before session transfer, role switch, delegated execution, AFK work, compaction, or recovery, write `HANDOFF.md` with `/handoff`.

For long sessions, build searchable memory with `pfo context-index <project>`, query it with `pfo context-search <project> <query>`, and keep `.codex-memory/resume-snapshot.md` current through `pfo context-snapshot`, `pfo resume`, or `/handoff`.

Connector-aware work routes through explicit skills:

- Fresh library, SDK, framework, or platform docs -> `/mcp-docs`
- Fresh public market, competitor, ICP, launch, or community signals -> `/market-scan`
- Browser UI smoke, Playwright smoke, or visual QA -> `/browser-check`
- GitHub issue, PR, CI, or release workflow -> `/github-workflow`
- Linear, Notion, Google Drive, or export sync -> `/tool-sync`
- Obsidian vault, wikilinks, linked notes, or local knowledge graph -> `/obsidian-export`

## Precedence

1. Workspace root `AGENTS.md` and `CODEX.md` mandatory Product Factory OS rule for new and existing project work.
2. Explicit user instruction for product-specific scope, stack, domain, or deployment constraints.
3. Project-local `AGENTS.md` and `CODEX.md` for additional project constraints.
4. Product Factory OS methodology defaults.

Project-local instructions may add constraints, but they do not replace the workspace Product Factory OS lifecycle for new or existing project work.

## Plugin Registry Note

In some environments `.agents/` or `.codex/` may be mounted read-only. In that case, keep the workspace policy files above and register the plugin later when a writable plugin registry is available.

The intended marketplace entry is:

```json
{
  "name": "product-factory-os",
  "displayName": "Product Factory OS",
  "version": "1.0.0",
  "source": {
    "source": "local",
    "path": "./product-factory-os"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity",
  "capabilities": [
    "Product Planning",
    "Execution Graph",
    "Code Generation",
    "Testing",
    "Deployment",
    "Memory",
    "Integrations",
    "Browser QA",
    "Hook Gates",
    "Route Snapshots"
  ]
}
```
