#!/usr/bin/env python3
import re
import sys


ROUTES = [
    (r"\b(last 30 days|market scan|recent community signals|fresh market signals|social signals|competitor buzz|user complaints|reddit|hacker news|polymarket|youtube sentiment)\b|последние 30 дней|свеж(ие|ий) сигнал|сигнал(ы)? рынка|что говорят пользователи|жалоб(ы|ах) пользовател|обсужда(ют|ния) пользовател", "/project -> /discover -> /market-scan"),
    (r"\b(validate idea|score idea|test hypothesis|kill weak ideas|product discovery|target users|market research|validation plan|competitor|icp)\b|проверь идею|оцени идею|проверь гипотез|отсе(й|ять) слаб|discovery|аудит рынка|целевая аудитория|конкурент", "/project -> /discover"),
    (r"\b(plan only|architecture first|docs first|planning only|write docs)\b|только план|сначала архитектур|код пока не пишем|подготовь документаци", "/project -> /blueprint"),
    (r"\b(i have docs|existing docs|make prompts|execution guide|codex guide)\b|есть документаци|сделай гайд|промпты для реализации", "/project -> /guide"),
    (r"\b(new project|build an app|create mvp|start a service|build (a )?(saas|bot|scraper|cli|api)|product factory|full cycle|end to end|from idea to shipped)\b|нов(ый|ое) проект|создай приложение|хочу mvp|сделай (saas|бот|парсер|api|cli)|фабрик[ау] продукт|полный цикл|от идеи до релиза|сделай проект целиком", "/project -> /kickstart"),
    (r"\b(adopt existing|onboard repo|onboard project|legacy project|connect methodology)\b|подключи методологию|адаптируй репозиторий|существующ(ий|его) проект", "/task -> /adopt"),
    (r"\b(handoff|transfer context|switch sessions?|compact context|delegate to next agent|afk run|role switch)\b|handoff|передай контекст|нов(ая|ую) сесси|смена роли|делегируй агенту|afk", "/task -> /handoff"),
    (r"\b(save session|remember context|persist state)\b|сохрани сессию|запомни контекст|сохрани контекст", "/task -> /session-save"),
    (r"\b(strategy|replan|roadmap|pivot|launch plan|funnel|feedback loop|content backlog|product iteration|autoresearch|self-improvement loop|fixed metric experiment|keep discard loop)\b|стратеги|перепланируй|roadmap|pivot|план запуска|воронк|обратн(ая|ую) связь|контент|итераци|самосовершенствован|цикл экспериментов|фиксированн(ая|ую) метрик|keep discard", "/task -> /strategy"),
    (r"\b(advise|compare options|tradeoff|recommend)\b|посоветуй|сравни варианты|компромисс|рекоменд", "/task -> /advisor"),
    (r"\b(grill me|stress[- ]test|challenge my (plan|design)|hard questions)\b|прожарь|стресс.?тест|проверь дизайн|жестк(ие|их) вопрос", "/task -> /grill-me"),
    (r"\b(stack trace|failing test|failing behavior|bug|error)\b|стек.?трейс|падает|ошибка|баг|не работает", "/task -> /bugfix"),
    (r"\b(add tests|test coverage|write tests|failing tests)\b|добавь тесты|покрытие|тесты падают|падают тесты", "/task -> /test"),
    (r"\b(refactor|cleanup|simplify|clean up)\b|рефакторинг|почисти код|упрости", "/task -> /refactor"),
    (r"\b(update docs|readme|api docs|documentation)\b|обнови документаци|readme|api docs", "/task -> /doc"),
    (r"\b(explain code|how does this work|walk me through)\b|объясни код|как это работает", "/task -> /explain"),
    (r"\b(seo|seo audit|search engine optimization|organic traffic|technical seo|meta tags?|sitemap|robots\.txt|canonical|schema markup|structured data|search console|indexing|keyword intent|content optimization)\b|поисков(ая|ую) оптимизац|органическ(ий|ого|ому|им|ом|ая|ую) трафик|мета.?тег|индексац|семантическ(ое|ого) ядро|сниппет", "/task -> /seo"),
    (r"\b(slow|optimi[sz]e|bottleneck|performance)\b|медленно|оптимизируй|узкое место|производительност", "/task -> /perf"),
    (r"\b(latest docs|current api|sdk docs|framework version|context7|mcp)\b|свеж(ая|ие) документаци|актуальн(ый|ая) api|документаци[яи] sdk", "/task -> /mcp-docs"),
    (r"\b(plugin caveman|caveman plugin|caveman mode|talk like caveman|less tokens?|token compression|terse replies|terse mode|compress replies)\b|плагин caveman|режим caveman|меньше токен|сжимай ответ|коротк(ие|ий|о) ответ|лаконичн(о|ые|ый)", "/task -> /caveman"),
    (r"\b(create skill|new pfo skill|new skill|add workflow|skill creator|skill-create|custom skill|domain pack|premium pack skill)\b|создай skill|нов(ый|ого) pfo skill|нов(ый|ого) skill|добавь workflow|расширь pfo|кастомн(ый|ого) skill", "/task -> /skill-create"),
    (r"\b(open localhost|browser smoke|visual qa|check ui|frontend smoke|playwright smoke|playwright check)\b|открой localhost|проверь ui|визуальн(ая|ую) проверк|playwright проверк", "/task -> /browser-check"),
    (r"\b(github actions|pull request|pr review|ci|pr|check run|release branch)\b|github actions|pull request|релизн(ая|ую) ветк", "/task -> /github-workflow"),
    (r"\b(obsidian|vault|wikilinks?|knowledge graph|linked notes?)\b|obsidian|граф знаний|связанн(ые|ых) заметк|вики.?ссылк", "/task -> /obsidian-export"),
    (r"\b(linear|notion|google drive|sync|export project state)\b|синхронизи|экспорт состояния|google drive", "/task -> /tool-sync"),
    (r"\b(code review|quality gate|validate changes|review)\b|ревью|проверь качество|валидаци", "/task -> /review"),
    (r"\b(security audit|owasp|secrets?|threat model|attack path|codex security diff scan|security diff scan)\b|аудит безопасности|секрет|модель угроз|путь атаки", "/task -> /security-audit"),
    (r"\b(dependency audit|deps audit|cve|licenses?)\b|аудит зависимост|cve|лицензи", "/task -> /deps-audit"),
    (r"\b(harden|production readiness|runbook|observability)\b|подготовь к продакшену|production-ready|наблюдаемост|ранбук", "/task -> /harden"),
    (r"\b(infrastructure|terraform|docker|kubernetes|helm|iac)\b|инфраструктур|terraform|docker|kubernetes|helm", "/task -> /infra"),
    (r"\b(deploy|release|ship to production|production)\b|деплой|релиз|выкатить|production|продакшен", "/task -> /deploy"),
    (r"\b(migration|schema change|database upgrade)\b|миграци|схема бд|обновить базу", "/task -> /migrate"),
]

DANGEROUS_ROUTES = {"/deploy", "/migrate", "/infra", "/tool-sync", "/github-workflow"}


def main() -> None:
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    text = prompt.lower()
    for pattern, route in ROUTES:
        if re.search(pattern, text):
            print(f"Suggested Product Factory OS route: {route}")
            if any(skill in route for skill in DANGEROUS_ROUTES):
                print("PFO risk guard: this route has external, infrastructure, migration, or production side effects; require explicit user confirmation before action.")
            return
    print("Suggested Product Factory OS route: inspect request, then use /project for new work or /task for existing code")


if __name__ == "__main__":
    main()
