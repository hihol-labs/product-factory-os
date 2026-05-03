#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import re


def classify(text: str) -> dict:
    lowered = text.lower()
    if re.search(r"mini app|мини|embedded", lowered):
        product_type = "mini_app"
    elif re.search(r"api|backend|webhook|вебхук|эндпо", lowered):
        product_type = "api_service"
    elif re.search(r"telegram bot|discord bot|\bbot\b|бот", lowered):
        product_type = "messaging_bot"
    elif re.search(r"saas|подпис", lowered):
        product_type = "saas"
    elif re.search(r"landing|лендинг|сайт", lowered):
        product_type = "landing_page"
    elif re.search(r"cli|терминал|command", lowered):
        product_type = "cli_tool"
    elif re.search(r"парсер|scraper|crawl", lowered):
        product_type = "data_scraper"
    elif re.search(r"shop|store|магазин|e-commerce", lowered):
        product_type = "ecommerce"
    else:
        product_type = "web_app"
    return {
        "raw": text,
        "route": "/project -> /kickstart",
        "productTypeHint": product_type,
        "nextCommand": "pfo new <project-name> --idea <voice transcript>",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize voice text into a PFO intent.")
    parser.add_argument("text")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(classify(args.text), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
