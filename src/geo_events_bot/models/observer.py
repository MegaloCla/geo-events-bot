from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import InlineKeyboardMarkup


class Observer(ABC):
    @abstractmethod
    async def send_message(
        self, message: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None: ...

    @abstractmethod
    async def send_photo(
        self,
        photo_bytes: bytes,
        caption: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None: ...
