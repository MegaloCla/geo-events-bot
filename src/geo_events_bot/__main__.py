import asyncio

from geo_events_bot.controllers.event_poller import Poller
from geo_events_bot.utils.env_var import get_env_variable

if __name__ == "__main__":
    TOKEN = get_env_variable("TELEGRAM_TOKEN")
    CHAT_ID = get_env_variable("CHAT_TELEGRAM_ID")

    poller = Poller(token=TOKEN, chat_id=CHAT_ID)

    asyncio.run(poller.start_polling(3))
