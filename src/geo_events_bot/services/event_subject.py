import asyncio
from typing import List

from geo_events_bot.models.observer import Observer


class EventSubject:
    def __init__(self):
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    async def notify_observers(self, message: str):
        tasks = [observer.send_message(message) for observer in self._observers]
        await asyncio.gather(*tasks)
