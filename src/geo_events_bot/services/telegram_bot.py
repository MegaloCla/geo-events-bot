from __future__ import annotations

from telegram import Bot, InlineKeyboardMarkup
from telegram.constants import ParseMode

from geo_events_bot.models.observer import Observer


class TelegramBotObserver(Observer):
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_message(
        self, message: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
            read_timeout=15,
            write_timeout=15,
        )

    async def send_photo(
        self,
        photo_bytes: bytes,
        caption: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        await self.bot.send_photo(
            chat_id=self.chat_id,
            photo=photo_bytes,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
            read_timeout=15,
            write_timeout=15,
        )
