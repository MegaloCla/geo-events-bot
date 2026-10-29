from unittest.mock import MagicMock, patch

import requests

from geo_events_bot.services.city_search import search_cities


def test_city_suggestions_include_region_and_skip_invalid_results():
    response = MagicMock()
    response.json.return_value = {
        "results": [
            {
                "id": 1,
                "name": "Roma",
                "latitude": 41.9,
                "longitude": 12.5,
                "admin1": "Lazio",
                "country": "Italia",
                "feature_code": "PPLC",
            },
            {"name": "Invalid"},
            {
                "id": 2,
                "name": "Romania",
                "latitude": 46,
                "longitude": 25,
                "feature_code": "PCLI",
            },
        ]
    }
    with patch(
        "geo_events_bot.services.city_search.requests.get", return_value=response
    ) as get:
        cities = search_cities("Rom")
    assert cities[0].label == "Roma, Lazio, Italia"  # noqa: S101
    assert len(cities) == 1  # noqa: S101
    assert get.call_args.kwargs["params"]["name"] == "Rom"  # noqa: S101


def test_short_city_query_does_not_call_api():
    with patch("geo_events_bot.services.city_search.requests.get") as get:
        assert search_cities("Ro") == []  # noqa: S101
    get.assert_not_called()


def test_city_service_failure_returns_no_suggestions():
    with patch(
        "geo_events_bot.services.city_search.requests.get",
        side_effect=requests.Timeout("Timeout"),
    ):
        assert search_cities("Roma") == []  # noqa: S101
