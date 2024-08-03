from typing import Union

import requests
from pydantic import ValidationError

from geo_events_bot.models.feature_collection_response import FeatureCollection
from geo_events_bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


def _get_earthquake_data(url) -> Union[dict, None]:
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        data = response.json()
        logger.info("Earthquake data fetched successfully")
        return data  # noqa: TRY300
    except requests.RequestException as e:
        logger.error("Error fetching earthquake data: %s", e, exc_info=True)  # noqa: G201
        return None


def _json_to_model(data) -> Union[FeatureCollection, None]:
    try:
        return FeatureCollection(**data)
    except ValidationError:
        logger.warning("Different kind of Event caught: %s", data, exc_info=True)
        return None


def get_geo_events(url: str) -> Union[FeatureCollection, None]:
    json_events = _get_earthquake_data(url)
    return _json_to_model(json_events)
