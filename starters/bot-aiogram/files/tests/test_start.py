from bot.handlers.start import start_message


def test_start_message() -> None:
    assert "PFO" in start_message()

