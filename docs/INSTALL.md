# Install And Onboarding

Product Factory OS is a Codex plugin-style repository plus an executable local runtime. The fastest path is:

```bash
git clone https://github.com/hihol-labs/product-factory-os.git
cd product-factory-os
bash packaging/install.sh --install-hooks
python3 scripts/pfo.py new smoke-product --workspace /tmp --idea "Smoke SaaS product"
python3 scripts/pfo.py plan /tmp/smoke-product
python3 scripts/pfo.py validate /tmp/smoke-product
```

Expected result:

```text
OK: plan stage recorded
OK: validated PFO project /tmp/smoke-product
```

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
python3 scripts/run_fixtures.py
python3 scripts/validate_execution_graph.py
python3 scripts/validate_state.py /path/to/project/.codex-memory/STATE.json
python3 scripts/validate_runtime.py
python3 scripts/validate_hooks.py
python3 scripts/meta_review.py
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

Hooks are optional but recommended for daily work:

```bash
bash packaging/install.sh --install-hooks
python3 scripts/validate_hooks.py
```

Installed hook layers:

- `route-reminder.py`: suggests `/project`, `/task`, or a specialized PFO skill.
- `preflight-context.py`: prints discovered docs, state, memory, and `.pfo/` contracts.
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

## Workspace Adoption Check

From the methodology repository:

```bash
python3 scripts/adoption_check.py
```

To create minimal `CODEX.md` and `.codex-memory/MEMORY.md` files for all first-level projects in the workspace:

```bash
python3 scripts/adoption_check.py --write
```

Use `--write` only when you intentionally want to onboard existing projects into the workspace defaults.

## New Project Bootstrap

New projects in `/home/hihol/projects` are Product Factory OS projects by default. To create the directory and initial PFO adoption files:

```bash
python3 scripts/pfo.py new my-product --idea "voice transcript or product idea"
```

This creates:

```text
CODEX.md
.codex-memory/MEMORY.md
.codex-memory/STATE.json
.pfo/
.pfo-starter.json
.github/workflows/validate.yml
justfile
```

Then generate executable planning artifacts:

```bash
python3 scripts/pfo.py plan ../my-product
python3 scripts/pfo.py validate ../my-product
```

`pfo plan` creates missing `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md`, and `QUALITY_GATES.md` while preserving files that already exist.

## Runtime CLI

```bash
python3 scripts/pfo.py new my-product --idea "voice transcript or product idea"
python3 scripts/pfo.py adopt ../existing-product --analyze --run-gates
python3 scripts/pfo.py analyze ../existing-product --run-gates --report
python3 scripts/pfo.py plan ../my-product
python3 scripts/pfo.py build ../my-product
python3 scripts/pfo.py test ../my-product
python3 scripts/pfo.py review ../my-product
python3 scripts/pfo.py validate ../my-product
python3 scripts/pfo.py status ../my-product
python3 scripts/pfo.py resume ../my-product
python3 scripts/pfo.py report ../my-product
python3 scripts/pfo.py metrics
python3 scripts/pfo.py export ../my-product --target github
python3 scripts/pfo.py export ../my-product --target google-drive
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

## Release Check

```bash
python3 scripts/release_check.py
```

## Troubleshooting

**`pfo validate` says planning files are missing.** Run `python3 scripts/pfo.py plan <project>` first, then fill or approve the generated TBD fields.

**A hook blocks a commit.** Run `python3 hooks/review-before-commit.py --full` and update the supporting docs, snapshots, or changelog named by the hook.

**Codex did not pick the expected skill.** Run `python3 hooks/route-reminder.py "<your prompt>"` and add a fixture plus snapshot if the route should be recognized.
