# Workspace Defaults

This document describes the mandatory Product Factory OS workspace behavior for `/home/hihol/projects`.

## Files

At workspace root:

```text
AGENTS.md
CODEX.md
PFO_WORKSPACE.json
```

`AGENTS.md` and `CODEX.md` are the human-readable operating rule files. `AGENTS.md` is included so Codex sessions opened directly inside a project or workspace receive the PFO rule without extra prompting.

`PFO_WORKSPACE.json` is the machine-readable policy file for scripts and future tooling.

## Behavior

For every new project in the workspace, Codex must automatically use:

```text
/project -> /kickstart
```

Planning-only and guide-only routes are secondary routes. They are used only when the user explicitly says not to build code or explicitly asks to convert existing docs into a guide.

Voice and natural-language commands are first-class input. The user does not need to manually choose skills, agents, or workflow stages.

After install, the short path is:

```bash
bash install.sh
pfo new <project-name> --idea "<voice transcript or product idea>"
```

The bootstrap creates:

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
```

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

For every existing project, Product Factory OS is also mandatory:

```text
/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save
```

Before major work in an existing project, PFO adoption must already be present. The installer and preflight hook create missing `AGENTS.md`, `CODEX.md`, `.codex-memory/`, and `.pfo/` contracts. If a project was added after install, run `pfo adopt <project> --analyze` or rely on the preflight hook to auto-adopt the first-level workspace project.

Hooks are installed by default in this workspace. They provide auto-adoption, route reminders, preflight context, skill completeness checks, commit completeness checks, and review-before-commit validation. Install or refresh them from the methodology repo with:

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

For non-trivial existing-project changes, create or update the relevant `EXECUTION_GRAPH.md` node. Tiny direct fixes may use the daily-work skill directly only after PFO adoption status and memory state are checked.

Before session transfer, role switch, delegated execution, AFK work, compaction, or recovery, write `HANDOFF.md` with `/handoff`.

Connector-aware work routes through explicit skills:

- Fresh library, SDK, framework, or platform docs -> `/mcp-docs`
- Fresh public market, competitor, ICP, launch, or community signals -> `/market-scan`
- Browser UI smoke, Playwright smoke, or visual QA -> `/browser-check`
- GitHub issue, PR, CI, or release workflow -> `/github-workflow`
- Linear, Notion, Google Drive, or export sync -> `/tool-sync`

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
  "version": "0.6.1",
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
