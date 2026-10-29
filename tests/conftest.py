from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from geo_events_bot.controllers import event_poller
from geo_events_bot.controllers.event_poller import Poller
from geo_events_bot.models.feature_collection_response import (
    Feature,
    Geometry,
    Properties,
)
from geo_events_bot.models.observer import Observer
from geo_events_bot.models.settings import Settings
from geo_events_bot.services.event_cache import EventCache
from geo_events_bot.services.event_subject import EventSubject


@pytest.fixture()
def subject():
    return EventSubject()


@pytest.fixture()
def observer():
    mock = MagicMock(Observer)
    mock.send_message = AsyncMock()
    mock.send_photo = AsyncMock()
    return mock


@pytest.fixture()
def feature():
    return Feature(
        type="Feature",
        properties=Properties(
            eventId=1,
            originId=1,
            time=datetime(2026, 1, 1, tzinfo=UTC),
            author="INGV",
            magType="ML",
            mag=3.0,
            magAuthor="INGV",
            type="earthquake",
            place="Roma",
            version=1,
            geojson_creationTime=datetime(2026, 1, 1, tzinfo=UTC),
        ),
        geometry=Geometry(type="Point", coordinates=[12.5, 41.9, 10.0]),
    )


@pytest.fixture()
def event_cache(tmp_path):
    cache = EventCache(cache_dir=str(tmp_path / "events"))
    yield cache
    cache.close()


@pytest.fixture()
def poller(monkeypatch, event_cache, observer):
    observer.bot = AsyncMock()
    token = "dummy_token"  # noqa: S105
    chat_id = "dummy_chat_id"
    monkeypatch.setattr(event_poller, "EventCache", lambda: event_cache)
    monkeypatch.setattr(event_poller, "TelegramBotObserver", lambda *_: observer)
    monkeypatch.setattr(
        event_poller, "generate_event_map", MagicMock(return_value=b"map")
    )
    return Poller(Settings(telegram_token=token, chat_id=chat_id))
