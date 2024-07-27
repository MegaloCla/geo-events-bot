import asyncio

from geo_events.controllers.event_poller import Poller
from geo_events.services.telegram_bot import TelegramBotObserver
from geo_events.utils.env_var import get_env_variable

if __name__ == "__main__":
    TOKEN = get_env_variable("TELEGRAM_TOKEN")
    CHAT_ID = get_env_variable("CHAT_TELEGRAM_ID")

    telegram_bot = TelegramBotObserver(token=TOKEN, chat_id=CHAT_ID)

    poller = Poller(telegram_bot)

    asyncio.run(poller.start_polling(3))
