from unittest.mock import AsyncMock, patch

import pytest
from telegram.error import TelegramError

from geo_events_bot.services.telegram_bot import TelegramBotObserver


@pytest.mark.asyncio()
@pytest.mark.parametrize("method", ["send_message", "send_photo"])
async def test_delivery_errors_propagate(method):
    bot = AsyncMock()
    getattr(bot, method).side_effect = TelegramError("Unavailable")
    with patch("geo_events_bot.services.telegram_bot.Bot", return_value=bot):
        observer = TelegramBotObserver("test", "chat")
    args = ("message",) if method == "send_message" else (b"photo", "caption")
    with pytest.raises(TelegramError, match="Unavailable"):
        await getattr(observer, method)(*args)
