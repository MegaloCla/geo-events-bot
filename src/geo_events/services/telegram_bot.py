from telegram import Bot
from telegram.error import TelegramError

from geo_events.services.observer import Observer
from geo_events.utils.logger import Logger

logger = Logger().get_logger()


class TelegramBotObserver(Observer):
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_message(self, message: str):
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except TelegramError as e:
            logger.error("Error sending message: %s", e, exc_info=True)  # noqa: G201
