#!/usr/bin/env python3
import re
import sys


ROUTES = [
    (r"\b(new project|build an app|create mvp|start a service|build (a )?(saas|bot|scraper|cli|api)|product factory)\b|нов(ый|ое) проект|создай приложение|хочу mvp|сделай (saas|бот|парсер|api|cli)|фабрик[ау] продукт", "/project"),
    (r"\b(stack trace|failing test|bug|error)\b|стек.?трейс|падает|ошибка|баг", "/task -> /bugfix"),
    (r"\b(security audit|owasp|secrets?)\b|аудит безопасности|секрет", "/task -> /security-audit"),
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
