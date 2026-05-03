# Install And Local Testing

Product Factory OS is a Codex plugin-style repository. During early development, test it as a local plugin directory and validate the methodology files before publishing.

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
python3 scripts/pfo_new_project.py my-product --idea "voice transcript or product idea"
```

This creates:

```text
CODEX.md
.codex-memory/MEMORY.md
.codex-memory/STATE.json
```

## Runtime CLI

```bash
python3 scripts/pfo.py new my-product --idea "voice transcript or product idea"
python3 scripts/pfo.py validate ../my-product
python3 scripts/pfo.py status ../my-product
python3 scripts/pfo.py resume ../my-product
python3 scripts/pfo.py report ../my-product
python3 scripts/pfo.py metrics
python3 scripts/pfo.py export ../my-product --target github
```

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
