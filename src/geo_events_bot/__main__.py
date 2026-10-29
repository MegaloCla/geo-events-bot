import asyncio

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
)

from geo_events_bot.controllers.event_poller import Poller
from geo_events_bot.controllers.location_controller import LocationController
from geo_events_bot.models.settings import Settings
from geo_events_bot.utils.env_var import get_env_variable


async def run_bot(poller: Poller) -> None:
    controller = LocationController(poller)

    application = Application.builder().bot(poller.bot.bot).build()
    application.add_handler(CommandHandler(["start", "zona"], controller.show))
    application.add_handler(InlineQueryHandler(controller.search))
    application.add_handler(CallbackQueryHandler(controller.apply, pattern=r"^zone:"))

    async with application:
        await application.start()
        try:
            if application.updater is not None:
                await application.updater.start_polling(
                    allowed_updates=["message", "inline_query", "callback_query"]
                )
            await poller.start_polling()
        finally:
            if application.updater is not None and application.updater.running:
                await application.updater.stop()
            await application.stop()


if __name__ == "__main__":
    settings = Settings(
        telegram_token=get_env_variable("TELEGRAM_TOKEN"),
        chat_id=get_env_variable("CHAT_TELEGRAM_ID"),
    )

    asyncio.run(run_bot(Poller(settings)))
