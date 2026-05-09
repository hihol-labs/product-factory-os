#!/usr/bin/env python3
import re
import sys


ROUTES = [
    (r"\b(validate idea|product discovery|target users|market research|competitor|icp)\b|проверь идею|discovery|аудит рынка|целевая аудитория|конкурент", "/project -> /discover"),
    (r"\b(plan only|architecture first|docs first|planning only|write docs)\b|только план|сначала архитектур|код пока не пишем|подготовь документаци", "/project -> /blueprint"),
    (r"\b(i have docs|existing docs|make prompts|execution guide|codex guide)\b|есть документаци|сделай гайд|промпты для реализации", "/project -> /guide"),
    (r"\b(new project|build an app|create mvp|start a service|build (a )?(saas|bot|scraper|cli|api)|product factory|full cycle|end to end)\b|нов(ый|ое) проект|создай приложение|хочу mvp|сделай (saas|бот|парсер|api|cli)|фабрик[ау] продукт|полный цикл", "/project -> /kickstart"),
    (r"\b(adopt existing|onboard repo|legacy project|connect methodology)\b|подключи методологию|адаптируй репозиторий|существующ(ий|его) проект", "/task -> /adopt"),
    (r"\b(save session|remember context|persist state)\b|сохрани сессию|запомни контекст|сохрани контекст", "/task -> /session-save"),
    (r"\b(strategy|replan|roadmap|pivot|launch plan)\b|стратеги|перепланируй|roadmap|pivot|план запуска", "/task -> /strategy"),
    (r"\b(advise|compare options|tradeoff|recommend)\b|посоветуй|сравни варианты|компромисс|рекоменд", "/task -> /advisor"),
    (r"\b(stack trace|failing test|bug|error)\b|стек.?трейс|падает|ошибка|баг", "/task -> /bugfix"),
    (r"\b(add tests|test coverage|write tests|failing tests)\b|добавь тесты|покрытие|тесты падают", "/task -> /test"),
    (r"\b(refactor|cleanup|simplify|clean up)\b|рефакторинг|почисти код|упрости", "/task -> /refactor"),
    (r"\b(update docs|readme|api docs|documentation)\b|обнови документаци|readme|api docs", "/task -> /doc"),
    (r"\b(explain code|how does this work|walk me through)\b|объясни код|как это работает", "/task -> /explain"),
    (r"\b(slow|optimi[sz]e|bottleneck|performance)\b|медленно|оптимизируй|узкое место|производительност", "/task -> /perf"),
    (r"\b(latest docs|current api|sdk docs|framework version|context7|mcp)\b|свеж(ая|ие) документаци|актуальн(ый|ая) api|документаци[яи] sdk", "/task -> /mcp-docs"),
    (r"\b(open localhost|browser smoke|visual qa|check ui|frontend smoke)\b|открой localhost|проверь ui|визуальн(ая|ую) проверк", "/task -> /browser-check"),
    (r"\b(github actions|pull request|pr review|ci|pr|check run|release branch)\b|github actions|pull request|релизн(ая|ую) ветк", "/task -> /github-workflow"),
    (r"\b(linear|notion|google drive|sync|export project state)\b|синхронизи|экспорт состояния|google drive", "/task -> /tool-sync"),
    (r"\b(code review|quality gate|validate changes|review)\b|ревью|проверь качество|валидаци", "/task -> /review"),
    (r"\b(security audit|owasp|secrets?)\b|аудит безопасности|секрет", "/task -> /security-audit"),
    (r"\b(dependency audit|deps audit|cve|licenses?)\b|аудит зависимост|cve|лицензи", "/task -> /deps-audit"),
    (r"\b(harden|production readiness|runbook|observability)\b|подготовь к продакшену|production-ready|наблюдаемост|ранбук", "/task -> /harden"),
    (r"\b(infrastructure|terraform|kubernetes|helm|iac)\b|инфраструктур|terraform|kubernetes|helm", "/task -> /infra"),
    (r"\b(deploy|release|production)\b|деплой|релиз|production|продакшен", "/task -> /deploy"),
    (r"\b(migration|schema change)\b|миграци|схема бд", "/task -> /migrate"),
]


def main() -> None:
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    text = prompt.lower()
    for pattern, route in ROUTES:
        if re.search(pattern, text):
            print(f"Suggested Product Factory OS route: {route}")
            return
    print("Suggested Product Factory OS route: inspect request, then use /project for new work or /task for existing code")


if __name__ == "__main__":
    main()
