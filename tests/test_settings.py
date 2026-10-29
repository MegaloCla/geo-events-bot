import pytest
from pydantic import ValidationError

from geo_events_bot.models.settings import Settings


def test_settings_do_not_expose_token_in_repr():
    settings = Settings(telegram_token="private-value", chat_id="123")  # noqa: S106
    assert "private-value" not in repr(settings)  # noqa: S101


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("polling_interval", 0),
        ("min_magnitude", -1),
        ("default_radius_km", float("nan")),
        ("location_choice_ttl", 0),
        ("location_choice_cache_size", 0),
        ("inline_cache_time", -1),
    ],
)
def test_invalid_settings(field, value):
    with pytest.raises(ValidationError):
        Settings.model_validate(
            {"telegram_token": "test", "chat_id": "123", field: value}
        )
