from typing import Union

import requests
from pydantic import ValidationError

from geo_events_bot.models.feature_collection_response import Feature, FeatureCollection
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
    if data is None:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        return FeatureCollection.model_validate(data)
    features = []
    for feature_data in data["features"]:
        try:
            features.append(Feature.model_validate(feature_data))
        except ValidationError as err:  # noqa: PERF203 - preserve valid events
            logger.warning("Skipping invalid earthquake event: %s", err)
    return FeatureCollection.model_validate({**data, "features": features})


def get_geo_events(url: str) -> Union[FeatureCollection, None]:
    json_events = _get_earthquake_data(url)
    try:
        return _json_to_model(json_events)
    except ValidationError as err:
        logger.warning("Error in parsing data: %s", err)
        return None
