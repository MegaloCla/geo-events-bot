from unittest.mock import AsyncMock, MagicMock

import pytest

from geo_events_bot.controllers.event_poller import Poller
from geo_events_bot.models.observer import Observer
from geo_events_bot.services.event_cache import EventCache
from geo_events_bot.services.event_subject import EventSubject


@pytest.fixture()
def subject():
    return EventSubject()


@pytest.fixture()
def observer():
    return MagicMock(Observer)


@pytest.fixture()
def poller():
    token = "dummy_token"  # noqa: S105
    chat_id = "dummy_chat_id"
    poller_instance = Poller(token, chat_id)
    poller_instance._cache = MagicMock(EventCache)  # noqa: SLF001
    poller_instance.subject = MagicMock(EventSubject)
    poller_instance.subject.add_observer = MagicMock()
    poller_instance.subject.notify_observers = AsyncMock()
    return poller_instance
