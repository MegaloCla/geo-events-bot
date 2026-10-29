from __future__ import annotations

import requests
from pydantic import ValidationError

from geo_events_bot.models.city import City
from geo_events_bot.utils.logger import Logger

logger = Logger(__name__).get_logger()
MIN_QUERY_LENGTH = 3


def search_cities(name: str) -> list[City]:
    if len(name.strip()) < MIN_QUERY_LENGTH:
        return []
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": name, "count": "5", "language": "it", "format": "json"},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        logger.exception("City search unavailable")
        return []
    if not isinstance(data, dict) or not isinstance(data.get("results", []), list):
        logger.warning("Invalid city search response")
        return []
    cities = []
    for item in data.get("results", []):
        try:
            city = City.model_validate(item)
            if city.feature_code.startswith("PPL"):
                cities.append(city)
        except ValidationError:  # noqa: PERF203 - skip malformed results
            logger.warning("Skipping invalid city search result")
    return cities
