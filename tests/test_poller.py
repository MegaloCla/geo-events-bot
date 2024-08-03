import datetime
from unittest.mock import MagicMock, patch

import pytest

import geo_events_bot.controllers.event_poller
from geo_events_bot.models.feature_collection_response import (
    Feature,
    Geometry,
    Properties,
)


@pytest.mark.asyncio()
@patch("geo_events_bot.controllers.event_poller.get_geo_events")
async def test_start_polling(mock_get_geo_events, poller):
    mock_get_geo_events.return_value = None

    await poller._process_events_fetched(min_magnitude=2)  # noqa: SLF001

    mock_get_geo_events.assert_called_once()
    poller._cache.get_new_events.assert_not_called()  # noqa: SLF001


@pytest.mark.asyncio()
@patch("geo_events_bot.controllers.event_poller.get_geo_events")
async def test_new_events_detected(mock_get_geo_events, poller):
    properties = Properties(
        eventId=1,
        originId=1,
        time=datetime.datetime.now(datetime.UTC),
        author="author",
        magType="type",
        mag=3.0,
        magAuthor="mag_author",
        type="type",
        place="place",
        version=1,
        geojson_creationTime=datetime.datetime.now(datetime.UTC),
    )
    geometry = Geometry(type="Point", coordinates=[0.0, 0.0])
    feature = Feature(type="Feature", properties=properties, geometry=geometry)

    mock_get_geo_events.return_value = MagicMock(features=[feature])
    poller._cache.get_new_events.return_value = [feature]  # noqa: SLF001

    await poller._process_events_fetched(min_magnitude=2)  # noqa: SLF001

    mock_get_geo_events.assert_called_once()


def test_filter_warning_events():
    features = [
        Feature(
            type="Feature",
            properties=Properties(
                eventId=1,
                originId=1,
                time=datetime.datetime.now(datetime.UTC),
                author="author1",
                magType="type1",
                mag=1.0,
                magAuthor="mag_author1",
                type="type1",
                place="place1",
                version=1,
                geojson_creationTime=datetime.datetime.now(datetime.UTC),
            ),
            geometry=Geometry(type="Point", coordinates=[0.0, 0.0]),
        ),
        Feature(
            type="Feature",
            properties=Properties(
                eventId=2,
                originId=2,
                time=datetime.datetime.now(datetime.UTC),
                author="author2",
                magType="type2",
                mag=3.0,
                magAuthor="mag_author2",
                type="type2",
                place="place2",
                version=1,
                geojson_creationTime=datetime.datetime.now(datetime.UTC),
            ),
            geometry=Geometry(type="Point", coordinates=[1.0, 1.0]),
        ),
        Feature(
            type="Feature",
            properties=Properties(
                eventId=3,
                originId=3,
                time=datetime.datetime.now(datetime.UTC),
                author="author3",
                magType="type3",
                mag=2.5,
                magAuthor="mag_author3",
                type="type3",
                place="place3",
                version=1,
                geojson_creationTime=datetime.datetime.now(datetime.UTC),
            ),
            geometry=Geometry(type="Point", coordinates=[2.0, 2.0]),
        ),
    ]
    filtered_events = geo_events_bot.controllers.event_poller._filter_warning_events(  # noqa: SLF001
        features, 2.0
    )
    assert len(filtered_events) == 2  # noqa: PLR2004, S101
    assert filtered_events[0].properties.mag == 3.0  # noqa: PLR2004, S101
    assert filtered_events[1].properties.mag == 2.5  # noqa: PLR2004, S101
