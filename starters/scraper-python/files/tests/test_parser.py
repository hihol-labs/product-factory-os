from scraper.parsers.core import parse_title


def test_parse_title() -> None:
    assert parse_title("<title>Price</title>") == "Price"

