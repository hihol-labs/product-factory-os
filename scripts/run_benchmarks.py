#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def classify(text: str) -> str:
    lowered = text.lower()
    if re.search(r"mini app|мини|embedded", lowered):
        return "mini_app"
    if re.search(r"api|backend|webhook|вебхук", lowered):
        return "api_service"
    if re.search(r"telegram bot|discord bot|\bbot\b|бот", lowered):
        return "messaging_bot"
    if re.search(r"saas|подпис|тариф", lowered):
        return "saas"
    if re.search(r"landing|лендинг|промо сайт", lowered):
        return "landing_page"
    if re.search(r"cli|терминал|batch rename", lowered):
        return "cli_tool"
    if re.search(r"парсер|scraper|мониторинг", lowered):
        return "data_scraper"
    if re.search(r"магазин|e-commerce|корзин|заказ", lowered):
        return "ecommerce"
    if re.search(r"automation|автоматизац|backoffice", lowered):
        return "internal_automation"
    return "web_app"


def main() -> None:
    data = json.loads((ROOT / "benchmarks" / "prompts.json").read_text(encoding="utf-8"))
    total = 0
    passed = 0
    failures = []
    for item in data["prompts"]:
        total += 1
        actual = classify(item["text"])
        if actual == item["expectedType"]:
            passed += 1
        else:
            failures.append({"id": item["id"], "expected": item["expectedType"], "actual": actual})
    result = {"total": total, "passed": passed, "accuracy": passed / total if total else 0, "failures": failures}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
