import asyncio

import pytest

from geo_events.models.observer import Observer


class TelegramBotObserverMock(Observer):
    async def send_message(self, message: str):
        await asyncio.sleep(1)
        return message


@pytest.fixture()
def telegram_observer_mock():
    return TelegramBotObserverMock()
