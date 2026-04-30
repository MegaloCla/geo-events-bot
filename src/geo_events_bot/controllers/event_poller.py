import asyncio
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from geo_events_bot.models.feature_collection_response import (
    Feature,
    format_event_message,
)
from geo_events_bot.services.event_cache import EventCache
from geo_events_bot.services.event_subject import EventSubject
from geo_events_bot.services.ingv_api import get_geo_events
from geo_events_bot.services.map_generator import generate_event_map
from geo_events_bot.services.telegram_bot import TelegramBotObserver
from geo_events_bot.utils.logger import Logger

logger = Logger(__name__).get_logger()

URL = "http://webservices.ingv.it/fdsnws/event/1/query?format=geojson"


class Poller:
    def __init__(self, token: str, chat_id: str):
        self.bot = TelegramBotObserver(token, chat_id)
        self.subject = EventSubject()
        self._cache = EventCache()

        self.subject.add_observer(self.bot)

    async def start_polling(self, polling_interval, min_magnitude=2):
        logger.info("Start polling INGV events data...")
        try:
            while True:
                await self._process_events_fetched(min_magnitude)
                await asyncio.sleep(polling_interval)
        finally:
            self._cache.close()

    async def _process_events_fetched(self, min_magnitude) -> None:
        data = await asyncio.to_thread(get_geo_events, URL)

        if data is not None:
            warning_events = _filter_warning_events(data.features, min_magnitude)
            warning_events.reverse()

            await self._process_warning_events(warning_events)
        else:
            logger.warning("No data returned.")

    async def _process_warning_events(self, warning_events: List[Feature]) -> None:
        new_events_obtained = self._cache.get_new_events(warning_events)
        if new_events_obtained:
            logger.info("New events detected: %s", new_events_obtained)
            for event in new_events_obtained:
                message = (
                    f"🚨 *New earthquake detected!* 🚨\n{format_event_message(event)}"
                )
                photo_bytes = await asyncio.to_thread(generate_event_map, event)
                reply_markup = _build_map_keyboard(event)
                await self.subject.notify_observers(message, photo_bytes, reply_markup)
        else:
            logger.info("No new events detected.")


def _build_map_keyboard(feature: Feature) -> InlineKeyboardMarkup:
    lat = feature.geometry.coordinates[1]
    lon = feature.geometry.coordinates[0]
    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    keyboard = [[InlineKeyboardButton("📍 OpenStreetMap", url=maps_url)]]
    return InlineKeyboardMarkup(keyboard)


def _filter_warning_events(
    features: List[Feature], min_magnitude: float
) -> List[Feature]:
    return list(
        filter(
            lambda geo_event: geo_event.properties.mag >= min_magnitude,
            features,
        )
    )
