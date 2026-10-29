from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.asyncio()


async def test_run_bot_stops_updates_and_application_on_exit(poller):
    import asyncio

    from geo_events_bot.__main__ import run_bot

    application = MagicMock()
    application.__aenter__ = AsyncMock(return_value=application)
    application.__aexit__ = AsyncMock(return_value=False)
    application.start = AsyncMock()
    application.stop = AsyncMock()
    application.updater.start_polling = AsyncMock()
    application.updater.stop = AsyncMock()
    application.updater.running = True
    poller.start_polling = AsyncMock(side_effect=asyncio.CancelledError())
    with patch("geo_events_bot.__main__.Application.builder") as builder:
        builder.return_value.bot.return_value.build.return_value = application
        with pytest.raises(asyncio.CancelledError):
            await run_bot(poller)
    application.start.assert_awaited_once()
    application.updater.start_polling.assert_awaited_once()
    application.updater.stop.assert_awaited_once()
    application.stop.assert_awaited_once()
