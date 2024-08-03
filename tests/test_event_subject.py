from unittest.mock import AsyncMock

import pytest


def test_add_observer(subject, observer):
    subject.add_observer(observer)
    assert observer in subject._observers  # noqa: SLF001, S101


def test_add_observer_duplicate(subject, observer):
    subject.add_observer(observer)
    subject.add_observer(observer)
    assert subject._observers.count(observer) == 1  # noqa: SLF001, S101


def test_remove_observer(subject, observer):
    subject.add_observer(observer)
    subject.remove_observer(observer)
    assert observer not in subject._observers  # noqa: SLF001, S101


def test_remove_observer_not_present(subject, observer):
    subject.remove_observer(observer)
    assert observer not in subject._observers  # noqa: SLF001, S101


@pytest.mark.asyncio()
async def test_notify_observers(subject, observer):
    observer.send_message = AsyncMock()
    subject.add_observer(observer)

    message = "Test message"
    await subject.notify_observers(message)

    observer.send_message.assert_called_once_with(message)
