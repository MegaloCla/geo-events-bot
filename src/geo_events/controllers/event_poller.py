import asyncio

from geo_events.models.feature_collection_response import format_event_message
from geo_events.services.event_cache import EventCache
from geo_events.services.event_subject import EventSubject
from geo_events.services.ingv_api import get_earthquake_data, json_to_model
from geo_events.services.telegram_bot import TelegramBotObserver
from geo_events.utils.logger import Logger

logger = Logger(__name__).get_logger()

URL = "http://webservices.ingv.it/fdsnws/event/1/query?format=geojson"


class Poller:
    def __init__(self, bot: TelegramBotObserver):
        self.bot = bot
        self.subject = EventSubject()
        self._cache = EventCache()

        self.subject.add_observer(bot)

    async def start_polling(self, polling_interval=2, min_magnitude=2):
        logger.info("Start polling INGV events data...")

        try:
            while True:
                json_events = get_earthquake_data(URL)
                data = json_to_model(json_events)

                warning_events = list(
                    filter(
                        lambda geo_event: geo_event.properties.mag > min_magnitude,
                        data.features,  # type: ignore  # noqa: PGH003
                    )
                )

                new_events = self._cache.get_new_events(warning_events)
                if new_events:
                    logger.info("New events detected: %s", new_events)
                    for event in new_events:
                        message = (
                            f"New earthquake detected: \n{format_event_message(event)}"
                        )
                        await self.subject.notify_observers(message)
                else:
                    logger.info("No new events detected.")

                await asyncio.sleep(polling_interval)
        finally:
            self._cache.close()
