from unittest.mock import MagicMock, patch

import pytest
import requests

from geo_events_bot.services.ingv_api import get_geo_events

URL = "https://example.com/events"


def fetch_payload(payload):
    response = MagicMock()
    response.json.return_value = payload
    with patch("geo_events_bot.services.ingv_api.requests.get", return_value=response):
        return get_geo_events(URL)


def test_get_geo_events_success(feature):
    result = fetch_payload(
        {"type": "FeatureCollection", "features": [feature.model_dump(by_alias=True)]}
    )
    assert result is not None  # noqa: S101
    assert result.features == [feature]  # noqa: S101


def test_invalid_events_do_not_discard_valid_ones(feature):
    invalid = feature.model_dump(by_alias=True)
    invalid["geometry"]["coordinates"] = [12.5]
    result = fetch_payload(
        {
            "type": "FeatureCollection",
            "features": [{}, invalid, feature.model_dump(by_alias=True)],
        }
    )
    assert result is not None  # noqa: S101
    assert result.features == [feature]  # noqa: S101


@pytest.mark.parametrize("payload", [None, [], {}, {"features": "invalid"}])
def test_invalid_response(payload):
    assert fetch_payload(payload) is None  # noqa: S101


def test_empty_response():
    result = fetch_payload({"type": "FeatureCollection", "features": []})
    assert result is not None  # noqa: S101
    assert result.features == []  # noqa: S101


def test_request_timeout():
    with patch(
        "geo_events_bot.services.ingv_api.requests.get",
        side_effect=requests.Timeout("Timeout"),
    ):
        assert get_geo_events(URL) is None  # noqa: S101


def test_http_error():
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("Server error")
    with patch("geo_events_bot.services.ingv_api.requests.get", return_value=response):
        assert get_geo_events(URL) is None  # noqa: S101
    response.json.assert_not_called()


def test_invalid_json():
    response = MagicMock()
    response.json.side_effect = requests.exceptions.JSONDecodeError("Invalid", "x", 0)
    with patch("geo_events_bot.services.ingv_api.requests.get", return_value=response):
        assert get_geo_events(URL) is None  # noqa: S101
