# Product Factory OS

Product Factory OS — это plugin-методология и runtime-фреймворк для Codex: путь от сырой идеи до рабочего, проверенного и готового к деплою проекта через детерминированный execution engine.

```text
IDEA -> PRODUCT_BLUEPRINT -> BUILD_PLAN -> EXECUTION_GRAPH -> BUILD -> TEST -> VALIDATE -> DEPLOY_READY -> SAVE_STATE
```

## Что Внутри

- 23 skills для создания проектов, ежедневной разработки, качества, операций, стратегии и памяти
- 6 agent-role описаний для архитектуры, ревью, тестов, аналитики, безопасности и операций
- Контракты skills: входы, выходы, side effects и idempotency
- Call graph, чтобы цепочки не становились хаотичными
- Trigger registry для маршрутизации естественного языка
- Rubrics для review, security, dependency audit и production readiness
- Fixtures и scripts для проверки методологии
- Workspace-default правила для `/home/hihol/projects`
- PFO runtime contracts: classifier, template library, product compiler, state machine, execution pipeline, memory schema, deployment abstraction и voice-first interface

## Быстрый Старт

Опишите идею:

```text
Хочу сделать сервис записи к частным репетиторам.
```

`/project` выберет маршрут:

- `A` полный цикл: план, код, тесты, review, deploy
- `B` только планирование: документы без кода
- `C` есть документы: создать пошаговый guide для реализации

Для существующего проекта:

```text
В текущем проекте падает POST /api/bookings.
```

`/task` направит задачу в `/bugfix`, `/test`, `/review`, `/security-audit`, `/deploy` или другой daily-work skill.

## Product Factory OS Runtime

PFO добавляет:

- `routing/product-classifier.json` — классификация SaaS, ботов, API, web apps, landing pages, CLI, mini apps, e-commerce, scrapers и internal automation.
- `templates/product-templates.json` — библиотека модульных шаблонов.
- `core/product-compiler.md` — компилятор idea -> Product Blueprint -> Build Plan -> Execution Graph.
- `execution/state-machine.json` — контролируемые переходы workflow.
- `memory/session-state.schema.json` — формат восстановления состояния.
- `deployment/deployment-targets.json` — deploy readiness checks.
- `.pfo/*` project contracts — универсальные guardrails проекта: scope lock, data authenticity, golden flows, regression contracts, fallback policy, diff risk и no silent substitution.

## Runtime CLI

PFO теперь имеет исполняемый CLI:

```bash
python3 scripts/pfo.py new my-product --idea "SaaS для учета подписок"
python3 scripts/pfo.py adopt
python3 scripts/pfo.py adopt ../existing-product --analyze --run-gates
python3 scripts/pfo.py analyze ../existing-product --run-gates --report
python3 scripts/pfo.py plan ../my-product
python3 scripts/pfo.py build ../my-product
python3 scripts/pfo.py test ../my-product
python3 scripts/pfo.py review ../my-product
python3 scripts/pfo.py validate ../my-product
python3 scripts/pfo.py contracts ../my-product --write
python3 scripts/pfo.py status ../my-product
python3 scripts/pfo.py resume ../my-product
python3 scripts/pfo.py report ../my-product
python3 scripts/pfo.py voice "создай Telegram бот для продаж"
python3 scripts/pfo.py metrics
python3 scripts/pfo.py export ../my-product --target github
```

Starter packs находятся в `starters/`. Golden paths находятся в `golden-paths/`.

Сгенерированные проекты получают `.pfo/` contracts, `.pfo-starter.json`, `.env.example`, `.github/workflows/validate.yml`, `justfile` и `PFO_REPORT.md`.

Дополнительные расширения платформы:

- `dashboard/` — статический dashboard.
- `benchmarks/` — benchmark suite для prompt-классификации.
- `packaging/` — install/update helper.
- `marketplace/` — local marketplace metadata.
- `integrations/` — контракты GitHub, Linear и Notion.

Для существующих проектов `pfo analyze` определяет monorepo, стек, package manager, доступные scripts, архитектурные признаки, security findings и optional gate results, затем сохраняет это в `.codex-memory/STATE.json` и `PFO_EXISTING_PROJECT_ANALYSIS.json`.

`pfo analyze` также создает/проверяет `.pfo/` project contracts и запускает `pfo_contract_gate.py`, чтобы не допустить тихую подмену реальных данных, выход за scope задачи или изменение пользовательского поведения под видом узкой правки.

## Open Core И Монетизация

Product Factory OS использует open-core модель:

- Локальный runtime, базовые starters, validators, skills, agents и методология являются open source.
- Premium starter packs, hosted dashboard, team workspaces, managed execution, enterprise policy и внедрение могут быть коммерческими расширениями.

Продукты, созданные через PFO, принадлежат их авторам. Использование PFO не требует открывать сгенерированные продукты.

См.:

- [Open Core Strategy](docs/OPEN_CORE.md)
- [Commercial Strategy](docs/COMMERCIAL.md)
- [Pricing Model](docs/PRICING.md)
- [Starter Pack Strategy](docs/PACKS.md)
- [PFO Cloud](docs/CLOUD.md)
- [GitHub Launch Checklist](docs/GITHUB_LAUNCH.md)
- [Initial Roadmap Issues](docs/GITHUB_ISSUES.md)
- [v0.5.0 Release Notes](docs/RELEASE_NOTES_v0.5.0.md)

## Проверка

```bash
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/validate_execution_graph.py
python3 scripts/validate_state.py /path/to/project/.codex-memory/STATE.json
python3 scripts/validate_runtime.py
python3 scripts/run_benchmarks.py
python3 scripts/meta_review.py
```

## Основное Правило Качества

Каждый значимый этап должен пройти:

1. Требования задокументированы.
2. Классификация продукта и архитектурный шаблон явные.
3. `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md` и `EXECUTION_GRAPH.md` согласованы.
4. Для изменённого поведения есть тесты.
5. Review status не равен `BLOCKED`.
6. `.pfo/` contracts не нарушены: scope lock, data authenticity, golden flows, regression contract, fallback policy, diff risk, no silent substitution.
7. Контекст сессии сохранён через `/session-save`.

## Документация

- [Methodology](docs/METHODOLOGY.md)
- [Skill Contracts](docs/SKILL_CONTRACTS.md)
- [Triggers](docs/TRIGGERS.md)
- [Install And Local Testing](docs/INSTALL.md)
- [Workspace Defaults](docs/WORKSPACE_DEFAULTS.md)
- [Roadmap](docs/ROADMAP.md)
- [PFO Architecture](docs/PFO_ARCHITECTURE.md)
- [Master Prompt RU](docs/MASTER_PROMPT.ru.md)

## Автоматическое Создание Проектов

В `/home/hihol/projects` новые проекты должны запускаться через Product Factory OS автоматически:

```text
/project -> /kickstart
```

Пользователь может давать голосовую или естественную команду. Codex выполняет routing, bootstrap, Product Compiler, build graph, проверки и сохранение состояния.

Bootstrap helper:

```bash
python3 /home/hihol/projects/product-factory-os/scripts/pfo_new_project.py my-product --idea "голосовая команда или идея продукта"
```

## Существующие Проекты

Существующие проекты в `/home/hihol/projects` тоже работают через Product Factory OS:

```text
/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save
```

Перед значимыми изменениями проект должен иметь:

```text
CODEX.md
.pfo/PROJECT_CONTRACT.md
.pfo/DATA_POLICY.md
.pfo/GOLDEN_FLOWS.md
.pfo/FORBIDDEN_CHANGES.md
.pfo/FALLBACK_POLICY.md
.pfo/SCOPE_LOCK.md
.codex-memory/MEMORY.md
.codex-memory/STATE.json
```

Если этих файлов нет, сначала используется `/adopt`.
