import asyncio
from typing import List

from geo_events_bot.models.feature_collection_response import (
    Feature,
    format_event_message,
)
from geo_events_bot.services.event_cache import EventCache
from geo_events_bot.services.event_subject import EventSubject
from geo_events_bot.services.ingv_api import get_earthquake_data, json_to_model
from geo_events_bot.services.telegram_bot import TelegramBotObserver
from geo_events_bot.utils.logger import Logger

logger = Logger(__name__).get_logger()

URL = "http://webservices.ingv.it/fdsnws/event/1/query?format=geojson"


class Poller:
    def __init__(self, token, chat_id):
        self.bot = TelegramBotObserver(token, chat_id)
        self.subject = EventSubject()
        self._cache = EventCache()

        self.subject.add_observer(self.bot)

    async def start_polling(self, polling_interval=3, min_magnitude=2):
        logger.info("Start polling INGV events data...")

        try:
            while True:
                json_events = get_earthquake_data(URL)
                data = json_to_model(json_events)

                if data is not None:
                    warning_events = _filter_warning_events(
                        data.features, min_magnitude
                    )

                    new_events_obtained = self._cache.get_new_events(warning_events)
                    if new_events_obtained:
                        logger.info("New events detected: %s", new_events_obtained)
                        for event in new_events_obtained:
                            message = f"🚨 **New earthquake detected!** 🚨\n{format_event_message(event)}"
                            await self.subject.notify_observers(message)
                    else:
                        logger.info("No new events detected.")

                    await asyncio.sleep(polling_interval)
        finally:
            self._cache.close()


def _filter_warning_events(
    features: List[Feature], min_magnitude: float
) -> List[Feature]:
    return list(
        filter(
            lambda geo_event: geo_event.properties.mag >= min_magnitude,
            features,
        )
    )
