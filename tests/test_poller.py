import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from telegram.error import TelegramError

from geo_events_bot.controllers import event_poller
from geo_events_bot.models.feature_collection_response import FeatureCollection
from geo_events_bot.services.map_generator import MapGenerationError

pytestmark = pytest.mark.asyncio()


async def test_no_data(poller, observer):
    with patch.object(event_poller, "get_geo_events", return_value=None):
        await poller._process_events_fetched(min_magnitude=2)  # noqa: SLF001
    observer.send_photo.assert_not_called()


async def test_notifies_once_after_success(poller, observer, feature):
    data = FeatureCollection(type="FeatureCollection", features=[feature])
    with patch.object(event_poller, "get_geo_events", return_value=data):
        await poller._process_events_fetched(min_magnitude=2)  # noqa: SLF001
        await poller._process_events_fetched(min_magnitude=2)  # noqa: SLF001
    observer.send_photo.assert_awaited_once()
    photo, message, keyboard = observer.send_photo.call_args.args
    assert photo == b"map"  # noqa: S101
    assert "New earthquake detected!" in message  # noqa: S101
    assert "Roma" in message  # noqa: S101
    assert keyboard.inline_keyboard  # noqa: S101


async def test_failed_delivery_is_retried(poller, observer, feature, event_cache):
    observer.send_photo.side_effect = [TelegramError("Unavailable"), None]
    await poller._process_warning_events([feature])  # noqa: SLF001
    assert event_cache.get_new_events([feature]) == [feature]  # noqa: S101
    await poller._process_warning_events([feature])  # noqa: SLF001
    assert event_cache.get_new_events([feature]) == []  # noqa: S101
    assert observer.send_photo.await_count == 2  # noqa: S101, PLR2004


@pytest.mark.parametrize("error", [OSError("Image"), MapGenerationError("Tiles")])
async def test_map_failure_sends_text(poller, observer, feature, event_cache, error):
    with patch.object(event_poller, "generate_event_map", side_effect=error):
        await poller._process_warning_events([feature])  # noqa: SLF001
    observer.send_photo.assert_not_called()
    observer.send_message.assert_awaited_once()
    assert "Roma" in observer.send_message.call_args.args[0]  # noqa: S101
    assert event_cache.get_new_events([feature]) == []  # noqa: S101


async def test_failed_event_does_not_block_next(poller, observer, feature, event_cache):
    second = feature.model_copy(
        update={"properties": feature.properties.model_copy(update={"event_id": 2})}
    )
    observer.send_photo.side_effect = [TelegramError("Unavailable"), None]
    await poller._process_warning_events([feature, second])  # noqa: SLF001
    assert event_cache.get_new_events([feature, second]) == [feature]  # noqa: S101


async def test_revisions_are_notified_once(poller, observer, feature):
    revised = feature.model_copy(
        update={"properties": feature.properties.model_copy(update={"version": 2})}
    )
    await poller._process_warning_events([feature])  # noqa: SLF001
    await poller._process_warning_events([revised])  # noqa: SLF001
    await poller._process_warning_events([revised, feature])  # noqa: SLF001
    assert observer.send_photo.await_count == 2  # noqa: S101, PLR2004
    assert "Earthquake updated!" in observer.send_photo.call_args.args[1]  # noqa: S101


async def test_failed_revision_is_retried(poller, observer, feature, event_cache):
    event_cache.add_event(feature)
    revised = feature.model_copy(
        update={"properties": feature.properties.model_copy(update={"version": 2})}
    )
    observer.send_photo.side_effect = [TelegramError("Unavailable"), None]
    await poller._process_warning_events([revised])  # noqa: SLF001
    assert event_cache.get_new_events([feature, revised]) == [revised]  # noqa: S101
    await poller._process_warning_events([revised])  # noqa: SLF001
    assert event_cache.get_new_events([revised]) == []  # noqa: S101


async def test_unexpected_processing_error_propagates(poller, feature, event_cache):
    with (
        patch.object(
            event_poller,
            "format_event_message",
            side_effect=ValueError("Invalid"),
        ),
        pytest.raises(ValueError, match="Invalid"),
    ):
        await poller._process_warning_events([feature])  # noqa: SLF001
    assert event_cache.get_new_events([feature]) == [feature]  # noqa: S101


async def test_polling_repeats_and_closes_cache(poller):
    poller._process_events_fetched = AsyncMock()  # noqa: SLF001
    with (
        patch.object(event_poller.asyncio, "sleep", new_callable=AsyncMock) as sleep,
        patch.object(poller._cache, "close") as close,  # noqa: SLF001
    ):
        sleep.side_effect = [None, asyncio.CancelledError()]
        with pytest.raises(asyncio.CancelledError):
            await poller.start_polling()
    assert poller._process_events_fetched.await_count == 2  # noqa: SLF001, S101, PLR2004
    close.assert_called_once()


async def test_unexpected_polling_error_propagates_and_closes_cache(poller):
    poller._process_events_fetched = AsyncMock(side_effect=TypeError("Bug"))  # noqa: SLF001
    with (
        patch.object(poller._cache, "close") as close,  # noqa: SLF001
        pytest.raises(TypeError, match="Bug"),
    ):
        await poller.start_polling()
    close.assert_called_once()


async def test_unexpected_map_error_propagates(poller, observer, feature, event_cache):
    with (
        patch.object(event_poller, "generate_event_map", side_effect=TypeError("Bug")),
        pytest.raises(TypeError, match="Bug"),
    ):
        await poller._process_warning_events([feature])  # noqa: SLF001
    observer.send_message.assert_not_called()
    observer.send_photo.assert_not_called()
    assert event_cache.get_new_events([feature]) == [feature]  # noqa: S101


async def test_filter_warning_events(feature):
    below_threshold = feature.model_copy(
        update={"properties": feature.properties.model_copy(update={"mag": 1.0})}
    )
    on_threshold = feature.model_copy(
        update={"properties": feature.properties.model_copy(update={"mag": 2.0})}
    )
    filtered = event_poller._filter_warning_events(  # noqa: SLF001
        [below_threshold, on_threshold, feature], 2.0
    )
    assert filtered == [on_threshold, feature]  # noqa: S101


async def test_location_filters_by_distance_and_magnitude(
    poller, feature, observer, event_cache
):
    from geo_events_bot.models.location_filter import LocationFilter

    poller.settings.location_filter = LocationFilter(
        city="Roma", latitude=41.9, longitude=12.5, radius_km=50
    )
    far = feature.model_copy(
        update={
            "properties": feature.properties.model_copy(update={"event_id": 2}),
            "geometry": feature.geometry.model_copy(
                update={"coordinates": [9.19, 45.46, 10]}
            ),
        }
    )
    weak = feature.model_copy(
        update={
            "properties": feature.properties.model_copy(
                update={"event_id": 3, "mag": 1.0}
            ),
        }
    )
    data = FeatureCollection(type="FeatureCollection", features=[feature, far, weak])
    with patch.object(event_poller, "get_geo_events", return_value=data):
        await poller._process_events_fetched(min_magnitude=2)  # noqa: SLF001
    observer.send_photo.assert_awaited_once()
    assert "Distanza da Roma: 0.0 km" in observer.send_photo.call_args.args[1]  # noqa: S101
    assert event_cache.get_new_events([far, weak]) == [far, weak]  # noqa: S101


async def test_radius_boundary_is_inclusive(poller, feature, observer):
    from geo_events_bot.models.location_filter import LocationFilter

    location = LocationFilter(city="Test", latitude=42, longitude=12.5, radius_km=100)
    location.radius_km = location.distance_km(41.9, 12.5)
    poller.settings.location_filter = location
    await poller._notify_event(feature)  # noqa: SLF001
    observer.send_photo.assert_awaited_once()


async def test_changed_filter_excludes_pending_event(
    poller, feature, observer, event_cache
):
    from geo_events_bot.models.location_filter import LocationFilter

    poller.settings.location_filter = LocationFilter(
        city="Milano", latitude=45.46, longitude=9.19, radius_km=50
    )
    await poller._process_warning_events([feature])  # noqa: SLF001
    observer.send_photo.assert_not_called()
    assert event_cache.get_new_events([feature]) == [feature]  # noqa: S101
