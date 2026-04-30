from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from geo_events_bot.utils.logger import Logger

if TYPE_CHECKING:
    from telegram import InlineKeyboardMarkup

    from geo_events_bot.models.observer import Observer

logger = Logger(__name__).get_logger()


class EventSubject:
    def __init__(self):
        self._observers: list[Observer] = []

    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    async def notify_observers(
        self,
        message: str,
        photo_bytes: bytes | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        tasks = []
        for observer in self._observers:
            if photo_bytes:
                tasks.append(observer.send_photo(photo_bytes, message, reply_markup))
            else:
                tasks.append(observer.send_message(message, reply_markup))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logger.error("Observer notification failed: %s", result)
