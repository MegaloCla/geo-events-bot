from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from geo_events_bot.models.observer import Observer
from geo_events_bot.utils.logger import Logger

logger = Logger().get_logger()


class TelegramBotObserver(Observer):
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_message(self, message: str):
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                read_timeout=15,
                write_timeout=15,
            )
        except TelegramError as e:
            logger.error("Error sending message: %s", e, exc_info=True)  # noqa: G201
