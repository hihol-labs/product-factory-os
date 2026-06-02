# Install And Onboarding

Product Factory OS is a Codex plugin-style repository plus an executable local runtime. The fastest path is:

```bash
git clone https://github.com/hihol-labs/product-factory-os.git
cd product-factory-os
bash install.sh
```

If the repository is not cloned inside your projects workspace:

```bash
bash install.sh --workspace ~/Projects
```

The installer validates the repository, installs the `pfo` command, installs hooks, writes workspace `AGENTS.md`, `CODEX.md`, `PFO_WORKSPACE.json`, and global `PFO_GLOBAL.json` policy files with default-on Codex `/goal` mode, then fully adopts existing first-level projects by creating missing project-level `AGENTS.md`, `CODEX.md`, `.codex-memory/`, `.pfo/`, analysis, contract gate output, `NEXT_STEP.md`, and `PFO_REPORT.md`.

The repository can be used in two modes:

- **Plugin mode:** Codex loads `.codex-plugin/plugin.json`, skills, and hook metadata.
- **Runtime mode:** `scripts/pfo.py` bootstraps, plans, analyzes, validates, reports, and exports PFO projects from the command line.

## Local Development

Clone or copy the repository:

```bash
git clone https://github.com/hihol-labs/product-factory-os.git
cd product-factory-os
```

Run validation:

```bash
python3 scripts/validate_structure.py
python3 scripts/validate_plan_quality.py /path/to/project
python3 scripts/validate_control_harness.py
python3 scripts/run_fixtures.py
python3 scripts/verify_triggers.py
python3 scripts/verify_fixture_contracts.py
python3 scripts/run_headless_fixtures.py --mode mock
python3 scripts/verify_skill_profiles.py
python3 scripts/validate_execution_graph.py
python3 scripts/validate_state.py /path/to/project/.codex-memory/STATE.json
python3 scripts/validate_runtime.py
python3 scripts/validate_context_runtime.py
python3 scripts/validate_tool_registry.py docs/templates/pfo/TOOL_CAPABILITY_REGISTRY.json integrations/tool-capability-registry.json
python3 scripts/validate_seo_growth_gate.py --self-check
python3 scripts/validate_security_report.py --self-check
python3 scripts/validate_hooks.py
python3 scripts/verify_manifest_drift.py
python3 scripts/verify_install_sync.py
python3 scripts/meta_review.py
python3 scripts/production_readiness.py
```

Real Codex-backed behavioural execution is optional and budgeted:

```bash
python3 scripts/run_headless_fixtures.py --mode command \
  --fixture planning-only \
  --output-root .pfo-headless-runs/live \
  --command-template 'python3 {root}/scripts/pfo_headless_adapter.py'
```

The validator also checks the Product Factory OS runtime layer:

```text
core/
routing/
templates/
pipelines/
execution/
memory/
deployment/
interface/
```

## Local Plugin Shape

The required plugin manifest lives at:

```text
.codex-plugin/plugin.json
```

It points to:

```text
skills: ./skills/
hooks: ./hooks/hooks.json
```

## Hook Installation

Hooks are installed by default:

```bash
bash install.sh
python3 scripts/validate_hooks.py
```

Installed hook layers:

- `route-reminder.py`: suggests `/project`, `/task`, or a specialized PFO skill.
- `preflight-context.py`: auto-enforces full PFO runtime for workspace projects and any local project discovered through `PFO_GLOBAL.json`, then prints discovered docs, state, memory, `.pfo/` contracts, and the default Codex `/goal` mode reminder.
- `session-diagnostics.py`: reports stale state, recovery, handoff, and telemetry warnings from project memory.
- `skill-completeness.py`: checks skills against contracts, triggers, fixtures, and route snapshots.
- `commit-completeness.py`: checks staged methodology diffs for supporting artifacts.
- `review-before-commit.py`: runs fast PFO validators before committing methodology changes.

See `hooks/README.md` for hook policy and smoke commands.

## Manual Smoke Test

Use these prompts in a Codex session after making the plugin available to your local plugin loader:

```text
I want to build a booking app for private tutors.
```

Expected route:

```text
/project -> /kickstart
```

```text
Мне нужно сначала подготовить план и архитектуру для заказчика. Код пока не пишем.
```

Expected route:

```text
/project -> /blueprint
```

```text
Проверь безопасность текущего API перед релизом.
```

Expected route:

```text
/task -> /security-audit
```

```text
Сделай Telegram бот для продаж с CRM и уведомлениями.
```

Expected route:

```text
/project -> /kickstart
```

## Release Checklist

Before tagging a version:

1. Update `.codex-plugin/plugin.json`.
2. Update `CHANGELOG.md`.
3. Run all validation scripts.
4. Confirm examples and fixtures still match the expected routes.
5. Check that new or changed skills are listed in `docs/SKILL_CONTRACTS.md` and `docs/TRIGGERS.md`.
6. Check that PFO runtime JSON contracts are valid.
7. Validate example execution graphs with `python3 scripts/validate_execution_graph.py`.
8. Validate the control harness with `python3 scripts/validate_control_harness.py`.
9. Validate context budget/search/snapshot wiring with `python3 scripts/validate_context_runtime.py`.

## Workspace Adoption Check

From the methodology repository:

```bash
python3 scripts/adoption_check.py
```

To create or refresh full PFO runtime files for all first-level projects in the workspace:

```bash
pfo adopt
```

This creates missing `AGENTS.md`, `CODEX.md`, `.codex-memory/`, and `.pfo/` contracts without overwriting existing project instructions, then runs repository analysis and writes `PFO_REPORT.md`.

## New Project Bootstrap

New projects are Product Factory OS projects by default. Codex should run this automatically when a user asks for a new product, whether the project is in the default workspace or another local folder:

```bash
pfo new my-product --idea "voice transcript or product idea"
```

This creates runtime files, starter files, planning artifacts, execution graph, and report:

```text
CODEX.md
AGENTS.md
.codex-memory/MEMORY.md
.codex-memory/STATE.json
.pfo/
.pfo-starter.json
.github/workflows/validate.yml
justfile
PFO_REPORT.md
IDEA_SCORECARD.md
VALIDATION_PLAN.md
PRODUCT_BLUEPRINT.md
PROJECT_ARCHITECTURE.md
BUILD_PLAN.md
EXECUTION_GRAPH.md
TEST_PLAN.md
QUALITY_GATES.md
```

Manual refresh remains available:

```bash
pfo plan ../my-product
pfo validate ../my-product
```

`pfo plan` creates missing `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md`, `FEEDBACK_LOG.md`, `ITERATION_REVIEW.md`, `FUNNEL_MODEL.md`, `ASSET_REGISTER.md`, `CONTENT_BACKLOG.md`, `SEO_GROWTH_GUARANTEE_GATE.md`, `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md`, and `QUALITY_GATES.md` while preserving files that already exist.

## Runtime CLI

```bash
pfo new my-product --idea "voice transcript or product idea"
pfo adopt ../existing-product
pfo analyze ../existing-product --run-gates --report
pfo discuss ../my-product --phase phase-1
pfo plan ../my-product
pfo manifest ../my-product --unit N1
pfo handoff ../my-product --from-role planner --to-role implementer --reason role-switch
pfo build ../my-product
pfo test ../my-product
pfo tdd-evidence ../my-product --red "pytest ... failed as expected" --green "pytest ... passed"
pfo root-cause ../my-product --summary "bad value enters parser" --evidence "trace shows parser input"
pfo verify-work ../my-product --evidence "tests passed" --pass-gate
pfo review-stage ../my-product --stage spec --status PASSED --evidence "matches manifest"
pfo review-stage ../my-product --stage quality --status PASSED --evidence "tests and review clean"
pfo review ../my-product
pfo validate ../my-product
pfo status ../my-product
pfo resume ../my-product
pfo report ../my-product
pfo finish-branch ../my-product --mode pr --verification "checks passed"
pfo brief ../my-product --mode recap
pfo learnings ../my-product --lesson "keep fallback explicit"
pfo metrics
pfo export ../my-product --target github
pfo export ../my-product --target google-drive
```

## OpenAI And MCP Integrations

Connector-aware workflows are documented in `docs/OPENAI_MCP_INTEGRATIONS.md`.

Use `/mcp-docs` for Context7 documentation checks, `/browser-check` for local UI smoke tests, `/github-workflow` for PR/CI/release work, and `/tool-sync` for Linear, Notion, Google Drive, or export-only synchronization.

## Benchmarks

```bash
python3 scripts/run_benchmarks.py
```

## Dashboard

Open `dashboard/index.html` locally or generate metrics:

```bash
python3 scripts/pfo.py metrics --workspace /home/hihol/projects > dashboard/metrics.json
```

The metrics payload includes `harnessEfficiency`, a comparable signal for recent methodology effectiveness:

- `timeToFirstValidUnitSeconds`: seconds from unit manifest to first passing verification.
- `repairLoopsPerVerifiedUnit`: lower is better; repeated blockers or failed validations increase it.
- `verificationPassRate` and `gatePassRate`: higher means the harness is catching and guiding work before late review.

## Release Check

```bash
python3 scripts/release_check.py
```

## Troubleshooting

**`pfo validate` says planning files are missing.** Run `python3 scripts/pfo.py plan <project>` first, then fill or approve the generated TBD fields.

**A hook blocks a commit.** Run `python3 hooks/review-before-commit.py --full` and update the supporting docs, snapshots, or changelog named by the hook.

**Codex did not pick the expected skill.** Run `python3 hooks/route-reminder.py "<your prompt>"` and add a fixture plus snapshot if the route should be recognized.
