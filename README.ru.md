# Product Factory OS

Product Factory OS — это plugin-методология и runtime-фреймворк для Codex: путь от сырой идеи до рабочего, проверенного и готового к деплою проекта через детерминированный execution engine.

```text
IDEA -> PRODUCT_BLUEPRINT -> BUILD_PLAN -> EXECUTION_GRAPH -> BUILD -> TEST -> VALIDATE -> DEPLOY_READY -> SAVE_STATE
```

## Что Внутри

- 35 skills для создания проектов, ежедневной разработки, качества, операций, стратегии, памяти, research, SEO, token-efficiency, расширения методологии, connector workflows и Obsidian knowledge export
- 15 agent-role описаний для архитектуры, ревью, тестов, аналитики, безопасности, релизов, UX, данных и интеграций
- Контракты skills: входы, выходы, side effects и idempotency
- Call graph, чтобы цепочки не становились хаотичными
- Trigger registry для маршрутизации естественного языка
- Rubrics для review, security, dependency audit и production readiness
- Route snapshots и fixtures для проверки всех skill routes
- Workspace hook layer: auto-adoption, route reminders, preflight context, security guard, context-budget routing, skill completeness, commit completeness и review-before-commit gates
- Workspace-default правила для `/home/hihol/projects`
- Маршруты OpenAI/Codex plugin, MCP и research для Context7, Last30Days, Browser Use, GitHub, Codex Security, Linear, Notion и Google Drive
- PFO runtime contracts: classifier, template library, product compiler, state machine, execution pipeline, memory schema, deployment abstraction и voice-first interface
- GSD-inspired autonomous layer: phase discussion, unit context manifest, dispatch journal, fail-closed verification, recovery state, telemetry, learnings и visual briefs
- Engineering Discipline v2 gates по мотивам Superpowers: TDD evidence, root-cause discipline, two-stage review, strict executable plans и branch finish hygiene
- Control harness: явное разделение feedforward/feedback и computational/inferential controls, чтобы deterministic gates блокировали повторяемые риски, а LLM-review отвечал за смысловую оценку

## Быстрый Старт

### Установка

```bash
git clone https://github.com/hihol-labs/product-factory-os.git
cd product-factory-os
bash install.sh
```

Эта одна команда валидирует PFO, ставит команду `pfo`, устанавливает hooks, пишет workspace-файлы `AGENTS.md` / `CODEX.md` / `PFO_WORKSPACE.json`, глобальные `PFO_GLOBAL.json` policy-файлы с включенным по умолчанию Codex `/goal` mode и автоматически доводит уже существующие проекты первого уровня до полного PFO-runtime: adoption files, contracts, анализ, contract gate, `NEXT_STEP.md` и `PFO_REPORT.md`.

Если репозиторий скачан не внутри папки проектов, укажите workspace один раз:

```bash
bash install.sh --workspace ~/Projects
```

После этого открывайте любой проект в workspace через Codex. Для существующих проектов PFO runtime уже подключен полностью. Для новых проектов достаточно описать идею; Codex должен сам запустить PFO bootstrap. CLI-вариант:

```bash
pfo new my-product --idea "SaaS для учета подписок"
```

`pfo new` сразу создает PFO runtime, starter files, planning artifacts, execution graph и `PFO_REPORT.md`; отдельный `pfo plan` для первичного формирования больше не нужен.

Новые проекты создаются local-first: обязательна папка проекта в workspace, локальный Git инициализируется до реализации, если репозитория еще нет. GitHub-репозиторий не является обязательным для bootstrap; его создание или подключение выполняется отдельно через `/github-workflow`, когда пользователь явно просит публикацию, PR/CI/release workflow или это задано workspace policy.

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

Для каждого нетривиального нового или существующего проекта PFO включает Codex `/goal` mode по умолчанию: цель фиксирует результат пользователя и активный PFO route, а закрывается только после gates, verification и state-save.

## Product Factory OS Runtime

PFO добавляет:

- `routing/product-classifier.json` — классификация SaaS, ботов, API, web apps, landing pages, CLI, mini apps, e-commerce, scrapers и internal automation.
- `templates/product-templates.json` — библиотека модульных шаблонов.
- `core/product-compiler.md` — компилятор idea -> Product Blueprint -> Build Plan -> Execution Graph.
- `docs/templates/IDEA_SCORECARD.md` и `VALIDATION_PLAN.md` — gate для слабых идей, evidence quality, customer discovery, гипотез и рыночных сигналов до расширения scope.
- `docs/templates/MARKET_BRIEF.md` — рыночный и adversarial discovery слой: конкуренты, альтернативы, неприятные сигналы и дифференциация.
- `docs/templates/FUNNEL_MODEL.md`, `GO_TO_MARKET.md`, `FEEDBACK_LOG.md`, `ITERATION_REVIEW.md`, `ASSET_REGISTER.md`, `CONTENT_BACKLOG.md` — слой воронки, MVP measurement, обратной связи, итераций, активов и контента.
- `docs/templates/SEO_GROWTH_GUARANTEE_GATE.md` — gate для SEO growth claims: baseline metric, target metric, measurement source, attribution window, implemented changes, exclusion factors, result decision и next iteration.
- `docs/templates/LAUNCH_MATURITY_GATE.md` и `SCALE_MOAT_REGISTER.md` — опциональные Launch/Scale maturity artifacts, не обязательные для каждого MVP.
- `execution/state-machine.json` — контролируемые переходы workflow.
- `memory/session-state.schema.json` — формат восстановления состояния.
- `memory/events.schema.json` — формат структурированного event log.
- `deployment/deployment-targets.json` — deploy readiness checks.
- `.pfo/*` project contracts — универсальные guardrails проекта: scope lock, data authenticity, golden flows, regression contracts, fallback policy, diff risk и no silent substitution.
- `.pfo/EXECUTION_POLICY.json`, `.pfo/PERMISSION_MATRIX.json`, `.pfo/PERMISSION_MATRIX.md`, `.pfo/VERIFICATION_CONTRACT.json`, `.pfo/TOOL_CAPABILITY_REGISTRY.json` и `.codex-memory/events.jsonl` — исполняемые policy, permissions, verification contract, tool registry и structured event log.

## Runtime CLI

PFO теперь имеет исполняемый CLI:

```bash
pfo new my-product --idea "SaaS для учета подписок"
pfo adopt
pfo adopt ../existing-product
pfo analyze ../existing-product --run-gates --report
pfo discuss ../my-product --phase phase-1 --note "API shape and fallback rules"
pfo plan ../my-product
pfo manifest ../my-product --unit N1 --goal "Primary booking flow"
pfo handoff ../my-product --from-role planner --to-role implementer --reason role-switch
pfo build ../my-product
pfo test ../my-product
pfo full-cycle ../my-product --note "run the standard PFO loop"
pfo tdd-evidence ../my-product --red "pytest ... failed as expected" --green "pytest ... passed"
pfo root-cause ../my-product --summary "bad value enters parser" --evidence "trace shows parser input" --hypothesis "validate before parse"
pfo verify-work ../my-product --evidence "tests and smoke passed" --pass-gate
pfo experiment-init ../my-product --metric "conversion_rate" --direction higher --budget-seconds 300 --run-command "pytest -q"
pfo experiment-record ../my-product --metric-value 0.42 --status auto --description "baseline or candidate"
pfo review-stage ../my-product --stage spec --status PASSED --evidence "matches manifest"
pfo review-stage ../my-product --stage quality --status PASSED --evidence "tests and review clean"
python3 scripts/validate_plan_quality.py ../my-product
pfo review ../my-product
pfo validate ../my-product
pfo contracts ../my-product --write
pfo status ../my-product
pfo resume ../my-product
pfo context-budget ../my-product --kind read --bytes 16000
pfo context-index ../my-product
pfo context-search ../my-product "failed verification"
pfo context-snapshot ../my-product --reason compaction
pfo report ../my-product
pfo finish-branch ../my-product --mode pr --verification "checks passed" --pr-url "https://github.com/..."
pfo brief ../my-product --mode recap
pfo learnings ../my-product --lesson "Keep provider fallback explicit" --problem "Fallbacks drift during deploy checks" --rule "Require fallback evidence in deploy nodes" --evidence "deploy gate recovery" --confidence 0.75
pfo improve ../my-product --from-learnings --propose
pfo learning-gate ../my-product --require-approved
pfo permission-check ../my-product --capability write --path .codex-memory/STATE.json
pfo event validate ../my-product
pfo tool-registry ../my-product
pfo voice "создай Telegram бот для продаж"
pfo metrics
pfo export ../my-product --target github
python3 scripts/pfo.py export ../my-product --target google-drive
pfo export ../my-product --target obsidian
```

Starter packs находятся в `starters/`. Golden paths находятся в `golden-paths/`.

PFO использует `PFO Default Stack v1` как golden path для новых продуктов: Python/FastAPI/Pydantic, PostgreSQL, Vue/TypeScript/Vite/TailwindCSS, Redis, S3-compatible storage, `just`, Docker и Nginx. Это preset по умолчанию, не жесткий запрет альтернатив; отклонения фиксируются в `PROJECT_ARCHITECTURE.md` с причиной, риском, ценой поддержки и влиянием на проверку.

Сгенерированные проекты автоматически получают `.pfo/` contracts, `.pfo-starter.json`, `.env.example`, `.github/workflows/validate.yml`, `justfile`, planning artifacts, execution graph и `PFO_REPORT.md`.

`pfo plan` создает недостающие `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md`, `FEEDBACK_LOG.md`, `ITERATION_REVIEW.md`, `FUNNEL_MODEL.md`, `ASSET_REGISTER.md`, `CONTENT_BACKLOG.md`, `PRODUCT_BLUEPRINT.md`, `PROJECT_ARCHITECTURE.md`, `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, `TEST_PLAN.md` и `QUALITY_GATES.md` на основе выбранного starter, но не перезаписывает уже существующие файлы.

`pfo discuss` фиксирует решения в `PHASE_CONTEXT.md`, `pfo manifest` создает `.pfo/UNIT_CONTEXT_MANIFEST.json`, `pfo handoff` пишет `HANDOFF.md` перед передачей сессии, `pfo verify-work` по умолчанию создает recovery-путь при неясной проверке, `pfo brief` делает локальный HTML-brief по статусу проекта.

`pfo experiment-init` и `pfo experiment-record` добавляют Autoresearch-style цикл самосовершенствования: один metric, фиксированный бюджет, защищенный evaluation harness, baseline-first лог `.pfo/EXPERIMENTS.tsv` и решение keep/discard/crash.

`pfo tdd-evidence`, `pfo root-cause`, `pfo review-stage` и `pfo finish-branch` добавляют строгие инженерные gates для behavior changes, bugfixes, unit review и PR/merge cleanup.

Дополнительные расширения платформы:

- `dashboard/` — статический dashboard.
- `benchmarks/` — benchmark suite для prompt-классификации.
- `packaging/` — install/update helper.
- `marketplace/` — local marketplace metadata.
- `integrations/` — контракты GitHub, Linear, Notion, Google Drive, Obsidian и MCP capabilities.
- `pfo export --target obsidian` создает `.pfo-integrations/obsidian/` с `PROJECT_INDEX.md`, `KNOWLEDGE_GRAPH.md`, planning docs, handoff, memory, state, gates и decisions.

Для существующих проектов `pfo analyze` определяет monorepo, стек, package manager, доступные scripts, архитектурные признаки, security findings и optional gate results, затем сохраняет это в `.codex-memory/STATE.json` и `PFO_EXISTING_PROJECT_ANALYSIS.json`.

`pfo analyze` также создает/проверяет `.pfo/` project contracts и запускает `pfo_contract_gate.py`, чтобы не допустить тихую подмену реальных данных, выход за scope задачи или изменение пользовательского поведения под видом узкой правки.

## Open Core И Монетизация

Product Factory OS использует open-core модель:

- Локальный runtime, базовые starters, validators, skills, agents и методология являются open source.
- Premium starter packs, hosted dashboard, team workspaces, managed execution, enterprise policy и внедрение могут быть коммерческими расширениями.

Продукты, созданные через PFO, принадлежат их авторам. Использование PFO не требует открывать сгенерированные продукты.

## Чего PFO Не Делает

- Не заменяет senior architecture/security/legal/compliance review для регулируемых или высокорисковых продуктов.
- Не деплоит, не мигрирует и не меняет production-инфраструктуру молча. Production-impacting операции требуют явного подтверждения.
- Не выдумывает production data, ответы провайдеров или реальные источники данных; fallback должен быть явно разрешен.
- Не гарантирует, что каждый сгенерированный проект сразу production-ready. PFO дает gates, contracts и evidence requirements, которые нужно пройти.
- Не требует открывать исходный код продуктов, созданных через PFO.
- Пока не является hosted team platform. Hosted dashboard, managed execution, team workspaces и enterprise policy относятся к open-core/commercial roadmap.

## Production Grade

PFO теперь проверяется как production-grade local runtime версии `1.0.0`. Главный gate:

```bash
python3 scripts/production_readiness.py
```

Он проверяет structure, control harness, route fixtures, trigger drift, behavioural contracts, headless fixture validation, skill risk profiles, runtime assets, hooks, manifest drift, install sync, benchmarks и meta-review.

См.:

- [Open Core Strategy](docs/OPEN_CORE.md)
- [Commercial Strategy](docs/COMMERCIAL.md)
- [Pricing Model](docs/PRICING.md)
- [Starter Pack Strategy](docs/PACKS.md)
- [PFO Cloud](docs/CLOUD.md)
- [GitHub Launch Checklist](docs/GITHUB_LAUNCH.md)
- [Initial Roadmap Issues](docs/GITHUB_ISSUES.md)
- [v1.0.0 Release Notes](docs/RELEASE_NOTES_v1.0.0.md)
- [v0.6.1 Release Notes](docs/RELEASE_NOTES_v0.6.1.md)
- [v0.6.0 Release Notes](docs/RELEASE_NOTES_v0.6.0.md)
- [v0.5.0 Release Notes](docs/RELEASE_NOTES_v0.5.0.md)
- [OpenAI And MCP Integrations](docs/OPENAI_MCP_INTEGRATIONS.md)
- [Agent Harness Engineering](docs/AGENT_HARNESS_ENGINEERING.md)
- [Harness Engineering Demo Integration](docs/HARNESS_ENGINEERING_DEMO_INTEGRATION.md)
- [Caveman Integration](docs/CAVEMAN_INTEGRATION.md)

## Проверка

```bash
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/validate_execution_graph.py
python3 scripts/validate_state.py /path/to/project/.codex-memory/STATE.json
python3 scripts/validate_runtime.py
python3 scripts/validate_hooks.py
python3 scripts/run_benchmarks.py
python3 scripts/meta_review.py
```

## Основное Правило Качества

Каждый значимый этап должен пройти:

1. Требования задокументированы.
2. Идея имеет `KILL`, `TEST` или `BUILD` решение в `IDEA_SCORECARD.md`.
3. Evidence quality отделяет реальные разговоры, прошлое поведение и опровергающие данные от мнений и founder belief.
4. Рискованные гипотезы проверяются через `VALIDATION_PLAN.md`.
5. Market/competitor risk проходит adversarial discovery в `MARKET_BRIEF.md`, когда это применимо.
6. До MVP launch определены activation, retention, PMF signals и false-positive traction, если рынок важен.
7. Launch/Scale maturity artifacts используются только когда стадия действительно требует их.
8. Классификация продукта и архитектурный шаблон явные.
9. `PRODUCT_BLUEPRINT.md`, `BUILD_PLAN.md` и `EXECUTION_GRAPH.md` согласованы.
10. Для автономной или delegated-работы есть `.pfo/UNIT_CONTEXT_MANIFEST.json`.
11. Перед передачей сессии или роли есть `HANDOFF.md`.
12. Для автономного улучшения есть `.pfo/EXPERIMENT_PROGRAM.md`, baseline, фиксированный budget, metric и keep/discard/crash лог.
13. Для behavior changes есть TDD red/green/refactor evidence или явное исключение.
14. Для bugfixes есть root-cause evidence до фикса.
15. Feedback, funnel и iteration decisions привязаны к сигналам, а не активности.
16. Reusable outcomes попадают в `ASSET_REGISTER.md` или `CONTENT_BACKLOG.md`.
17. Verification не является неясной: missing/ambiguous evidence ведет в recovery, а не в pass.
18. Spec compliance review выполнен до code quality review.
19. Review status не равен `BLOCKED`.
20. `.pfo/` contracts не нарушены: scope lock, data authenticity, golden flows, regression contract, fallback policy, diff risk, no silent substitution.
21. Branch finish фиксирует PR, merge, keep или discard decision, если это в scope.
22. Контекст сессии сохранён через `/session-save`.

## Документация

- [Methodology](docs/METHODOLOGY.md)
- [Skill Contracts](docs/SKILL_CONTRACTS.md)
- [Triggers](docs/TRIGGERS.md)
- [Install And Onboarding](docs/INSTALL.md)
- [Workspace Defaults](docs/WORKSPACE_DEFAULTS.md)
- [Roadmap](docs/ROADMAP.md)
- [GSD Integration Notes](docs/GSD_INTEGRATION.md)
- [Superpowers Integration Notes](docs/SUPERPOWERS_INTEGRATION.md)
- [PFO Architecture](docs/PFO_ARCHITECTURE.md)
- [Master Prompt RU](docs/MASTER_PROMPT.ru.md)

## Автоматическое Создание Проектов

В любой локальной папке, где Codex работает над проектом, PFO должен подключаться автоматически через глобальный `PFO_GLOBAL.json`. Новые проекты запускаются через Product Factory OS:

```text
/project -> /kickstart
```

Пользователь может давать голосовую или естественную команду. Codex выполняет routing, bootstrap, Product Compiler, build graph, проверки и сохранение состояния.

Codex `/goal` mode запускается как часть этого runtime: цель создается или продолжается до implementation и остается активной до прохождения PFO gates и сохранения состояния.

Bootstrap helper:

```bash
pfo new my-product --idea "голосовая команда или идея продукта"
```

## Существующие Проекты

Существующие проекты в `/home/hihol/projects` тоже работают через Product Factory OS:

```text
/task -> adoption-check -> repository-analysis -> task-classification -> daily-work skill -> gates -> state-save
```

То же правило `/goal` действует перед `/task`: цель должна включать запрошенное изменение и выбранный daily-work route.

Перед значимыми изменениями проект должен иметь:

```text
CODEX.md
AGENTS.md
.pfo/PROJECT_CONTRACT.md
.pfo/DATA_POLICY.md
.pfo/GOLDEN_FLOWS.md
.pfo/FORBIDDEN_CHANGES.md
.pfo/FALLBACK_POLICY.md
.pfo/SCOPE_LOCK.md
.codex-memory/MEMORY.md
.codex-memory/STATE.json
PFO_EXISTING_PROJECT_ANALYSIS.json
PFO_CONTRACT_GATE.json
PFO_REPORT.md
```

Если этих файлов нет, `bash install.sh` или preflight hook создают их автоматически, запускают анализ и пишут `PFO_REPORT.md`; вручную достаточно `pfo adopt <project>`.
