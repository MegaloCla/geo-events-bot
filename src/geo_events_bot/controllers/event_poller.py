from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from geo_events_bot.models.feature_collection_response import (
    Feature,
    format_event_message,
)
from geo_events_bot.services.event_cache import EventCache
from geo_events_bot.services.event_subject import EventSubject
from geo_events_bot.services.ingv_api import get_geo_events
from geo_events_bot.services.map_generator import MapGenerationError, generate_event_map
from geo_events_bot.services.settings_store import SettingsStore
from geo_events_bot.services.telegram_bot import TelegramBotObserver
from geo_events_bot.utils.logger import Logger

if TYPE_CHECKING:
    from geo_events_bot.models.location_filter import LocationFilter
    from geo_events_bot.models.settings import Settings

logger = Logger(__name__).get_logger()

URL = "http://webservices.ingv.it/fdsnws/event/1/query?format=geojson"


class Poller:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.bot = TelegramBotObserver(settings.telegram_token, settings.chat_id)
        self.subject = EventSubject()
        self._cache = EventCache()
        self._settings_store = SettingsStore(directory=self._cache.cache.directory)
        if self.settings.location_filter is None:
            self.settings.location_filter = self._settings_store.load_location_filter()

        self.subject.add_observer(self.bot)

    def set_location_filter(self, location_filter: LocationFilter | None) -> None:
        self._settings_store.save_location_filter(location_filter)
        self.settings.location_filter = location_filter

    async def start_polling(self):
        logger.info("Start polling INGV events data...")
        try:
            while True:
                await self._process_events_fetched(self.settings.min_magnitude)
                await asyncio.sleep(self.settings.polling_interval)
        finally:
            self._cache.close()

    async def _process_events_fetched(self, min_magnitude) -> None:
        data = await asyncio.to_thread(get_geo_events, URL)

        if data is not None:
            warning_events = _filter_warning_events(data.features, min_magnitude)
            if self.settings.location_filter is not None:
                warning_events = [
                    event
                    for event in warning_events
                    if self.settings.location_filter.distance_km(
                        event.geometry.coordinates[1], event.geometry.coordinates[0]
                    )
                    <= self.settings.location_filter.radius_km
                ]
            warning_events.reverse()

            await self._process_warning_events(warning_events)
        else:
            logger.warning("No data returned.")

    async def _process_warning_events(self, warning_events: list[Feature]) -> None:
        new_events_obtained = self._cache.get_new_events(warning_events)
        if new_events_obtained:
            logger.info("New events detected: %s", new_events_obtained)
            for event in new_events_obtained:
                await self._notify_event(event)
        else:
            logger.info("No new events detected.")

    async def _notify_event(self, event: Feature) -> None:
        title = (
            "Earthquake updated!"
            if event.properties.version > 1
            else "New earthquake detected!"
        )
        message = f"🚨 *{title}* 🚨\n{format_event_message(event)}"
        distance_km = None
        if self.settings.location_filter is not None:
            distance_km = self.settings.location_filter.distance_km(
                event.geometry.coordinates[1], event.geometry.coordinates[0]
            )
            if distance_km > self.settings.location_filter.radius_km:
                return
            message += f"\n📍 Distanza da {self.settings.location_filter.city}: {distance_km:.1f} km\n"
        photo_bytes = None
        try:
            photo_bytes = await asyncio.to_thread(
                generate_event_map, event, distance_km=distance_km
            )
        except (MapGenerationError, OSError):
            logger.exception(
                "Map unavailable for event %s; sending text", event.properties.event_id
            )
        reply_markup = _build_map_keyboard(event)
        if await self.subject.notify_observers(message, photo_bytes, reply_markup):
            self._cache.add_event(event)


def _build_map_keyboard(feature: Feature) -> InlineKeyboardMarkup:
    lat = feature.geometry.coordinates[1]
    lon = feature.geometry.coordinates[0]
    maps_url = (
        f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=10/{lat}/{lon}"
    )
    keyboard = [[InlineKeyboardButton("📍 OpenStreetMap", url=maps_url)]]
    return InlineKeyboardMarkup(keyboard)


def _filter_warning_events(
    features: list[Feature], min_magnitude: float
) -> list[Feature]:
    return list(
        filter(
            lambda geo_event: geo_event.properties.mag >= min_magnitude,
            features,
        )
    )
