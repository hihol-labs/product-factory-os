# Product Factory OS v0.5.0

Initial public runtime release.

## Highlights

- Deterministic Product Factory OS runtime for Codex.
- Product classification for SaaS, bots, APIs, web apps, landing pages, CLI tools, mini apps, e-commerce, scrapers, and internal automation.
- Product compiler flow: idea -> blueprint -> build plan -> execution graph.
- State machine, execution pipeline, memory schema, deployment checks, and voice-first command contract.
- 27 Codex skills and 15 agent role contracts.
- OpenAI/Codex plugin and MCP routes for Context7 documentation, Browser Use smoke tests, GitHub PR/CI workflow, Codex Security scans, Linear, Notion, and Google Drive sync.
- Runtime CLI with `new`, `adopt`, `plan`, `build`, `test`, `review`, `validate`, `status`, `resume`, `report`, `voice`, `metrics`, and `export`.
- Starter packs and golden paths for the main product categories.
- Open-core and commercial boundary documentation.

## Validation

The release is expected to pass:

```bash
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/validate_execution_graph.py
python3 scripts/validate_runtime.py
python3 scripts/run_benchmarks.py
python3 scripts/release_check.py
```

## Install Smoke Test

```bash
git clone https://github.com/hihol-labs/product-factory-os.git
cd product-factory-os
python3 scripts/release_check.py
python3 scripts/pfo.py voice "создай SaaS для учета подписок"
```
